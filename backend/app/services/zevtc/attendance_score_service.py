# -*- coding: utf-8 -*-
# 模块功能：出勤评分服务
# 作者：系统
# 创建日期：2026-05-04

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.json_loader import load_json_config
from app.models.log.fight import Fight
from app.constants.dict_values import RoleType
from app.models.log.fight_stats import FightStats


def get_account_score_breakdown(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """获取账号的评分维度明细（用于前端模态框展示）
    严格依据 scoring_rule 表中当前启用的维度配置进行展示，
    将该账号在统计周期内所有 fight_stats 中的 score_breakdown 按维度求平均值
    根据该账号最常用的职业确定角色类型和规则配置    """
    from app.services.game.game_data_service import GameDataService
    from app.services.scoring.scoring_rule_service import ScoringRuleService
    from app.utils.db.dict_utils import get_dict_label
    from app.services.wvw.scoring_service import ScoringService

    # 查询该账号的所有FightStats（带日期筛选）
    query = (
        db.query(FightStats)
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
    )
    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    if end_date:
        query = query.filter(Fight.start_time < end_date)

    stats_list = query.all()
    if not stats_list:
        return None

    # 确定该账号最常用的职业和角色类型
    profession_count: Dict[str, int] = {}
    for stat in stats_list:
        if stat.profession:
            profession_count[stat.profession] = profession_count.get(stat.profession, 0) + 1

    # 获取最常用职业
    most_used_profession = None
    if profession_count:
        most_used_profession = max(profession_count.items(), key=lambda x: x[1])[0]

    # 确定角色类型
    game_data = GameDataService()
    role_type = game_data.get_role_type(most_used_profession) if most_used_profession else RoleType.DPS

    # 获取评分规则服务
    rule_service = ScoringRuleService(db)
    
    # 获取评分规则
    rules = ScoringService.get_scoring_rules(db, role_type, most_used_profession)
    
    # 获取评分规则的维度详细信息（用于展示）
    display_rules = rule_service.get_rules_for_profession(role_type, most_used_profession, active_only=True)
    display_rules_dict = {rule.dimension: rule for rule in display_rules}

    # 按维度聚集评分
    total_score_sum = 0.0
    dimension_values: Dict[str, List[float]] = {}

    for stat in stats_list:
        total_score_sum += float(stat.ai_score or 0)
        if stat.score_breakdown:
            for dim, score in stat.score_breakdown.items():
                dimension_values.setdefault(dim, []).append(float(score))

    if not dimension_values:
        return None

    # 构建维度详情 - 优先使用规则中的维度和描述
    dimensions = {}
    
    # 首先添加规则中定义的维度
    for rule in display_rules:
        dim = rule.dimension
        values = dimension_values.get(dim, [])
        avg_score = round(sum(values) / len(values), 2) if values else 0
        dimensions[dim] = {
            "score": avg_score,
            "weight": rule.weight,
            "label": rule.description or get_dict_label("scoring_dimension", dim) or dim,
            "weighted_score": round(avg_score * rule.weight, 2),
        }
    
    # 添加其他可能存在但规则中未明确的维度
    for dim, values in sorted(dimension_values.items()):
        if dim not in dimensions:
            avg_score = round(sum(values) / len(values), 2)
            weight = rules.get(f"{dim}_weight", 0)
            dimensions[dim] = {
                "score": avg_score,
                "weight": weight,
                "label": get_dict_label("scoring_dimension", dim) or dim,
                "weighted_score": round(avg_score * weight, 2),
            }

    total_fights = len(stats_list)
    avg_total_score = round(total_score_sum / total_fights, 2) if total_fights > 0 else 0

    return {
        "account": account_name,
        "total_fights": total_fights,
        "avg_total_score": avg_total_score,
        "avg_grade": ScoringService.get_grade(avg_total_score),
        "role_type": role_type,
        "role_label": rule_service.get_role_label(role_type),
        "most_used_profession": most_used_profession,
        "dimensions": dimensions,
    }


def _get_default_abilities() -> Dict[str, float]:
    """返回默认综合能力评分（从 JSON 配置加载）"""
    config = load_json_config("scoring_rules")
    defaults = config.get("default_abilities", {}) if config else {}
    if not defaults:
        return {
            "damage": 70,
            "healing": 60,
            "survival": 65,
            "support": 55,
            "utility": 60,
            "mobility": 65,
        }
    return defaults.copy()


def _get_profession_and_role_type(
    stats_list: List[FightStats],
) -> Tuple[Optional[str], str]:
    """根据战斗统计数据确定最常用的职业和角色类型"""
    from app.services.game.game_data_service import GameDataService

    profession_count: Dict[str, int] = {}
    for stat in stats_list:
        if stat.profession:
            profession_count[stat.profession] = profession_count.get(stat.profession, 0) + 1

    most_used_profession = None
    if profession_count:
        most_used_profession = max(profession_count.items(), key=lambda x: x[1])[0]

    game_data = GameDataService()
    role_type = (
        game_data.get_role_type(most_used_profession)
        if most_used_profession
        else RoleType.DPS
    )
    return most_used_profession, role_type


def _calculate_damage_ability(
    total_damage: float, fight_count: int, total_avg_score: float
) -> float:
    """计算输出能力评分"""
    damage_score = min(
        100, (total_damage / fight_count / 50000) * 60 + (total_avg_score / 100) * 40
    )
    return round(damage_score, 1)


def _calculate_healing_ability(
    total_healing: float, fight_count: int, total_avg_score: float
) -> float:
    """计算治疗能力评分"""
    healing_score = min(
        100, (total_healing / fight_count / 100000) * 70 + (total_avg_score / 100) * 30
    )
    return round(healing_score, 1)


def _calculate_survival_ability(
    total_kills: float, total_deaths: float, total_avg_score: float
) -> float:
    """计算生存能力评分"""
    survival_base = 50
    kd = total_kills / max(total_deaths, 1)
    survival_score = min(100, survival_base + kd * 10 + (total_avg_score / 100) * 30)
    return round(survival_score, 1)


def _calculate_support_ability(
    avg_might: float,
    avg_fury: float,
    avg_alacrity: float,
    avg_quickness: float,
    avg_protection: float,
    avg_stability: float,
    total_strips: float,
    total_cleanses: float,
    fight_count: int,
    total_avg_score: float,
) -> float:
    """计算辅助能力评分"""
    boons_score = (
        avg_might + avg_fury + avg_alacrity + avg_quickness + avg_protection + avg_stability
    ) / 6
    support_score = min(
        100,
        boons_score * 0.5
        + (total_strips + total_cleanses) / fight_count * 10
        + (total_avg_score / 100) * 30,
    )
    return round(support_score, 1)


def _calculate_mechanics_ability(total_avg_score: float) -> float:
    """计算技能（机制）能力评分"""
    utility_score = min(100, total_avg_score * 0.8 + 20)
    return round(utility_score, 1)


def _calculate_mobility_ability(
    most_used_profession: Optional[str], total_avg_score: float
) -> float:
    """计算机动能力评分（高机动性职业从字典表读取）"""
    is_mobile = False
    if most_used_profession:
        from app.utils.db.dict_utils import get_dict_item_by_value
        item = get_dict_item_by_value("profession", most_used_profession)
        if item and item.get("remark"):
            import json
            try:
                extra = json.loads(item["remark"])
                is_mobile = extra.get("is_mobile", False)
            except json.JSONDecodeError:
                pass
    mobility_score = min(100, (total_avg_score * 0.7) + (30 if is_mobile else 15))
    return round(mobility_score, 1)


def _apply_role_type_adjustments(
    abilities: Dict[str, float], role_type: str
) -> None:
    """根据角色类型调整各维度权重（原地修改，从 JSON 配置加载）"""
    config = load_json_config("scoring_rules") or {}
    adjustments = config.get("role_adjustments", {})
    adj = adjustments.get(role_type, {})

    if role_type == RoleType.SUPPORT or role_type == RoleType.HEALING:
        abilities["healing"] = min(100, abilities["healing"] + adj.get("healing_bonus", 15))
        abilities["support"] = min(100, abilities["support"] + adj.get("support_bonus", 10))
    elif role_type == RoleType.TANK:
        abilities["survival"] = min(100, abilities["survival"] + adj.get("survival_bonus", 15))
    elif role_type == RoleType.CONDITION:
        abilities["damage"] = min(100, abilities["damage"] + adj.get("damage_bonus", 5))
    # dps 保持不变


def _calculate_comprehensive_abilities(
    db: Session,
    account_name: str,
    character_list: List[Dict[str, Any]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, float]:
    """基于评分规则计算综合能力评分

    维度： 输出、治疗、生存、辅助、技能、机动
        - 输出：基于伤害和职业定位
        - 治疗：基于治疗量和职业定义        - 生存：基于死亡次数和KD
        - 辅助：基于增益覆盖和机制能力      - 技能：基于评分和技能能力        - 机动：基于职业特性
    Returns:
        综合能力字典，各维度分数据-100分    """
    default_abilities = _get_default_abilities()

    if not character_list:
        return default_abilities

    # 获取该账号的所有战斗统计数据
    stats_query = (
        db.query(FightStats)
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
    )

    if start_date:
        stats_query = stats_query.filter(Fight.start_time >= start_date)
    if end_date:
        stats_query = stats_query.filter(Fight.start_time < end_date)

    stats_list = stats_query.all()

    if not stats_list:
        return default_abilities

    # 确定最常用的职业和角色类型
    most_used_profession, role_type = _get_profession_and_role_type(stats_list)

    # 计算累计数据
    total_damage = sum(float(s.damage or 0) for s in stats_list)
    total_healing = sum(float(s.healing or 0) for s in stats_list)
    total_deaths = sum(float(s.dead_count or 0) for s in stats_list)
    total_kills = sum(float(s.killed or 0) for s in stats_list)
    total_strips = sum(float(s.boon_strips or 0) for s in stats_list)
    total_cleanses = sum(float(s.condition_cleanses or 0) for s in stats_list)
    total_avg_score = sum(float(s.ai_score or 0) for s in stats_list) / len(stats_list)

    # 计算增益覆盖率平均值
    avg_might = sum(float(s.might_uptime or 0) for s in stats_list) / len(stats_list)
    avg_fury = sum(float(s.fury_uptime or 0) for s in stats_list) / len(stats_list)
    avg_alacrity = sum(float(s.alacrity_uptime or 0) for s in stats_list) / len(stats_list)
    avg_quickness = sum(float(s.quickness_uptime or 0) for s in stats_list) / len(stats_list)
    avg_protection = sum(float(s.protection_uptime or 0) for s in stats_list) / len(stats_list)
    avg_stability = sum(float(s.stability_uptime or 0) for s in stats_list) / len(stats_list)

    fight_count = len(stats_list)

    # 计算各维度分数
    abilities: Dict[str, float] = {}
    abilities["damage"] = _calculate_damage_ability(total_damage, fight_count, total_avg_score)
    abilities["healing"] = _calculate_healing_ability(total_healing, fight_count, total_avg_score)
    abilities["survival"] = _calculate_survival_ability(total_kills, total_deaths, total_avg_score)
    abilities["support"] = _calculate_support_ability(
        avg_might,
        avg_fury,
        avg_alacrity,
        avg_quickness,
        avg_protection,
        avg_stability,
        total_strips,
        total_cleanses,
        fight_count,
        total_avg_score,
    )
    abilities["utility"] = _calculate_mechanics_ability(total_avg_score)
    abilities["mobility"] = _calculate_mobility_ability(most_used_profession, total_avg_score)

    # 根据角色类型调整权重
    _apply_role_type_adjustments(abilities, role_type)

    return abilities
