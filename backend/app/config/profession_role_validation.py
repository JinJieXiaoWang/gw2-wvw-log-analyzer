# -*- coding: utf-8 -*-
# 模块功能：职业角色定位校验配置
# 说明：定义各精英特长的推荐角色定位，与前端 professionRoleValidation.ts 保持同步

from typing import Dict, Optional

# 精英特长推荐角色定位映射
# 数据来源：backend/app/data/seeds/v1.0.0/006_gw_elite_specialization.json
RECOMMENDED_ROLE_MAP: Dict[str, str] = {
    # Guardian
    "Dragonhunter": "dps",
    "Firebrand": "support",
    "Willbender": "dps",
    "Luminary": "support",
    # Warrior
    "Berserker": "dps",
    "Spellbreaker": "control",
    "Bladesworn": "dps",
    "Paragon": "tank",
    # Engineer
    "Scrapper": "support",
    "Holosmith": "dps",
    "Mechanist": "support",
    "Amalgam": "dps",
    # Ranger
    "Druid": "support",
    "Soulbeast": "dps",
    "Untamed": "dps",
    "Galeshot": "dps",
    # Thief
    "Daredevil": "dps",
    "Deadeye": "dps",
    "Specter": "dps",
    "Antiquary": "support",
    # Elementalist
    "Tempest": "support",
    "Weaver": "dps",
    "Catalyst": "dps",
    "Evoker": "dps",
    # Mesmer
    "Chronomancer": "support",
    "Mirage": "dps",
    "Virtuoso": "dps",
    "Troubadour": "support",
    # Necromancer
    "Reaper": "dps",
    "Scourge": "support",
    "Harbinger": "dps",
    "Ritualist": "support",
    # Revenant
    "Herald": "support",
    "Renegade": "dps",
    "Vindicator": "dps",
    "Conduit": "support",
}

ROLE_LABEL_MAP: Dict[str, str] = {
    "dps": "输出",
    "support": "辅助",
    "tank": "坦克",
    "control": "控制",
}


def get_recommended_role(profession: str) -> Optional[str]:
    """获取精英特长的推荐角色定位"""
    return RECOMMENDED_ROLE_MAP.get(profession)


def check_role_conflict(profession: str, current_role: str) -> Optional[Dict[str, str]]:
    """检查角色定位是否与推荐定位冲突
    
    Returns:
        冲突信息字典，无冲突返回 None
    """
    recommended = get_recommended_role(profession)
    if not recommended:
        return None
    if recommended == current_role:
        return None
    return {
        "profession": profession,
        "current_role": current_role,
        "current_role_label": ROLE_LABEL_MAP.get(current_role, current_role),
        "recommended_role": recommended,
        "recommended_role_label": ROLE_LABEL_MAP.get(recommended, recommended),
        "message": f"{profession} 的推荐定位为「{ROLE_LABEL_MAP.get(recommended, recommended)}」，"
                   f"当前设置为「{ROLE_LABEL_MAP.get(current_role, current_role)}」",
    }


def is_high_risk_role_combination(role_type: str, profession: str) -> bool:
    """检查是否为高风险的角色-职业组合"""
    recommended = get_recommended_role(profession)
    if not recommended:
        return False
    return recommended != role_type
