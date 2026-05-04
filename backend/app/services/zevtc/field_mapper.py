# -*- coding: utf-8 -*-
# 模块功能：EI JSON 字段映射模块
# 作者：系统自动生成
# 创建日期：2026-05-04
# 依赖说明：Python 3.8+

from typing import Any, Dict

from app.utils.logger import logger


class EIJsonFieldMapper:
    # EI JSON 字段映射器

    # EI API 到数据库的字段映射
    EI_API_TO_DB = {
        # 通用字段
        "acc": "account",
        "name": "character_name",
        "profession": "profession",
        "group": "group_id",
        "isCommander": "has_commander_tag",
        # DPS 数据字段
        "damage": "damage",
        "dps": "dps",
        "powerDamage": "power_damage",
        "condiDamage": "condi_damage",
        "breakbarDamage": "breakbar_damage",
        # Encounter 字段
        "bossName": "encounter_name",
        "duration": "duration",
        "success": "success",
    }

    # 本地解析器到数据库的字段映射
    LOCAL_PARSER_TO_DB = {
        # 通用字段
        "account": "account",
        "name": "character_name",
        "profession": "profession",
        "group": "group_id",
        "hasCommanderTag": "has_commander_tag",
        "has_commander_tag": "has_commander_tag",
        # DPS 数据字段
        "totalDamage": "damage",
        "total_damage": "damage",
        "dps": "dps",
        "powerDamage": "power_damage",
        "power_damage": "power_damage",
        "condiDamage": "condi_damage",
        "condi_damage": "condi_damage",
        "breakbarDamage": "breakbar_damage",
        "breakbar_damage": "breakbar_damage",
        # Encounter 字段
        "encounterName": "encounter_name",
        "encounter_name": "encounter_name",
        "duration": "duration",
        "success": "success",
    }

    @classmethod
    def map_ei_api_player(cls, ei_player: Dict, dps_data: Dict) -> Dict:
        # 功能：将 EI API 玩家数据映射为数据库格式
        # 参数：
        #   ei_player: EI API 玩家数据
        #   dps_data: DPS 数据（来自 validator）
        # 返回：数据库格式的玩家数据

        db_data = {
            "account": ei_player.get("acc"),
            "character_name": ei_player.get("name"),
            "profession": ei_player.get("profession"),
            "group_id": int(ei_player.get("group", 0)),
            "has_commander_tag": bool(ei_player.get("isCommander", False)),
        }

        # 合并 DPS 数据
        db_data.update(dps_data)

        return db_data

    @classmethod
    def map_ei_api_encounter(cls, ei_encounter: Dict) -> Dict:
        # 功能：将 EI API Encounter 数据映射为数据库格式
        return {
            "encounter_name": ei_encounter.get("bossName", ""),
            "duration": float(ei_encounter.get("duration", 0)),
            "success": bool(ei_encounter.get("success", False)),
        }

    @classmethod
    def map_local_parser_player(cls, local_player: Dict) -> Dict:
        # 功能：将本地解析器玩家数据映射为数据库格式
        db_data = {}

        # 尝试各种可能的字段名
        for source_field, target_field in cls.LOCAL_PARSER_TO_DB.items():
            if source_field in local_player:
                # 类型转换
                value = local_player[source_field]
                if target_field == "group_id":
                    value = int(value) if value is not None else 0
                elif target_field == "has_commander_tag":
                    value = bool(value) if value is not None else False
                elif target_field in ["damage", "dps", "power_damage", "condi_damage", "breakbar_damage"]:
                    value = int(value) if value is not None else 0

                db_data[target_field] = value

        return db_data

    @classmethod
    def get_value_with_fallback(cls, data: Dict, fields: list, default: Any = None) -> Any:
        # 功能：按优先级从多个字段中获取值
        for field in fields:
            if field in data and data[field] is not None:
                return data[field]
        return default

    @classmethod
    def normalize_commander_field(cls, data: Dict) -> bool:
        # 功能：标准化指挥官字段（兼容多种字段名）
        fields_to_check = ["isCommander", "hasCommanderTag", "has_commander_tag"]
        for field in fields_to_check:
            if field in data:
                return bool(data[field])
        return False
