# -*- coding: utf-8 -*-
"""
数据看板核心聚合服务
功能：基于 fights / fight_stats / members / evtc_log 提供多维统计
作者：系统
创建日期：2026-05-04
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.models.account_character import AccountCharacter
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.log import Log
from app.models.member import Member
from app.utils.logger import logger


# =====================================================================
# 辅助函数
# =====================================================================


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


# =====================================================================
# 1. 核心 KPI 概览
# =====================================================================


def get_overview(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取核心 KPI 概览"""
    start_date, end_date = _get_date_range(days)

    # 战斗统计
    fight_query = db.query(Fight)
    fight_query = _apply_time_filter(fight_query, start_date, end_date)
    total_fights = fight_query.count()

    # 总参与人次（所有 fight_stats 记录数）
    participation_query = db.query(FightStats).join(Fight, FightStats.fight_id == Fight.id)
    participation_query = _apply_time_filter(participation_query, start_date, end_date)
    total_participations = participation_query.count()

    # 总伤害 / 总治疗
    damage_healing = (
        db.query(
            func.sum(Fight.total_damage).label("total_damage"),
            func.sum(Fight.total_healing).label("total_healing"),
        )
        .select_from(Fight)
    )
    damage_healing = _apply_time_filter(damage_healing, start_date, end_date)
    dh = damage_healing.first()
    total_damage = int(dh.total_damage or 0) if dh else 0
    total_healing = int(dh.total_healing or 0) if dh else 0

    # 活跃账号数（有 fight_stats 记录的不同 account）
    active_accounts_query = (
        db.query(distinct(FightStats.account))
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    active_accounts_query = _apply_time_filter(active_accounts_query, start_date, end_date)
    active_accounts = active_accounts_query.count()

    # 角色总数（account_characters 表）
    total_characters = db.query(func.count(AccountCharacter.id)).scalar() or 0

    # 解析日志数
    parsed_logs = (
        db.query(func.count(Log.id))
        .filter(Log.parse_status == "completed")
    )
    if start_date:
        parsed_logs = parsed_logs.filter(Log.upload_time >= start_date)
    parsed_logs = parsed_logs.filter(Log.upload_time <= end_date)
    parsed_logs = parsed_logs.scalar() or 0

    # 平均 AI 评分
    avg_score_query = (
        db.query(func.avg(FightStats.ai_score))
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    avg_score_query = _apply_time_filter(avg_score_query, start_date, end_date)
    avg_ai_score = avg_score_query.scalar()

    # 环比变化（与上一个周期对比）
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
        "active_accounts": active_accounts,
        "total_characters": int(total_characters),
        "parsed_logs": int(parsed_logs),
        "avg_ai_score": round(float(avg_ai_score), 2) if avg_ai_score else 0,
        "change": {
            "fights": _pct_change(total_fights, prev_fights),
            "damage": _pct_change(total_damage, prev_damage),
            "healing": _pct_change(total_healing, prev_healing),
            "accounts": _pct_change(active_accounts, prev_accounts),
        },
    }


# =====================================================================
# 2. 时间趋势
# =====================================================================


def get_trends(db: Session, days: int = 30, metric: str = "damage") -> Dict[str, Any]:
    """获取时间趋势数据

    Args:
        metric: "fights" | "damage" | "healing" | "kills" | "active_accounts"
    """
    start_date, end_date = _get_date_range(days)

    # 生成日期列表（补零）
    date_list = []
    current = start_date.date() if start_date else (end_date - timedelta(days=days)).date()
    end = end_date.date()
    while current <= end:
        date_list.append(str(current))
        current += timedelta(days=1)

    if metric == "active_accounts":
        # 每日活跃账号数
        query = (
            db.query(
                func.date(Fight.start_time).label("date"),
                func.count(distinct(FightStats.account)).label("value"),
            )
            .join(FightStats, Fight.id == FightStats.fight_id)
        )
        query = _apply_time_filter(query, start_date, end_date)
        query = query.group_by(func.date(Fight.start_time))
        results = {str(r.date): int(r.value) for r in query.all()}

    elif metric == "fights":
        # 每日战斗场次
        query = (
            db.query(
                func.date(Fight.start_time).label("date"),
                func.count(Fight.id).label("value"),
            )
        )
        query = _apply_time_filter(query, start_date, end_date)
        query = query.group_by(func.date(Fight.start_time))
        results = {str(r.date): int(r.value) for r in query.all()}

    elif metric == "healing":
        query = (
            db.query(
                func.date(Fight.start_time).label("date"),
                func.sum(Fight.total_healing).label("value"),
            )
        )
        query = _apply_time_filter(query, start_date, end_date)
        query = query.group_by(func.date(Fight.start_time))
        results = {str(r.date): int(r.value or 0) for r in query.all()}

    elif metric == "kills":
        query = (
            db.query(
                func.date(Fight.start_time).label("date"),
                func.sum(Fight.kill_count).label("value"),
            )
        )
        query = _apply_time_filter(query, start_date, end_date)
        query = query.group_by(func.date(Fight.start_time))
        results = {str(r.date): int(r.value or 0) for r in query.all()}

    else:
        # 默认 damage
        query = (
            db.query(
                func.date(Fight.start_time).label("date"),
                func.sum(Fight.total_damage).label("value"),
            )
        )
        query = _apply_time_filter(query, start_date, end_date)
        query = query.group_by(func.date(Fight.start_time))
        results = {str(r.date): int(r.value or 0) for r in query.all()}

    # 补零
    values = [results.get(d, 0) for d in date_list]

    return {
        "dates": date_list,
        "values": values,
        "metric": metric,
        "period_days": days,
    }


# =====================================================================
# 3. 职业分布
# =====================================================================


def get_profession_distribution(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取职业分布（按最新战斗的职业统计，不因转职拆分）"""
    start_date, end_date = _get_date_range(days)

    # 子查询：每个角色最新战斗的职业
    latest_profession_subq = (
        db.query(
            FightStats.character_name,
            FightStats.profession,
            func.row_number().over(
                partition_by=FightStats.character_name,
                order_by=Fight.start_time.desc()
            ).label("rn")
        )
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.character_name.isnot(None))
    )
    latest_profession_subq = _apply_time_filter(latest_profession_subq, start_date, end_date)
    latest_profession_subq = latest_profession_subq.subquery()

    # 统计每个职业的出现次数和总伤害
    query = (
        db.query(
            latest_profession_subq.c.profession,
            func.count(distinct(latest_profession_subq.c.character_name)).label("count"),
            func.sum(FightStats.damage).label("total_damage"),
        )
        .join(FightStats, FightStats.character_name == latest_profession_subq.c.character_name)
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(latest_profession_subq.c.rn == 1)
    )
    query = _apply_time_filter(query, start_date, end_date)
    query = query.group_by(latest_profession_subq.c.profession)
    query = query.order_by(func.count(distinct(latest_profession_subq.c.character_name)).desc())

    items = []
    for r in query.all():
        items.append({
            "profession": r.profession or "Unknown",
            "count": int(r.count or 0),
            "total_damage": int(r.total_damage or 0),
        })

    return {
        "period_days": days,
        "items": items,
        "total": len(items),
    }


# =====================================================================
# 4. 地图统计
# =====================================================================


def get_map_stats(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取地图统计（出场热度）"""
    start_date, end_date = _get_date_range(days)

    query = (
        db.query(
            Fight.map_name,
            func.count(Fight.id).label("fight_count"),
            func.avg(Fight.duration_sec).label("avg_duration"),
            func.sum(Fight.total_damage).label("total_damage"),
            func.avg(Fight.player_count).label("avg_player_count"),
        )
        .filter(Fight.map_name.isnot(None))
    )
    query = _apply_time_filter(query, start_date, end_date)
    query = query.group_by(Fight.map_name)
    query = query.order_by(func.count(Fight.id).desc())

    items = []
    for r in query.all():
        items.append({
            "map_name": r.map_name or "未知地图",
            "fight_count": int(r.fight_count or 0),
            "avg_duration_sec": round(float(r.avg_duration or 0)),
            "total_damage": int(r.total_damage or 0),
            "avg_player_count": round(float(r.avg_player_count or 0), 1),
        })

    return {
        "period_days": days,
        "items": items,
        "total": len(items),
    }


# =====================================================================
# 5. 玩家排行
# =====================================================================


def get_top_players(
    db: Session,
    days: int = 30,
    sort_by: str = "damage",
    limit: int = 20,
) -> Dict[str, Any]:
    """获取玩家排行（按 account 聚合）"""
    start_date, end_date = _get_date_range(days)

    valid_sort = {
        "damage", "dps", "healing", "killed", "ai_score",
        "damage_taken", "boon_strips", "condition_cleanses", "resurrects"
    }
    sort_column = sort_by if sort_by in valid_sort else "damage"

    # 按 account 聚合
    query = (
        db.query(
            FightStats.account,
            func.count(FightStats.id).label("fight_count"),
            func.sum(FightStats.damage).label("total_damage"),
            func.avg(FightStats.dps).label("avg_dps"),
            func.sum(FightStats.healing).label("total_healing"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.avg(FightStats.ai_score).label("avg_ai_score"),
            func.sum(FightStats.damage_taken).label("total_damage_taken"),
            func.sum(FightStats.boon_strips).label("total_boon_strips"),
            func.sum(FightStats.condition_cleanses).label("total_cleanses"),
            func.sum(FightStats.resurrects).label("total_resurrects"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    query = _apply_time_filter(query, start_date, end_date)
    query = query.group_by(FightStats.account)

    # 排序
    sort_col_map = {
        "damage": func.sum(FightStats.damage),
        "dps": func.avg(FightStats.dps),
        "healing": func.sum(FightStats.healing),
        "killed": func.sum(FightStats.killed),
        "ai_score": func.avg(FightStats.ai_score),
        "damage_taken": func.sum(FightStats.damage_taken),
        "boon_strips": func.sum(FightStats.boon_strips),
        "condition_cleanses": func.sum(FightStats.condition_cleanses),
        "resurrects": func.sum(FightStats.resurrects),
    }
    order_col = sort_col_map.get(sort_column, func.sum(FightStats.damage))
    query = query.order_by(order_col.desc())
    query = query.limit(limit)

    items = []
    for r in query.all():
        kills = int(r.total_kills or 0)
        deaths = int(r.total_deaths or 0)
        items.append({
            "account": r.account,
            "fight_count": int(r.fight_count or 0),
            "total_damage": int(r.total_damage or 0),
            "avg_dps": round(float(r.avg_dps or 0)),
            "total_healing": int(r.total_healing or 0),
            "total_kills": kills,
            "total_deaths": deaths,
            "kd_ratio": round(kills / max(deaths, 1), 2),
            "avg_ai_score": round(float(r.avg_ai_score or 0), 2),
            "total_damage_taken": int(r.total_damage_taken or 0),
            "total_boon_strips": int(r.total_boon_strips or 0),
            "total_cleanses": int(r.total_cleanses or 0),
            "total_resurrects": int(r.total_resurrects or 0),
        })

    return {
        "period_days": days,
        "sort_by": sort_column,
        "items": items,
        "total": len(items),
    }


# =====================================================================
# 6. 最近战斗
# =====================================================================


def get_recent_fights(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """获取最近战斗记录"""
    fights = (
        db.query(Fight)
        .order_by(Fight.start_time.desc())
        .limit(limit)
        .all()
    )

    items = []
    for f in fights:
        items.append({
            "fight_id": f.id,
            "log_id": f.log_id,
            "map_name": f.map_name or "未知地图",
            "server_name": f.server_name,
            "start_time": f.start_time.isoformat() if f.start_time else None,
            "duration_sec": f.duration_sec or 0,
            "player_count": f.player_count or 0,
            "total_damage": int(f.total_damage or 0),
            "total_healing": int(f.total_healing or 0),
            "kill_count": f.kill_count or 0,
            "death_count": f.death_count or 0,
        })

    return items


# =====================================================================
# 7. 解析状态分布
# =====================================================================


def get_parse_status_distribution(db: Session) -> Dict[str, Any]:
    """获取日志解析状态分布"""
    total = db.query(func.count(Log.id)).scalar() or 0

    status_query = (
        db.query(Log.parse_status, func.count(Log.id).label("count"))
        .group_by(Log.parse_status)
        .all()
    )

    items = []
    for status, count in status_query:
        items.append({
            "status": status,
            "count": int(count),
            "percentage": round((count / max(total, 1)) * 100, 2),
        })

    return {
        "total": int(total),
        "items": items,
    }


# =====================================================================
# 8. AI 评分分布
# =====================================================================


def get_ai_score_distribution(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取 AI 评分分布"""
    start_date, end_date = _get_date_range(days)

    # 按分数段统计
    ranges = [
        (0, 60, "D"),
        (60, 70, "C"),
        (70, 80, "B"),
        (80, 90, "A"),
        (90, 100, "S"),
    ]

    query = (
        db.query(FightStats.ai_score)
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.ai_score.isnot(None))
    )
    query = _apply_time_filter(query, start_date, end_date)

    scores = [float(s.ai_score) for s in query.all()]
    total = len(scores)

    items = []
    for low, high, grade in ranges:
        count = sum(1 for s in scores if low <= s < high)
        items.append({
            "grade": grade,
            "range": f"{low}-{high}",
            "count": count,
            "percentage": round((count / max(total, 1)) * 100, 2),
        })

    # 处理 >= 100 的特殊情况
    count_s_plus = sum(1 for s in scores if s >= 100)
    if count_s_plus > 0:
        items[-1]["count"] += count_s_plus
        items[-1]["percentage"] = round((items[-1]["count"] / max(total, 1)) * 100, 2)

    return {
        "period_days": days,
        "total": total,
        "avg_score": round(sum(scores) / max(total, 1), 2) if scores else 0,
        "items": items,
    }


# =====================================================================
# 9. Buff 概览
# =====================================================================


def get_buff_overview(db: Session, days: int = 30) -> Dict[str, Any]:
    """获取平均 Buff 覆盖率概览"""
    start_date, end_date = _get_date_range(days)

    query = (
        db.query(
            func.avg(FightStats.might_uptime).label("might"),
            func.avg(FightStats.fury_uptime).label("fury"),
            func.avg(FightStats.quickness_uptime).label("quickness"),
            func.avg(FightStats.alacrity_uptime).label("alacrity"),
            func.avg(FightStats.protection_uptime).label("protection"),
            func.avg(FightStats.stability_uptime).label("stability"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
    )
    query = _apply_time_filter(query, start_date, end_date)
    r = query.first()

    def _f(v):
        return round(float(v or 0), 2)

    return {
        "period_days": days,
        "buffs": {
            "might": _f(r.might),
            "fury": _f(r.fury),
            "quickness": _f(r.quickness),
            "alacrity": _f(r.alacrity),
            "protection": _f(r.protection),
            "stability": _f(r.stability),
        },
    }
