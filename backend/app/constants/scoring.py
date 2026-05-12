# -*- coding: utf-8 -*-
"""
评分系统常量配置
集中管理评分规则相关的业务常量，避免硬编码分散在路由层?"""

# 角色描述映射（业务层定义，与字典表解耦）
ROLE_DESCRIPTIONS = {
    "dps": "以伤害输出为主要职责",
    "support": "以治疗和增益为主要职责",
    "tank": "以吸收伤害和控制为主要职责",
    "condition": "以症状伤害为主要职责",
    "healing": "以纯治疗为主要职责",
    "control": "以控场打断为主要职责",
    "utility": "以功能辅助为主要职责",
}

# 评分维度列表
SCORING_DIMENSIONS = [
    {"key": "damage", "label": "总伤害"},
    {"key": "power_damage", "label": "直伤"},
    {"key": "condition_damage", "label": "症状伤害"},
    {"key": "healing", "label": "治疗量"},
    {"key": "boons", "label": "增益覆盖"},
    {"key": "alacrity", "label": "敏捷覆盖"},
    {"key": "quickness", "label": "急速覆盖"},
    {"key": "survival", "label": "生存能力"},
    {"key": "strips", "label": "破法"},
    {"key": "cleanses", "label": "清症?"},
    {"key": "kills", "label": "击杀"},
    {"key": "breakbar", "label": "蔑视"},
    {"key": "damage_taken", "label": "承受伤害"},
    {"key": "blocked_count", "label": "格挡"},
    {"key": "evaded_count", "label": "闪避"},
]

# 默认评分规则权重（规则表为空时的兜底配置）
DEFAULT_FALLBACK_RULES = {
    "damage_weight": 0.35,
    "power_damage_weight": 0.15,
    "condition_damage_weight": 0.15,
    "healing_weight": 0.20,
    "boons_weight": 0.10,
    "alacrity_weight": 0.05,
    "quickness_weight": 0.05,
    "survival_weight": 0.10,
    "strips_weight": 0.03,
    "cleanses_weight": 0.02,
    "kills_weight": 0.05,
    "breakbar_weight": 0.03,
    "min_score_threshold": 0.0,
    "max_score_cap": 100.0,
}

# 评分规则内存缓存 TTL（秒）
RULE_CACHE_TTL_SECONDS = 60.0

# 默认综合能力评分（出勤评分模块）
DEFAULT_ABILITIES = {
    "damage": 70,
    "healing": 60,
    "survival": 65,
    "support": 55,
    "utility": 60,
    "mobility": 65,
}

# 高机动性职业列表（用于机动能力评分）
MOBILE_PROFESSIONS = ["盗贼", "游侠", "战士", "魂武者"]
