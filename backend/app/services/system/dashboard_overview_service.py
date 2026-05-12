﻿# -*- coding: utf-8 -*-
"""数据看板概览服务"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.models.auth.account_character import AccountCharacter
from app.models.auth.member import Member
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.models.log.log import Log
from app.utils.logger import logger


def _get_date_range(days: int) -> Tuple[Optional[datetime], datetime]:
    """将天数转换为查询时间范围"""
    end_date = datetime.now()
    if days <= 0:
        return None, end_date
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def _apply_time_filter(query, start_date: Optional[datetime], end_date: datetime):
    """为查询应用时间范围过滤（基于 Fight.start_time）"""
    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    query = query.filter(Fight.start_time <= end_date)
    return query


def get_overview(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取核心 KPI 概览"""
    start_date, end_date = _get_date_range(days)
    fight_query = db.query(Fight)
    fight_query = _apply_time_filter(fight_query, start_date, end_date)
    total_fights = fight_query.count()
    participation_query = db.query(FightStats).join(Fight, FightStats.fight_id == Fight.id)
    participation_query = _apply_time_filter(participation_query, start_date, end_date)
    total_participations = participation_query.count()
    damage_healing_killed = (
        db.query(
            func.sum(Fight.total_damage).label("total_damage"),
            func.sum(Fight.total_healing).label("total_healing"),
            func.sum(Fight.kill_count).label("total_killed"),
        )
        .select_from(Fight)
    )
    damage_healing_killed = _apply_time_filter(damage_healing_killed, start_date, end_date)
    dhk = damage_healing_killed.first()
    total_damage = int(dhk.total_damage or 0) if dhk else 0
    total_healing = int(dhk.total_healing or 0) if dhk else 0
    total_killed = int(dhk.total_killed or 0) if dhk else 0
    active_accounts_query = (
        db.query(distinct(FightStats.account))
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    active_accounts_query = _apply_time_filter(active_accounts_query, start_date, end_date)
    active_accounts = active_accounts_query.count()
    total_characters = db.query(func.count(AccountCharacter.id)).scalar() or 0
    parsed_logs = (
        db.query(func.count(Log.id))
        .filter(Log.parse_status == "completed")
    )
    if start_date:
        parsed_logs = parsed_logs.filter(Log.upload_time >= start_date)
    parsed_logs = parsed_logs.filter(Log.upload_time <= end_date)
    parsed_logs = parsed_logs.scalar() or 0
    avg_score_query = (
        db.query(func.avg(FightStats.ai_score))
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    avg_score_query = _apply_time_filter(avg_score_query, start_date, end_date)
    avg_ai_score = avg_score_query.scalar()
    prev_start = start_date - timedelta(days=days) if start_date else None
    prev_end = end_date - timedelta(days=days)
    prev_fights = _apply_time_filter(db.query(Fight), prev_start, prev_end).count()
    prev_damage = (
        _apply_time_filter(
            db.query(func.sum(Fight.total_damage)).select_from(Fight),
            prev_start, prev_end
        ).scalar() or 0
    )
    prev_healing = (
        _apply_time_filter(
            db.query(func.sum(Fight.total_healing)).select_from(Fight),
            prev_start, prev_end
        ).scalar() or 0
    )
    prev_killed = (
        _apply_time_filter(
            db.query(func.sum(Fight.kill_count)).select_from(Fight),
            prev_start, prev_end
        ).scalar() or 0
    )
    prev_accounts = (
        _apply_time_filter(
            db.query(distinct(FightStats.account)).join(Fight, FightStats.fight_id == Fight.id),
            prev_start, prev_end
        ).count()
    )
    def _pct_change(current, previous):
        if previous == 0:
            return 0
        return round(((current - previous) / previous) * 100)
    return {
        "period_days": days,
        "total_fights": total_fights,
        "total_participations": total_participations,
        "total_damage": total_damage,
        "total_healing": total_healing,
        "total_killed": total_killed,
        "active_accounts": active_accounts,
        "total_characters": int(total_characters),
        "parsed_logs": int(parsed_logs),
        "avg_ai_score": round(float(avg_ai_score), 2) if avg_ai_score else 0,
        "change": {
            "fights": _pct_change(total_fights, prev_fights),
            "damage": _pct_change(total_damage, prev_damage),
            "healing": _pct_change(total_healing, prev_healing),
            "killed": _pct_change(total_killed, prev_killed),
            "accounts": _pct_change(active_accounts, prev_accounts),
        },
    }
