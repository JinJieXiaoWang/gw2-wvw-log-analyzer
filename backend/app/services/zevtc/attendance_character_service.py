# -*- coding: utf-8 -*-
# 模块功能：角色综合能力评分服务
# 说明：从 attendance_service.py 拆分，支持按角色独立计算综合能力

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.json_loader import load_json_config
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats


# 评分规则维度 → 六维能力映射
_RULE_DIMENSION_MAP: Dict[str, str] = {
    "damage": "damage",
    "power_damage": "damage",
    "condition_damage": "damage",
    "healing": "healing",
    "survival": "survival",
    "boons": "support",
    "alacrity": "support",
    "quickness": "support",
    "cleanses": "support",
    "strips": "utility",
    "breakbar": "utility",
    "blocked_count": "utility",
    "evaded_count": "utility",
    "interrupts": "utility",
}


def _get_ability_adjustments_from_rules(rules: List[Any]) -> Dict[str, float]:
    """根据评分规则计算六维能力调整因子
    
    将评分规则中的维度权重聚合到六维能力上，返回各维度的权重占比。
    占比高的维度会在最终分数中获得加成。
    """
    if not rules:
        return {}
    
    # 按六维能力聚合权重
    ability_weights: Dict[str, float] = {}
    for rule in rules:
        ability = _RULE_DIMENSION_MAP.get(rule.dimension)
        if ability:
            ability_weights[ability] = ability_weights.get(ability, 0) + rule.weight
    
    if not ability_weights:
        return {}
    
    total_weight = sum(ability_weights.values())
    if total_weight <= 0:
        return {}
    
    # 归一化为占比，并计算调整因子（占比越高，调整因子越大，范围 0.9~1.15）
    adjustments = {}
    for ability, weight in ability_weights.items():
        ratio = weight / total_weight
        # 占比 0% → 0.90, 占比 50% → 1.025, 占比 100% → 1.15
        adjustments[ability] = 0.90 + ratio * 0.25
    
    return adjustments


