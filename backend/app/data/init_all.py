# -*- coding: utf-8 -*-
"""
统一数据初始化入口

功能：项目启动时唯一的初始化执行所有表的执行所有表的种子数据导入口
所有数据以 Python 内嵌字典.py 压缩包形式维护，不再依赖任何外部文件

初始化顺序：
1. 系统菜单 (sys_menu)
2. 字典类型 (sys_dict_type) - ?role/scoring_dimension/game_mode
3. 角色定位 (gw_role_type)
4. 基础职业 (gw_profession)
5. 精英特长 (gw_elite_specialization)
6. 游戏静态数据(gw_skill / gw_specialization / gw_trait / gw_skill_palette / gw_buff)
7. Build 图书馆(build)

作者： 帅妹妹丶.8297
创建日期: 2026-05-12
"""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.data import seed_data
from app.models.game.build import Build
from app.models.game.dictionary import SysDictData, SysDictType
from app.models.game.game_static_data import (
    GwBuff,
    GwSkill,
    GwSkillPalette,
    GwSpecialization,
    GwTrait,
)
from app.models.game.profession import (
    GwEliteSpecialization,
    GwProfession,
    GwRoleType,
)
from app.models.system.sys_menu import SysMenu
from app.services.game.build_service import create_build
from app.utils.logger import logger

# =============================================================================
# 系统菜单种子数据
# =============================================================================
_SYS_MENU_SEED = [
    {
        "menu_name": "数据看板",
        "parent_id": 0,
        "order_num": 1,
        "path": "/",
        "component": "dashboard/index",
        "route_name": "home",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "home",
        "perms": None,
        "remark": "数据总览首页（公开）",
    },
    {
        "menu_name": "日志管理",
        "parent_id": 0,
        "order_num": 2,
        "path": "/logs",
        "component": "logs/index",
        "route_name": "logs",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "log",
        "perms": None,
        "remark": "日志管理页面（公开）",
    },
    {
        "menu_name": "出勤统计",
        "parent_id": 0,
        "order_num": 3,
        "path": "/attendance",
        "component": "attendance/index",
        "route_name": "attendance",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "users",
        "perms": None,
        "remark": "出勤统计页面（公开）",
    },
    {
        "menu_name": "技能循环分析",
        "parent_id": 0,
        "order_num": 4,
        "path": "/skill-analysis",
        "component": "skill/index",
        "route_name": "skill-analysis",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "activity",
        "perms": None,
        "remark": "技能循环分析页面（公开）",
    },
    {
        "menu_name": "配置图书馆",
        "parent_id": 0,
        "order_num": 5,
        "path": "/builds",
        "component": "builds/library",
        "route_name": "builds",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "book",
        "perms": None,
        "remark": "配置图书馆页面（公开）",
    },
    {
        "menu_name": "Build解析",
        "parent_id": 0,
        "order_num": 6,
        "path": "/build-parser",
        "component": "builds/parser",
        "route_name": "build-parser",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "code",
        "perms": None,
        "remark": "Build代码解析页面（公开）",
    },
    {
        "menu_name": "系统管理",
        "parent_id": 0,
        "order_num": 7,
        "path": "",
        "component": None,
        "route_name": "",
        "menu_type": "M",
        "visible": "0",
        "status": "0",
        "icon": "settings",
        "perms": "manage_users",
        "remark": "系统管理目录（管理员）",
    },
    {
        "menu_name": "系统设置",
        "parent_id": 7,
        "order_num": 1,
        "path": "/settings",
        "component": "settings/index",
        "route_name": "settings",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "cog",
        "perms": "manage_users",
        "remark": "系统设置页面（管理员）",
    },
    {
        "menu_name": "评分规则",
        "parent_id": 7,
        "order_num": 2,
        "path": "/scoring-rules",
        "component": "settings/scoring",
        "route_name": "scoring-rules",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "award",
        "perms": "manage_users",
        "remark": "评分规则页面（管理员）",
    },
    {
        "menu_name": "字典管理",
        "parent_id": 7,
        "order_num": 3,
        "path": "/dictionary",
        "component": "system/dictionary",
        "route_name": "Dictionary",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "list",
        "perms": "manage_users",
        "remark": "字典管理页面（管理员）",
    },
    {
        "menu_name": "职业管理",
        "parent_id": 7,
        "order_num": 4,
        "path": "/professions",
        "component": "system/professions",
        "route_name": "professions",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "users",
        "perms": "manage_users",
        "remark": "职业、精英特长、角色定位管理（管理员）",
    },
]


# =============================================================================
# 字典类型种子数据（profession/specialization/buff_id 已迁移至专业表，此处不再录入口
# =============================================================================
_SYS_DICT_TYPE_SEED = [
    {
        "dict_type": "role",
        "dict_name": "角色定位",
        "status": 0,
        "sort_order": 1,
        "remark": "激?角色定位",
        "is_system": 1,
    },
    {
        "dict_type": "scoring_dimension",
        "dict_name": "评分维度",
        "status": 0,
        "sort_order": 2,
        "remark": "评分指标维度",
        "is_system": 1,
    },
    {
        "dict_type": "game_mode",
        "dict_name": "游戏模式",
        "status": 0,
        "sort_order": 3,
        "remark": "激?游戏模式",
        "is_system": 1,
    },
]

