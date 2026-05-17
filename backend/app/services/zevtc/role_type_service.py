# -*- coding: utf-8 -*-
# 模块功能：角色定位服务
# 说明：统一的角色定位逻辑，消除不同接口间的不一致性

from typing import Dict, List, Optional, Any, Tuple

from app.models.log.fight_stats import FightStats


def get_role_type_by_profession(profession: Optional[str]) -> str:
    """根据职业名称获取固有角色定位

    从游戏数据（精英特长配置）中读取 role_type，不回退到权重覆盖逻辑。
    这是角色定位的唯一来源，确保所有接口返回一致的结果。
    """
    if not profession:
        return "dps"

    from app.services.game.game_data_service import GameDataService
    game_data = GameDataService()
    return game_data.get_role_type(profession) or "dps"


def get_most_used_profession(stats_list: List[FightStats]) -> Optional[str]:
    """根据战斗统计确定最常用的职业"""
    profession_count: Dict[str, int] = {}
    for stat in stats_list:
        if stat.profession:
            profession_count[stat.profession] = profession_count.get(stat.profession, 0) + 1

    if profession_count:
        return max(profession_count.items(), key=lambda x: x[1])[0]
    return None


def get_profession_and_role_type(
    stats_list: List[FightStats],
) -> Tuple[Optional[str], str]:
    """统一接口：根据战斗统计数据确定最常用的职业和角色类型

    返回: (most_used_profession, role_type)
    """
    most_used_profession = get_most_used_profession(stats_list)
    role_type = get_role_type_by_profession(most_used_profession)
    return most_used_profession, role_type
