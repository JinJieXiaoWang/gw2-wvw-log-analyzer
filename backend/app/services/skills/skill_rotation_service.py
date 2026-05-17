# 模块功能: 技能循环分析服务
# 说明: 从 EI 同步数据中提取真实技能循环，提供分析、对比和报告导出

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.log.zevtc_data import EiPlayer, EiSkillMap
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


# ==================== 核心数据查询 ====================

def _get_ei_player(log_id: int, account: str, db: Session) -> Optional[EiPlayer]:
    """查询指定日志和账号的EI玩家数据"""
    return db.query(EiPlayer).filter(
        EiPlayer.log_id == log_id,
        EiPlayer.account == account
    ).first()


def _get_skill_map(log_id: int, db: Session) -> Dict[int, Dict[str, Any]]:
    """构建技能ID到技能信息的映射"""
    skills = db.query(EiSkillMap).filter(EiSkillMap.log_id == log_id).all()
    result = {}
    for s in skills:
        # skill_key 格式为 "s12345" 或 "-2"
        key = s.skill_key
        if key.startswith("s"):
            try:
                skill_id = int(key[1:])
            except ValueError:
                continue
        else:
            try:
                skill_id = int(key)
            except ValueError:
                continue
        result[skill_id] = {
            "name": s.name or f"Skill {skill_id}",
            "icon": s.icon or "",
            "gw2_skill_id": s.gw2_skill_id,
            "auto_attack": bool(s.auto_attack),
            "is_swap": bool(s.is_swap),
            "is_instant_cast": bool(s.is_instant_cast),
            "is_trait_proc": bool(s.is_trait_proc),
        }
    return result


def _get_fight_stats(log_id: int, account: str, db: Session) -> Optional[FightStats]:
    """查询玩家的战斗统计数据"""
    fights = db.query(Fight).filter(Fight.log_id == log_id).all()
    if not fights:
        return None
    fight_ids = [f.id for f in fights]
    return db.query(FightStats).filter(
        FightStats.fight_id.in_(fight_ids),
        FightStats.account == account
    ).first()


def _parse_rotation(rotation_json: List[Dict], skill_map: Dict[int, Dict]) -> List[Dict[str, Any]]:
    """将EI rotation JSON解析为标准化事件列表"""
    events = []
    event_id = 0
    for skill_entry in rotation_json:
        skill_id = skill_entry.get("id", 0)
        skill_info = skill_map.get(skill_id, {
            "name": f"Skill {skill_id}",
            "icon": "",
            "auto_attack": False,
            "is_swap": skill_id == -2,
            "is_instant_cast": False,
            "is_trait_proc": False,
        })
        for cast in skill_entry.get("skills", []):
            duration = cast.get("duration", 0) or 0
            time_gained = cast.get("timeGained", 0) or 0
            # 判断状态: full(完整施放), interrupted(打断), instant(瞬发), swap(武器切换)
            if skill_info.get("is_swap"):
                state = "swap"
            elif skill_info.get("is_instant_cast"):
                state = "instant"
            elif duration > 0 and time_gained < 0:
                state = "interrupted"
            else:
                state = "full"
            events.append({
                "id": event_id,
                "cast_time": cast.get("castTime", 0),
                "duration": duration,
                "skill_id": skill_id,
                "skill_name": skill_info.get("name", f"Skill {skill_id}"),
                "skill_icon": skill_info.get("icon", ""),
                "state": state,
                "time_gained": time_gained,
                "quickness": cast.get("quickness", 0),
                "auto_attack": skill_info.get("auto_attack", False),
                "is_swap": skill_info.get("is_swap", False),
                "is_trait_proc": skill_info.get("is_trait_proc", False),
            })
            event_id += 1
    # 按施放时间排序
    events.sort(key=lambda e: e["cast_time"])
    # 重新分配连续ID
    for i, e in enumerate(events):
        e["id"] = i
    return events


def _build_cycles(events: List[Dict]) -> List[Dict[str, Any]]:
    """将事件列表按武器切换分割为循环"""
    if not events:
        return []
    cycles = []
    current_cycle = []
    cycle_id = 0
    for evt in events:
        if evt["is_swap"] and current_cycle:
            # 结束当前循环，开始新循环
            cycles.append(_finalize_cycle(current_cycle, cycle_id))
            cycle_id += 1
            current_cycle = [evt]
        else:
            current_cycle.append(evt)
    # 处理最后一个循环
    if current_cycle:
        cycles.append(_finalize_cycle(current_cycle, cycle_id))
    return cycles


