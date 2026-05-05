# -*- coding: utf-8 -*-
# 模块功能：字典数据初始化器
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：SQLAlchemy, json

import json
import os
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.dictionary import SysDictData, SysDictType


class DictionaryDataInitializer:
    # 功能：字典数据初始化器
    # 参数：无
    # 返回：无

    def __init__(self, db: Session):
        # 功能：初始化器构造函数
        # 参数：db - 数据库会话
        self.db = db
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(self.base_dir, "app", "data")

    # 职业颜色映射表
    PROFESSION_COLORS = {
        "Guardian": "#0078D4",
        "Warrior": "#D47B00",
        "Engineer": "#00CC6A",
        "Ranger": "#F59E00",
        "Thief": "#A13790",
        "Elementalist": "#AA0000",
        "Mesmer": "#B34CCC",
        "Necromancer": "#68768A",
        "Revenant": "#00A9B5",
    }

    # 角色定位颜色映射表
    ROLE_COLORS = {
        "dps": "#FF6B35",
        "support": "#35B0FF",
        "condition": "#9A3412",
        "healing": "#166534",
        "control": "#1f2937",
        "utility": "#155e75",
    }

    # 评分维度颜色映射表
    SCORING_DIMENSION_COLORS = {
        "damage": "#ff4500",
        "power_damage": "#32cd32",
        "condition_damage": "#9400d3",
        "healing": "#00ced1",
        "boons": "#ffd700",
        "alacrity": "#87ceeb",
        "quickness": "#da70d6",
        "survival": "#4169e1",
        "strips": "#ff1745",
        "cleanses": "#1aff1a",
        "kills": "#00bfff",
        "breakbar": "#b0c4de",
    }

    # 游戏模式颜色映射表
    GAME_MODE_COLORS = {
        "wvw": "#6b21a8",
        "pve": "#166534",
        "pvp": "#991b1b",
        "strikes": "#3730a3",
        "raids": "#1f2937",
    }


    # 精英特长颜色映射表 - 按职业分组，便于区分
    SPECIALIZATION_COLORS = {
        # Guardian 精英特长 - 蓝色系
        "Dragonhunter": "#4A90D9",
        "Firebrand": "#D94A4A",
        "Willbender": "#D9D94A",
        "Luminary": "#FFD700",
        # Warrior 精英特长 - 橙色系
        "Berserker": "#FF6B35",
        "Spellbreaker": "#35B0FF",
        "Bladesworn": "#FF35B0",
        "Paragon": "#FFB035",
        # Engineer 精英特长 - 绿色系
        "Scrapper": "#35FF6B",
        "Holosmith": "#FF9E35",
        "Mechanist": "#6BFF35",
        "Amalgam": "#35D9FF",
        # Ranger 精英特长 - 棕色系
        "Druid": "#8B4513",
        "Soulbeast": "#D2691E",
        "Untamed": "#556B2F",
        "Galeshot": "#6B8E23",
        # Thief 精英特长 - 紫色系
        "Daredevil": "#9370DB",
        "Deadeye": "#8A2BE2",
        "Specter": "#9932CC",
        "Antiquary": "#BA55D3",
        # Elementalist 精英特长 - 多彩系
        "Tempest": "#FF4500",
        "Weaver": "#1E90FF",
        "Catalyst": "#FFD700",
        "Evoker": "#00CED1",
        # Mesmer 精英特长 - 粉色系
        "Chronomancer": "#FF69B4",
        "Mirage": "#DA70D6",
        "Virtuoso": "#FF1493",
        "Troubadour": "#C71585",
        # Necromancer 精英特长 - 灰绿系
        "Reaper": "#2F4F4F",
        "Scourge": "#8B0000",
        "Harbinger": "#556B2F",
        "Ritualist": "#006400",
        # Revenant 精英特长 - 蓝绿系
        "Herald": "#008B8B",
        "Renegade": "#2E8B57",
        "Vindicator": "#4682B4",
        "Conduit": "#5F9EA0",
    }

    def initialize_dict_types(self) -> Dict[str, int]:
        # 功能：初始化字典类型
        # 参数：无
        # 返回：字典类型映射（key为类型编码，value为创建状态（0表示跳过，1表示创建）
        dict_types_data = [
            {
                "dict_type": "profession",
                "dict_name": "职业",
                "status": 0,
                "sort_order": 1,
                "remark": "激战2职业枚举",
                "is_system": 1
            },
            {
                "dict_type": "specialization",
                "dict_name": "精英特长",
                "status": 0,
                "sort_order": 2,
                "remark": "激战2精英特长枚举",
                "is_system": 1
            },
            {
                "dict_type": "role",
                "dict_name": "角色定位",
                "status": 0,
                "sort_order": 3,
                "remark": "激战2角色定位",
                "is_system": 1
            },
            {
                "dict_type": "scoring_dimension",
                "dict_name": "评分维度",
                "status": 0,
                "sort_order": 4,
                "remark": "评分指标维度",
                "is_system": 1
            },
            {
                "dict_type": "game_mode",
                "dict_name": "游戏模式",
                "status": 0,
                "sort_order": 5,
                "remark": "激战2游戏模式",
                "is_system": 1
            },
            {
                "dict_type": "buff_id",
                "dict_name": "增益ID",
                "status": 0,
                "sort_order": 6,
                "remark": "技能增益ID映射",
                "is_system": 1
            }
        ]

        result = {}
        for type_data in dict_types_data:
            existing = self.db.query(SysDictType).filter(
                SysDictType.dict_type == type_data["dict_type"]).first()
            if not existing:
                dict_type = SysDictType(**type_data)
                self.db.add(dict_type)
                result[type_data["dict_type"]] = 1
            else:
                # 已存在的预置类型，标记为系统预置
                if hasattr(existing, 'is_system') and not existing.is_system:
                    existing.is_system = 1
                result[type_data["dict_type"]] = 0

        self.db.commit()
        return result

    def initialize_professions(self) -> Dict[str, int]:
        # 功能：初始化职业字典数据
        # 参数：无
        # 返回：统计信息（创建和跳过的数量）
        professions_file = os.path.join(self.data_dir, "professions.json")
        result = {"created": 0, "skipped": 0}

        professions = [
            ("Guardian", "守护者"),
            ("Warrior", "战士"),
            ("Engineer", "工程师"),
            ("Ranger", "游侠"),
            ("Thief", "潜行者"),
            ("Elementalist", "元素使"),
            ("Mesmer", "幻术师"),
            ("Necromancer", "唤灵师"),
            ("Revenant", "魂武者"),
        ]

        for dict_value, dict_label in professions:
            existing = self.db.query(SysDictData).filter(
                SysDictData.dict_type == "profession",
                SysDictData.dict_value == dict_value
            ).first()

            css_class = self.PROFESSION_COLORS.get(dict_value, "#333333")

            if not existing:
                dict_data = SysDictData(
                    dict_type="profession",
                    dict_value=dict_value,
                    dict_label=dict_label,
                    css_class=css_class,
                    status=0,
                    dict_sort=result["created"],
                    remark=f"{dict_value}职业"
                )
                self.db.add(dict_data)
                result["created"] += 1
            else:
                # 如果已存在但没有有效颜色，则更新颜色
                if existing.css_class in [None, "", "#333333"]:
                    existing.css_class = css_class
                result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_specializations(self) -> Dict[str, int]:
        # 功能：初始化精英特长字典数据
        # 参数：无
        # 返回：统计信息
        professions_file = os.path.join(self.data_dir, "professions.json")
        result = {"created": 0, "skipped": 0}

        if os.path.exists(professions_file):
            with open(professions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "elite_specs" in data:
                elite_specs = list(data["elite_specs"].keys())
                for spec_name in elite_specs:
                    existing = self.db.query(SysDictData).filter(
                        SysDictData.dict_type == "specialization",
                        SysDictData.dict_value == spec_name
                    ).first()

                    spec_info = data["elite_specs"].get(spec_name, {})
                    dict_label = spec_info.get("name_cn", spec_name)
                    # 使用预定义的颜色值，如果没有则使用默认值
                    css_class = self.SPECIALIZATION_COLORS.get(spec_name, "#333333")

                    if not existing:
                        dict_data = SysDictData(
                            dict_type="specialization",
                            dict_value=spec_name,
                            dict_label=dict_label,
                            css_class=css_class,
                            status=0,
                            dict_sort=result["created"],
                            remark=f"{spec_name}精英特长"
                        )
                        self.db.add(dict_data)
                        result["created"] += 1
                    else:
                        # 如果已存在但没有有效颜色，则更新颜色
                        if existing.css_class in [None, "", "#333333"]:
                            existing.css_class = css_class
                        result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_roles(self) -> Dict[str, int]:
        # 功能：初始化角色定位字典数据
        # 参数：无
        # 返回：统计信息
        roles = [
            ("dps", "输出"),
            ("support", "辅助"),
            ("condition", "症状"),
            ("healing", "治疗"),
            ("control", "控制"),
            ("utility", "功能"),
        ]

        result = {"created": 0, "skipped": 0}
        for dict_value, dict_label in roles:
            existing = self.db.query(SysDictData).filter(
                SysDictData.dict_type == "role",
                SysDictData.dict_value == dict_value
            ).first()

            css_class = self.ROLE_COLORS.get(dict_value, "#333333")

            if not existing:
                dict_data = SysDictData(
                    dict_type="role",
                    dict_value=dict_value,
                    dict_label=dict_label,
                    css_class=css_class,
                    status=0,
                    dict_sort=result["created"],
                    remark=f"{dict_label}角色"
                )
                self.db.add(dict_data)
                result["created"] += 1
            else:
                # 如果已存在但没有有效颜色，则更新颜色
                if existing.css_class in [None, "", "#333333"]:
                    existing.css_class = css_class
                result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_scoring_dimensions(self) -> Dict[str, int]:
        # 功能：初始化评分维度字典数据
        # 参数：无
        # 返回：统计信息
        dimensions = [
            ("damage", "伤害"),
            ("power_damage", "直伤"),
            ("condition_damage", "症状伤害"),
            ("healing", "治疗"),
            ("boons", "增益"),
            ("alacrity", "敏捷"),
            ("quickness", "急速"),
            ("survival", "生存"),
            ("strips", "破法"),
            ("cleanses", "净化"),
            ("kills", "击杀"),
            ("breakbar", "蔑视条"),
        ]

        result = {"created": 0, "skipped": 0}
        for dict_value, dict_label in dimensions:
            existing = self.db.query(SysDictData).filter(
                SysDictData.dict_type == "scoring_dimension",
                SysDictData.dict_value == dict_value
            ).first()

            css_class = self.SCORING_DIMENSION_COLORS.get(dict_value, "#333333")

            if not existing:
                dict_data = SysDictData(
                    dict_type="scoring_dimension",
                    dict_value=dict_value,
                    dict_label=dict_label,
                    css_class=css_class,
                    status=0,
                    dict_sort=result["created"],
                    remark=f"{dict_label}评分维度"
                )
                self.db.add(dict_data)
                result["created"] += 1
            else:
                # 如果已存在但没有有效颜色，则更新颜色
                if existing.css_class in [None, "", "#333333"]:
                    existing.css_class = css_class
                result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_game_modes(self) -> Dict[str, int]:
        # 功能：初始化游戏模式字典数据
        # 参数：无
        # 返回：统计信息
        game_modes = [
            ("wvw", "世界之战"),
            ("pve", "玩家对战环境"),
            ("pvp", "玩家对战玩家"),
            ("strikes", "碎层"),
            ("raids", "团队副本"),
        ]

        result = {"created": 0, "skipped": 0}
        for dict_value, dict_label in game_modes:
            existing = self.db.query(SysDictData).filter(
                SysDictData.dict_type == "game_mode",
                SysDictData.dict_value == dict_value
            ).first()

            css_class = self.GAME_MODE_COLORS.get(dict_value, "#333333")

            if not existing:
                dict_data = SysDictData(
                    dict_type="game_mode",
                    dict_value=dict_value,
                    dict_label=dict_label,
                    css_class=css_class,
                    status=0,
                    dict_sort=result["created"],
                    remark=f"{dict_label}模式"
                )
                self.db.add(dict_data)
                result["created"] += 1
            else:
                # 如果已存在但没有有效颜色，则更新颜色
                if existing.css_class in [None, "", "#333333"]:
                    existing.css_class = css_class
                result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_buff_ids(self) -> Dict[str, int]:
        # 功能：初始化增益ID字典数据
        # 参数：无
        # 返回：统计信息
        buffs_file = os.path.join(self.data_dir, "buffs.json")
        result = {"created": 0, "skipped": 0}

        if os.path.exists(buffs_file):
            with open(buffs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "buffs" in data:
                for buff_name, buff_info in data["buffs"].items():
                    existing = self.db.query(SysDictData).filter(
                        SysDictData.dict_type == "buff_id",
                        SysDictData.dict_value == str(buff_info.get("id", buff_name))
                    ).first()

                    dict_value = str(buff_info.get("id", buff_name))
                    dict_label = buff_info.get("name", buff_name)

                    if not existing:
                        dict_data = SysDictData(
                            dict_type="buff_id",
                            dict_value=dict_value,
                            dict_label=dict_label,
                            css_class="#20b2aa",
                            status=0,
                            dict_sort=result["created"],
                            remark=f"{dict_label}增益"
                        )
                        self.db.add(dict_data)
                        result["created"] += 1
                    else:
                        result["skipped"] += 1

        self.db.commit()
        return result

    def initialize_all(self, force: bool = False) -> Dict[str, Any]:
        # 功能：初始化所有字典数据
        # 参数：force - 是否强制重新初始化
        # 返回：初始化结果统计
        if force:
            self.db.query(SysDictData).delete()
            self.db.query(SysDictType).delete()
            self.db.commit()

        types_result = self.initialize_dict_types()
        professions_result = self.initialize_professions()
        specializations_result = self.initialize_specializations()
        roles_result = self.initialize_roles()
        scoring_result = self.initialize_scoring_dimensions()
        game_modes_result = self.initialize_game_modes()
        buff_ids_result = self.initialize_buff_ids()

        total_created = (
            professions_result["created"] +
            specializations_result["created"] +
            roles_result["created"] +
            scoring_result["created"] +
            game_modes_result["created"] +
            buff_ids_result["created"]
        )

        total_skipped = (
            professions_result["skipped"] +
            specializations_result["skipped"] +
            roles_result["skipped"] +
            scoring_result["skipped"] +
            game_modes_result["skipped"] +
            buff_ids_result["skipped"]
        )

        return {
            "total_created": total_created,
            "total_skipped": total_skipped,
            "details": {
                "types": types_result,
                "professions": professions_result,
                "specializations": specializations_result,
                "roles": roles_result,
                "scoring_dimensions": scoring_result,

                "game_modes": game_modes_result,
                "buff_ids": buff_ids_result
            }
        }

    def init_all_dictionaries(self, force: bool = False) -> Dict[str, Any]:
        # 功能：初始化所有字典数据（别名方法）
        # 参数：force - 是否强制重新初始化
        # 返回：初始化结果统计
        return self.initialize_all(force)