_SYS_DICT_DATA_SEED = {
    "role": [
        ("dps", "输出", "#FF6B35"),
        ("support", "辅助", "#35B0FF"),
        ("tank", "承伤", "#9D4EDD"),
        ("condition", "症状", "#9A3412"),
        ("healing", "治疗", "#166534"),
        ("control", "控制", "#1f2937"),
        ("utility", "功能", "#155e75"),
    ],
    "scoring_dimension": [
        ("damage", "伤害", "#ff4500"),
        ("power_damage", "直伤", "#32cd32"),
        ("condition_damage", "症状伤害", "#9400d3"),
        ("healing", "治疗", "#00ced1"),
        ("boons", "增益", "#ffd700"),
        ("alacrity", "敏捷", "#87ceeb"),
        ("quickness", "急速", "#da70d6"),
        ("survival", "生存", "#4169e1"),
        ("strips", "破法", "#ff1745"),
        ("cleanses", "清症", "#1aff1a"),
        ("kills", "击杀", "#00bfff"),
        ("breakbar", "蔑视", "#b0c4de"),
    ],
    "game_mode": [
        ("wvw", "世界之战", "#6b21a8"),
        ("pve", "玩家对战环境", "#166534"),
        ("pvp", "玩家对战玩家", "#991b1b"),
        ("strikes", "碎层", "#3730a3"),
        ("raids", "团队副本", "#1f2937"),
    ],
}


# =============================================================================
# 角色定位种子数据
# =============================================================================
_ROLE_TYPE_SEED = [
    {
        "role_key": "dps",
        "role_name": "输出",
        "color": "#FF4D6A",
        "icon": "pi pi-bolt",
        "sort_order": 1,
    },
    {
        "role_key": "support",
        "role_name": "辅助",
        "color": "#00D68F",
        "icon": "pi pi-heart",
        "sort_order": 2,
    },
    {
        "role_key": "tank",
        "role_name": "坦克",
        "color": "#165DFF",
        "icon": "pi pi-shield",
        "sort_order": 3,
    },
]


# =============================================================================
# 基础职业种子数据
# =============================================================================
_PROFESSION_SEED = [
    {
        "profession_key": "Guardian",
        "profession_name": "守护者",
        "profession_name_en": "Guardian",
        "color": "#ffc107",
        "icon": "Guardian.png",
        "default_role": "support",
        "possible_roles": ["dps", "support", "tank"],
        "sort_order": 1,
    },
    {
        "profession_key": "Warrior",
        "profession_name": "战士",
        "profession_name_en": "Warrior",
        "color": "#ff5722",
        "icon": "Warrior.png",
        "default_role": "dps",
        "possible_roles": ["dps", "support", "tank"],
        "sort_order": 2,
    },
    {
        "profession_key": "Engineer",
        "profession_name": "工程师",
        "profession_name_en": "Engineer",
        "color": "#795548",
        "icon": "Engineer.png",
        "default_role": "support",
        "possible_roles": ["dps", "support"],
        "sort_order": 3,
    },
    {
        "profession_key": "Ranger",
        "profession_name": "游侠",
        "profession_name_en": "Ranger",
        "color": "#4caf50",
        "icon": "Ranger.png",
        "default_role": "dps",
        "possible_roles": ["dps", "support"],
        "sort_order": 4,
    },
    {
        "profession_key": "Thief",
        "profession_name": "潜行者",
        "profession_name_en": "Thief",
        "color": "#607d8b",
        "icon": "Thief.png",
        "default_role": "dps",
        "possible_roles": ["dps"],
        "sort_order": 5,
    },
    {
        "profession_key": "Elementalist",
        "profession_name": "元素使",
        "profession_name_en": "Elementalist",
        "color": "#e91e63",
        "icon": "Elementalist.png",
        "default_role": "dps",
        "possible_roles": ["dps", "support"],
        "sort_order": 6,
    },
    {
        "profession_key": "Mesmer",
        "profession_name": "幻术师",
        "profession_name_en": "Mesmer",
        "color": "#9c27b0",
        "icon": "Mesmer.png",
        "default_role": "support",
        "possible_roles": ["dps", "support"],
        "sort_order": 7,
    },
    {
        "profession_key": "Necromancer",
        "profession_name": "唤灵师",
        "profession_name_en": "Necromancer",
        "color": "#00bcd4",
        "icon": "Necromancer.png",
        "default_role": "support",
        "possible_roles": ["dps", "support"],
        "sort_order": 8,
    },
    {
        "profession_key": "Revenant",
        "profession_name": "魂武者",
        "profession_name_en": "Revenant",
        "color": "#3f51b5",
        "icon": "Revenant.png",
        "default_role": "support",
        "possible_roles": ["dps", "support", "tank"],
        "sort_order": 9,
    },
]