def _finalize_cycle(events: List[Dict], cycle_id: int) -> Dict[str, Any]:
    """完成循环数据计算"""
    total_damage = sum(e.get("damage", 0) for e in events)
    interrupted_count = sum(1 for e in events if e["state"] == "interrupted")
    start_time = events[0]["cast_time"] if events else 0
    end_time = events[-1]["cast_time"] + events[-1].get("duration", 0) if events else 0
    return {
        "id": cycle_id,
        "events": events,
        "duration": end_time - start_time,
        "start": start_time,
        "end": end_time,
        "interrupted_count": interrupted_count,
        "total_damage": total_damage,
        "skill_count": len([e for e in events if not e.get("is_swap")]),
    }


def _calculate_stats(events: List[Dict], fight_stats: Optional[FightStats]) -> Dict[str, Any]:
    """计算技能循环统计指标"""
    if not events:
        return {
            "total_casts": 0,
            "total_damage": 0,
            "avg_dps": 0,
            "skill_cast_uptime": 0,
            "interrupted_rate": 0,
            "auto_attack_rate": 0,
            "top_skills": [],
            "buff_coverage": {},
        }
    total_casts = len([e for e in events if not e.get("is_swap")])
    interrupted = sum(1 for e in events if e["state"] == "interrupted")
    auto_attacks = sum(1 for e in events if e.get("auto_attack"))
    # 技能占用时间 / 总战斗时间
    total_duration = events[-1]["cast_time"] + events[-1].get("duration", 0) - events[0]["cast_time"] if len(events) > 1 else 1
    cast_time = sum(e.get("duration", 0) for e in events if e.get("duration", 0) > 0)
    uptime = (cast_time / total_duration * 100) if total_duration > 0 else 0
    # Top skills
    skill_counts = {}
    for e in events:
        sid = e["skill_id"]
        if sid not in skill_counts:
            skill_counts[sid] = {"skill_id": sid, "skill_name": e["skill_name"], "skill_icon": e["skill_icon"], "count": 0}
        skill_counts[sid]["count"] += 1
    top_skills = sorted(skill_counts.values(), key=lambda x: x["count"], reverse=True)[:5]
    total_skill_casts = sum(s["count"] for s in top_skills) or 1
    for s in top_skills:
        s["percent"] = round(s["count"] / total_skill_casts * 100, 1)
    return {
        "total_casts": total_casts,
        "total_damage": getattr(fight_stats, "damage", 0) or 0,
        "avg_dps": getattr(fight_stats, "dps", 0) or 0,
        "skill_cast_uptime": round(uptime, 1),
        "interrupted_rate": round(interrupted / total_casts * 100, 1) if total_casts else 0,
        "auto_attack_rate": round(auto_attacks / total_casts * 100, 1) if total_casts else 0,
        "top_skills": top_skills,
        "buff_coverage": {
            "Might": getattr(fight_stats, "might_uptime", 0) or 0,
            "Fury": getattr(fight_stats, "fury_uptime", 0) or 0,
            "Quickness": getattr(fight_stats, "quickness_uptime", 0) or 0,
            "Alacrity": getattr(fight_stats, "alacrity_uptime", 0) or 0,
            "Protection": getattr(fight_stats, "protection_uptime", 0) or 0,
            "Stability": getattr(fight_stats, "stability_uptime", 0) or 0,
        } if fight_stats else {},
    }


def _generate_mistakes(events: List[Dict]) -> List[Dict[str, Any]]:
    """基于真实事件生成失误分析"""
    mistakes = []
    interrupted_events = [e for e in events if e["state"] == "interrupted"]
    for i, evt in enumerate(interrupted_events[:3]):
        mistakes.append({
            "type": "interrupt",
            "description": f"在 {evt['cast_time']//1000} 秒打断了 [{evt['skill_name']}] 的施放",
            "impact": "high" if i == 0 else "medium",
            "cast_time": evt["cast_time"],
            "skill_name": evt["skill_name"],
        })
    # 检测长时间无技能施放（>5秒）
    for i in range(1, len(events)):
        gap = events[i]["cast_time"] - events[i-1]["cast_time"]
        if gap > 5000 and not events[i].get("is_swap") and not events[i-1].get("is_swap"):
            mistakes.append({
                "type": "downtime",
                "description": f"在 {events[i-1]['cast_time']//1000} 秒出现 {gap//1000} 秒的技能空档",
                "impact": "medium",
                "cast_time": events[i-1]["cast_time"],
                "duration": gap,
            })
            if len(mistakes) >= 5:
                break
    return mistakes


