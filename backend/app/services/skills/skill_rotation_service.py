# -*- coding: utf-8 -*-
# 模块功能：技能循环分析服务（简化版）
# 说明：基于现有 fight_stats 数据提供可用分析，无详细技能时间线

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


def analyze_skill_rotation(
    db: Session,
    log_id: int,
    member_id: Optional[int] = None,
    account: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """基于 fight_stats 提供简化版技能分析

    Args:
        db: 数据库会话
        log_id: 日志ID
        member_id: 成员ID（可选）
        account: 玩家账号（可选，与 member_id 二选一）

    Returns:
        分析数据字典，无数据时返回 None
    """
    fights = db.query(Fight).filter(Fight.log_id == log_id).all()
    if not fights:
        return None

    fight_ids = [f.id for f in fights]

    query = db.query(FightStats).filter(FightStats.fight_id.in_(fight_ids))
    if member_id is not None:
        query = query.filter(FightStats.member_id == member_id)
    elif account:
        query = query.filter(FightStats.account == account)
    else:
        return None

    fight_stats = query.all()

    if not fight_stats:
        return None

    count = len(fight_stats)

    def _avg(field: str) -> float:
        total = sum(float(getattr(fs, field) or 0) for fs in fight_stats)
        return total / count if count > 0 else 0.0

    return {
        "member_id": member_id,
        "account": account,
        "log_id": log_id,
        "fight_count": count,
        "total_damage": sum(fs.damage or 0 for fs in fight_stats),
        "avg_dps": round(_avg("dps")),
        "total_healing": sum(fs.healing or 0 for fs in fight_stats),
        "skill_cast_uptime": round(_avg("skill_cast_uptime"), 2),
        "buffs": {
            "might": round(_avg("might_uptime"), 2),
            "fury": round(_avg("fury_uptime"), 2),
            "quickness": round(_avg("quickness_uptime"), 2),
            "alacrity": round(_avg("alacrity_uptime"), 2),
            "protection": round(_avg("protection_uptime"), 2),
            "stability": round(_avg("stability_uptime"), 2),
        },
        "survival": {
            "damage_taken": sum(fs.damage_taken or 0 for fs in fight_stats),
            "deaths": sum(fs.dead_count or 0 for fs in fight_stats),
            "downs": sum(fs.down_count or 0 for fs in fight_stats),
            "dodge_count": sum(fs.dodge_count or 0 for fs in fight_stats),
        },
        "combat": {
            "killed": sum(fs.killed or 0 for fs in fight_stats),
            "downed": sum(fs.downed or 0 for fs in fight_stats),
            "boon_strips": sum(fs.boon_strips or 0 for fs in fight_stats),
            "condition_cleanses": sum(
                fs.condition_cleanses or 0 for fs in fight_stats
            ),
            "interrupts": sum(fs.interrupts or 0 for fs in fight_stats),
        },
    }
