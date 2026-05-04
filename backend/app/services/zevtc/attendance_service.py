# -*- coding: utf-8 -*-
# 模块功能：出勤统计服务层 v2.0
# 作者：系统
# 创建日期：2026-05-04
# 依赖说明：SQLAlchemy
# 核心规则：
#   1. members 表仅保存 account_name（账号维度）
#   2. 角色信息统一去 account_characters 表查询
#   3. 统计归属日期严格使用 fight.start_time（日志内容日期），与 upload_time 无关
#   4. 同一角色在自然日内无论多少日志，只计 1 次出勤
#   5. 同一账号按自然日去重（当天多角色只计 1 次账号出勤）

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.models.account_character import AccountCharacter
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.member import Member


def get_account_attendance_list(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    server_name: Optional[str] = None,
    map_name: Optional[str] = None,
    profession: Optional[str] = None,
    sort_by: str = "attendance_count",
    sort_order: str = "desc",
) -> Tuple[List[Dict[str, Any]], int]:
    """获取账号出勤列表（按 account 维度聚合）

    出勤次数 = 该账号在统计周期内有多少个不同的自然日有战斗记录
    （同一自然日内无论多少日志/多少角色，只计 1 次账号出勤）

    返回字段：
        account, character_count, attendance_count, total_duration_sec,
        total_damage, total_healing, total_kills, total_deaths,
        kd_ratio, avg_score, last_attendance
    """
    # 子查询：该账号在 account_characters 中的角色数量
    char_count_subq = (
        select(func.count(AccountCharacter.id))
        .where(AccountCharacter.account_name == FightStats.account)
        .correlate(FightStats)
        .scalar_subquery()
    )

    query = db.query(
        FightStats.account,
        char_count_subq.label("character_count"),
        # 核心变更：按自然日去重计数
        func.count(distinct(func.date(Fight.start_time))).label("attendance_count"),
        func.sum(Fight.duration_sec).label("total_duration_sec"),
        func.sum(FightStats.damage).label("total_damage"),
        func.sum(FightStats.healing).label("total_healing"),
        func.sum(FightStats.killed).label("total_kills"),
        func.sum(FightStats.dead_count).label("total_deaths"),
        func.avg(FightStats.ai_score).label("avg_score"),
        func.max(Fight.start_time).label("last_attendance"),
    ).join(Fight, FightStats.fight_id == Fight.id)

    # 筛选条件（全部基于 Fight.start_time，与 upload_time 无关）
    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    if end_date:
        query = query.filter(Fight.start_time < end_date)
    if server_name:
        query = query.filter(Fight.server_name == server_name)
    if map_name:
        query = query.filter(Fight.map_name.like(f"%{map_name}%"))
    if profession:
        query = query.filter(FightStats.profession == profession)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                FightStats.account.like(like),
                FightStats.character_name.like(like),
            )
        )

    query = query.group_by(FightStats.account)

    # 排序（order_map 也要同步更新为按自然日去重）
    order_map = {
        "attendance_count": func.count(distinct(func.date(Fight.start_time))),
        "total_damage": func.sum(FightStats.damage),
        "total_healing": func.sum(FightStats.healing),
        "total_kills": func.sum(FightStats.killed),
        "total_deaths": func.sum(FightStats.dead_count),
        "total_duration_sec": func.sum(Fight.duration_sec),
        "avg_score": func.avg(FightStats.ai_score),
        "last_attendance": func.max(Fight.start_time),
    }
    order_col = order_map.get(sort_by, func.count(distinct(func.date(Fight.start_time))))
    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    # 总数（group_by 后需用子查询计数）
    total = db.query(func.count()).select_from(query.subquery()).scalar() or 0

    skip = (page - 1) * page_size
    results = query.offset(skip).limit(page_size).all()

    items = []
    for r in results:
        kills = int(r.total_kills or 0)
        deaths = int(r.total_deaths or 0)
        items.append(
            {
                "account": r.account,
                "character_count": int(r.character_count or 0),
                "attendance_count": int(r.attendance_count or 0),
                "total_duration_sec": int(r.total_duration_sec or 0),
                "total_damage": int(r.total_damage or 0),
                "total_healing": int(r.total_healing or 0),
                "total_kills": kills,
                "total_deaths": deaths,
                "kd_ratio": round(kills / max(deaths, 1), 2),
                "avg_score": round(float(r.avg_score), 2) if r.avg_score else 0,
                "last_attendance": (
                    r.last_attendance.isoformat() if r.last_attendance else None
                ),
            }
        )

    return items, total


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
        - 最近 20 条战斗记录
    """
    # 账号基本信息
    member = (
        db.query(Member).filter(Member.account_name == account_name).first()
    )

    # 该账号下所有角色（来自 account_characters）
    characters = (
        db.query(AccountCharacter)
        .filter(AccountCharacter.account_name == account_name)
        .order_by(AccountCharacter.last_seen_date.desc())
        .all()
    )

    # 每个角色的出勤统计（按角色名分组，不按 profession 拆分）
    # 角色换了职业仍然是同一个角色，profession 取最新战斗的职业
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

    # 获取每个角色最新战斗的职业（不因转职而拆分）
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
        .filter(FightStats.account == account_name)
        .subquery()
    )

    latest_professions = {
        row.character_name: row.profession
        for row in db.query(latest_profession_subq)
        .filter(latest_profession_subq.c.rn == 1)
        .all()
    }

    # 汇总统计（整个账号，按自然日去重）
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

    summary = summary_query.first()

    # 如果该账号没有任何出勤记录，返回 None
    if not summary or (summary.attendance_count or 0) == 0:
        return None

    # 最近战斗记录（该账号所有角色的最近 20 条）
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

    recent_fights = recent_query.order_by(Fight.start_time.desc()).limit(20).all()

    # 组装角色数据
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

    # 组装最近战斗记录
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

    total_kills = int(summary.total_kills or 0)
    total_deaths = int(summary.total_deaths or 0)

    return {
        "account": account_name,
        "guild_tag": member.guild_tag if member else None,
        "join_date": member.join_date.isoformat() if member and member.join_date else None,
        "summary": {
            # 账号维度：按自然日去重（当天多角色只计 1 次）
            "attendance_count": int(summary.attendance_count or 0),
            "total_duration_sec": int(summary.total_duration_sec or 0),
            "total_damage": int(summary.total_damage or 0),
            "total_healing": int(summary.total_healing or 0),
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
            "avg_score": round(float(summary.avg_score), 2) if summary.avg_score else 0,
            "last_attendance": (
                summary.last_attendance.isoformat()
                if summary.last_attendance
                else None
            ),
        },
        "characters": character_list,
        "character_count": len(character_list),
        "recent_fights": recent_records,
    }


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

    返回：
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
            func.sum(FightStats.healing).label("total_healing"),
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


def get_distinct_servers(db: Session) -> List[str]:
    """获取所有出现过的服务器名称（用于筛选下拉框）"""
    results = (
        db.query(Fight.server_name)
        .filter(Fight.server_name.isnot(None))
        .distinct()
        .order_by(Fight.server_name)
        .all()
    )
    return [r[0] for r in results if r[0]]


def get_distinct_maps(db: Session) -> List[str]:
    """获取所有出现过的地图名称（用于筛选下拉框）"""
    results = (
        db.query(Fight.map_name)
        .filter(Fight.map_name.isnot(None))
        .distinct()
        .order_by(Fight.map_name)
        .all()
    )
    return [r[0] for r in results if r[0]]


def get_distinct_professions(db: Session) -> List[str]:
    """获取所有出现过的职业（用于筛选下拉框）"""
    results = (
        db.query(FightStats.profession)
        .filter(FightStats.profession.isnot(None))
        .distinct()
        .order_by(FightStats.profession)
        .all()
    )
    return [r[0] for r in results if r[0]]
