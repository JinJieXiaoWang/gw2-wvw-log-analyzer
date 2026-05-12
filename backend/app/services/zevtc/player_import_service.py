# -*- coding: utf-8 -*-
"""玩家数据导入服务（members + fight_stats 批量插入口""

from datetime import date
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.utils.logger import logger

from .fight_data_extractor import build_fight_stats_mappings
from .player_import_utils import (
    bulk_insert_fight_stats,
    build_account_to_player,
    collect_needed_accounts_and_pairs,
    fetch_existing_data,
    process_members_and_characters,
)


def insert_players(db: Session, fight_id: int, players: List[Dict[str, Any]]):
    """插入/更新 members + fight_stats（并发安全版?
    过滤规则?    - 仅导入包?account 数据的记?    - 同一 fight 内同一 account 去重，防止断线重连导致重复记?    - 更新 AccountCharacter 映射，支持同一 account 多个角色

    【v4.0 变更】删除导入时评分计算，只保存原始数据?    评分移至查询阶段（PlayerScoreService），规则更新立即生效?    """
    today = date.today()

    # 批量预查询：收集所?account ?account-character ?    needed_accounts, needed_pairs = collect_needed_accounts_and_pairs(players)

    # 一次性查询所有已存在?AccountCharacter ?Member
    existing_acs, existing_members = fetch_existing_data(db, needed_accounts, needed_pairs)

    # 第一步：处理 Member ?AccountCharacter（内存字?O(1) 查找?    new_acs, member_map = process_members_and_characters(
        players, existing_acs, existing_members, db, today
    )
    if new_acs:
        db.add_all(new_acs)

    # 第二步：flush 获取所?member.id
    db.flush()

    # 第三步：创建 fight_stats
    account_to_player = build_account_to_player(players)
    fight_stats_mappings = build_fight_stats_mappings(fight_id, member_map, account_to_player)

    # 第四步：批量插入
    bulk_insert_fight_stats(db, fight_stats_mappings, fight_id)
