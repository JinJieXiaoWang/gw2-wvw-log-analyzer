# -*- coding: utf-8 -*-
"""玩家数据导入工具模块（members + fight_stats 公共逻辑）"""

from datetime import date
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy import tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.auth.account_character import AccountCharacter
from app.models.auth.member import Member
from app.models.log.fight_stats import FightStats
from app.utils.logger import logger


def collect_needed_accounts_and_pairs(
    players: List[Dict[str, Any]],
) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """从玩家列表中提取需要查询的所有 account 和 account-character 对"""
    needed_accounts: Set[str] = set()
    needed_pairs: Set[Tuple[str, str]] = set()
    for p in players:
        account = p.get("account", "").strip()[:100]
        if account:
            needed_accounts.add(account)
            needed_pairs.add((account, p.get("character_name", "").strip()[:100]))
    return needed_accounts, needed_pairs


def fetch_existing_data(
    db: Session,
    needed_accounts: Set[str],
    needed_pairs: Set[Tuple[str, str]],
) -> Tuple[Dict[Tuple[str, str], AccountCharacter], Dict[str, Member]]:
    """批量预查询已存在的 AccountCharacter 和 Member 记录"""
    existing_acs: Dict[Tuple[str, str], AccountCharacter] = {}
    if needed_pairs:
        existing_acs = {
            (ac.account_name, ac.character_name): ac
            for ac in db.query(AccountCharacter)
            .filter(
                tuple_(
                    AccountCharacter.account_name, AccountCharacter.character_name
                ).in_(needed_pairs)
            )
            .all()
        }

    existing_members: Dict[str, Member] = {}
    if needed_accounts:
        existing_members = {
            m.account_name: m
            for m in db.query(Member)
            .filter(Member.account_name.in_(needed_accounts))
            .all()
        }

    return existing_acs, existing_members


def process_members_and_characters(
    players: List[Dict[str, Any]],
    existing_acs: Dict[Tuple[str, str], AccountCharacter],
    existing_members: Dict[str, Member],
    db: Session,
    today: date = None,
) -> Tuple[List[AccountCharacter], Dict[str, Member]]:
    """处理 Member 和 AccountCharacter 的更新/创建（内存字典 O(1) 查找）

    过滤规则：
    - 仅处理包含 account 数据 的记录
    - 同一 fight 内同一 account 去重

    Returns:
        (new_acs, member_map)
    """
    if today is None:
        today = date.today()
    seen_accounts: set = set()
    new_acs: List[AccountCharacter] = []
    member_map: Dict[str, Member] = {}

    for p in players:
        account = p.get("account", "").strip()[:100]
        if not account:
            continue
        if account in seen_accounts:
            continue
        seen_accounts.add(account)

        character_name = p.get("character_name", "").strip()[:100]
        profession = p.get("profession", "").strip()[:50]

        ac = existing_acs.get((account, character_name))
        if ac:
            ac.last_seen_date = today
            ac.seen_count += 1
            if profession and ac.profession != profession:
                ac.profession = profession
        else:
            new_acs.append(
                AccountCharacter(
                    account_name=account,
                    character_name=character_name,
                    profession=profession,
                    first_seen_date=today,
                    last_seen_date=today,
                    seen_count=1,
                )
            )

        member = existing_members.get(account)
        if not member:
            member = Member(account_name=account)
            db.add(member)
            existing_members[account] = member

        member_map[account] = member

    return new_acs, member_map


def build_account_to_player(players: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """构建 account -> player 映射（同一 account 仅保留第一条）"""
    account_to_player: Dict[str, Dict] = {}
    for p in players:
        account = p.get("account", "").strip()
        if account and account not in account_to_player:
            account_to_player[account] = p
    return account_to_player


def bulk_insert_fight_stats(
    db: Session,
    fight_stats_mappings: List[Dict[str, Any]],
    fight_id: int,
) -> None:
    """批量插入 fight_stats，失败时逐条回退插入口"""
    if not fight_stats_mappings:
        return
    try:
        db.bulk_insert_mappings(FightStats, fight_stats_mappings)
        db.flush()
    except IntegrityError as exc:
        logger.error(
            f"[import] bulk_insert_mappings(FightStats) 失败: "
            f"fight_id={fight_id}, mappings_count={len(fight_stats_mappings)}, "
            f"error={exc}",
            exc_info=True,
        )
        for idx, mapping in enumerate(fight_stats_mappings):
            try:
                db.bulk_insert_mappings(FightStats, [mapping])
                db.flush()
            except IntegrityError as inner_exc:
                logger.error(
                    f"[import] 单条插入失败 idx={idx}, "
                    f"account={mapping.get('account')}, "
                    f"member_id={mapping.get('member_id')}, "
                    f"error={inner_exc}"
                )
                raise
        raise