def _generate_optimizations(events: List[Dict], fight_stats: Optional[FightStats]) -> List[Dict[str, Any]]:
    """生成优化建议"""
    opts = []
    if not events:
        return opts
    # 检查打断率
    interrupted = sum(1 for e in events if e["state"] == "interrupted")
    total = len([e for e in events if not e.get("is_swap")])
    if total > 0 and interrupted / total > 0.05:
        opts.append({
            "priority": "high",
            "title": "降低技能打断率",
            "description": f"当前打断率为 {interrupted}/{total} ({round(interrupted/total*100,1)}%)，建议在安全位置完成技能施放",
            "expected_impact": f"预计可减少 {interrupted} 次技能损失",
        })
    # 检查Buff覆盖
    if fight_stats:
        might = getattr(fight_stats, "might_uptime", 0) or 0
        if might < 80:
            opts.append({
                "priority": "medium",
                "title": "提升威能覆盖率",
                "description": f"当前威能覆盖率为 {round(might,1)}%，建议提升至85%以上",
                "expected_impact": "预计可提升5-8%的总伤害",
            })
        quickness = getattr(fight_stats, "quickness_uptime", 0) or 0
        if quickness < 70:
            opts.append({
                "priority": "high",
                "title": "提升急速覆盖率",
                "description": f"当前急速覆盖率为 {round(quickness,1)}%，建议保持在80%以上",
                "expected_impact": "预计可提升10-15%的DPS",
            })
    return opts


# ==================== 公共API ====================

def get_player_rotation(log_id: int, account: str, db: Session) -> Dict[str, Any]:
    """获取指定玩家在指定日志中的技能循环数据"""
    ei_player = _get_ei_player(log_id, account, db)
    if not ei_player:
        return {"found": False, "account": account, "log_id": log_id}
    skill_map = _get_skill_map(log_id, db)
    events = _parse_rotation(ei_player.rotation_json or [], skill_map)
    fight_stats = _get_fight_stats(log_id, account, db)
    cycles = _build_cycles(events)
    return {
        "found": True,
        "log_id": log_id,
        "account": account,
        "character_name": ei_player.character_name or "",
        "profession": ei_player.profession or "",
        "fight_duration": max(e["cast_time"] + e.get("duration", 0) for e in events) if events else 0,
        "events": events,
        "cycles": cycles,
        "stats": _calculate_stats(events, fight_stats),
        "mistakes": _generate_mistakes(events),
        "optimizations": _generate_optimizations(events, fight_stats),
    }


def analyze_skill_rotation(log_id: int, account: str, db: Session) -> Dict[str, Any]:
    """分析技能循环（兼容旧接口）"""
    return get_player_rotation(log_id, account, db)


