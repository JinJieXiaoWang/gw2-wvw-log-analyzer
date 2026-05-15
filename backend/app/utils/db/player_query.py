# -*- coding: utf-8 -*-
"""
玩家查询工具函数（已停用）
注意：Fight、Member、FightStats模型已被移除，相关功能已停用
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.utils.error.exceptions import BadRequestException, NotFoundException


def query_player(
    db: Session,
    log_id: int,
    fight_stats_id: Optional[int] = None,
    instance_id: Optional[int] = None,
    account_name: Optional[str] = None,
    member_name: Optional[str] = None,
) -> Tuple[Optional[Dict], Optional[Dict], Optional[int], bool]:
    """
    统一玩家查询函数（已停用）

    参数优先级：fight_stats_id > instance_id > account_name > member_name

    返回值：
        (fight_stats_dict, member_dict, instance_id, is_ambiguous)
        - fight_stats_dict: 战斗统计数据（字典格式）
        - member_dict: 玩家数据（字典格式）
        - instance_id: 实例ID
        - is_ambiguous: 是否有歧义

    注意：由于Fight、Member、FightStats模型已被移除，此函数返回空数据
    """
    return None, None, instance_id if instance_id else None, False


def get_player_fight_stats(
    db: Session,
    log_id: int,
    instance_id: Optional[int] = None,
    account_name: Optional[str] = None,
    member_name: Optional[str] = None,
) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    获取玩家战斗统计（已停用）
    参数优先级：instance_id > account_name > member_name

    返回值：(None, None) 或 (fight_stats_dict, member_dict)

    注意：由于FightStats和Member模型已被移除，此函数返回空数据
    """
    return None, None


def get_members_by_log(db: Session, log_id: int) -> List[Dict]:
    """
    获取日志中的所有成员（已停用）

    注意：由于Member模型已被移除，此函数返回空列表
    """
    return []


def get_member_fights(db: Session, member_id: int) -> List[Dict]:
    """
    获取成员参与的所有战斗（已停用）

    注意：由于Fight和FightStats模型已被移除，此函数返回空列表
    """
    return []