# =============================================================================
# 精英特长种子数据
# =============================================================================
_ELITE_SPEC_SEED = [
    # Guardian
    {
        "spec_key": "Dragonhunter",
        "spec_name": "猎龙者",
        "spec_name_en": "Dragonhunter",
        "profession_key": "Guardian",
        "color": "#ffc107",
        "icon": "Dragonhunter.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 1,
    },
    {
        "spec_key": "Firebrand",
        "spec_name": "燃火者",
        "spec_name_en": "Firebrand",
        "profession_key": "Guardian",
        "color": "#ff7043",
        "icon": "Firebrand.png",
        "default_role": "support",
        "dps_type": "hybrid",
        "scoring_config": {
            "quickness": 20,
            "boons": 15,
            "strips": 15,
            "cleanses": 15,
            "survival": 15,
            "healing": 20,
        },
        "is_key_support": 1,
        "sort_order": 2,
    },
    {
        "spec_key": "Willbender",
        "spec_name": "破锋者",
        "spec_name_en": "Willbender",
        "profession_key": "Guardian",
        "color": "#ffa726",
        "icon": "Willbender.png",
        "default_role": "dps",
        "dps_type": "hybrid",
        "scoring_config": {"damage": 40, "breakbar": 25, "kills": 20, "survival": 15},
        "sort_order": 3,
    },
    {
        "spec_key": "Luminary",
        "spec_name": "圣辉者",
        "spec_name_en": "Luminary",
        "profession_key": "Guardian",
        "color": "#ffca28",
        "icon": "Luminary.png",
        "default_role": "support",
        "dps_type": "hybrid",
        "scoring_config": {
            "quickness": 15,
            "alacrity": 15,
            "boons": 20,
            "strips": 10,
            "cleanses": 10,
            "survival": 15,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
    # Warrior
    {
        "spec_key": "Berserker",
        "spec_name": "狂战士",
        "spec_name_en": "Berserker",
        "profession_key": "Warrior",
        "color": "#ff5722",
        "icon": "Berserker.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 50, "breakbar": 25, "kills": 15, "survival": 10},
        "sort_order": 1,
    },
    {
        "spec_key": "Spellbreaker",
        "spec_name": "破法者",
        "spec_name_en": "Spellbreaker",
        "profession_key": "Warrior",
        "color": "#ff7043",
        "icon": "Spellbreaker.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {
            "damage": 35,
            "breakbar": 20,
            "strips": 20,
            "kills": 15,
            "survival": 10,
        },
        "sort_order": 2,
    },
    {
        "spec_key": "Bladesworn",
        "spec_name": "誓剑士",
        "spec_name_en": "Bladesworn",
        "profession_key": "Warrior",
        "color": "#ff8a65",
        "icon": "Bladesworn.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 55, "breakbar": 20, "kills": 15, "survival": 10},
        "sort_order": 3,
    },
    {
        "spec_key": "Paragon",
        "spec_name": "圣言者",
        "spec_name_en": "Paragon",
        "profession_key": "Warrior",
        "color": "#ffa726",
        "icon": "Paragon.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 15,
            "alacrity": 10,
            "boons": 20,
            "strips": 15,
            "cleanses": 10,
            "survival": 15,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
    # Engineer
    {
        "spec_key": "Scrapper",
        "spec_name": "机械师",
        "spec_name_en": "Scrapper",
        "profession_key": "Engineer",
        "color": "#795548",
        "icon": "Scrapper.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 15,
            "alacrity": 15,
            "boons": 15,
            "strips": 15,
            "cleanses": 15,
            "survival": 10,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 1,
    },
    {
        "spec_key": "Holosmith",
        "spec_name": "全息师",
        "spec_name_en": "Holosmith",
        "profession_key": "Engineer",
        "color": "#8d6e63",
        "icon": "Holosmith.png",
        "default_role": "dps",
        "dps_type": "hybrid",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 2,
    },
    {
        "spec_key": "Mechanist",
        "spec_name": "玉偃师",
        "spec_name_en": "Mechanist",
        "profession_key": "Engineer",
        "color": "#a1887f",
        "icon": "Mechanist.png",
        "default_role": "support",
        "dps_type": "hybrid",
        "scoring_config": {
            "quickness": 10,
            "alacrity": 20,
            "boons": 15,
            "strips": 15,
            "cleanses": 15,
            "survival": 10,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 3,
    },
    {
        "spec_key": "Amalgam",
        "spec_name": "流金师",
        "spec_name_en": "Amalgam",
        "profession_key": "Engineer",
        "color": "#bcaaa4",
        "icon": "Amalgam.png",
        "default_role": "dps",
        "dps_type": "hybrid",
        "scoring_config": {
            "damage": 40,
            "breakbar": 25,
            "kills": 20,
            "cleanses": 5,
            "survival": 10,
        },
        "sort_order": 4,
    },
    # Ranger
    {
        "spec_key": "Druid",
        "spec_name": "德鲁伊",
        "spec_name_en": "Druid",
        "profession_key": "Ranger",
        "color": "#4caf50",
        "icon": "Druid.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 0,
            "alacrity": 0,
            "boons": 20,
            "strips": 10,
            "cleanses": 10,
            "survival": 15,
            "healing": 45,
        },
        "is_key_support": 1,
        "sort_order": 1,
    },
    {
        "spec_key": "Soulbeast",
        "spec_name": "魂兽师",
        "spec_name_en": "Soulbeast",
        "profession_key": "Ranger",
        "color": "#66bb6a",
        "icon": "Soulbeast.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 2,
    },
    {
        "spec_key": "Untamed",
        "spec_name": "狂兽师",
        "spec_name_en": "Untamed",
        "profession_key": "Ranger",
        "color": "#81c784",
        "icon": "Untamed.png",
        "default_role": "dps",
        "dps_type": "hybrid",
        "scoring_config": {"damage": 40, "breakbar": 25, "kills": 20, "survival": 15},
        "sort_order": 3,
    },
    {
        "spec_key": "Galeshot",
        "spec_name": "风行者",
        "spec_name_en": "Galeshot",
        "profession_key": "Ranger",
        "color": "#a5d6a7",
        "icon": "Galeshot.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 4,
    },
    # Thief
    {
        "spec_key": "Daredevil",
        "spec_name": "独行侠",
        "spec_name_en": "Daredevil",
        "profession_key": "Thief",
        "color": "#607d8b",
        "icon": "Daredevil.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 1,
    },
    {
        "spec_key": "Deadeye",
        "spec_name": "神枪手",
        "spec_name_en": "Deadeye",
        "profession_key": "Thief",
        "color": "#78909c",
        "icon": "Deadeye.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 2,
    },
    {
        "spec_key": "Specter",
        "spec_name": "缚影者",
        "spec_name_en": "Specter",
        "profession_key": "Thief",
        "color": "#90a4ae",
        "icon": "Specter.png",
        "default_role": "dps",
        "dps_type": "condi",
        "scoring_config": {
            "damage": 40,
            "breakbar": 20,
            "kills": 20,
            "cleanses": 10,
            "survival": 10,
        },
        "sort_order": 3,
    },
    {
        "spec_key": "Antiquary",
        "spec_name": "彩戏师",
        "spec_name_en": "Antiquary",
        "profession_key": "Thief",
        "color": "#b0bec5",
        "icon": "Antiquary.png",
        "default_role": "support",
        "dps_type": "condi",
        "scoring_config": {
            "damage": 35,
            "breakbar": 15,
            "strips": 15,
            "kills": 15,
            "cleanses": 10,
            "survival": 10,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
    # Elementalist
    {
        "spec_key": "Tempest",
        "spec_name": "暴风使",
        "spec_name_en": "Tempest",
        "profession_key": "Elementalist",
        "color": "#e91e63",
        "icon": "Tempest.png",
        "default_role": "support",
        "dps_type": "hybrid",
        "scoring_config": {
            "quickness": 0,
            "alacrity": 0,
            "boons": 20,
            "strips": 15,
            "cleanses": 15,
            "survival": 10,
            "healing": 40,
        },
        "is_key_support": 1,
        "sort_order": 1,
    },
    {
        "spec_key": "Weaver",
        "spec_name": "编织者",
        "spec_name_en": "Weaver",
        "profession_key": "Elementalist",
        "color": "#ec407a",
        "icon": "Weaver.png",
        "default_role": "dps",
        "dps_type": "hybrid",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 2,
    },
    {
        "spec_key": "Catalyst",
        "spec_name": "元晶师",
        "spec_name_en": "Catalyst",
        "profession_key": "Elementalist",
        "color": "#f06292",
        "icon": "Catalyst.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 3,
    },
    {
        "spec_key": "Evoker",
        "spec_name": "唤元师",
        "spec_name_en": "Evoker",
        "profession_key": "Elementalist",
        "color": "#f48fb1",
        "icon": "Evoker.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 4,
    },
    # Mesmer
    {
        "spec_key": "Chronomancer",
        "spec_name": "时空术士",
        "spec_name_en": "Chronomancer",
        "profession_key": "Mesmer",
        "color": "#9c27b0",
        "icon": "Chronomancer.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 20,
            "alacrity": 20,
            "boons": 15,
            "strips": 15,
            "cleanses": 10,
            "survival": 10,
            "healing": 10,
        },
        "is_key_support": 1,
        "sort_order": 1,
    },
    {
        "spec_key": "Mirage",
        "spec_name": "幻象术士",
        "spec_name_en": "Mirage",
        "profession_key": "Mesmer",
        "color": "#ab47bc",
        "icon": "Mirage.png",
        "default_role": "dps",
        "dps_type": "condi",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 2,
    },
    {
        "spec_key": "Virtuoso",
        "spec_name": "灵刃术士",
        "spec_name_en": "Virtuoso",
        "profession_key": "Mesmer",
        "color": "#ba68c8",
        "icon": "Virtuoso.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 3,
    },
    {
        "spec_key": "Troubadour",
        "spec_name": "吟游诗人",
        "spec_name_en": "Troubadour",
        "profession_key": "Mesmer",
        "color": "#ce93d8",
        "icon": "Troubadour.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 15,
            "alacrity": 15,
            "boons": 20,
            "strips": 10,
            "cleanses": 10,
            "survival": 15,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
    # Necromancer
    {
        "spec_key": "Reaper",
        "spec_name": "夺魂者",
        "spec_name_en": "Reaper",
        "profession_key": "Necromancer",
        "color": "#00bcd4",
        "icon": "Reaper.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 1,
    },
    {
        "spec_key": "Scourge",
        "spec_name": "灾厄师",
        "spec_name_en": "Scourge",
        "profession_key": "Necromancer",
        "color": "#26c6da",
        "icon": "Scourge.png",
        "default_role": "support",
        "dps_type": "condi",
        "scoring_config": {
            "quickness": 0,
            "alacrity": 0,
            "boons": 10,
            "strips": 20,
            "cleanses": 20,
            "survival": 15,
            "healing": 35,
        },
        "is_key_support": 1,
        "sort_order": 2,
    },
    {
        "spec_key": "Harbinger",
        "spec_name": "先驱者",
        "spec_name_en": "Harbinger",
        "profession_key": "Necromancer",
        "color": "#4dd0e1",
        "icon": "Harbinger.png",
        "default_role": "dps",
        "dps_type": "condi",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 3,
    },
    {
        "spec_key": "Ritualist",
        "spec_name": "祭祀者",
        "spec_name_en": "Ritualist",
        "profession_key": "Necromancer",
        "color": "#80deea",
        "icon": "Ritualist.png",
        "default_role": "support",
        "dps_type": "condi",
        "scoring_config": {
            "quickness": 10,
            "alacrity": 10,
            "boons": 15,
            "strips": 15,
            "cleanses": 15,
            "survival": 15,
            "healing": 20,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
    # Revenant
    {
        "spec_key": "Herald",
        "spec_name": "预告者",
        "spec_name_en": "Herald",
        "profession_key": "Revenant",
        "color": "#3f51b5",
        "icon": "Herald.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 0,
            "alacrity": 0,
            "boons": 25,
            "strips": 15,
            "cleanses": 10,
            "survival": 20,
            "healing": 30,
        },
        "is_key_support": 1,
        "sort_order": 1,
    },
    {
        "spec_key": "Renegade",
        "spec_name": "龙魂使",
        "spec_name_en": "Renegade",
        "profession_key": "Revenant",
        "color": "#5c6bc0",
        "icon": "Renegade.png",
        "default_role": "dps",
        "dps_type": "condi",
        "scoring_config": {
            "damage": 40,
            "breakbar": 25,
            "strips": 15,
            "kills": 10,
            "survival": 10,
        },
        "sort_order": 2,
    },
    {
        "spec_key": "Vindicator",
        "spec_name": "裁决者",
        "spec_name_en": "Vindicator",
        "profession_key": "Revenant",
        "color": "#7986cb",
        "icon": "Vindicator.png",
        "default_role": "dps",
        "dps_type": "power",
        "scoring_config": {"damage": 45, "breakbar": 25, "kills": 20, "survival": 10},
        "sort_order": 3,
    },
    {
        "spec_key": "Conduit",
        "spec_name": "契灵使",
        "spec_name_en": "Conduit",
        "profession_key": "Revenant",
        "color": "#9fa8da",
        "icon": "Conduit.png",
        "default_role": "support",
        "dps_type": "power",
        "scoring_config": {
            "quickness": 15,
            "alacrity": 15,
            "boons": 20,
            "strips": 10,
            "cleanses": 10,
            "survival": 15,
            "healing": 15,
        },
        "is_key_support": 1,
        "sort_order": 4,
    },
]


# =============================================================================
# 初始化系统菜单
# =============================================================================


def _init_sys_menu(db: Session) -> int:
    """初始化系统菜单"""
    if db.query(SysMenu).count() > 0:
        logger.info("sys_menu 已有数据，跳过")
        return 0
    now = datetime.now()
    for record in _SYS_MENU_SEED:
        db.add(
            SysMenu(
                **record,
                create_time=now,
                update_time=now,
                create_by="system",
                update_by="system",
            )
        )
    db.commit()
    logger.info(f"sys_menu 初始化完成 {len(_SYS_MENU_SEED)} 条记录")
    return len(_SYS_MENU_SEED)


def _init_sys_dict_type(db: Session) -> int:
    """初始化字典类型（role / scoring_dimension / game_mode?"""
    created = 0
    for record in _SYS_DICT_TYPE_SEED:
        existing = (
            db.query(SysDictType)
            .filter(SysDictType.dict_type == record["dict_type"])
            .first()
        )
        if not existing:
            db.add(SysDictType(**record))
            created += 1
    db.commit()
    logger.info(f"sys_dict_type 初始化完成 {created} 条记录")
    return created


def _init_sys_dict_data(db: Session) -> int:
    """初始化字典数据（role / scoring_dimension / game_mode）"""
    created = 0
    for dict_type, items in _SYS_DICT_DATA_SEED.items():
        for idx, (value, label, color) in enumerate(items):
            existing = (
                db.query(SysDictData)
                .filter(
                    SysDictData.dict_type == dict_type,
                    SysDictData.dict_value == value,
                )
                .first()
            )
            if not existing:
                db.add(
                    SysDictData(
                        dict_type=dict_type,
                        dict_value=value,
                        dict_label=label,
                        css_class=color,
                        status=0,
                        dict_sort=idx,
                        remark=f"{label}{'角色' if dict_type == 'role' else '维度' if dict_type == 'scoring_dimension' else '模式'}",
                    )
                )
                created += 1
    db.commit()
    logger.info(f"sys_dict_data 初始化完成 {created} 条记录")
    return created


def _init_role_types(db: Session) -> int:
    """初始化角色定义"""
    created = 0
    for record in _ROLE_TYPE_SEED:
        existing = (
            db.query(GwRoleType)
            .filter(GwRoleType.role_key == record["role_key"])
            .first()
        )
        if not existing:
            db.add(GwRoleType(**record))
            created += 1
    db.commit()
    logger.info(f"gw_role_type 初始化完成 {created} 条记录")
    return created


def _init_professions(db: Session) -> int:
    """初始化基础职业"""
    created = 0
    for record in _PROFESSION_SEED:
        existing = (
            db.query(GwProfession)
            .filter(GwProfession.profession_key == record["profession_key"])
            .first()
        )
        if not existing:
            db.add(GwProfession(**record))
            created += 1
    db.commit()
    logger.info(f"gw_profession 初始化完成 {created} 条")
    return created


def _init_elite_specializations(db: Session) -> int:
    """初始化精英特性线"""
    created = 0
    for record in _ELITE_SPEC_SEED:
        existing = (
            db.query(GwEliteSpecialization)
            .filter(GwEliteSpecialization.spec_key == record["spec_key"])
            .first()
        )
        if not existing:
            db.add(GwEliteSpecialization(**record))
            created += 1
    db.commit()
    logger.info(f"gw_elite_specialization 初始化完成 {created} 条")
    return created


def _init_game_static_data(db: Session) -> Dict[str, int]:
    """初始化游戏静态数据（seed_data 解压导入口）"""
    results = {}

    # gw_skill
    if db.query(GwSkill).count() == 0:
        data = seed_data.get_skills()
        batch_size = 500
        for idx, item in enumerate(data, 1):
            db.add(
                GwSkill(
                    id=item.get("id"),
                    name=item.get("name"),
                    name_cn=item.get("name_cn"),
                    description=item.get("description"),
                    icon=item.get("icon"),
                    slot=item.get("slot"),
                    type=item.get("type"),
                    weapon_type=item.get("weapon_type"),
                    professions=item.get("professions", []),
                    facts=item.get("facts", []),
                    chat_link=item.get("chat_link"),
                    flags=item.get("flags", []),
                )
            )
            if idx % batch_size == 0:
                db.commit()
        db.commit()
        results["gw_skill"] = len(data)
        logger.info(f"gw_skill 导入完成: {len(data)} 条")
    else:
        results["gw_skill"] = 0

    # gw_specialization
    if db.query(GwSpecialization).count() == 0:
        data = seed_data.get_specializations()
        for item in data:
            db.add(
                GwSpecialization(
                    id=item.get("id"),
                    name=item.get("name"),
                    profession=item.get("profession"),
                    elite=item.get("elite", False),
                    minor_traits=item.get("minor_traits", []),
                    major_traits=item.get("major_traits", []),
                    icon=item.get("icon"),
                    background=item.get("background"),
                )
            )
        db.commit()
        results["gw_specialization"] = len(data)
        logger.info(f"gw_specialization 导入完成: {len(data)} 条")
    else:
        results["gw_specialization"] = 0

    # gw_trait
    if db.query(GwTrait).count() == 0:
        data = seed_data.get_traits()
        batch_size = 500
        for idx, item in enumerate(data, 1):
            db.add(
                GwTrait(
                    id=item.get("id"),
                    name=item.get("name"),
                    description=item.get("description"),
                    icon=item.get("icon"),
                    slot=item.get("slot"),
                    tier=item.get("tier"),
                    order=item.get("order"),
                    specialization=item.get("specialization"),
                    facts=item.get("facts", []),
                )
            )
            if idx % batch_size == 0:
                db.commit()
        db.commit()
        results["gw_trait"] = len(data)
        logger.info(f"gw_trait 导入完成: {len(data)} 条")
    else:
        results["gw_trait"] = 0

    # gw_skill_palette
    if db.query(GwSkillPalette).count() == 0:
        data = seed_data.get_skill_palettes()
        batch_size = 500
        for idx, item in enumerate(data, 1):
            db.add(
                GwSkillPalette(
                    palette_id=item.get("palette_id"),
                    skill_id=item.get("skill_id"),
                    profession=item.get("profession", "Unknown"),
                )
            )
            if idx % batch_size == 0:
                db.commit()
        db.commit()
        results["gw_skill_palette"] = len(data)
        logger.info(f"gw_skill_palette 导入完成: {len(data)} 条")
    else:
        results["gw_skill_palette"] = 0

    # gw_buff
    if db.query(GwBuff).count() == 0:
        data = seed_data.get_buffs()
        for buff_name, item in data.get("buffs", {}).items():
            db.add(
                GwBuff(
                    id=item.get("id"),
                    name=item.get("name"),
                    name_cn=item.get("name_cn"),
                    category=item.get("category"),
                    stacking=item.get("stacking"),
                    max_stacks=item.get("max_stacks"),
                    is_key_buff=item.get("is_key_buff", False),
                    icon=item.get("icon"),
                    description=item.get("description"),
                )
            )
        db.commit()
        results["gw_buff"] = len(data.get("buffs", {}))
        logger.info(f"gw_buff 导入完成: {len(data.get('buffs', {}))} 条")
    else:
        results["gw_buff"] = 0

    return results


def _init_builds(db: Session) -> Dict[str, Any]:
    """初始化Build 图书馆数据（seed_data 解压导入口）"""
    from app.services.game.bdcode_service import get_bdcode_service

    existing = db.query(Build).count()
    if existing > 0:
        return {"initialized": False, "count": 0, "errors": []}

    builds_data = seed_data.get_builds_initial()
    bdcode_service = get_bdcode_service()
    success_count = 0
    failure_count = 0
    errors = []

    for idx, raw in enumerate(builds_data, 1):
        try:
            db_data = {
                "slug": raw.get("slug", ""),
                "title": raw.get("title", ""),
                "profession": raw.get("profession", ""),
                "profession_color": raw.get("profession_color"),
                "elite_spec": raw.get("elite_spec"),
                "role": raw.get("role", "dps"),
                "sub_roles": raw.get("sub_roles", []),
                "armor_type": raw.get("armor_type", ""),
                "weapons": raw.get("weapons", []),
                "relic": raw.get("relic", ""),
                "rune": raw.get("rune", ""),
                "food": raw.get("food", ""),
                "wrench": raw.get("wrench", ""),
                "infusion": raw.get("infusion", ""),
                "attr_requirements": raw.get("attr_requirements", []),
                "bd_code": raw.get("bd_code", ""),
                "trait_lines": raw.get("trait_lines", []),
                "rotation_commands": raw.get("rotation_commands", []),
                "mechanics": raw.get("mechanics", []),
                "videos": raw.get("videos", []),
                "author": raw.get("author", ""),
                "word_count": raw.get("word_count", 0),
                "is_meta": raw.get("is_meta", False),
            }

            if (
                not db_data["title"]
                or not db_data["bd_code"]
                or not db_data["profession"]
            ):
                raise ValueError("缺少必填字段（title/bd_code/profession?）")

            # 如果 JSON 中没有解析特性线但有 BD Code，尝试解?
            if not db_data["trait_lines"] and db_data["bd_code"]:
                try:
                    result = bdcode_service.parse_bdcode(
                        db_data["bd_code"], include_icons=False
                    )
                    if result.get("success"):
                        api_data = result.get("data")
                        if not db_data["profession"]:
                            db_data["profession"] = api_data.get("profession", "")
                        if not db_data["profession_color"]:
                            color_map = {
                                "Warrior": "#E85D04",
                                "Guardian": "#FAA307",
                                "Revenant": "#9D4EDD",
                                "Ranger": "#06D6A0",
                                "Engineer": "#7B8FA1",
                                "Necromancer": "#8D0801",
                                "Mesmer": "#4361EE",
                                "Elementalist": "#FF6B6B",
                                "Thief": "#C0363D",
                            }
                            db_data["profession_color"] = color_map.get(
                                db_data["profession"], "#888888"
                            )
                        if not db_data["elite_spec"]:
                            specs = api_data.get("specializations", [])
                            elite = next((s for s in specs if s.get("is_elite")), None)
                            if elite:
                                db_data["elite_spec"] = elite.get(
                                    "name_cn"
                                ) or elite.get("name")
                        db_data["trait_lines"] = []
                        for s in api_data.get("specializations", []):
                            traits = s.get("selected_traits", [])
                            if len(traits) == 3:
                                db_data["trait_lines"].append(
                                    {
                                        "name": s.get("name_cn") or s.get("name") or "",
                                        "choices": [int(t) for t in traits],
                                    }
                                )
                except Exception:
                    pass

            create_build(db, db_data)
            success_count += 1
        except Exception as e:
            errors.append(
                f"[{idx}/{len(builds_data)}] {raw.get('title', 'Unknown')} - {e}"
            )
            failure_count += 1

    return {"initialized": True, "count": success_count, "errors": errors}


# =============================================================================
# 独立 API（供管理员手动触发）
# =============================================================================


def init_dictionary_data(db: Session) -> Dict[str, Any]:
    """初始化字典数据（role / scoring_dimension / game_mode）"""
    types_created = _init_sys_dict_type(db)
    data_created = _init_sys_dict_data(db)
    return {
        "total_created": types_created + data_created,
        "total_skipped": 0,
        "details": {
            "types": {t["dict_type"]: 1 for t in _SYS_DICT_TYPE_SEED},
            "roles": {
                "created": len([i for i in _SYS_DICT_DATA_SEED["role"]]),
                "skipped": 0,
            },
            "scoring_dimensions": {
                "created": len([i for i in _SYS_DICT_DATA_SEED["scoring_dimension"]]),
                "skipped": 0,
            },
            "game_modes": {
                "created": len([i for i in _SYS_DICT_DATA_SEED["game_mode"]]),
                "skipped": 0,
            },
        },
    }


# =============================================================================
# 统一入口
# =============================================================================


def _init_admin(db: Session) -> Dict[str, Any]:
    """初始化预置管理员账号"""
    from app.services.auth.auth_service import init_predefined_admin

    admin = init_predefined_admin(db)
    return {"initialized": True, "username": admin.username}


def _init_scoring_rules(db: Session) -> Dict[str, Any]:
    """初始化评分规则、版本表及职业特定规则"""
    from app.models.game.profession import GwEliteSpecialization
    from app.models.scoring.scoring_rule import ScoringRule
    from app.services.scoring.scoring_rule_service import ScoringRuleService

    scoring_service = ScoringRuleService(db)
    results = {}

    # 初始化默认评分规则
    scoring_init = scoring_service.init_default_rules_if_empty()
    results["default_rules"] = scoring_init

    # 初始化评分规则版本表
    version_init = scoring_service.init_version_if_empty()
    results["version"] = version_init

    # 从数据库精英特长数据导入默认职业特定规则
    existing_count = (
        db.query(ScoringRule)
        .filter(ScoringRule.profession.isnot(None))
        .count()
    )
    
    if existing_count > 0:
        results["profession_rules"] = {"initialized": False, "reason": "已有职业特定规则", "count": existing_count}
    else:
        # 从数据库读取所有精英特长
        elite_specs = db.query(GwEliteSpecialization).all()
        total_created = 0
        
        for spec in elite_specs:
            scoring_config = spec.scoring_config
            if not scoring_config or not isinstance(scoring_config, dict):
                continue
            
            default_role = spec.default_role or "dps"
            
            # 归一化权重
            total_weight = sum(scoring_config.values())
            if total_weight <= 0:
                continue
            
            sort_order = 1
            for dimension, weight in scoring_config.items():
                normalized_weight = round(weight / total_weight, 4)
                rule = ScoringRule(
                    role_type=default_role,
                    profession=spec.spec_key,
                    dimension=dimension,
                    weight=normalized_weight,
                    description=f"{spec.spec_name} 默认 {dimension} 权重",
                    sort_order=sort_order,
                    is_active=True,
                )
                db.add(rule)
                sort_order += 1
                total_created += 1
        
        db.commit()
        if total_created > 0:
            logger.info(f"从数据库精英特长导入职业特定规则: 共 {total_created} 条")
            results["profession_rules"] = {"initialized": True, "count": total_created}
        else:
            results["profession_rules"] = {"initialized": False, "reason": "没有可用的评分配置数据"}

    return results


def _load_dictionaries(db: Session) -> Dict[str, Any]:
    """加载字典缓存"""
    from app.utils.db.dict_utils import load_all_dictionaries

    load_all_dictionaries(db)
    return {"initialized": True}


def initialize_all(db: Session) -> Dict[str, Any]:
    """
    执行所有数据初始化

    按顺序：
    1. sys_menu
    2. sys_dict_type + sys_dict_data
    3. gw_role_type
    4. gw_profession
    5. gw_elite_specialization
    6. 游戏静态数据（gw_skill / gw_spec / gw_trait / gw_palette / gw_buff）
    7. build
    8. 预置管理员
    9. 评分规则
    10. 字典缓存
    """
    logger.info("=" * 60)
    logger.info("开始执行统一数据初始化")
    logger.info("=" * 60)

    results = {
        "sys_menu": _init_sys_menu(db),
        "sys_dict_type": _init_sys_dict_type(db),
        "sys_dict_data": _init_sys_dict_data(db),
        "gw_role_type": _init_role_types(db),
        "gw_profession": _init_professions(db),
        "gw_elite_specialization": _init_elite_specializations(db),
        "game_static": _init_game_static_data(db),
        "builds": _init_builds(db),
        "admin": _init_admin(db),
        "scoring_rules": _init_scoring_rules(db),
        "dictionaries": _load_dictionaries(db),
    }

    def _extract_count(v):
        if isinstance(v, int):
            return v
        if isinstance(v, dict):
            # game_static: Dict[str, int]
            if all(isinstance(x, int) for x in v.values()):
                return sum(v.values())
            # builds: {"initialized": ..., "count": int, "errors": list}
            return v.get("count", 0)
        return 0

    total = sum(_extract_count(v) for v in results.values())
    logger.info("=" * 60)
    logger.info(f"统一数据初始化完成，共导入{total} 条记录")
    logger.info("=" * 60)
    return results