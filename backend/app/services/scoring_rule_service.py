# -*- coding: utf-8 -*-
# 模块功能：评分规则配置服务
# 说明：管理基于角色类型的评分规则 CRUD 与初始化

import json
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.scoring_rule import ScoringRule, ScoringRulePreset
from app.utils.logger import logger


# 系统默认评分规则配置
DEFAULT_RULES = {
    "dps": [
        {"dimension": "damage", "weight": 0.40, "description": "总伤害输出权重", "sort_order": 1},
        {"dimension": "power_damage", "weight": 0.15, "description": "直伤输出权重", "sort_order": 2},
        {"dimension": "condition_damage", "weight": 0.15, "description": "症状伤害权重", "sort_order": 3},
        {"dimension": "survival", "weight": 0.10, "description": "生存能力权重", "sort_order": 4},
        {"dimension": "kills", "weight": 0.08, "description": "击杀贡献权重", "sort_order": 5},
        {"dimension": "breakbar", "weight": 0.05, "description": "蔑视条伤害权重", "sort_order": 6},
        {"dimension": "strips", "weight": 0.04, "description": "破法权重", "sort_order": 7},
        {"dimension": "cleanses", "weight": 0.03, "description": "净化权重", "sort_order": 8},
    ],
    "support": [
        {"dimension": "healing", "weight": 0.30, "description": "治疗量权重", "sort_order": 1},
        {"dimension": "boons", "weight": 0.20, "description": "增益覆盖权重", "sort_order": 2},
        {"dimension": "alacrity", "weight": 0.15, "description": "敏捷覆盖权重", "sort_order": 3},
        {"dimension": "quickness", "weight": 0.15, "description": "急速覆盖权重", "sort_order": 4},
        {"dimension": "cleanses", "weight": 0.08, "description": "净化权重", "sort_order": 5},
        {"dimension": "strips", "weight": 0.05, "description": "破法权重", "sort_order": 6},
        {"dimension": "survival", "weight": 0.05, "description": "生存能力权重", "sort_order": 7},
        {"dimension": "damage", "weight": 0.02, "description": "输出补充权重", "sort_order": 8},
    ],
    "tank": [
        {"dimension": "damage_taken", "weight": 0.25, "description": "承受伤害权重", "sort_order": 1},
        {"dimension": "survival", "weight": 0.20, "description": "生存能力权重", "sort_order": 2},
        {"dimension": "blocked_count", "weight": 0.12, "description": "格挡次数权重", "sort_order": 3},
        {"dimension": "evaded_count", "weight": 0.10, "description": "闪避次数权重", "sort_order": 4},
        {"dimension": "damage", "weight": 0.10, "description": "反击输出权重", "sort_order": 5},
        {"dimension": "breakbar", "weight": 0.08, "description": "控制贡献权重", "sort_order": 6},
        {"dimension": "strips", "weight": 0.08, "description": "破法权重", "sort_order": 7},
        {"dimension": "cleanses", "weight": 0.07, "description": "净化权重", "sort_order": 8},
    ],
}

ROLE_LABELS = {
    "dps": "输出",
    "support": "辅助",
    "tank": "承伤",
}

DIMENSION_LABELS = {
    "damage": "总伤害",
    "power_damage": "直伤",
    "condition_damage": "症状伤害",
    "healing": "治疗量",
    "boons": "增益覆盖",
    "alacrity": "敏捷覆盖",
    "quickness": "急速覆盖",
    "survival": "生存能力",
    "strips": "破法",
    "cleanses": "净化",
    "kills": "击杀",
    "breakbar": "蔑视条",
    "damage_taken": "承受伤害",
    "blocked_count": "格挡",
    "evaded_count": "闪避",
}


