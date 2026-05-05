# -*- coding: utf-8 -*-
# 模块功能：EI JSON 数据验证模块
# 作者：系统自动生成
# 创建日期：2026-05-04
# 依赖说明：Python 3.8+

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.core.zevtc.constants import INVALID_ACCOUNT_PATTERNS
from app.utils.logger import logger


@dataclass
class ValidationResult:
    # 验证结果数据类
    success: bool
    data: Optional[Dict] = None
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class EIJsonValidator:
    # EI JSON 数据验证器

    # 玩家数据必需字段（支持多种字段名）
    # 格式：{ 标准字段名: [ 可能的字段名列表 ] }
    PLAYER_REQUIRED_FIELDS = {
        "account": ["acc", "account"],
        "name": ["name"],
        "profession": ["profession"],
        "group": ["group"],
        "has_commander_tag": ["isCommander", "hasCommanderTag"],
    }

    # 预编译正则表达式
    _invalid_account_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in INVALID_ACCOUNT_PATTERNS]

    @classmethod
    def is_valid_account_name(cls, account_name: Optional[str]) -> bool:
        """验证账号名称是否有效。
        
        只过滤明确的黑名单账号（如 "Non Squad Player"），其他账号都允许通过。
        
        Args:
            account_name: 账号名称
            
        Returns:
            True 表示有效，False 表示无效（在黑名单中）
        """
        # 检查是否为空
        if not account_name or not isinstance(account_name, str):
            return False
        
        # 去除首尾空格后检查是否为空
        account_name_stripped = account_name.strip()
        if not account_name_stripped:
            return False
        
        # 检查黑名单，只有在黑名单中的才拒绝
        for regex in cls._invalid_account_regexes:
            if regex.match(account_name_stripped):
                return False
        
        # 其他所有账号都允许通过
        return True

    @classmethod
    def validate_account_name(cls, account_name: Optional[str]) -> Tuple[bool, str]:
        """验证账号名称并返回详细结果。
        
        Args:
            account_name: 账号名称
            
        Returns:
            (is_valid: bool, reason: str)
        """
        if not account_name or not isinstance(account_name, str):
            return False, "账号名称为空或不是字符串"
        
        account_name_stripped = account_name.strip()
        if not account_name_stripped:
            return False, "账号名称为空"
        
        # 检查黑名单
        for regex in cls._invalid_account_regexes:
            if regex.match(account_name_stripped):
                return False, f"账号名称在黑名单中（匹配模式: {regex.pattern}）"
        
        # 其他所有情况都通过
        return True, "验证通过"

    # Encounter 数据必需字段（降低要求，不强制要求）
    ENCOUNTER_REQUIRED_FIELDS = []

    # 数值范围规则
    VALUE_RANGES = {
        "group": {"min": 0, "max": 100},
        "dps": {"min": 0, "max": 1000000},
        "damage": {"min": 0, "max": 1000000000},
    }

    # 指挥官标记字段冲突检测
    COMMANDER_FIELDS = ["isCommander", "hasCommanderTag", "has_commander_tag"]

    # 假玩家/NPC 标记字段
    SKIP_FLAGS = ["isFake", "friendlyNPC"]

    @classmethod
    def _get_field_value(cls, player: Dict, possible_fields: List[str], default=None):
        # 功能：从多个可能的字段名中获取值
        for field in possible_fields:
            if field in player and player[field] is not None:
                return player[field]
        return default

    @classmethod
    def validate_players(cls, players: List[Dict]) -> Tuple[List[Dict], List[str], List[str]]:
        # 功能：验证玩家数组
        # 参数：players - 玩家数据数组
        # 返回：(有效玩家列表, 错误列表, 警告列表)
        valid_players = []
        errors = []
        warnings = []

        if not players:
            errors.append("players 数组为空")
            return valid_players, errors, warnings

        for idx, player in enumerate(players):
            result = cls._validate_single_player(player, idx)
            if result.success and result.data:
                valid_players.append(result.data)
            # 即使验证失败也不阻止导入，只记录错误
            if result.errors:
                warnings.extend([f"玩家 #{idx}: {err}" for err in result.errors])
            warnings.extend(result.warnings)

        return valid_players, errors, warnings

    @classmethod
    def _validate_single_player(cls, player: Dict, index: int) -> ValidationResult:
        # 功能：验证单个玩家数据（更加宽松的验证策略）
        errors = []
        warnings = []
        validated_data = {}

        # 检测假玩家 / NPC
        skip_reasons = []
        for flag in cls.SKIP_FLAGS:
            if player.get(flag):
                skip_reasons.append(flag)
        if skip_reasons:
            warnings.append(f"玩家 #{index} 被标记为假玩家/NPC ({', '.join(skip_reasons)})，建议跳过")
            validated_data["_should_skip"] = True

        # 检测指挥官标记字段冲突
        commander_values = {}
        for field in cls.COMMANDER_FIELDS:
            if field in player:
                commander_values[field] = player[field]
        if len(commander_values) > 1:
            # 如果多个字段存在且值不一致，发出警告
            unique_values = set(bool(v) for v in commander_values.values())
            if len(unique_values) > 1:
                warnings.append(
                    f"玩家 #{index} 指挥官标记字段冲突: {commander_values}，"
                    f"将使用 hasCommanderTag > isCommander > has_commander_tag 的优先级"
                )

        # 验证必需字段（使用多种可能的字段名）
        for standard_field, possible_fields in cls.PLAYER_REQUIRED_FIELDS.items():
            value = cls._get_field_value(player, possible_fields)
            if value is None:
                # 对于非关键字段，提供默认值而不是报错
                if standard_field == "group":
                    value = 1
                    warnings.append(f"玩家 #{index} 缺少 group 字段，使用默认值 1")
                elif standard_field == "has_commander_tag":
                    value = False
                    warnings.append(f"玩家 #{index} 缺少 isCommander/hasCommanderTag 字段，使用默认值 False")
                else:
                    errors.append(f"玩家 #{index} 缺少必需字段: {standard_field} (可能的字段名: {possible_fields})")
            validated_data[standard_field] = value

        # 验证字段类型（使用多种可能的字段名）
        account_value = cls._get_field_value(player, ["acc", "account"])
        name_value = cls._get_field_value(player, ["name"])
        profession_value = cls._get_field_value(player, ["profession"])
        group_value = cls._get_field_value(player, ["group"])
        commander_value = cls._get_field_value(player, ["isCommander", "hasCommanderTag"])

        if account_value is not None and not isinstance(account_value, str):
            warnings.append(f"玩家 #{index} 的账户字段不是字符串类型")
            validated_data["account"] = str(account_value) if account_value is not None else ""

        if name_value is not None and not isinstance(name_value, str):
            warnings.append(f"玩家 #{index} 的 name 不是字符串类型")
            validated_data["name"] = str(name_value) if name_value is not None else ""

        if profession_value is not None and not isinstance(profession_value, str):
            warnings.append(f"玩家 #{index} 的 profession 不是字符串类型")
            validated_data["profession"] = str(profession_value) if profession_value is not None else ""

        # 验证数值范围并确保类型正确
        try:
            group = int(group_value) if group_value is not None else 1
            validated_data["group"] = group
            if group < cls.VALUE_RANGES["group"]["min"] or group > cls.VALUE_RANGES["group"]["max"]:
                warnings.append(
                    f"玩家 #{index} 的 group 值 {group} 超出范围 [{cls.VALUE_RANGES['group']['min']}-{cls.VALUE_RANGES['group']['max']}]"
                )
        except (ValueError, TypeError):
            warnings.append(f"玩家 #{index} 的 group 值无效，使用默认值 1")
            validated_data["group"] = 1

        # 确保指挥官标记是布尔类型
        validated_data["has_commander_tag"] = bool(commander_value) if commander_value is not None else False

        # 验证通过，复制原始数据并保留所有字段
        validated_data.update(player)

        # 即使有错误也返回成功（宽松策略）
        return ValidationResult(success=True, data=validated_data, warnings=warnings)

    @classmethod
    def validate_encounter(cls, encounter: Optional[Dict]) -> ValidationResult:
        # 功能：验证 Encounter 数据（宽松验证）
        if not encounter:
            return ValidationResult(success=True, data={}, warnings=["encounter 数据为空，使用默认值"])

        warnings = []
        validated_data = {}

        # 验证通过（不再强制要求字段）
        validated_data.update(encounter)

        return ValidationResult(success=True, data=validated_data, warnings=warnings)

    @classmethod
    def validate_dps_data(cls, player: Dict) -> Tuple[Dict, List[str]]:
        # 功能：验证和提取玩家 DPS 数据
        data = {}
        warnings = []

        details = player.get("details", {})
        dps_all = details.get("dpsAll", [])

        if dps_all and len(dps_all) > 0:
            dps_obj = dps_all[0]

            # 提取并验证伤害数据
            data["damage"] = cls._validate_numeric(dps_obj.get("damage"), 0, "damage", warnings)
            data["dps"] = cls._validate_numeric(dps_obj.get("dps"), 0, "dps", warnings)
            data["power_damage"] = cls._validate_numeric(dps_obj.get("powerDamage"), 0, "powerDamage", warnings)
            data["condi_damage"] = cls._validate_numeric(dps_obj.get("condiDamage"), 0, "condiDamage", warnings)
            data["breakbar_damage"] = cls._validate_numeric(dps_obj.get("breakbarDamage"), 0, "breakbarDamage", warnings)
        else:
            warnings.append("玩家缺少 dpsAll 数据")
            data["damage"] = 0
            data["dps"] = 0
            data["power_damage"] = 0
            data["condi_damage"] = 0
            data["breakbar_damage"] = 0

        return data, warnings

    @classmethod
    def _validate_numeric(cls, value: Any, default: Any, field_name: str, warnings: List[str]) -> Any:
        # 功能：验证数值类型，如果无效则使用默认值
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str) and value.replace(".", "", 1).isdigit():
            return float(value)
        warnings.append(f"字段 {field_name} 不是有效数值，使用默认值 {default}")
        return default

    @classmethod
    def validate_ei_json(cls, ei_json: Dict) -> Tuple[List[Dict], Optional[Dict], List[str], List[str]]:
        # 功能：完整验证 EI JSON 数据（宽松验证）
        # 返回：(有效玩家列表, 有效encounter数据, 错误列表, 警告列表)
        errors = []
        warnings = []

        # 验证顶层结构（宽松要求）
        if "players" not in ei_json:
            warnings.append("EI JSON 缺少 players 数组，使用空数组")
            ei_json["players"] = []

        if "encounter" not in ei_json:
            warnings.append("EI JSON 缺少 encounter 对象")

        # 验证玩家数据
        valid_players, player_errors, player_warnings = cls.validate_players(ei_json["players"])
        errors.extend(player_errors)
        warnings.extend(player_warnings)

        # 验证 Encounter 数据
        encounter_result = cls.validate_encounter(ei_json.get("encounter"))
        valid_encounter = None
        if encounter_result.success:
            valid_encounter = encounter_result.data
        warnings.extend(encounter_result.warnings)

        return valid_players, valid_encounter, errors, warnings
