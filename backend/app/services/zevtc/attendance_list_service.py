# -*- coding: utf-8 -*-
# 模块功能：出勤列表查询服务
# 作者：系统
# 创建日期：2026-05-04

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.models.auth.account_character import AccountCharacter
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


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
    """获取账号出勤列表（按 account 维度聚合?

    出勤次数 = 该账号在统计周期内有多少个不同的自然日有战斗记录
    （同一自然日内无论多少日志/多少角色，只?1 次账号出勤）

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
        # 核心变更：按自然日去重计?
        func.count(distinct(func.date(Fight.start_time))).label("attendance_count"),
        func.sum(Fight.duration_sec).label("total_duration_sec"),
        func.sum(FightStats.damage).label("total_damage"),
        func.sum(FightStats.healing).label("total_healing"),
        func.sum(FightStats.killed).label("total_kills"),
        func.sum(FightStats.dead_count).label("total_deaths"),
        func.avg(FightStats.ai_score).label("avg_score"),
        func.max(Fight.start_time).label("last_attendance"),
    ).join(Fight, FightStats.fight_id == Fight.id)

    # 筛选条件（全部基于 Fight.start_time，与 upload_time 无关系
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

    # 总数（group_by 后需用子查询计数据
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
