# -*- coding: utf-8 -*-
# 模块功能：战斗记录业务逻辑服务
# 作者：系统
# 创建日期：2026-04-27
# 更新日期：2026-05-01
# 说明：v2.0 扩展——释放更多标量字段，支撑多维战斗分析

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.zevtc_data import EiPlayer, EiSkillMap
from app.utils.logger import logger


def get_fight_by_id(db: Session, fight_id: int) -> Optional[Fight]:
    """根据ID获取战斗"""
    return db.query(Fight).filter(Fight.id == fight_id).first()


def get_fight_with_stats(db: Session, fight_id: int) -> Optional[Fight]:
    """获取战斗详情（含统计数据）"""
    return (
        db.query(Fight)
        .options(joinedload(Fight.fight_stats).joinedload(FightStats.member))
        .filter(Fight.id == fight_id)
        .first()
    )


def get_fights_by_log_id(db: Session, log_id: int) -> List[Fight]:
    """根据日志ID获取战斗列表"""
    return (
        db.query(Fight).filter(Fight.log_id == log_id).order_by(Fight.start_time).all()
    )


def get_fights(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    map_name: Optional[str] = None,
    server_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Tuple[List[Fight], int]:
    """获取战斗列表（支持筛选和分页）"""
    query = db.query(Fight)

    if map_name:
        query = query.filter(Fight.map_name.like(f"%{map_name}%"))
    if server_name:
        query = query.filter(Fight.server_name.like(f"%{server_name}%"))
    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    if end_date:
        query = query.filter(Fight.start_time <= end_date)

    total = query.count()
    fights = query.order_by(Fight.start_time.desc()).offset(skip).limit(limit).all()
    return fights, total


def get_fight_stats(db: Session, fight_id: int) -> List[FightStats]:
    """获取战斗统计数据"""
    return db.query(FightStats).filter(FightStats.fight_id == fight_id).all()


def _get_friendly_team_id(stats) -> Optional[int]:
    """从 FightStats 列表推断友方 team_id。
    策略：有 account 的玩家最多的非零 team 为友方。
    若无非零 team，返回 None（表示旧日志，需用 account 判断）。
    """
    team_counts: Dict[int, Dict[str, int]] = {}
    for s in stats:
        tid = s.team_id or 0
        if tid not in team_counts:
            team_counts[tid] = {"total": 0, "with_account": 0}
        team_counts[tid]["total"] += 1
        if s.account:
            team_counts[tid]["with_account"] += 1

    # 排除 team_id=0（NPC / 未分类）
    non_zero = {k: v for k, v in team_counts.items() if k != 0}
    if non_zero:
        return max(non_zero, key=lambda k: non_zero[k]["with_account"])
    return None


def get_log_player_stats(
    db: Session, log_id: int, sort_by: str = "damage"
) -> List[Dict[str, Any]]:
    """
    获取日志的玩家排行榜（仅友方玩家，用于 /logs/{log_id} 页面）
    直接查询 fight_stats 表，无需 JOIN evtc_event
    v2.0: 释放全部标量字段，支撑多维战斗分析
    v2.2: 按 team_id 过滤敌方，不再混入友方列表
    v2.3: 严格按 log_id 查询，确保数据与特定上传文件准确关联，不跨文件汇总
    """
    # 严格按 log_id 查询单个 fight，确保数据隔离
    fight = db.query(Fight).filter(Fight.log_id == log_id).first()
    if not fight:
        return []

    valid_sort = {
        "damage",
        "dps",
        "power_damage",
        "condi_damage",
        "breakbar_damage",
        "critical_rate",
        "flanking_rate",
        "killed",
        "down_count",
        "dead_count",
        "damage_taken",
        "boon_strips",
        "condition_cleanses",
        "resurrects",
        "might_uptime",
        "quickness_uptime",
        "fury_uptime",
        "alacrity_uptime",
        "protection_uptime",
        "stability_uptime",
        "ai_score",
        "healing",
    }
    sort_column = sort_by if sort_by in valid_sort else "damage"

    # 只查询该特定fight的数据，确保不跨文件汇总
    all_stats = (
        db.query(FightStats)
        .filter(FightStats.fight_id == fight.id)
        .order_by(getattr(FightStats, sort_column).desc())
        .all()
    )

    # 按 team_id 区分友方/敌方
    friendly_team = _get_friendly_team_id(all_stats)
    if friendly_team is not None:
        stats = [s for s in all_stats if s.team_id == friendly_team]
    else:
        # 旧日志：用 account 判断（有 account 为友方）
        stats = [s for s in all_stats if s.account]

    def _float(v):
        return float(v) if v is not None else 0

    return [
        {
            "id": s.id,
            "member_id": s.member_id,
            "account": s.account,
            "character_name": s.character_name,
            "profession": s.profession,
            "group_id": s.group_id,
            "has_commander_tag": bool(s.has_commander_tag),
            # 伤害
            "damage": s.damage,
            "dps": s.dps,
            "power_damage": s.power_damage,
            "condi_damage": s.condi_damage,
            "breakbar_damage": s.breakbar_damage,
            # 命中质量
            "critical_rate": _float(s.critical_rate),
            "flanking_rate": _float(s.flanking_rate),
            "glance_rate": _float(s.glance_rate),
            "missed": s.missed,
            "interrupts": s.interrupts,
            "swap_count": s.swap_count,
            # 击杀/控制
            "killed": s.killed,
            "down_count": s.down_count,
            "dead_count": s.dead_count,
            # 防御/生存
            "damage_taken": s.damage_taken,
            "blocked_count": s.blocked_count,
            "evaded_count": s.evaded_count,
            "dodge_count": s.dodge_count,
            # 支援
            "boon_strips": s.boon_strips,
            "condition_cleanses": s.condition_cleanses,
            "resurrects": s.resurrects,
            "condi_cleanse_ally": s.condi_cleanse_ally,
            "boon_strips_ally": s.boon_strips_ally,
            "healing": s.healing,
            # Buff 覆盖率
            "might_uptime": _float(s.might_uptime),
            "fury_uptime": _float(s.fury_uptime),
            "quickness_uptime": _float(s.quickness_uptime),
            "alacrity_uptime": _float(s.alacrity_uptime),
            "protection_uptime": _float(s.protection_uptime),
            "stability_uptime": _float(s.stability_uptime),
            # AI 评分
            "ai_score": _float(s.ai_score),
            "score_grade": s.score_grade,
        }
        for s in stats
    ]


def get_enemy_players(db: Session, log_id: int) -> List[Dict[str, Any]]:
    """
    获取日志中的敌方目标。
    新日志：按 team_id 区分（非友方 team 的为敌方）。
    旧日志：无 account 或 account 为空的玩家。
    严格按 log_id 查询，确保数据与特定上传文件准确关联
    """
    # 严格按 log_id 查询单个 fight
    fight = db.query(Fight).filter(Fight.log_id == log_id).first()
    if not fight:
        return []

    # 只查询该 fight 的数据，不跨文件汇总
    all_stats = db.query(FightStats).filter(FightStats.fight_id == fight.id).all()

    friendly_team = _get_friendly_team_id(all_stats)
    if friendly_team is not None:
        stats = [s for s in all_stats if s.team_id != friendly_team]
    else:
        stats = [s for s in all_stats if not s.account]

    stats = sorted(stats, key=lambda s: s.damage or 0, reverse=True)

    def _float(v):
        return float(v) if v is not None else 0

    return [
        {
            "id": s.id,
            "member_id": s.member_id,
            "account": s.account,
            "character_name": s.character_name,
            "profession": s.profession,
            "group_id": s.group_id,
            "has_commander_tag": bool(s.has_commander_tag),
            "damage": s.damage,
            "dps": s.dps,
            "damage_taken": s.damage_taken,
            "critical_rate": _float(s.critical_rate),
            "flanking_rate": _float(s.flanking_rate),
            "glance_rate": _float(s.glance_rate),
            "missed": s.missed,
            "down_count": s.down_count,
            "dead_count": s.dead_count,
        }
        for s in stats
    ]


def get_fight_aggregate_stats(db: Session, log_id: int) -> Dict[str, Any]:
    """
    获取战斗聚合统计（用于概览页 KPI 卡片）
    严格按 log_id 查询，确保数据与特定上传文件准确关联
    """
    # 严格按 log_id 查询单个 fight
    fight = db.query(Fight).filter(Fight.log_id == log_id).first()
    if not fight:
        return {}

    # 只查询该 fight 的数据，不跨文件汇总
    stats = db.query(FightStats).filter(FightStats.fight_id == fight.id).all()
    if not stats:
        return {}

    total_players = len(stats)
    total_damage = sum(s.damage or 0 for s in stats)
    total_power = sum(s.power_damage or 0 for s in stats)
    total_condi = sum(s.condi_damage or 0 for s in stats)
    total_breakbar = sum(s.breakbar_damage or 0 for s in stats)
    total_taken = sum(s.damage_taken or 0 for s in stats)
    total_healing = sum(s.healing or 0 for s in stats)
    total_kills = sum(s.killed or 0 for s in stats)
    total_deaths = sum(s.dead_count or 0 for s in stats)
    total_downs = sum(s.down_count or 0 for s in stats)
    total_strips = sum(s.boon_strips or 0 for s in stats)
    total_cleanses = sum(s.condition_cleanses or 0 for s in stats)
    total_res = sum(s.resurrects or 0 for s in stats)
    avg_dps = round(sum(s.dps or 0 for s in stats) / max(total_players, 1))
    avg_crit = sum(_float(s.critical_rate) for s in stats) / max(total_players, 1)

    return {
        "duration_sec": fight.duration_sec,
        "player_count": total_players,
        "total_damage": total_damage,
        "total_power_damage": total_power,
        "total_condi_damage": total_condi,
        "total_breakbar_damage": total_breakbar,
        "total_damage_taken": total_taken,
        "total_healing": total_healing,
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "total_downs": total_downs,
        "total_boon_strips": total_strips,
        "total_condition_cleanses": total_cleanses,
        "total_resurrects": total_res,
        "avg_dps": avg_dps,
        "avg_critical_rate": round(avg_crit, 2),
    }


def _float(v):
    return float(v) if v is not None else 0


def get_player_rotation(
    db: Session, log_id: int, account: str
) -> Optional[Dict[str, Any]]:
    """
    获取指定玩家在指定日志中的技能循环、技能释放次数、武器配置和死亡回放。
    查询 EiPlayer + EiSkillMap。
    """
    player = (
        db.query(EiPlayer)
        .filter(EiPlayer.log_id == log_id, EiPlayer.account == account)
        .first()
    )

    if not player:
        return None

    # 技能映射表（从 ei_skill_map 查）
    skill_maps = db.query(EiSkillMap).filter(EiSkillMap.log_id == log_id).all()
    skill_map = {}
    for sm in skill_maps:
        skill_map[str(sm.gw2_skill_id)] = {
            "name": sm.name,
            "gw2_id": sm.gw2_skill_id,
            "skill_key": sm.skill_key,
        }

    # 从 rotation_json 统计 skill_casts（EI JSON 的 statsAll 中没有 skillCasts 字段）
    skill_casts = {}
    if player.rotation_json and isinstance(player.rotation_json, list):
        for rot in player.rotation_json:
            if isinstance(rot, dict):
                sid = str(rot.get("id", ""))
                count = len(rot.get("skills", []))
                if sid and count > 0:
                    skill_casts[sid] = skill_casts.get(sid, 0) + count

    return {
        "account": player.account,
        "character_name": player.character_name,
        "profession": player.profession,
        "rotation": player.rotation_json or [],
        "skill_casts": skill_casts,
        "skill_map": skill_map,
        "weapons": player.weapons_json or [],
        "death_recap": player.death_recap_json or [],
        "consumables": player.consumables_json or {"food": [], "utility": []},
    }
