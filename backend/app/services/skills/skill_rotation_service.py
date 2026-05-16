# 模块功能: 技能循环分析服务
# 作者: 帅姐姐
# 创建日期: 2026-05-14

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


def analyze_skill_rotation(log_id: int, account: str, db: Session) -> Dict[str, Any]:
    """
    分析技能循环
    """
    # 查询战斗数据
    fights = db.query(Fight).filter(Fight.log_id == log_id).all()
    if not fights:
        return {
            "log_id": log_id,
            "member_id": 0,
            "account": account,
            "character_name": "",
            "profession": "",
            "fight_duration": 0,
            "events": [],
            "cycles": [],
            "stats": {
                "total_casts": 0,
                "total_damage": 0,
                "avg_dps": 0,
                "skill_cast_uptime": 0,
                "interrupted_rate": 0,
                "auto_attack_rate": 0,
                "top_skills": [],
                "buff_coverage": {}
            },
            "mistakes": [],
            "optimizations": []
        }
    
    fight_ids = [f.id for f in fights]
    
    # 查询玩家战斗数据
    fight_stats_list = db.query(FightStats).filter(
        FightStats.fight_id.in_(fight_ids),
        FightStats.account == account
    ).all()
    
    if not fight_stats_list:
        return {
            "log_id": log_id,
            "member_id": 0,
            "account": account,
            "character_name": "",
            "profession": "",
            "fight_duration": fights[0].duration if fights and fights[0].duration else 0,
            "events": [],
            "cycles": [],
            "stats": {
                "total_casts": 0,
                "total_damage": 0,
                "avg_dps": 0,
                "skill_cast_uptime": 0,
                "interrupted_rate": 0,
                "auto_attack_rate": 0,
                "top_skills": [],
                "buff_coverage": {}
            },
            "mistakes": [],
            "optimizations": []
        }
    
    stats = fight_stats_list[0]
    total_damage = sum(fs.damage or 0 for fs in fight_stats_list)
    avg_dps = sum(fs.dps or 0 for fs in fight_stats_list) / len(fight_stats_list)
    
    # 生成模拟的技能事件数据
    events = _generate_mock_events(stats)
    
    return {
        "log_id": log_id,
        "member_id": stats.member_id if hasattr(stats, 'member_id') else 0,
        "account": stats.account or "",
        "character_name": stats.character or "",
        "profession": stats.profession or "",
        "fight_duration": fights[0].duration if fights and fights[0].duration else 0,
        "events": events,
        "cycles": _generate_mock_cycles(events),
        "stats": {
            "total_casts": len(events),
            "total_damage": total_damage,
            "avg_dps": int(avg_dps),
            "skill_cast_uptime": 65.5,
            "interrupted_rate": 4.2,
            "auto_attack_rate": 18.3,
            "top_skills": _generate_mock_top_skills(stats, total_damage),
            "buff_coverage": {
                "Might": stats.buff_might or 0,
                "Fury": stats.buff_fury or 0,
                "Quickness": stats.buff_quickness or 0,
                "Alacrity": stats.buff_alacrity or 0,
                "Protection": stats.buff_protection or 0,
                "Stability": stats.buff_stability or 0
            }
        },
        "mistakes": _generate_mock_mistakes(),
        "optimizations": _generate_mock_optimizations(stats)
    }


