# -*- coding: utf-8 -*-
"""玩家验证工具模块"""
from app.services.zevtc.data_validator import EIJsonValidator
from app.utils.logger import logger

INVALID_ACCOUNT_STATS = {
    'total_skipped': 0,
    'blacklist_matches': 0,
    'format_errors': 0,
    'empty_accounts': 0,
}


def resolve_commander_tag(ei_player: dict) -> bool:
    """?EI JSON 解析指挥官标记?""
    if "hasCommanderTag" in ei_player:
        return bool(ei_player["hasCommanderTag"])
    if "isCommander" in ei_player:
        return bool(ei_player["isCommander"])
    return False


def should_skip_player(player_data) -> bool:
    """判断是否为需要跳过的假玩?NPC或无效账号?
    跳过规则?    1. isFake ?friendlyNPC 标记为真
    2. 账号名称在黑名单中（?"Non Squad Player"?    3. 账号为空或全是空?
    Args:
        player_data: 玩家数据（dict ?PlayerStats dataclass?
    Returns:
        True 表示需要跳过，False 表示有效玩家
    """
    if isinstance(player_data, dict):
        is_fake = bool(player_data.get("isFake") or player_data.get("friendlyNPC"))
        account = player_data.get("account", "").strip()
    else:
        is_fake = bool(
            getattr(player_data, "is_fake", False) or getattr(player_data, "friendly_npc", False)
        )
        account = getattr(player_data, "account", "").strip()

    if is_fake:
        logger.debug(f"[import] 跳过假玩?NPC: {account}")
        return True

    if not EIJsonValidator.is_valid_account_name(account):
        if not account:
            INVALID_ACCOUNT_STATS['empty_accounts'] += 1
            logger.debug(f"[import] 跳过空账?)
        else:
            valid, reason = EIJsonValidator.validate_account_name(account)
            if "黑名? in reason:
                INVALID_ACCOUNT_STATS['blacklist_matches'] += 1
            INVALID_ACCOUNT_STATS['total_skipped'] += 1
            logger.debug(f"[import] 跳过无效账号 '{account}': {reason}")
        return True

    return False
