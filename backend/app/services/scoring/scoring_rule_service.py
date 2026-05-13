# -*- coding: utf-8 -*-
# 模块功能：评分规则配置服务
# 说明：管理基于角色类型和职业的评分规则 CRUD、版本管理与初始化

import json
import os
from typing import Any, Dict, List, Optional

from app.models.scoring.scoring_rule import ScoringRule, ScoringRulePreset
from app.models.scoring.scoring_rule_version import ScoringRuleVersion
from app.schemas.scoring.scoring_rule import ScoringRuleResponse
from app.utils.db.dict_utils import get_dict_options
from app.utils.logger import logger
from sqlalchemy.orm import Session

# 默认评分规则配置文件路径
_DEFAULT_RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config", "default_scoring_rules.json"
)


def _load_default_rules_from_file() -> Dict[str, List[Dict[str, Any]]]:
    """从 JSON 配置文件加载默认评分规则（非代码硬编码）"""
    try:
        with open(_DEFAULT_RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载默认评分规则文件失败: {e}")
        return {}


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
        self, role_type: str, profession: Optional[str] = None, active_only: bool = True
    ) -> List[ScoringRule]:
        """获取指定角色类型的评分规则
        
        Args:
            role_type: 角色类型 dps/support/tank
            profession: 精英特长/职业名称，None 表示查询通用规则
            active_only: 仅返回启用的规则
        """
        query = self.db.query(ScoringRule).filter(
            ScoringRule.role_type == role_type,
            ScoringRule.profession == profession,
        )
        if active_only:
            query = query.filter(ScoringRule.is_active == True)
        return query.order_by(ScoringRule.sort_order).all()

    def get_rules_for_profession(
        self, role_type: str, profession: Optional[str] = None, active_only: bool = True
    ) -> List[ScoringRule]:
        """获取用于评分的规则，优先返回职业特定规则，无则回退到通用规则
        
        Args:
            role_type: 角色类型 dps/support/tank
            profession: 精英特长/职业名称
            active_only: 仅返回启用的规则
        """
        # 先查询职业特定规则
        if profession:
            specific_rules = self.get_rules_by_role(role_type, profession, active_only)
            if specific_rules:
                return specific_rules

        # 回退到通用规则
        return self.get_rules_by_role(role_type, None, active_only)

    def _get_enabled_role_types(self) -> List[str]:
        """从字典表获取启用的角色类型列表（status=0）"""
        options = get_dict_options("role")
        return [opt["value"] for opt in options]

    def get_all_rules(self, active_only: bool = True) -> Dict[str, List[ScoringRule]]:
        """获取所有启用的角色类型的通用评分规则，按角色分组"""
        result = {}
        for role in self._get_enabled_role_types():
            result[role] = self.get_rules_by_role(role, None, active_only)
        return result

    def get_profession_rules(self, profession: str, active_only: bool = True) -> Dict[str, List[ScoringRule]]:
        """获取指定职业的所有启用角色类型规则"""
        result = {}
        for role in self._get_enabled_role_types():
            rules = self.get_rules_by_role(role, profession, active_only)
            if rules:
                result[role] = rules
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
                ScoringRule.profession == data.get("profession"),
                ScoringRule.dimension == data["dimension"],
            )
            .first()
        )
        if existing:
            prof_desc = f"职业 {data.get('profession')} " if data.get("profession") else "通用 "
            raise ValueError(
                f"角色类型 {data['role_type']} 下{prof_desc}已存在维度 {data['dimension']} 的规则"
            )

        rule = ScoringRule(**data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        prof_info = f"/{data.get('profession')}" if data.get("profession") else ""
        logger.info(f"创建评分规则: {rule.role_type}{prof_info}/{rule.dimension} = {rule.weight}")
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

    def delete_profession_rules(self, profession: str, role_type: Optional[str] = None) -> int:
        """删除指定职业的所有特定规则
        
        Returns:
            删除的规则数量
        """
        query = self.db.query(ScoringRule).filter(ScoringRule.profession == profession)
        if role_type:
            query = query.filter(ScoringRule.role_type == role_type)
        count = query.count()
        query.delete(synchronize_session=False)
        self.db.commit()
        logger.info(f"删除职业特定规则: {profession}, 共 {count} 条")
        return count

    def batch_update_rules(
        self, role_type: str, rules_data: List[dict], profession: Optional[str] = None
    ) -> Dict:
        """批量更新角色类型的评分规则
        
        当 profession 为 None 时更新通用规则；有值时更新该职业的特定规则。
        批量更新后自动递增规则版本号。
        """
        # 删除该角色类型 + 职业 的现有规则
        query = self.db.query(ScoringRule).filter(
            ScoringRule.role_type == role_type,
            ScoringRule.profession == profession,
        )
        query.delete(synchronize_session=False)

        created = []
        for item in rules_data:
            item["role_type"] = role_type
            item["profession"] = profession
            rule = ScoringRule(**item)
            self.db.add(rule)
            created.append(rule)

        self.db.commit()
        for rule in created:
            self.db.refresh(rule)

        prof_info = f"职业 {profession} " if profession else "通用 "
        logger.info(f"批量更新评分规则: {role_type} {prof_info}共 {len(created)} 条")
        return {"role_type": role_type, "profession": profession, "count": len(created)}

    def reset_to_default(self, role_type: Optional[str] = None) -> Dict:
        """重置为系统默认规则（仅重置通用规则，不删除职业特定规则）
        
        默认规则从 JSON 配置文件读取，不再硬编码在 Python 代码中。
        """
        default_rules = _load_default_rules_from_file()
        if not default_rules:
            logger.warning("默认评分规则文件为空或加载失败，无法重置")
            return {"reset_roles": [], "count": 0, "error": "默认规则文件不可用"}

        enabled_roles = self._get_enabled_role_types()
        targets = [role_type] if role_type else enabled_roles
        total = 0

        for rt in targets:
            if rt not in default_rules:
                continue

            # 仅删除通用规则（profession is null）
            self.db.query(ScoringRule).filter(
                ScoringRule.role_type == rt,
                ScoringRule.profession.is_(None),
            ).delete(synchronize_session=False)

            # 插入默认规则
            for item in default_rules[rt]:
                rule = ScoringRule(
                    role_type=rt,
                    profession=None,
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

    def get_rules_for_scoring(
        self, role_type: str = "dps", profession: Optional[str] = None
    ) -> Dict[str, float]:
        """获取用于评分的规则字典（兼容旧版 scoring_service 接口）
        
        优先返回职业特定规则，无则回退到通用规则。
        """
        rules = self.get_rules_for_profession(role_type, profession, active_only=True)
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
        """获取角色类型中文标签（优先查字典表）"""
        options = get_dict_options("role")
        for opt in options:
            if opt.get("value") == role_type:
                return opt.get("label", role_type)
        return role_type

    def get_professions_with_rules(self, role_type: Optional[str] = None) -> List[str]:
        """获取已配置职业特定规则的职业列表"""
        from sqlalchemy import distinct
        query = self.db.query(distinct(ScoringRule.profession)).filter(
            ScoringRule.profession.isnot(None)
        )
        if role_type:
            query = query.filter(ScoringRule.role_type == role_type)
        return [row[0] for row in query.all() if row[0]]

    # ==================== 版本管理 ====================

    def get_current_version(self) -> int:
        """获取当前最新版本号"""
        latest = (
            self.db.query(ScoringRuleVersion)
            .order_by(ScoringRuleVersion.version.desc())
            .first()
        )
        return latest.version if latest else 0

    def bump_version(self, description: str = "") -> ScoringRuleVersion:
        """递增规则版本号，创建新版本记录
        
        Returns:
            新创建的版本记录
        """
        current = self.get_current_version()
        new_version = ScoringRuleVersion(
            version=current + 1,
            description=description or "规则变更",
            status="pending",
        )
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        logger.info(f"评分规则版本递增: {current} -> {new_version.version}")
        return new_version

    def get_version_by_id(self, version_id: int) -> Optional[ScoringRuleVersion]:
        """通过ID获取版本记录"""
        return self.db.query(ScoringRuleVersion).filter(ScoringRuleVersion.id == version_id).first()

    def get_versions(self, skip: int = 0, limit: int = 20) -> List[ScoringRuleVersion]:
        """获取版本历史列表"""
        return (
            self.db.query(ScoringRuleVersion)
            .order_by(ScoringRuleVersion.version.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def init_version_if_empty(self) -> Dict:
        """如果版本表为空，初始化版本0"""
        count = self.db.query(ScoringRuleVersion).count()
        if count > 0:
            return {"initialized": False, "reason": "版本表已有数据", "count": count}

        version = ScoringRuleVersion(
            version=0,
            description="系统初始版本",
            status="completed",
        )
        self.db.add(version)
        self.db.commit()
        logger.info("初始化评分规则版本表: version=0")
        return {"initialized": True, "version": 0}

    # ==================== 职业规则初始化 ====================

    def init_profession_rules_from_db(self) -> Dict:
        """从数据库导入默认职业特定规则
        
        仅当 scoring_rule 表中没有任何职业特定规则时执行。
        将数据库中精英特长的 scoring_config 整数权重归一化为浮点权重。
        """
        from app.services.game.profession_service import ProfessionService
        
        # 检查是否已有职业特定规则
        existing_count = (
            self.db.query(ScoringRule)
            .filter(ScoringRule.profession.isnot(None))
            .count()
        )
        if existing_count > 0:
            return {"initialized": False, "reason": "已有职业特定规则", "count": existing_count}

        try:
            logger.debug("开始从数据库查询精英特长数据以初始化职业特定规则...")
            
            # 从数据库获取精英特长数据
            prof_service = ProfessionService(self.db)
            elite_specs = prof_service.get_all_specs(active_only=False)
            
            logger.debug(f"查询到 {len(elite_specs)} 个精英特长")
            
            total_created = 0

            for spec in elite_specs:
                spec_name = spec.get("spec_key")
                scoring_config = spec.get("scoring_config")
                
                if not scoring_config or not spec_name:
                    continue

                default_role = spec.get("default_role", "dps")

                # 归一化权重
                total_weight = sum(scoring_config.values())
                if total_weight <= 0:
                    continue

                sort_order = 1
                for dimension, weight in scoring_config.items():
                    normalized_weight = round(weight / total_weight, 4)
                    rule = ScoringRule(
                        role_type=default_role,
                        profession=spec_name,
                        dimension=dimension,
                        weight=normalized_weight,
                        description=f"{spec_name} 默认 {dimension} 权重",
                        sort_order=sort_order,
                        is_active=True,
                    )
                    self.db.add(rule)
                    sort_order += 1
                    total_created += 1

            self.db.commit()
            logger.info(f"从数据库导入职业特定规则: 共 {total_created} 条")
            return {"initialized": True, "count": total_created}
            
        except Exception as e:
            logger.error(f"从数据库导入职业特定规则失败: {e}", exc_info=True)
            return {"initialized": False, "reason": f"数据库查询失败: {e}"}

    def get_role_types_data(self) -> List[Dict[str, Any]]:
        """获取所有启用的角色类型配置（含描述、颜色等前端展示字段）"""
        from app.constants.scoring import ROLE_DESCRIPTIONS
        from app.services.game.profession_service import ProfessionService

        prof_service = ProfessionService(self.db)
        role_types = prof_service.get_all_role_types()

        roles = []
        for rt in role_types:
            role_key = rt.get("role_key", "")
            roles.append({
                "type": role_key,
                "label": rt.get("role_name", role_key),
                "description": ROLE_DESCRIPTIONS.get(role_key, ""),
                "color": rt.get("color", "#6b7280"),
            })
        return roles

    def get_scoring_rules_data(
        self,
        role_type: Optional[str] = None,
        profession: Optional[str] = None,
        active_only: bool = True,
    ) -> Dict[str, Any]:
        """获取评分规则响应数据（含条件分支与数据组装）"""
        if profession:
            rules = self.get_rules_by_role(role_type or "dps", profession, active_only)
            return {
                "role_type": role_type or "dps",
                "profession": profession,
                "role_label": self.get_role_label(role_type or "dps"),
                "rules": [ScoringRuleResponse.model_validate(r) for r in rules],
            }
        elif role_type:
            rules = self.get_rules_by_role(role_type, None, active_only)
            return {
                "role_type": role_type,
                "role_label": self.get_role_label(role_type),
                "rules": [ScoringRuleResponse.model_validate(r) for r in rules],
            }
        else:
            all_rules = self.get_all_rules(active_only)
            return {
                role: {
                    "role_type": role,
                    "role_label": self.get_role_label(role),
                    "rules": [ScoringRuleResponse.model_validate(r) for r in rules],
                }
                for role, rules in all_rules.items()
            }

    def get_version_with_progress(self, version_id: int) -> Optional[Dict[str, Any]]:
        """获取版本详情并计算进度百分比"""
        from app.schemas.scoring.scoring_recalculation import ScoringRuleVersionResponse

        version = self.get_version_by_id(version_id)
        if not version:
            return None

        progress = 0.0
        if version.total_records > 0:
            progress = round(version.updated_records / version.total_records * 100, 2)

        data = ScoringRuleVersionResponse.model_validate(version).model_dump()
        data["progress_percent"] = progress
        return data

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
