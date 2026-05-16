# -*- coding: utf-8 -*-
# 模块功能：出勤详情查询服务
# 作者：系统
# 创建日期：2026-05-04

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.auth.account_character import AccountCharacter
from app.models.auth.member import Member
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats

from .attendance_score_service import _calculate_comprehensive_abilities


def _query_account_base_info(
    db: Session, account_name: str
) -> Tuple[Optional[Member], List[AccountCharacter]]:
    """查询账号基本信息和角色列表"""
    member = db.query(Member).filter(Member.account_name == account_name).first()
    characters = (
        db.query(AccountCharacter)
        .filter(AccountCharacter.account_name == account_name)
        .order_by(AccountCharacter.last_seen_date.desc())
        .all()
    )
    return member, characters


def _query_character_stats(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """查询每个角色的出勤统计（按角色名分组）"""
    char_stats_query = (
        db.query(
            FightStats.character_name,
            func.count(distinct(func.date(Fight.start_time))).label("attendance_count"),
            func.sum(FightStats.damage).label("total_damage"),
            func.sum(FightStats.healing).label("total_healing"),
            func.avg(FightStats.dps).label("avg_dps"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.avg(FightStats.ai_score).label("avg_score"),
            func.max(Fight.start_time).label("last_attendance"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
    )

    if start_date:
        char_stats_query = char_stats_query.filter(Fight.start_time >= start_date)
    if end_date:
        char_stats_query = char_stats_query.filter(Fight.start_time < end_date)

    char_stats = (
        char_stats_query.group_by(FightStats.character_name)
        .order_by(func.count(distinct(func.date(Fight.start_time))).desc())
        .all()
    )
    return char_stats


def _query_latest_professions(
    db: Session, account_name: str
) -> Dict[str, str]:
    """获取每个角色最新战斗的职业（不因转职而拆分）"""
    latest_profession_subq = (
        db.query(
            FightStats.character_name,
            FightStats.profession,
            func.row_number().over(
                partition_by=FightStats.character_name,
                order_by=Fight.start_time.desc(),
            ).label("rn"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
        .subquery()
    )

    return {
        row.character_name: row.profession
        for row in db.query(latest_profession_subq)
        .filter(latest_profession_subq.c.rn == 1)
        .all()
    }


def _query_account_summary(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """查询账号汇总统计（整个账号，按自然日去重）"""
    summary_query = (
        db.query(
            func.count(distinct(func.date(Fight.start_time))).label("attendance_count"),
            func.sum(Fight.duration_sec).label("total_duration_sec"),
            func.sum(FightStats.damage).label("total_damage"),
            func.sum(FightStats.healing).label("total_healing"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.avg(FightStats.ai_score).label("avg_score"),
            func.max(Fight.start_time).label("last_attendance"),
        )
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
    )

    if start_date:
        summary_query = summary_query.filter(Fight.start_time >= start_date)
    if end_date:
        summary_query = summary_query.filter(Fight.start_time < end_date)

    return summary_query.first()


def _query_recent_fights(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """查询最?20 条战斗记录"""
    recent_query = (
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
            FightStats.healing,
            FightStats.killed,
            FightStats.dead_count,
            FightStats.ai_score,
            FightStats.might_uptime,
            FightStats.fury_uptime,
            FightStats.quickness_uptime,
            FightStats.alacrity_uptime,
            FightStats.protection_uptime,
            FightStats.stability_uptime,
        )
        .join(FightStats, Fight.id == FightStats.fight_id)
        .filter(FightStats.account == account_name)
    )

    if start_date:
        recent_query = recent_query.filter(Fight.start_time >= start_date)
    if end_date:
        recent_query = recent_query.filter(Fight.start_time < end_date)

    return recent_query.order_by(Fight.start_time.desc()).limit(20).all()


def _query_attendance_trend(db: Session, account_name: str) -> List[int]:
    """查询最?7 天出勤趋势"""
    # 7 天前的日期
    today = datetime.now().date()
    trend_dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    trend_start_dt = datetime.combine(trend_dates[0], datetime.min.time())

    trend_query = (
        db.query(
            func.date(Fight.start_time).label("fight_date"),
            func.count(distinct(Fight.id)).label("count"),
        )
        .join(FightStats, Fight.id == FightStats.fight_id)
        .filter(FightStats.account == account_name)
        .filter(Fight.start_time >= trend_start_dt)
        .group_by(func.date(Fight.start_time))
    )
    trend_map = {row.fight_date: row.count for row in trend_query.all()}
    return [int(trend_map.get(d, 0)) for d in trend_dates]


def _build_character_list(
    char_stats, latest_professions: Dict[str, str]
) -> List[Dict[str, Any]]:
    """组装角色统计数据列表"""
    character_list = []
    for cs in char_stats:
        kills = int(cs.total_kills or 0)
        deaths = int(cs.total_deaths or 0)
        character_list.append(
            {
                "character_name": cs.character_name,
                "profession": latest_professions.get(cs.character_name, ""),
                "attendance_count": int(cs.attendance_count or 0),
                "total_damage": int(cs.total_damage or 0),
                "total_healing": int(cs.total_healing or 0),
                "avg_dps": round(float(cs.avg_dps), 2) if cs.avg_dps else 0,
                "total_kills": kills,
                "total_deaths": deaths,
                "kd_ratio": round(kills / max(deaths, 1), 2),
                "avg_score": round(float(cs.avg_score), 2) if cs.avg_score else 0,
                "last_attendance": (
                    cs.last_attendance.isoformat() if cs.last_attendance else None
                ),
            }
        )
    return character_list


def _build_recent_records(recent_fights) -> List[Dict[str, Any]]:
    """组装最近战斗记录列表"""
    recent_records = []
    for rf in recent_fights:
        recent_records.append(
            {
                "fight_id": rf.fight_id,
                "map_name": rf.map_name or "Unknown",
                "server_name": rf.server_name,
                "fight_date": rf.start_time.isoformat() if rf.start_time else None,
                "duration_sec": rf.duration_sec or 0,
                "character_name": rf.character_name,
                "profession": rf.profession,
                "damage": rf.damage or 0,
                "dps": rf.dps or 0,
                "healing": rf.healing or 0,
                "killed": rf.killed or 0,
                "dead_count": rf.dead_count or 0,
                "ai_score": round(float(rf.ai_score), 2) if rf.ai_score else 0,
                "buffs": {
                    "might": float(rf.might_uptime or 0),
                    "fury": float(rf.fury_uptime or 0),
                    "quickness": float(rf.quickness_uptime or 0),
                    "alacrity": float(rf.alacrity_uptime or 0),
                    "protection": float(rf.protection_uptime or 0),
                    "stability": float(rf.stability_uptime or 0),
                },
            }
        )
    return recent_records


def _build_summary_dict(summary, recent_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """组装账号汇总统计字典"""
    total_kills = int(summary.total_kills or 0)
    total_deaths = int(summary.total_deaths or 0)
    server_name = recent_records[0]["server_name"] if recent_records else None

    return {
        "attendance_count": int(summary.attendance_count or 0),
        "total_duration_sec": int(summary.total_duration_sec or 0),
        "total_damage": int(summary.total_damage or 0),
        "total_healing": int(summary.total_healing or 0),
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
        "avg_score": round(float(summary.avg_score), 2) if summary.avg_score else 0,
        "last_attendance": (
            summary.last_attendance.isoformat() if summary.last_attendance else None
        ),
    }, server_name


def get_account_detail(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """获取指定账号的出勤详情    

    包含：
        - 账号汇总统计（attendance_count 按自然日去重）
        - 该账号下所有角色的出勤统计（每个角色独立按自然日去重）
        - 最近20 条战斗记录
    """
    # 账号基本信息
    member, _ = _query_account_base_info(db, account_name)

    # 每个角色的出勤统计（按角色名分组）
    char_stats = _query_character_stats(db, account_name, start_date, end_date)

    # 获取每个角色最新战斗的职业
    latest_professions = _query_latest_professions(db, account_name)

    # 汇总统计（整个账号，按自然日去重）
    summary = _query_account_summary(db, account_name, start_date, end_date)

    # 如果该账号没有任何出勤记录，返回 None
    if not summary or (summary.attendance_count or 0) == 0:
        return None

    # 最近战斗记录（按自然日去重）
    recent_fights = _query_recent_fights(db, account_name, start_date, end_date)

    # 组装角色数据
    character_list = _build_character_list(char_stats, latest_professions)

    # 组装最近战斗记录
    recent_records = _build_recent_records(recent_fights)

    # 组装汇总统计字典
    summary_dict, server_name = _build_summary_dict(summary, recent_records)

    # 最近7天出勤趋势
    attendance_trend = _query_attendance_trend(db, account_name)

    # 计算综合能力评分
    comprehensive_abilities = _calculate_comprehensive_abilities(
        db, account_name, character_list, start_date, end_date
    )

    return {
        "account": account_name,
        "guild_tag": member.guild_tag if member else None,
        "server": server_name,
        "rank": None,  # members 表暂?rank 字段，预?
        "join_date": member.join_date.isoformat() if member and member.join_date else None,
        "summary": summary_dict,
        "characters": character_list,
        "character_count": len(character_list),
        "recent_fights": recent_records,
        "attendance_trend": attendance_trend,
        "comprehensive_abilities": comprehensive_abilities,
    }
