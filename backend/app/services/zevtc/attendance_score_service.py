# -*- coding: utf-8 -*-
# 模块功能：出勤评分服务
# 作者：系统
# 创建日期：2026-05-04

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.json_loader import load_json_config
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


def get_account_score_breakdown(
    db: Session,
    account_name: str,
    profession: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """获取账号的评分维度明细（用于前端模态框展示）
    严格依据 scoring_rule 表中当前启用的维度配置进行展示，
    将该账号在统计周期内所有 fight_stats 中的 score_breakdown 按维度求平均值
    
    Args:
        profession: 指定职业（精英特长英文名），为 None 时自动计算最常用职业
    """
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

    # 确定职业和角色类型
    if profession:
        # 指定了职业：直接使用该职业查询规则
        target_profession = profession
        # 从该职业的数据中重新过滤 stats_list（只保留该职业的数据）
        stats_list = [s for s in stats_list if s.profession == profession]
        if not stats_list:
            return None
    else:
        # 未指定职业：计算最常用职业
        profession_count: Dict[str, int] = {}
        for stat in stats_list:
            if stat.profession:
                profession_count[stat.profession] = profession_count.get(stat.profession, 0) + 1
        target_profession = max(profession_count.items(), key=lambda x: x[1])[0] if profession_count else None

    # 确定角色类型 — 从数据库直接查询，避免 GameDataService 缓存数据不准
    role_type = _get_role_type_from_db(db, target_profession) if target_profession else "dps"

    # 获取评分规则服务
    rule_service = ScoringRuleService(db)
    
    # 根据评分模式选择规则来源
    scoring_mode = ScoringService._get_scoring_mode(db)
    
    if scoring_mode == "profession_based" and target_profession:
        # 职业评分模式：优先使用职业特定规则
        rules = ScoringService.get_scoring_rules(db, role_type, target_profession)
        display_rules = rule_service.get_rules_for_profession(role_type, target_profession, active_only=True)
    else:
        # 角色定位评分模式：强制使用通用规则
        rules = ScoringService.get_scoring_rules(db, role_type, None)
        display_rules = rule_service.get_rules_by_role(role_type, None, active_only=True)
    
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

    # 获取通用规则的标准描述（用于统一显示效果）
    generic_rules = rule_service.get_rules_by_role(role_type, None, active_only=True)
    generic_desc_map = {rule.dimension: rule.description for rule in generic_rules if rule.description}

    # 构建维度详情 - 使用通用规则的标准描述，确保职业特定规则与通用规则显示一致
    dimensions = {}
    
    # 首先添加规则中定义的维度
    for rule in display_rules:
        dim = rule.dimension
        values = dimension_values.get(dim, [])
        avg_score = round(sum(values) / len(values), 2) if values else 0
        # 优先使用通用规则的标准描述，避免职业特定规则 description 格式不一致
        standard_label = generic_desc_map.get(dim) or get_dict_label("scoring_dimension", dim) or rule.description or dim
        dimensions[dim] = {
            "score": avg_score,
            "weight": rule.weight,
            "label": standard_label,
            "weighted_score": round(avg_score * rule.weight, 2),
        }
    
    # 严格只展示该角色类型评分规则中定义的维度

    total_fights = len(stats_list)
    avg_total_score = round(total_score_sum / total_fights, 2) if total_fights > 0 else 0

    # 数据驱动的角色定位
    data_role = _detect_role_by_data(stats_list)

    return {
        "account": account_name,
        "total_fights": total_fights,
        "avg_total_score": avg_total_score,
        "avg_grade": ScoringService.get_grade(avg_total_score),
        "role_type": role_type,
        "role_label": rule_service.get_role_label(role_type),
        "profession_role_type": role_type,
        "profession_role_label": rule_service.get_role_label(role_type),
        "data_role_type": data_role["role_type"],
        "data_role_label": data_role["role_label"],
        "data_role_reason": data_role["reason"],
        "most_used_profession": target_profession,
        "most_used_profession_cn": _get_profession_name(db, target_profession),
        "dimensions": dimensions,
    }


def _detect_role_by_data(stats_list: List[FightStats]) -> Dict[str, str]:
    """根据实际战斗数据判定角色定位（数据驱动）
    
    判定逻辑：
    - Support: 治疗量 > 0 且 (might_uptime > 50% 或 quickness_uptime > 30%)
    - Tank: 承伤量 > 团队平均120% 且 死亡次数 <= 团队平均
    - Control: 削增益次数 > 团队平均120% 或 清症次数 > 团队平均120%
    - DPS: 以上都不是，但伤害量高
    """
    if not stats_list:
        return {"role_type": "dps", "role_label": "输出", "reason": "无战斗数据"}

    # 计算团队平均值（用于相对比较）
    team_avg_damage = sum((s.damage or 0) for s in stats_list) / len(stats_list)
    team_avg_healing = sum((s.healing or 0) for s in stats_list) / len(stats_list)
    team_avg_damage_taken = sum((s.damage_taken or 0) for s in stats_list) / len(stats_list)
    team_avg_boon_strips = sum((s.boon_strips or 0) for s in stats_list) / len(stats_list)
    team_avg_cleanses = sum((s.condition_cleanses or 0) for s in stats_list) / len(stats_list)
    team_avg_deaths = sum((s.dead_count or 0) for s in stats_list) / len(stats_list)

    # 计算该账号的平均值
    avg_healing = sum((s.healing or 0) for s in stats_list) / len(stats_list)
    avg_might = sum(float(s.might_uptime or 0) for s in stats_list) / len(stats_list)
    avg_quickness = sum(float(s.quickness_uptime or 0) for s in stats_list) / len(stats_list)
    avg_damage_taken = sum((s.damage_taken or 0) for s in stats_list) / len(stats_list)
    avg_boon_strips = sum((s.boon_strips or 0) for s in stats_list) / len(stats_list)
    avg_cleanses = sum((s.condition_cleanses or 0) for s in stats_list) / len(stats_list)
    avg_deaths = sum((s.dead_count or 0) for s in stats_list) / len(stats_list)
    avg_damage = sum((s.damage or 0) for s in stats_list) / len(stats_list)

    ROLE_LABELS = {"dps": "输出", "support": "辅助", "tank": "坦克", "control": "控制"}

    # Support 判定：有治疗且增益覆盖高
    if avg_healing > 0 and (avg_might > 50 or avg_quickness > 30):
        return {
            "role_type": "support",
            "role_label": ROLE_LABELS["support"],
            "reason": f"治疗量{avg_healing:.0f}，增益覆盖(Might:{avg_might:.0f}%/Quick:{avg_quickness:.0f}%)",
        }

    # Tank 判定：承伤高且生存能力强
    if team_avg_damage_taken > 0 and avg_damage_taken > team_avg_damage_taken * 1.2:
        if avg_deaths <= team_avg_deaths * 1.2:
            return {
                "role_type": "tank",
                "role_label": ROLE_LABELS["tank"],
                "reason": f"承伤量{avg_damage_taken:.0f}（团队均值{team_avg_damage_taken:.0f}的{avg_damage_taken/team_avg_damage_taken*100:.0f}%）",
            }

    # Control 判定：削增益或清症高
    if team_avg_boon_strips > 0 and avg_boon_strips > team_avg_boon_strips * 1.2:
        return {
            "role_type": "control",
            "role_label": ROLE_LABELS["control"],
            "reason": f"削增益{avg_boon_strips:.0f}次（团队均值{team_avg_boon_strips:.0f}的{avg_boon_strips/team_avg_boon_strips*100:.0f}%）",
        }
    if team_avg_cleanses > 0 and avg_cleanses > team_avg_cleanses * 1.2:
        return {
            "role_type": "control",
            "role_label": ROLE_LABELS["control"],
            "reason": f"清症{avg_cleanses:.0f}次（团队均值{team_avg_cleanses:.0f}的{avg_cleanses/team_avg_cleanses*100:.0f}%）",
        }

    # 默认 DPS
    damage_ratio = (avg_damage / team_avg_damage * 100) if team_avg_damage > 0 else 0
    return {
        "role_type": "dps",
        "role_label": ROLE_LABELS["dps"],
        "reason": f"伤害量{avg_damage:.0f}（团队均值的{damage_ratio:.0f}%）",
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

    if role_type == "support":
        abilities["healing"] = min(100, abilities["healing"] + adj.get("healing_bonus", 15))
        abilities["support"] = min(100, abilities["support"] + adj.get("support_bonus", 10))
    elif role_type == "tank":
        abilities["survival"] = min(100, abilities["survival"] + adj.get("survival_bonus", 15))
    elif role_type == "control":
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

    # 确定最常用的职业和角色类型（使用统一角色定位服务）
    from app.services.zevtc.role_type_service import get_profession_and_role_type
    most_used_profession, role_type = get_profession_and_role_type(stats_list)

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


def _get_profession_name(db: Session, profession_key: Optional[str]) -> Optional[str]:
    """根据精英特长英文键获取中文名称"""
    if not profession_key:
        return None
    from app.services.game.profession_service import ProfessionService
    service = ProfessionService(db)
    spec = service.get_spec_by_key(profession_key)
    if spec:
        return spec.get("spec_name") or profession_key
    # 回退：尝试作为基础职业查询
    prof = service.get_profession(profession_key)
    return prof.get("profession_name") if prof else profession_key


def _get_role_type_from_db(db: Session, profession_key: str) -> str:
    """从数据库查询精英特长的角色定位，避免使用可能过时的缓存数据"""
    from app.services.game.profession_service import ProfessionService
    service = ProfessionService(db)
    spec = service.get_spec_by_key(profession_key)
    if spec:
        return spec.get("role_type", "dps") or "dps"
    # 回退：尝试从基础职业查询
    prof = service.get_profession(profession_key)
    if prof:
        return prof.get("role_type", "dps") or "dps"
    return "dps"