def compare_rotations(
    log_id: int,
    account: str,
    benchmark_account: str,
    db: Session
) -> Dict[str, Any]:
    """对比两个玩家的技能循环"""
    actual = get_player_rotation(log_id, account, db)
    benchmark = get_player_rotation(log_id, benchmark_account, db)
    if not actual.get("found") or not benchmark.get("found"):
        return {
            "success": False,
            "message": "找不到指定玩家的数据",
            "actual": actual,
            "benchmark": benchmark,
        }
    # 对比指标
    a_stats = actual.get("stats", {})
    b_stats = benchmark.get("stats", {})
    comparisons = {
        "total_casts": {
            "actual": a_stats.get("total_casts", 0),
            "benchmark": b_stats.get("total_casts", 0),
            "diff": a_stats.get("total_casts", 0) - b_stats.get("total_casts", 0),
        },
        "avg_dps": {
            "actual": a_stats.get("avg_dps", 0),
            "benchmark": b_stats.get("avg_dps", 0),
            "diff": a_stats.get("avg_dps", 0) - b_stats.get("avg_dps", 0),
            "diff_percent": round((a_stats.get("avg_dps", 0) - b_stats.get("avg_dps", 0)) / max(b_stats.get("avg_dps", 1), 1) * 100, 1),
        },
        "interrupted_rate": {
            "actual": a_stats.get("interrupted_rate", 0),
            "benchmark": b_stats.get("interrupted_rate", 0),
            "diff": round(a_stats.get("interrupted_rate", 0) - b_stats.get("interrupted_rate", 0), 1),
        },
        "skill_cast_uptime": {
            "actual": a_stats.get("skill_cast_uptime", 0),
            "benchmark": b_stats.get("skill_cast_uptime", 0),
            "diff": round(a_stats.get("skill_cast_uptime", 0) - b_stats.get("skill_cast_uptime", 0), 1),
        },
    }
    return {
        "success": True,
        "actual_account": account,
        "benchmark_account": benchmark_account,
        "actual": actual,
        "benchmark": benchmark,
        "comparisons": comparisons,
    }


def get_ideal_rotations(profession: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取理想循环模板（静态数据，后续可扩展为数据库配置）"""
    templates = {
        "default": {
            "name": "通用循环模板",
            "description": "适用于大多数职业的基础循环",
            "steps": [
                {"order": 1, "action": "起手爆发技能", "timing": "战斗开始后立即"},
                {"order": 2, "action": "维持核心Buff", "timing": "每5-10秒刷新"},
                {"order": 3, "action": "主要伤害技能", "timing": "冷却完成即使用"},
                {"order": 4, "action": "填充技能/自动攻击", "timing": "技能间隙"},
                {"order": 5, "action": "武器切换", "timing": "主手技能进入冷却"},
            ],
        },
        "Troubadour": {
            "name": "吟游诗人循环模板",
            "description": "基于急速和增益覆盖的辅助循环",
            "steps": [
                {"order": 1, "action": "放置领域技能", "timing": "战斗开始后立即"},
                {"order": 2, "action": "刷新急速来源", "timing": "每3-5秒"},
                {"order": 3, "action": "维持威能堆叠", "timing": "每7秒"},
                {"order": 4, "action": "支援技能", "timing": "队友需要时"},
                {"order": 5, "action": "武器切换获取新技能", "timing": "冷却完成"},
            ],
        },
    }
    if profession and profession in templates:
        return [templates[profession]]
    return [templates["default"]]


def export_rotation_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """生成报告数据结构（前端可基于此生成PDF/JSON）"""
    return {
        "report_title": f"技能循环分析报告 - {data.get('account', '')}",
        "generated_at": "",  # 前端填充
        "summary": {
            "profession": data.get("profession", ""),
            "fight_duration": data.get("fight_duration", 0),
            "total_casts": data.get("stats", {}).get("total_casts", 0),
            "avg_dps": data.get("stats", {}).get("avg_dps", 0),
        },
        "stats": data.get("stats", {}),
        "mistakes": data.get("mistakes", []),
        "optimizations": data.get("optimizations", []),
        "top_skills": data.get("stats", {}).get("top_skills", []),
    }


def health_check(db: Session) -> Dict[str, Any]:
    """服务健康检查"""
    try:
        # 简单查询验证数据库连接
        count = db.query(EiPlayer).limit(1).count()
        return {
            "status": "healthy",
            "database": "connected",
            "ei_player_records": count,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


# 错误码定义
ERROR_CODES = {
    "ROTATION_001": {"code": "ROTATION_001", "message": "找不到指定的战斗日志", "solution": "请检查日志ID是否正确"},
    "ROTATION_002": {"code": "ROTATION_002", "message": "找不到指定的玩家数据", "solution": "请检查玩家账号是否正确，或该玩家未参与此战斗"},
    "ROTATION_003": {"code": "ROTATION_003", "message": "该玩家没有技能循环数据", "solution": "可能是EI解析数据缺失，请重新上传日志"},
    "ROTATION_004": {"code": "ROTATION_004", "message": "对比基准玩家不存在", "solution": "请检查对比账号是否正确"},
    "ROTATION_005": {"code": "ROTATION_005", "message": "参数缺失", "solution": "请提供必要的请求参数"},
}
