# -*- coding: utf-8 -*-
# 模块功能：成员出勤业务逻辑服务
# 作者：系统
# 创建日期：2026-04-27
# 更新日期：2026-05-04
# 说明：
#   members 表仅保存 account_name，所有角色/职业信息去 account_characters 查。

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fight_stats import FightStats
from app.models.member import Member
from app.utils.cache import cache_result


def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:
    """根据ID获取成员"""
    return db.query(Member).filter(Member.id == member_id).first()


def get_member_by_account(db: Session, account_name: str) -> Optional[Member]:
    """根据账号名获取成员"""
    return db.query(Member).filter(Member.account_name == account_name).first()


def get_members(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    guild_tag: Optional[str] = None,
) -> Tuple[List[Member], int]:
    """获取成员列表"""
    query = db.query(Member)

    if guild_tag:
        query = query.filter(Member.guild_tag == guild_tag)

    total = query.count()
    members = query.offset(skip).limit(limit).all()
    return members, total


def get_member_stats(db: Session, member_id: int) -> dict:
    """获取成员统计数据（跨所有战斗聚合）"""
    stats = (
        db.query(
            func.count(FightStats.id).label("total_fights"),
            func.sum(FightStats.damage).label("total_damage"),
            func.sum(FightStats.healing).label("total_healing"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.avg(FightStats.dps).label("avg_dps"),
            func.avg(FightStats.ai_score).label("avg_score"),
        )
        .filter(FightStats.member_id == member_id)
        .first()
    )

    return {
        "total_fights": stats.total_fights or 0,
        "total_damage": stats.total_damage or 0,
        "total_healing": stats.total_healing or 0,
        "total_kills": stats.total_kills or 0,
        "total_deaths": stats.total_deaths or 0,
        "avg_dps": float(stats.avg_dps) if stats.avg_dps else 0,
        "avg_score": float(stats.avg_score) if stats.avg_score else 0,
    }


@cache_result(ttl=300)
def get_member_ranking(
    db: Session, skip: int = 0, limit: int = 20, sort_by: str = "total_damage"
) -> List[dict]:
    """获取成员排名（跨战斗聚合，按 account 维度）"""
    order_column = {
        "total_fights": func.count(FightStats.id),
        "total_kills": func.sum(FightStats.killed),
        "total_damage": func.sum(FightStats.damage),
        "total_healing": func.sum(FightStats.healing),
        "avg_dps": func.avg(FightStats.dps),
    }.get(sort_by, func.sum(FightStats.damage))

    results = (
        db.query(
            Member,
            func.count(FightStats.id).label("fight_count"),
            func.sum(FightStats.killed).label("total_kills"),
            func.sum(FightStats.dead_count).label("total_deaths"),
            func.sum(FightStats.damage).label("damage_sum"),
            func.avg(FightStats.dps).label("avg_dps"),
        )
        .outerjoin(FightStats, Member.id == FightStats.member_id)
        .group_by(Member.id)
        .order_by(order_column.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    ranking = []
    for i, (
        member,
        fight_count,
        total_kills,
        total_deaths,
        damage_sum,
        avg_dps,
    ) in enumerate(results):
        ranking.append(
            {
                "rank": skip + i + 1,
                "member_id": member.id,
                "account_name": member.account_name,
                "total_fights": fight_count,
                "total_kills": total_kills or 0,
                "total_deaths": total_deaths or 0,
                "total_damage": damage_sum or 0,
                "avg_dps": float(avg_dps) if avg_dps else 0,
            }
        )

    return ranking