def calculate_character_abilities(
    db: Session,
    account_name: str,
    character_name: str,
    profession: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, float]:
    """计算指定角色的综合能力评分（6维）

    维度：damage / healing / survival / support / utility / mobility
    
    计算逻辑：
    1. 基于角色实际战斗数据计算基础分数
    2. 查询该职业的评分规则，根据规则权重调整各维度分数
    3. 根据角色类型做最终微调
    """
    from app.services.game.profession_service import ProfessionService
    from app.services.scoring.scoring_rule_service import ScoringRuleService

    default_abilities = _get_default_abilities()

    stats_query = (
        db.query(FightStats)
        .join(Fight, FightStats.fight_id == Fight.id)
        .filter(FightStats.account == account_name)
        .filter(FightStats.character_name == character_name)
    )
    if start_date:
        stats_query = stats_query.filter(Fight.start_time >= start_date)
    if end_date:
        stats_query = stats_query.filter(Fight.start_time < end_date)

    stats_list = stats_query.all()
    if not stats_list:
        return default_abilities

    # 从数据库直接查询角色定位，避免使用可能过时的缓存
    role_type = _get_role_type_from_db(db, profession) if profession else "dps"

    # 查询该职业的评分规则（用于动态调整权重）
    rule_service = ScoringRuleService(db)
    scoring_rules = rule_service.get_rules_for_profession(role_type, profession, active_only=True)
    ability_adjustments = _get_ability_adjustments_from_rules(scoring_rules)

    total_damage = sum(float(s.damage or 0) for s in stats_list)
    total_healing = sum(float(s.healing or 0) for s in stats_list)
    total_deaths = sum(float(s.dead_count or 0) for s in stats_list)
    total_kills = sum(float(s.killed or 0) for s in stats_list)
    total_boon_strips = sum(float(s.boon_strips or 0) for s in stats_list)
    total_cleanses = sum(float(s.condition_cleanses or 0) for s in stats_list)
    total_interrupts = sum(float(s.interrupts or 0) for s in stats_list)
    total_dodge_count = sum(float(s.dodge_count or 0) for s in stats_list)

    avg_might = sum(float(s.might_uptime or 0) for s in stats_list) / len(stats_list)
    avg_fury = sum(float(s.fury_uptime or 0) for s in stats_list) / len(stats_list)
    avg_quickness = sum(float(s.quickness_uptime or 0) for s in stats_list) / len(stats_list)
    avg_alacrity = sum(float(s.alacrity_uptime or 0) for s in stats_list) / len(stats_list)
    avg_protection = sum(float(s.protection_uptime or 0) for s in stats_list) / len(stats_list)
    avg_stability = sum(float(s.stability_uptime or 0) for s in stats_list) / len(stats_list)

    fight_count = len(stats_list)

    # 基础分数计算
    damage_score = min(100.0, max(30.0, (total_damage / max(fight_count * 500000, 1)) * 100))
    damage_score = 0.7 * damage_score + 0.3 * ((avg_might + avg_fury) / 2)

    healing_score = min(100.0, max(30.0, (total_healing / max(fight_count * 200000, 1)) * 100))

    survival_death_penalty = (total_deaths / max(fight_count * 2, 1)) * 50
    survival_score = 100 - survival_death_penalty
    survival_score = 0.6 * survival_score + 0.4 * avg_protection
    survival_score = min(100.0, max(30.0, survival_score))

    support_buffs = (avg_quickness + avg_alacrity + avg_might + avg_fury) / 4
    support_score = 0.5 * support_buffs + 0.3 * healing_score + 0.2 * (total_boon_strips / max(fight_count * 20, 1) * 100)
    support_score = min(100.0, max(30.0, support_score))

    utility_score = (
        (total_interrupts / max(fight_count * 5, 1)) * 33
        + (total_cleanses / max(fight_count * 20, 1)) * 33
        + (total_boon_strips / max(fight_count * 20, 1)) * 34
    )
    utility_score = min(100.0, max(30.0, utility_score))

    mobility_score = (total_dodge_count / max(fight_count * 10, 1)) * 50 + avg_stability * 0.5
    mobility_score = min(100.0, max(30.0, mobility_score))

    abilities = {
        "damage": round(damage_score, 1),
        "healing": round(healing_score, 1),
        "survival": round(survival_score, 1),
        "support": round(support_score, 1),
        "utility": round(utility_score, 1),
        "mobility": round(mobility_score, 1),
    }

    # 根据评分规则权重动态调整（优先应用，因为基于职业特定数据）
    for ability, factor in ability_adjustments.items():
        if ability in abilities:
            abilities[ability] = round(min(100.0, abilities[ability] * factor), 1)

    # 根据角色类型做最终微调
    _apply_role_type_adjustments(abilities, role_type)

    return abilities


def _get_default_abilities() -> Dict[str, float]:
    """返回默认综合能力评分（从 JSON 配置加载）"""
    config = load_json_config("scoring_rules")
    defaults = config.get("default_abilities", {}) if config else {}
    if not defaults:
        return {
            "damage": 70.0,
            "healing": 60.0,
            "survival": 65.0,
            "support": 55.0,
            "utility": 60.0,
            "mobility": 65.0,
        }
    return defaults.copy()


