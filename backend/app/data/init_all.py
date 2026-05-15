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

import json
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.initialization import SeedDataLoader
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
from app.services.system.sys_config_service import SysConfigService
from app.utils.logger import logger

# =============================================================================
# 种子数据加载（优先从构建模块加载，回退到内嵌数据）
# =============================================================================

def _try_load_seed_from_module(var_name: str, default_data: Any) -> Any:
    """尝试从构建生成的 seed_modules.py 加载种子数据"""
    try:
        from app.data._generated.seed_modules import load_seed
        file_map = {
            "_SYS_MENU_SEED": "v1.0.0/001_sys_menu.json",
            "_SYS_DICT_TYPE_SEED": "v1.0.0/002_sys_dict_type.json",
            "_SYS_DICT_DATA_SEED": "v1.0.0/003_sys_dict_data.json",
            "_ROLE_TYPE_SEED": "v1.0.0/004_gw_role_type.json",
            "_PROFESSION_SEED": "v1.0.0/005_gw_profession.json",
            "_ELITE_SPEC_SEED": "v1.0.0/006_gw_elite_specialization.json",
        }
        file_name = file_map.get(var_name)
        if file_name:
            loaded = load_seed(file_name)
            data = loaded.get("data", default_data)
            logger.info(f"[init_all] 从 seed_modules 加载 {var_name}")
            return data
    except Exception:
        pass
    return default_data


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
        "menu_name": "AI分析",
        "parent_id": 0,
        "order_num": 5,
        "path": "/ai-analysis",
        "component": "data/ai-analysis",
        "route_name": "AiAnalysis",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "sparkles",
        "perms": None,
        "remark": "AI分析页面（公开）",
    },
    {
        "menu_name": "配置图书馆",
        "parent_id": 0,
        "order_num": 6,
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
        "order_num": 7,
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
        "order_num": 8,
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
# =============================================================================
# 字典类型种子数据
# 说明：所有业务配置类枚举数据统一在此声明，系统启动时自动录入字典表
# =============================================================================
_SYS_DICT_TYPE_SEED = [
    {
        "dict_type": "role",
        "dict_name": "\u89d2\u8272\u5b9a\u4f4d",
        "status": 0,
        "sort_order": 1,
        "remark": "\u6218\u6597\u89d2\u8272\u5b9a\u4f4d",
        "is_system": 1,
    },
    {
        "dict_type": "scoring_dimension",
        "dict_name": "\u8bc4\u5206\u7ef4\u5ea6",
        "status": 0,
        "sort_order": 2,
        "remark": "\u8bc4\u5206\u6307\u6807\u7ef4\u5ea6",
        "is_system": 1,
    },
    {
        "dict_type": "game_mode",
        "dict_name": "\u6e38\u620f\u6a21\u5f0f",
        "status": 0,
        "sort_order": 3,
        "remark": "\u6e38\u620f\u6a21\u5f0f",
        "is_system": 1,
    },
    {
        "dict_type": "parse_status",
        "dict_name": "\u89e3\u6790\u72b6\u6001",
        "status": 0,
        "sort_order": 4,
        "remark": "\u65e5\u5fd7\u89e3\u6790\u751f\u547d\u5468\u671f\u72b6\u6001",
        "is_system": 1,
    },
    {
        "dict_type": "buff",
        "dict_name": "\u589e\u76ca\u6548\u679c",
        "status": 0,
        "sort_order": 5,
        "remark": "\u6218\u6597\u589e\u76ca\u6548\u679c\u540d\u79f0\u6620\u5c04",
        "is_system": 1,
    },
    {
        "dict_type": "dashboard_time_range",
        "dict_name": "\u4eea\u8868\u76d8\u65f6\u95f4\u8303\u56f4",
        "status": 0,
        "sort_order": 6,
        "remark": "\u6570\u636e\u770b\u677f\u65f6\u95f4\u7b5b\u9009\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "skill_state",
        "dict_name": "\u6280\u80fd\u72b6\u6001",
        "status": 0,
        "sort_order": 7,
        "remark": "\u6280\u80fd\u5faa\u73af\u65f6\u95f4\u8f74\u72b6\u6001\u6807\u7b7e",
        "is_system": 1,
    },
    {
        "dict_type": "permission",
        "dict_name": "\u6743\u9650\u6807\u8bc6",
        "status": 0,
        "sort_order": 8,
        "remark": "\u7cfb\u7edf\u6743\u9650\u6807\u8bc6\u5217\u8868",
        "is_system": 1,
    },
    {
        "dict_type": "scoring_mode",
        "dict_name": "\u8bc4\u5206\u6a21\u5f0f",
        "status": 0,
        "sort_order": 9,
        "remark": "\u8bc4\u5206\u89c4\u5219\u5e94\u7528\u65b9\u5f0f",
        "is_system": 1,
    },
    {
        "dict_type": "grade_level",
        "dict_name": "\u8bc4\u5206\u7b49\u7ea7",
        "status": 0,
        "sort_order": 10,
        "remark": "\u8bc4\u5206\u7b49\u7ea7\u5212\u5206",
        "is_system": 1,
    },
    {
        "dict_type": "session_timeout",
        "dict_name": "\u4f1a\u8bdd\u8d85\u65f6",
        "status": 0,
        "sort_order": 11,
        "remark": "\u4f1a\u8bdd\u8d85\u65f6\u65f6\u95f4\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "setting_tab",
        "dict_name": "\u8bbe\u7f6e\u9009\u9879\u5361",
        "status": 0,
        "sort_order": 12,
        "remark": "\u7cfb\u7edf\u8bbe\u7f6e\u9875\u9762\u5185\u9009\u9879\u5361",
        "is_system": 1,
    },
    {
        "dict_type": "chart_mode",
        "dict_name": "\u56fe\u8868\u6a21\u5f0f",
        "status": 0,
        "sort_order": 13,
        "remark": "\u6570\u636e\u56fe\u8868\u5c55\u793a\u6a21\u5f0f",
        "is_system": 1,
    },
    {
        "dict_type": "sort_field",
        "dict_name": "\u6392\u5e8f\u5b57\u6bb5",
        "status": 0,
        "sort_order": 14,
        "remark": "\u6570\u636e\u6392\u5e8f\u5b57\u6bb5\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "time_range",
        "dict_name": "\u65f6\u95f4\u8303\u56f4",
        "status": 0,
        "sort_order": 15,
        "remark": "\u65f6\u95f4\u7b5b\u9009\u8303\u56f4\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "metric_type",
        "dict_name": "\u6307\u6807\u7c7b\u578b",
        "status": 0,
        "sort_order": 16,
        "remark": "\u6570\u636e\u5206\u6790\u6307\u6807\u7c7b\u578b",
        "is_system": 1,
    },
    {
        "dict_type": "export_format",
        "dict_name": "\u5bfc\u51fa\u683c\u5f0f",
        "status": 0,
        "sort_order": 17,
        "remark": "\u6570\u636e\u5bfc\u51fa\u683c\u5f0f\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "theme_color",
        "dict_name": "\u4e3b\u9898\u989c\u8272",
        "status": 0,
        "sort_order": 18,
        "remark": "\u754c\u9762\u4e3b\u9898\u989c\u8272\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "number_format",
        "dict_name": "\u6570\u5b57\u683c\u5f0f",
        "status": 0,
        "sort_order": 19,
        "remark": "\u6570\u636e\u5c55\u793a\u6570\u5b57\u683c\u5f0f\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "sys_normal_disable",
        "dict_name": "\u901a\u7528\u72b6\u6001",
        "status": 0,
        "sort_order": 20,
        "remark": "\u901a\u7528\u542f\u7528\u7981\u7528\u72b6\u6001",
        "is_system": 1,
    },
    {
        "dict_type": "sys_yes_no",
        "dict_name": "\u662f\u5426",
        "status": 0,
        "sort_order": 21,
        "remark": "\u901a\u7528\u662f\u5426\u9009\u9879",
        "is_system": 1,
    },
    {
        "dict_type": "scoring_rule_status",
        "dict_name": "\u8bc4\u5206\u89c4\u5219\u7248\u672c\u72b6\u6001",
        "status": 0,
        "sort_order": 22,
        "remark": "\u8bc4\u5206\u89c4\u5219\u7248\u672c\u5904\u7406\u72b6\u6001",
        "is_system": 1,
    },
]

# 字典数据种子：格式 (value, label, color, remark)
# remark 字段存储扩展属性（如描述、分类标记等）
_SYS_DICT_DATA_SEED = {
    "sys_normal_disable": [
        ("0", "\u542f\u7528", "#22c55e", "\u6b63\u5e38\u4f7f\u7528"),
        ("1", "\u7981\u7528", "#ef4444", "\u5df2\u505c\u7528"),
    ],
    "sys_yes_no": [
        ("Y", "\u662f", "#22c55e", "\u80af\u5b9a\u9009\u9879"),
        ("N", "\u5426", "#6b7280", "\u5426\u5b9a\u9009\u9879"),
    ],
    "scoring_rule_status": [
        ("pending", "\u5f85\u5904\u7406", "#6b7280", "\u7b49\u5f85\u5f00\u59cb"),
        ("processing", "\u5904\u7406\u4e2d", "#3b82f6", "\u6b63\u5728\u6267\u884c"),
        ("completed", "\u5df2\u5b8c\u6210", "#22c55e", "\u5904\u7406\u5b8c\u6210"),
        ("failed", "\u5931\u8d25", "#ef4444", "\u5904\u7406\u5931\u8d25"),
    ],
    "role": [
        ("dps", "\u8f93\u51fa", "#FF6B35", "\u4ee5\u4f24\u5bb3\u8f93\u51fa\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("support", "\u8f85\u52a9", "#35B0FF", "\u4ee5\u6cbb\u7597\u548c\u589e\u76ca\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("tank", "\u627f\u4f24", "#9D4EDD", "\u4ee5\u5438\u6536\u4f24\u5bb3\u548c\u63a7\u5236\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("condition", "\u75c7\u72b6", "#9A3412", "\u4ee5\u75c7\u72b6\u4f24\u5bb3\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("healing", "\u6cbb\u7597", "#166534", "\u4ee5\u7eaf\u6cbb\u7597\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("control", "\u63a7\u5236", "#1f2937", "\u4ee5\u63a7\u573a\u6253\u65ad\u4e3a\u4e3b\u8981\u804c\u8d23"),
        ("utility", "\u529f\u80fd", "#155e75", "\u4ee5\u529f\u80fd\u8f85\u52a9\u4e3a\u4e3b\u8981\u804c\u8d23"),
    ],
    "scoring_mode": [
        ("role_based", "\u89d2\u8272\u5b9a\u4f4d\u8bc4\u5206", "#165DFF", "\u6309\u89d2\u8272\u5b9a\u4f4d\u8bc4\u5206"),
        ("profession_based", "\u804c\u4e1a\u8bc4\u5206", "#00B42A", "\u6309\u804c\u4e1a\u8bc4\u5206"),
    ],
    "scoring_dimension": [
        ("damage", "\u4f24\u5bb3", "#ff4500", "\u603b\u4f24\u5bb3"),
        ("power_damage", "\u76f4\u4f24", "#32cd32", "\u76f4\u4f24"),
        ("condition_damage", "\u75c7\u72b6\u4f24\u5bb3", "#9400d3", "\u75c7\u72b6\u4f24\u5bb3"),
        ("healing", "\u6cbb\u7597", "#00ced1", "\u6cbb\u7597\u91cf"),
        ("boons", "\u589e\u76ca", "#ffd700", "\u589e\u76ca\u8986\u76d6"),
        ("alacrity", "\u654f\u6377", "#87ceeb", "\u654f\u6377\u8986\u76d6"),
        ("quickness", "\u6025\u901f", "#da70d6", "\u6025\u901f\u8986\u76d6"),
        ("survival", "\u751f\u5b58", "#4169e1", "\u751f\u5b58\u80fd\u529b"),
        ("strips", "\u7834\u6cd5", "#ff1745", "\u7834\u6cd5"),
        ("cleanses", "\u6e05\u75c7", "#1aff1a", "\u6e05\u75c7"),
        ("kills", "\u51fb\u6740", "#00bfff", "\u51fb\u6740"),
        ("breakbar", "\u9119\u89c6", "#b0c4de", "\u9119\u89c6"),
    ],
    "game_mode": [
        ("wvw", "\u4e16\u754c\u4e4b\u6218", "#6b21a8", ""),
        ("pve", "\u73a9\u5bb6\u5bf9\u6218\u73af\u5883", "#166534", ""),
        ("pvp", "\u73a9\u5bb6\u5bf9\u6218\u73a9\u5bb6", "#991b1b", ""),
        ("strikes", "\u788e\u5c42", "#3730a3", ""),
        ("raids", "\u56e2\u961f\u526f\u672c", "#1f2937", ""),
    ],
    "parse_status": [
        ("pending", "\u5f85\u89e3\u6790", "#6b7280", ""),
        ("parsing", "\u89e3\u6790\u4e2d", "#f59e0b", ""),
        ("completed", "\u5df2\u5b8c\u6210", "#10b981", ""),
        ("failed", "\u5931\u8d25", "#ef4444", ""),
        ("retrying", "\u91cd\u8bd5\u4e2d", "#3b82f6", ""),
        ("partial", "\u90e8\u5206\u5b8c\u6210", "#f97316", ""),
    ],
    "buff": [
        ("717", "Regeneration", "#4caf50", ""),
        ("718", "Swiftness", "#2196f3", ""),
        ("719", "Fury", "#ff9800", ""),
        ("725", "Might", "#f44336", ""),
        ("726", "Vigor", "#9c27b0", ""),
        ("728", "Protection", "#00bcd4", ""),
        ("740", "Aegis", "#ffeb3b", ""),
        ("743", "Stability", "#795548", ""),
        ("1122", "Quickness", "#e91e63", ""),
        ("1187", "Resistance", "#607d8b", ""),
        ("26980", "Alacrity", "#3f51b5", ""),
        ("26981", "Resolution", "#009688", ""),
        ("9283", "Empathy", "#8bc34a", ""),
        ("110942", "Stone", "#795548", ""),
        ("13797", "Geomancy", "#ff5722", ""),
    ],
    "dashboard_time_range": [
        ("7d", "\u6700\u8fd17\u5929", "#3b82f6", ""),
        ("30d", "\u6700\u8fd130\u5929", "#3b82f6", ""),
        ("90d", "\u6700\u8fd190\u5929", "#3b82f6", ""),
        ("all", "\u5168\u90e8", "#6b7280", ""),
    ],
    "skill_state": [
        ("cast", "\u65bd\u6cd5", "#3b82f6", ""),
        ("channel", "\u5f15\u5bfc", "#8b5cf6", ""),
        ("instant", "\u77ac\u53d1", "#10b981", ""),
        ("auto", "\u81ea\u52a8\u653b\u51fb", "#6b7280", ""),
        ("flip", "\u7ffb\u8f6c", "#f59e0b", ""),
    ],
    "permission": [
        ("add", "\u65b0\u589e", "#10b981", ""),
        ("edit", "\u7f16\u8f91", "#3b82f6", ""),
        ("delete", "\u5220\u9664", "#ef4444", ""),
        ("view", "\u67e5\u770b", "#6b7280", ""),
        ("export", "\u5bfc\u51fa", "#f59e0b", ""),
        ("import", "\u5bfc\u5165", "#8b5cf6", ""),
    ],
    "grade_level": [
        ("S", "S\u7ea7", "#f59e0b", "\u5353\u8d8a"),
        ("A", "A\u7ea7", "#10b981", "\u4f18\u79c0"),
        ("B", "B\u7ea7", "#3b82f6", "\u826f\u597d"),
        ("C", "C\u7ea7", "#6b7280", "\u4e00\u822c"),
        ("D", "D\u7ea7", "#ef4444", "\u5f85\u63d0\u5347"),
        ("F", "F\u7ea7", "#991b1b", "\u4e0d\u53ca\u683c"),
    ],
    "session_timeout": [
        ("15", "15\u5206\u949f", "#6b7280", ""),
        ("30", "30\u5206\u949f", "#6b7280", ""),
        ("60", "60\u5206\u949f", "#6b7280", ""),
        ("120", "120\u5206\u949f", "#6b7280", ""),
    ],
    "setting_tab": [
        ("account", "\u8d26\u53f7\u8bbe\u7f6e", "#3b82f6", ""),
        ("parsing", "\u89e3\u6790\u53c2\u6570", "#f59e0b", ""),
        ("export", "\u5bfc\u51fa\u683c\u5f0f", "#10b981", ""),
        ("theme", "\u754c\u9762\u4e3b\u9898", "#8b5cf6", ""),
        ("notifications", "\u901a\u77e5\u8bbe\u7f6e", "#06b6d4", ""),
        ("scoring-rules", "\u8bc4\u5206\u89c4\u5219", "#ef4444", ""),
        ("profession-mgmt", "\u804c\u4e1a\u7ba1\u7406", "#dc2626", ""),
        ("system-params", "\u7cfb\u7edf\u53c2\u6570", "#f97316", ""),
        ("dictionary", "\u5b57\u5178\u7ba1\u7406", "#84cc16", ""),
        ("security", "\u5b89\u5168\u8bbe\u7f6e", "#64748b", ""),
        ("watermark", "\u6c34\u5370\u8bbe\u7f6e", "#64748b", ""),
    ],
    "chart_mode": [
        ("bar", "\u67f1\u72b6\u56fe", "#3b82f6", ""),
        ("line", "\u6298\u7ebf\u56fe", "#10b981", ""),
        ("pie", "\u997c\u56fe", "#f59e0b", ""),
        ("radar", "\u96f7\u8fbe\u56fe", "#8b5cf6", ""),
    ],
    "sort_field": [
        ("damage", "\u4f24\u5bb3", "#ef4444", ""),
        ("dps", "DPS", "#f59e0b", ""),
        ("heal", "\u6cbb\u7597", "#10b981", ""),
        ("hps", "HPS", "#3b82f6", ""),
        ("time", "\u65f6\u95f4", "#6b7280", ""),
    ],
    "time_range": [
        ("7d", "\u6700\u8fd17\u5929", "#3b82f6", ""),
        ("30d", "\u6700\u8fd130\u5929", "#3b82f6", ""),
        ("90d", "\u6700\u8fd190\u5929", "#3b82f6", ""),
        ("180d", "\u6700\u8fd1180\u5929", "#3b82f6", ""),
        ("365d", "\u6700\u8fd1365\u5929", "#3b82f6", ""),
    ],
    "metric_type": [
        ("damage", "\u4f24\u5bb3", "#ef4444", ""),
        ("heal", "\u6cbb\u7597", "#10b981", ""),
        ("boon", "\u589e\u76ca", "#f59e0b", ""),
        ("cleanse", "\u6e05\u75c7", "#3b82f6", ""),
        ("stab", "\u7a33\u56fa", "#8b5cf6", ""),
        ("dodge", "\u95ea\u907f", "#06b6d4", ""),
        ("downed", "\u51fb\u5012", "#f59e0b", ""),
        ("fights", "\u573a\u6b21", "#3b82f6", ""),
        ("active_accounts", "\u6d3b\u8dc3", "#a855f7", ""),
    ],
    "export_format": [
        ("json", "JSON", "#3b82f6", ""),
        ("csv", "CSV", "#10b981", ""),
        ("xlsx", "Excel", "#f59e0b", ""),
        ("pdf", "PDF", "#ef4444", ""),
    ],
    "theme_color": [
        ("blue", "\u84dd\u8272", "#165DFF", ""),
        ("purple", "\u7d2b\u8272", "#722ED1", ""),
        ("green", "\u7eff\u8272", "#00B42A", ""),
        ("orange", "\u6a59\u8272", "#FF7D00", ""),
        ("red", "\u7ea2\u8272", "#F53F3F", ""),
    ],
    "number_format": [
        ("auto", "\u81ea\u52a8", "", ""),
        ("comma", "\u5343\u4f4d\u5206\u9694\u7b26 (1,000)", "", ""),
        ("scientific", "\u79d1\u5b66\u8ba1\u6570\u6cd5 (1.0e6)", "", ""),
    ],
}

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
# 种子数据动态覆盖（优先使用构建模块中的数据）
# =============================================================================
_SYS_MENU_SEED = _try_load_seed_from_module("_SYS_MENU_SEED", _SYS_MENU_SEED)
_SYS_DICT_TYPE_SEED = _try_load_seed_from_module("_SYS_DICT_TYPE_SEED", _SYS_DICT_TYPE_SEED)
_SYS_DICT_DATA_SEED = _try_load_seed_from_module("_SYS_DICT_DATA_SEED", _SYS_DICT_DATA_SEED)
_ROLE_TYPE_SEED = _try_load_seed_from_module("_ROLE_TYPE_SEED", _ROLE_TYPE_SEED)
_PROFESSION_SEED = _try_load_seed_from_module("_PROFESSION_SEED", _PROFESSION_SEED)
_ELITE_SPEC_SEED = _try_load_seed_from_module("_ELITE_SPEC_SEED", _ELITE_SPEC_SEED)


# =============================================================================
# 初始化系统菜单
# =============================================================================


def _init_sys_menu(db: Session) -> int:
    """初始化系统菜单（支持新增和更新）"""
    from app.utils.cache.cache import Cache
    
    now = datetime.now()
    created = 0
    updated = 0
    
    # 【兼容性】确保虚拟根节点存在（menu_id=0），解决 parent_id=0 的外键引用问题
    # MySQL 严格模式下，parent_id=0 必须引用存在的 menu_id=0
    root = db.query(SysMenu).filter(SysMenu.menu_id == 0).first()
    if not root:
        db.add(
            SysMenu(
                menu_id=0,
                menu_name="ROOT",
                parent_id=0,
                order_num=0,
                path="",
                menu_type="M",
                visible="1",
                status="0",
                icon="",
                create_time=now,
                update_time=now,
                create_by="system",
                update_by="system",
            )
        )
        db.flush()
        logger.info("已插入虚拟根节点 menu_id=0")
    
    for record in _SYS_MENU_SEED:
        existing = db.query(SysMenu).filter(
            SysMenu.menu_name == record["menu_name"],
            SysMenu.parent_id == record["parent_id"]
        ).first()
        
        if existing:
            # 更新现有菜单
            for key, value in record.items():
                if key != "menu_name" and key != "parent_id":
                    setattr(existing, key, value)
            existing.update_time = now
            existing.update_by = "system"
            updated += 1
        else:
            # 创建新菜单
            db.add(
                SysMenu(
                    **record,
                    create_time=now,
                    update_time=now,
                    create_by="system",
                    update_by="system",
                )
            )
            created += 1
    
    db.commit()
    
    # 清除菜单缓存
    cache = Cache()
    keys_to_delete = [key for key in cache.cache if key.startswith("menu:")]
    for key in keys_to_delete:
        cache.delete(key)
    logger.info(f"菜单缓存已清除")
    
    logger.info(f"sys_menu 初始化完成：新增 {created} 条，更新 {updated} 条")
    return created


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


def _cleanup_profession_dict(db: Session) -> int:
    """清理字典表中的 profession 类型数据
    
    说明：职业和精英特长数据由 gw_profession / gw_elite_specialization 表管理，
    不再存储在字典表中。此函数确保存量 profession 字典数据被彻底清除。
    """
    deleted = 0
    # 删除 profession 类型的字典数据
    deleted_data = (
        db.query(SysDictData)
        .filter(SysDictData.dict_type == "profession")
        .delete(synchronize_session=False)
    )
    deleted += deleted_data
    
    # 删除 profession 类型的字典类型
    deleted_type = (
        db.query(SysDictType)
        .filter(SysDictType.dict_type == "profession")
        .delete(synchronize_session=False)
    )
    deleted += deleted_type
    
    if deleted > 0:
        db.commit()
        logger.info(f"已清理字典表中 profession 类型数据（{deleted} 条记录）")
    return deleted


def _init_sys_config(db: Session) -> int:
    """初始化系统配置（sys_config 表）"""
    try:
        from app.services.system.sys_config_service import DEFAULT_CONFIGS
        SysConfigService.init_default_configs(db)
        return len(DEFAULT_CONFIGS)
    except Exception as e:
        logger.error(f"sys_config 初始化失败: {e}")
        return 0


def _init_sys_dict_data(db: Session) -> int:
    """初始化字典数据（所有在 _SYS_DICT_DATA_SEED 中声明的类型）"""
    created = 0
    for dict_type, items in _SYS_DICT_DATA_SEED.items():
        for idx, item in enumerate(items):
            # 支持3元组 (value, label, color) 或4元组 (value, label, color, remark)
            if len(item) == 3:
                value, label, color = item
                remark = f"{label}{'角色' if dict_type == 'role' else '维度' if dict_type == 'scoring_dimension' else '模式'}"
            else:
                value, label, color, remark = item

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
                        remark=remark,
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
    """初始化游戏静态数据（从 seed_modules 加载）"""
    results = {}

    # gw_skill
    if db.query(GwSkill).count() == 0:
        data = SeedDataLoader.load("game_static_bdcode_skills")
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
        data = SeedDataLoader.load("game_static_bdcode_specializations")
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
        data = SeedDataLoader.load("game_static_bdcode_traits")
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
        data = SeedDataLoader.load("game_static_skill_palettes")
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
        data = SeedDataLoader.load("game_static_buffs")
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
    """初始化Build 图书馆数据（从 seed_modules 加载）"""
    from app.services.game.bdcode_service import get_bdcode_service

    existing = db.query(Build).count()
    if existing > 0:
        return {"initialized": False, "count": 0, "errors": []}

    builds_data = SeedDataLoader.load("builds_initial")
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
    # 先清理不应存在于字典表的数据
    _cleanup_profession_dict(db)
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


def initialize_all(db: Session, force: bool = False) -> Dict[str, Any]:
    """
    执行所有数据初始化（强化版）

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

    Args:
        db: 数据库会话
        force: 强制重新初始化（忽略版本记录）

    Returns:
        初始化结果摘要

    Raises:
        InitializationError: 任何步骤失败时抛出，调用方必须终止启动
    """
    from app.core.initialization import InitializationError, RetryConfig
    from app.services.system.initialization_service import InitializationService

    logger.info("=" * 60)
    logger.info("开始执行统一数据初始化（强化版）")
    logger.info("=" * 60)

    try:
        retry_config = RetryConfig(max_attempts=5, base_delay=1.0, max_delay=30.0)
        service = InitializationService(db, retry_config=retry_config, force=force)
        summary = service.run()

        # 【关键】SKIPPED 不是错误，是正常状态——版本已应用
        if summary.get("skipped"):
            logger.info("=" * 60)
            logger.info(f"统一数据初始化已跳过: {summary.get('message', '版本已应用')}")
            logger.info("=" * 60)
            return summary.get("results", {})

        # 兼容旧版返回值格式
        results = summary.get("results", {})

        def _extract_count(v):
            if isinstance(v, int):
                return v
            if isinstance(v, dict):
                if all(isinstance(x, int) for x in v.values()):
                    return sum(v.values())
                return v.get("count", 0)
            return 0

        total = sum(_extract_count(v) for v in results.values())
        logger.info("=" * 60)
        logger.info(f"统一数据初始化完成，共导入 {total} 条记录")
        logger.info("=" * 60)
        return results

    except InitializationError as e:
        logger.error("=" * 60)
        logger.error(f"初始化失败: {e}")
        logger.error(f"失败步骤: {e.step}")
        logger.error(f"错误类型: {e.error_type}")
        logger.error(f"建议: {e.suggestion}")
        if e.data_snippet:
            logger.error(f"数据片段: {json.dumps(e.data_snippet, ensure_ascii=False, default=str)[:1000]}")
        logger.error("=" * 60)
        raise