def _generate_mock_events(stats: FightStats) -> List[Dict[str, Any]]:
    """生成模拟的技能事件"""
    skills = [
        {"id": 1, "name": "主要伤害技能", "icon": "https://gw2icons.com/icon/12345.png"},
        {"id": 2, "name": "次要伤害技能", "icon": "https://gw2icons.com/icon/12346.png"},
        {"id": 3, "name": "辅助技能", "icon": "https://gw2icons.com/icon/12347.png"},
        {"id": 4, "name": "爆发技能", "icon": "https://gw2icons.com/icon/12348.png"},
        {"id": 5, "name": "恢复技能", "icon": "https://gw2icons.com/icon/12349.png"},
    ]
    
    events = []
    current_time = 0
    for i in range(50):
        skill = skills[i % len(skills)]
        state = "full" if i % 10 != 0 else "interrupted"
        auto_attack = i % 5 == 0
        
        events.append({
            "id": i,
            "cast_time": current_time,
            "duration": 1500 if not auto_attack else 500,
            "skill_id": skill["id"],
            "skill_name": skill["name"],
            "skill_icon": skill["icon"],
            "state": state,
            "time_gained": 1200 if not auto_attack else 400,
            "quickness": 25 if i % 3 == 0 else 0,
            "auto_attack": auto_attack,
            "damage": 5000 if not auto_attack else 1000,
            "targets": 3
        })
        current_time += 2000
    
    return events


def _generate_mock_cycles(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成模拟的技能循环"""
    if not events:
        return []
    
    cycles = []
    for i in range(3):
        start_idx = i * 10
        end_idx = start_idx + 10
        cycle_events = events[start_idx:end_idx] if end_idx < len(events) else events[start_idx:]
        
        total_damage = sum(e["damage"] for e in cycle_events)
        interrupted_count = sum(1 for e in cycle_events if e["state"] == "interrupted")
        
        cycles.append({
            "id": i,
            "events": cycle_events,
            "duration": cycle_events[-1]["cast_time"] - cycle_events[0]["cast_time"] + cycle_events[-1]["duration"] if cycle_events else 0,
            "start": cycle_events[0]["cast_time"] if cycle_events else 0,
            "end": cycle_events[-1]["cast_time"] + cycle_events[-1]["duration"] if cycle_events else 0,
            "interrupted_count": interrupted_count,
            "total_damage": total_damage
        })
    
    return cycles


def _generate_mock_top_skills(stats: FightStats, total_damage: int) -> List[Dict[str, Any]]:
    """生成模拟的技能统计"""
    return [
        {
            "skill_id": 1,
            "skill_name": "主要伤害技能",
            "skill_icon": "https://gw2icons.com/icon/12345.png",
            "count": 15,
            "damage": total_damage * 0.4 if total_damage else 0,
            "percent": 40.0,
            "avg_cast_time": 1500
        },
        {
            "skill_id": 2,
            "skill_name": "次要伤害技能",
            "skill_icon": "https://gw2icons.com/icon/12346.png",
            "count": 12,
            "damage": total_damage * 0.25 if total_damage else 0,
            "percent": 25.0,
            "avg_cast_time": 1200
        },
        {
            "skill_id": 3,
            "skill_name": "辅助技能",
            "skill_icon": "https://gw2icons.com/icon/12347.png",
            "count": 8,
            "damage": total_damage * 0.15 if total_damage else 0,
            "percent": 15.0,
            "avg_cast_time": 800
        }
    ]


def _generate_mock_mistakes() -> List[Dict[str, Any]]:
    """生成模拟的错误信息"""
    return [
        {
            "type": "interrupt",
            "description": "在第15秒打断了主要技能释放",
            "impact": "high"
        },
        {
            "type": "late",
            "description": "在第48秒延迟释放了关键技能",
            "impact": "medium"
        }
    ]


def _generate_mock_optimizations(stats: FightStats) -> List[Dict[str, Any]]:
    """生成模拟的优化建议"""
    return [
        {
            "priority": "high",
            "title": "提升技能释放时机",
            "description": "建议在战斗开始阶段更早地使用主要爆发技能",
            "expected_impact": "预计可以提升10%的总伤害"
        },
        {
            "priority": "medium",
            "title": "优化Buff覆盖率",
            "description": f"Might覆盖率为{stats.buff_might if stats.buff_might else 0}%，建议提升至85%以上",
            "expected_impact": "预计可以提升5%的持续伤害"
        }
    ]