def get_daily_fights(
    db: Session,
    account_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """获取账号的战斗记录并按日期分组

    Returns:
        按日期倒序排列的每日战斗分组列表
    """
    from collections import OrderedDict

    query = (
        db.query(
            Fight.id.label("fight_id"),
            Fight.map_name,
            Fight.server_name,
            Fight.start_time,
            Fight.duration_sec,
            FightStats.character_name,
            FightStats.profession,
            FightStats.damage,
            FightStats.dps,
            FightStats.killed,
            FightStats.dead_count,
            FightStats.ai_score,
        )
        .join(FightStats, Fight.id == FightStats.fight_id)
        .filter(FightStats.account == account_name)
    )

    if start_date:
        query = query.filter(Fight.start_time >= start_date)
    if end_date:
        query = query.filter(Fight.start_time < end_date)

    rows = query.order_by(Fight.start_time.desc()).limit(limit).all()

    # 批量查询职业中文名
    prof_keys = list(set(r.profession for r in rows if r.profession))
    prof_name_map: Dict[str, str] = {}
    if prof_keys:
        from app.models.game.profession import GwEliteSpecialization, GwProfession
        spec_rows = (
            db.query(GwEliteSpecialization.spec_key, GwEliteSpecialization.spec_name)
            .filter(GwEliteSpecialization.spec_key.in_(prof_keys))
            .all()
        )
        prof_name_map = {row.spec_key: row.spec_name for row in spec_rows}
        # 未找到的尝试作为基础职业查询
        missing = [k for k in prof_keys if k not in prof_name_map]
        if missing:
            prof_rows = (
                db.query(GwProfession.profession_key, GwProfession.profession_name)
                .filter(GwProfession.profession_key.in_(missing))
                .all()
            )
            for row in prof_rows:
                prof_name_map[row.profession_key] = row.profession_name

    daily_map: OrderedDict[str, Dict[str, Any]] = OrderedDict()

    for row in rows:
        date_str = row.start_time.strftime("%Y-%m-%d") if row.start_time else "Unknown"
        if date_str not in daily_map:
            daily_map[date_str] = {
                "date": date_str,
                "day_of_week": _get_day_of_week(row.start_time),
                "fight_count": 0,
                "total_duration_sec": 0,
                "total_damage": 0,
                "total_kills": 0,
                "total_deaths": 0,
                "fights": [],
            }
        day = daily_map[date_str]
        day["fight_count"] += 1
        day["total_duration_sec"] += row.duration_sec or 0
        day["total_damage"] += row.damage or 0
        day["total_kills"] += row.killed or 0
        day["total_deaths"] += row.dead_count or 0
        prof_cn = prof_name_map.get(row.profession, row.profession) if row.profession else None
        day["fights"].append({
            "fight_id": row.fight_id,
            "time": row.start_time.strftime("%H:%M") if row.start_time else "--:--",
            "map_name": row.map_name or "Unknown",
            "duration_sec": row.duration_sec or 0,
            "character_name": row.character_name,
            "profession_en": row.profession,
            "profession": prof_cn,
            "damage": row.damage or 0,
            "dps": row.dps or 0,
            "killed": row.killed or 0,
            "dead_count": row.dead_count or 0,
            "ai_score": round(float(row.ai_score), 2) if row.ai_score else 0,
        })

    return list(daily_map.values())


def _get_day_of_week(dt: Optional[datetime]) -> str:
    """返回星期几的中文名称"""
    if not dt:
        return "未知"
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[dt.weekday()]


def _get_role_type_from_db(db: Session, profession_key: str) -> str:
    """从数据库查询精英特长的角色定位，避免使用可能过时的缓存数据"""
    from app.services.game.profession_service import ProfessionService
    service = ProfessionService(db)
    spec = service.get_spec_by_key(profession_key)
    if spec:
        return spec.get("role_type", "dps") or "dps"
    prof = service.get_profession(profession_key)
    if prof:
        return prof.get("role_type", "dps") or "dps"
    return "dps"


def _apply_role_type_adjustments(
    abilities: Dict[str, float],
    role_type: str,
) -> None:
    """根据角色类型调整各维度权重（原地修改字典）"""
    config = load_json_config("scoring_rules") or {}
    adjustments = config.get("role_adjustments", {})
    adj = adjustments.get(role_type, {})

    if role_type == "support":
        abilities["healing"] = min(100.0, abilities["healing"] * adj.get("healing_multiplier", 1.3))
        abilities["support"] = min(100.0, abilities["support"] * adj.get("support_multiplier", 1.3))
        abilities["damage"] = abilities["damage"] * adj.get("damage_multiplier", 0.8)
    elif role_type == "tank":
        abilities["survival"] = min(100.0, abilities["survival"] * adj.get("survival_multiplier", 1.3))
        abilities["support"] = min(100.0, abilities["support"] * adj.get("support_multiplier", 1.1))
    elif role_type == "control":
        abilities["utility"] = min(100.0, abilities["utility"] * adj.get("utility_multiplier", 1.3))
