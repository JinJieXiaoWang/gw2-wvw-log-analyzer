# -*- coding: utf-8 -*-
# 模块功能：角色出勤详情查询服务
# 作者：系统
# 创建日期：2026-05-04

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


def get_character_detail(
    db: Session,
    account_name: str,
    character_name: str,
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
    """获取指定角色的详细战斗记录

    返回:
        - 战斗记录列表
        - 总数
        - 该角色的汇总统计（attendance_count 按自然日去重）
    """
    query = (
        db.query(
            Fight.id.label("fight_id"),
            Fight.map_name,
            Fight.server_name,
            Fight.start_time,
            Fight.duration_sec,
            FightStats.character_name,
            FightStats.profession,
            FightStats.damage,
            FightStats.dps,
            FightStats.power_damage,
            FightStats.condi_damage,
            FightStats.breakbar_damage,
            FightStats.healing,
            FightStats.downed,
            FightStats.killed,
            FightStats.dead_count,
            FightStats.down_count,
            FightStats.damage_taken,
            FightStats.critical_rate,
            FightStats.flanking_rate,
            FightStats.glance_rate,
            FightStats.missed,
            FightStats.interrupts,
            FightStats.swap_count,
            FightStats.blocked_count,
            FightStats.evaded_count,
            FightStats.dodge_count,
            FightStats.boon_strips,
            FightStats.condition_cleanses,
            FightStats.resurrects,
            FightStats.might_uptime,
            FightStats.fury_uptime,
            FightStats.quickness_uptime,
            FightStats.alacrity_uptime,
            FightStats.protection_uptime,
            FightStats.stability_uptime,
            FightStats.ai_score,
            FightStats.score_grade,
        )
        .join(FightStats, Fight.id == FightStats.fight_id)
        .filter(FightStats.account == account_name)
        .filter(FightStats.character_name == character_name)
    )

    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    if end_date:
        query = query.filter(Fight.start_time < end_date)

    # 汇总统计（按自然日去重）
    agg = (
        db.query(
            func.count(distinct(func.date(Fight.start_time))).label("attendance_count"),
            func.sum(FightStats.damage).label("total_damage"),
            func.sum(FightStats.downed).label("total_downed"),
            func.avg(FightStats.dps).label("avg_dps"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.avg(FightStats.ai_score).label("avg_score"),
            func.max(Fight.start_time).label("last_attendance"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
        .filter(FightStats.character_name == character_name)
    )

    if start_date:
        agg = agg.filter(Fight.start_time >= start_date)
    if end_date:
        agg = agg.filter(Fight.start_time < end_date)

    agg_result = agg.first()

    total = query.count()
    skip = (page - 1) * page_size
    results = query.order_by(Fight.start_time.desc()).offset(skip).limit(page_size).all()

    items = []
    for r in results:
        items.append(
            {
                "fight_id": r.fight_id,
                "map_name": r.map_name or "Unknown",
                "server_name": r.server_name,
                "fight_date": r.start_time.isoformat() if r.start_time else None,
                "duration_sec": r.duration_sec or 0,
                "profession": r.profession,
                "damage": r.damage or 0,
                "dps": r.dps or 0,
                "power_damage": r.power_damage or 0,
                "condi_damage": r.condi_damage or 0,
                "breakbar_damage": r.breakbar_damage or 0,
                "healing": r.healing or 0,
                "downed": r.downed or 0,
                "killed": r.killed or 0,
                "dead_count": r.dead_count or 0,
                "down_count": r.down_count or 0,
                "damage_taken": r.damage_taken or 0,
                "critical_rate": float(r.critical_rate or 0),
                "flanking_rate": float(r.flanking_rate or 0),
                "glance_rate": float(r.glance_rate or 0),
                "missed": r.missed or 0,
                "interrupts": r.interrupts or 0,
                "swap_count": r.swap_count or 0,
                "blocked_count": r.blocked_count or 0,
                "evaded_count": r.evaded_count or 0,
                "dodge_count": r.dodge_count or 0,
                "boon_strips": r.boon_strips or 0,
                "condition_cleanses": r.condition_cleanses or 0,
                "resurrects": r.resurrects or 0,
                "buffs": {
                    "might": float(r.might_uptime or 0),
                    "fury": float(r.fury_uptime or 0),
                    "quickness": float(r.quickness_uptime or 0),
                    "alacrity": float(r.alacrity_uptime or 0),
                    "protection": float(r.protection_uptime or 0),
                    "stability": float(r.stability_uptime or 0),
                },
                "ai_score": round(float(r.ai_score), 2) if r.ai_score else 0,
                "score_grade": r.score_grade,
            }
        )

    total_kills = int(agg_result.total_kills or 0)
    total_deaths = int(agg_result.total_deaths or 0)

    summary = {
        "attendance_count": int(agg_result.attendance_count or 0),
        "total_damage": int(agg_result.total_damage or 0),
        "total_healing": int(agg_result.total_healing or 0),
        "avg_dps": round(float(agg_result.avg_dps), 2) if agg_result.avg_dps else 0,
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
        "avg_score": round(float(agg_result.avg_score), 2) if agg_result.avg_score else 0,
        "last_attendance": (
            agg_result.last_attendance.isoformat()
            if agg_result.last_attendance
            else None
        ),
    }

    return items, total, summary