class ScoringRuleService:
    """评分规则服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_rules_by_role(
        self, role_type: str, active_only: bool = True
    ) -> List[ScoringRule]:
        """获取指定角色类型的评分规则"""
        query = self.db.query(ScoringRule).filter(
            ScoringRule.role_type == role_type
        )
        if active_only:
            query = query.filter(ScoringRule.is_active == True)
        return query.order_by(ScoringRule.sort_order).all()

    def get_all_rules(self, active_only: bool = True) -> Dict[str, List[ScoringRule]]:
        """获取所有角色类型的评分规则，按角色分组"""
        result = {}
        for role in ["dps", "support", "tank"]:
            result[role] = self.get_rules_by_role(role, active_only)
        return result

    def get_rule_by_id(self, rule_id: int) -> Optional[ScoringRule]:
        """通过ID获取评分规则"""
        return self.db.query(ScoringRule).filter(ScoringRule.id == rule_id).first()

    def create_rule(self, data: dict) -> ScoringRule:
        """创建评分规则"""
        existing = (
            self.db.query(ScoringRule)
            .filter(
                ScoringRule.role_type == data["role_type"],
                ScoringRule.dimension == data["dimension"],
            )
            .first()
        )
        if existing:
            raise ValueError(
                f"角色类型 {data['role_type']} 下已存在维度 {data['dimension']} 的规则"
            )

        rule = ScoringRule(**data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"创建评分规则: {rule.role_type}/{rule.dimension} = {rule.weight}")
        return rule

    def update_rule(self, rule_id: int, data: dict) -> Optional[ScoringRule]:
        """更新评分规则"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return None

        for key, value in data.items():
            if value is not None and hasattr(rule, key):
                setattr(rule, key, value)

        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"更新评分规则 ID={rule_id}")
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        """删除评分规则"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return False
        self.db.delete(rule)
        self.db.commit()
        logger.info(f"删除评分规则 ID={rule_id}")
        return True

    def batch_update_rules(self, role_type: str, rules_data: List[dict]) -> Dict:
        """批量更新角色类型的评分规则"""
        # 先删除该角色类型下所有现有规则
        self.db.query(ScoringRule).filter(
            ScoringRule.role_type == role_type
        ).delete()

        created = []
        for item in rules_data:
            item["role_type"] = role_type
            rule = ScoringRule(**item)
            self.db.add(rule)
            created.append(rule)

        self.db.commit()
        for rule in created:
            self.db.refresh(rule)

        logger.info(f"批量更新评分规则: {role_type}, 共 {len(created)} 条")
        return {"role_type": role_type, "count": len(created)}

    def reset_to_default(self, role_type: Optional[str] = None) -> Dict:
        """重置为系统默认规则"""
        targets = [role_type] if role_type else ["dps", "support", "tank"]
        total = 0

        for rt in targets:
            if rt not in DEFAULT_RULES:
                continue

            # 删除现有规则
            self.db.query(ScoringRule).filter(
                ScoringRule.role_type == rt
            ).delete()

            # 插入默认规则
            for item in DEFAULT_RULES[rt]:
                rule = ScoringRule(
                    role_type=rt,
                    dimension=item["dimension"],
                    weight=item["weight"],
                    description=item.get("description", ""),
                    sort_order=item.get("sort_order", 0),
                    is_active=True,
                )
                self.db.add(rule)
                total += 1

        self.db.commit()
        logger.info(f"重置评分规则为默认: {targets}, 共 {total} 条")
        return {"reset_roles": targets, "count": total}

    def init_default_rules_if_empty(self) -> Dict:
        """如果表为空，初始化默认规则"""
        count = self.db.query(ScoringRule).count()
        if count > 0:
            return {"initialized": False, "reason": "评分规则表已有数据", "count": count}

        result = self.reset_to_default()
        return {"initialized": True, **result}

    def get_rules_for_scoring(self, role_type: str = "dps") -> Dict[str, float]:
        """获取用于评分的规则字典（兼容旧版 scoring_service 接口）"""
        rules = self.get_rules_by_role(role_type, active_only=True)
        result = {}
        for rule in rules:
            weight_key = f"{rule.dimension}_weight"
            result[weight_key] = rule.weight
        # 补充默认值
        result.setdefault("min_score_threshold", 0.0)
        result.setdefault("max_score_cap", 100.0)
        return result

    def get_dimension_label(self, dimension: str) -> str:
        """获取维度中文标签"""
        return DIMENSION_LABELS.get(dimension, dimension)

    def get_role_label(self, role_type: str) -> str:
        """获取角色类型中文标签"""
        return ROLE_LABELS.get(role_type, role_type)

    def get_preset_by_role(self, role_type: str) -> Optional[ScoringRulePreset]:
        """获取角色类型的预设"""
        return (
            self.db.query(ScoringRulePreset)
            .filter(ScoringRulePreset.role_type == role_type)
            .first()
        )

    def save_preset(self, role_type: str, preset_name: str, rules: List[dict]) -> ScoringRulePreset:
        """保存预设"""
        existing = self.get_preset_by_role(role_type)
        preset_data = json.dumps(rules, ensure_ascii=False)

        if existing:
            existing.preset_name = preset_name
            existing.preset_data = preset_data
            self.db.commit()
            self.db.refresh(existing)
            return existing

        preset = ScoringRulePreset(
            role_type=role_type,
            preset_name=preset_name,
            preset_data=preset_data,
        )
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset
