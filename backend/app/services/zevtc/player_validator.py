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
    """解析 EI JSON 中的指挥官标记
    检查 "hasCommanderTag" 或 "isCommander" 字段，返回布尔值
    Args:
        ei_player: 单个玩家的 EI 数据（dict）
    Returns:
        bool: 是否为指挥官
    """
    if "hasCommanderTag" in ei_player:
        return bool(ei_player["hasCommanderTag"])
    if "isCommander" in ei_player:
        return bool(ei_player["isCommander"])
    return False


def should_skip_player(player_data) -> bool:
    """判断是否为需要跳过的假玩 NPC 或无效账号
    跳过规则：
    1. isFake 或 friendlyNPC 标记为真
    2. 账号名称在黑名单中（Non Squad Player）
    3. 账号为空或全是空格
    Args:
        player_data: 玩家数据（dict 或 dataclass）
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
        logger.debug(f"[import] 跳过假玩玩家/NPC: {account}")
        return True

    if not EIJsonValidator.is_valid_account_name(account):
        if not account:
            INVALID_ACCOUNT_STATS['empty_accounts'] += 1
            logger.debug(f"[import] 跳过空账号: {account}")
        else:
            valid, reason = EIJsonValidator.validate_account_name(account)
            if "黑名单" in reason:
                INVALID_ACCOUNT_STATS['blacklist_matches'] += 1
            INVALID_ACCOUNT_STATS['total_skipped'] += 1
            logger.debug(f"[import] 跳过无效账号 '{account}': {reason}")
        return True

    return False
