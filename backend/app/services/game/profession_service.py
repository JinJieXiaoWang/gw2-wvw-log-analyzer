# -*- coding: utf-8 -*-
# 模块功能：职业数据服务层
# 作者：System
# 创建日期：2026-05-11
# 依赖说明：SQLAlchemy
# 说明：统一管理GW2职业、精英特长、角色定位的层级数据

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.game.profession import (
    GwEliteSpecialization,
    GwProfession,
    GwRoleType,
)
from app.constants.dict_values import RoleType
from app.utils.logger import logger


class ProfessionService:
    """
    职业数据服务层
    提供职业、精英特长、角色定位的CRUD操作和数据查询
    """

    def __init__(self, db: Session):
        self.db = db

    def _role_type_to_dict(self, role: GwRoleType) -> Dict[str, Any]:
        """将角色定位对象转为字典"""
        return {
            "id": role.id,
            "role_key": role.role_key,
            "role_name": role.role_name,
            "color": role.color,
            "icon": role.icon,
            "sort_order": role.sort_order,
        }

    def _profession_to_dict(self, profession: GwProfession, include_specs: bool = False) -> Dict[str, Any]:
        """将职业对象转为字典"""
        result = {
            "id": profession.id,
            "profession_key": profession.profession_key,
            "profession_name": profession.profession_name,
            "profession_name_en": profession.profession_name_en,
            "color": profession.color,
            "icon": profession.icon,
            "is_active": profession.is_active,
            "sort_order": profession.sort_order,
        }

        if include_specs:
            specs = self.get_specs_by_profession(profession.profession_key)
            result["elite_specializations"] = specs

        return result

    def _spec_to_dict(self, spec: GwEliteSpecialization) -> Dict[str, Any]:
        """将精英特长对象转为字典"""
        return {
            "id": spec.id,
            "spec_key": spec.spec_key,
            "spec_name": spec.spec_name,
            "spec_name_en": spec.spec_name_en,
            "profession_key": spec.profession_key,
            "color": spec.color,
            "icon": spec.icon,
            "role_type": spec.role_type,
            "dps_type": spec.dps_type,
            "scoring_config": spec.scoring_config or {},
            "is_active": spec.is_active,
            "sort_order": spec.sort_order,
        }

    # ==================== 角色定位操作 ====================

    def get_all_role_types(self) -> List[Dict[str, Any]]:
        """获取所有角色定位列表"""
        roles = self.db.query(GwRoleType).order_by(GwRoleType.sort_order).all()
        return [self._role_type_to_dict(r) for r in roles]

    def get_role_type(self, role_key: str) -> Optional[Dict[str, Any]]:
        """根据key获取角色定位"""
        role = self.db.query(GwRoleType).filter(GwRoleType.role_key == role_key).first()
        return self._role_type_to_dict(role) if role else None

    # ==================== 职业操作 ====================

    def get_all_professions(self, include_specs: bool = False, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取所有职业列表"""
        query = self.db.query(GwProfession)
        if active_only:
            query = query.filter(GwProfession.is_active == 1)
        professions = query.order_by(GwProfession.sort_order).all()
        return [self._profession_to_dict(p, include_specs) for p in professions]

    def get_profession(self, profession_key: str, include_specs: bool = False) -> Optional[Dict[str, Any]]:
        """根据key获取职业信息"""
        profession = self.db.query(GwProfession).filter(
            GwProfession.profession_key == profession_key
        ).first()
        return self._profession_to_dict(profession, include_specs) if profession else None

    def get_profession_by_id(self, profession_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取职业信息"""
        profession = self.db.query(GwProfession).filter(GwProfession.id == profession_id).first()
        return self._profession_to_dict(profession) if profession else None

    def get_profession_color(self, profession_key: str) -> str:
        """获取职业颜色"""
        profession = self.get_profession(profession_key)
        return profession.get("color", "#6b7280") if profession else "#6b7280"

    def get_profession_name(self, profession_key: str) -> str:
        """获取职业中文名称"""
        profession = self.get_profession(profession_key)
        return profession.get("profession_name", profession_key) if profession else profession_key

    # ==================== 精英特长操作 ====================

    def get_all_specs(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取所有精英特长列表"""
        query = self.db.query(GwEliteSpecialization)
        if active_only:
            query = query.filter(GwEliteSpecialization.is_active == 1)
        specs = query.order_by(GwEliteSpecialization.sort_order).all()
        return [self._spec_to_dict(s) for s in specs]

    def get_spec_by_key(self, spec_key: str) -> Optional[Dict[str, Any]]:
        """根据key获取精英特长"""
        spec = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.spec_key == spec_key
        ).first()
        return self._spec_to_dict(spec) if spec else None

    def get_specs_by_profession(self, profession_key: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取指定职业的所有精英特长"""
        query = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.profession_key == profession_key
        )
        if active_only:
            query = query.filter(GwEliteSpecialization.is_active == 1)
        specs = query.order_by(GwEliteSpecialization.sort_order).all()
        return [self._spec_to_dict(s) for s in specs]

    def get_spec_profession(self, spec_key: str) -> Optional[str]:
        """获取精英特长所属的职业"""
        spec = self.get_spec_by_key(spec_key)
        return spec.get("profession_key") if spec else None

    def get_spec_role_type(self, spec_key: str) -> str:
        """获取精英特长角色定位"""
        spec = self.get_spec_by_key(spec_key)
        return spec.get("role_type", RoleType.DPS) if spec else RoleType.DPS

    def get_spec_color(self, spec_key: str) -> Optional[str]:
        """获取精英特长颜色"""
        spec = self.get_spec_by_key(spec_key)
        return spec.get("color") if spec else None

    # ==================== 层级查询 ====================

    def get_profession_with_specs(self, profession_key: str) -> Optional[Dict[str, Any]]:
        """获取职业及其所有精英特长"""  
        return self.get_profession(profession_key, include_specs=True)

    def get_profession_spec_cascade(self) -> List[Dict[str, Any]]:
        """获取职业-精英特长级联数据（用于前端级联选择器）"""
        professions = self.get_all_professions(include_specs=False)
        result = []
        for prof in professions:
            specs = self.get_specs_by_profession(prof["profession_key"])
            result.append({
                "value": prof["profession_key"],
                "label": prof["profession_name"],
                "color": prof["color"],
                "elite_specs": [
                    {
                        "value": spec["spec_key"],
                        "label": spec["spec_name"],
                        "color": spec["color"],
                    }
                    for spec in specs
                ],
            })
        return result

    def get_role_spec_mapping(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取角色定位到精英特长的映射（用于评分规则页面）"""
        result: Dict[str, List[Dict[str, Any]]] = {}
        specs = self.get_all_specs()

        for spec in specs:
            role = spec.get("role_type", RoleType.DPS)
            if role not in result:
                result[role] = []
            result[role].append(spec)

        return result

    def get_all_profession_spec_options(self) -> List[Dict[str, Any]]:
        """获取所有职业和精英特长选项（扁平结构，用于下拉选择）"""
        professions = self.get_all_professions()
        options = []

        for prof in professions:
            specs = self.get_specs_by_profession(prof["profession_key"])
            options.append({
                "profession": prof,
                "specs": specs,
            })

        return options

    # ==================== 统计信息 ====================

    def get_statistics(self) -> Dict[str, int]:
        """获取职业数据统计"""
        return {
            "role_types_count": self.db.query(GwRoleType).count(),
            "professions_count": self.db.query(GwProfession).filter(GwProfession.is_active == 1).count(),
            "elite_specs_count": self.db.query(GwEliteSpecialization).filter(GwEliteSpecialization.is_active == 1).count(),
        }

    # ==================== CRUD 操作 ====================

    def update_spec_role_type(self, spec_key: str, role_key: str) -> bool:
        """更新精英特长的角色定位"""
        spec = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.spec_key == spec_key
        ).first()
        if not spec:
            return False
        spec.role_type = role_key
        self.db.commit()
        logger.info(f"更新精英特长 {spec_key} 的角色定位为 {role_key}")
        return True

    def create_profession(self, profession_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新职业"""
        existing = self.db.query(GwProfession).filter(
            GwProfession.profession_key == profession_data.get("profession_key")
        ).first()
        if existing:
            return None
        profession = GwProfession(**profession_data)
        self.db.add(profession)
        self.db.commit()
        self.db.refresh(profession)
        return self._profession_to_dict(profession)

    def update_profession(self, profession_key: str, profession_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新职业信息"""
        profession = self.db.query(GwProfession).filter(
            GwProfession.profession_key == profession_key
        ).first()
        if not profession:
            return None
        for key, value in profession_data.items():
            if hasattr(profession, key):
                setattr(profession, key, value)
        self.db.commit()
        self.db.refresh(profession)
        return self._profession_to_dict(profession)

    def delete_profession(self, profession_key: str) -> bool:
        """删除职业（软删除）"""
        profession = self.db.query(GwProfession).filter(
            GwProfession.profession_key == profession_key
        ).first()
        if not profession:
            return False
        profession.is_active = 0
        self.db.commit()
        logger.info(f"软删除职业 {profession_key}")
        return True

    def create_elite_spec(self, spec_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新精英特长"""
        existing = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.spec_key == spec_data.get("spec_key")
        ).first()
        if existing:
            return None
        spec = GwEliteSpecialization(**spec_data)
        self.db.add(spec)
        self.db.commit()
        self.db.refresh(spec)
        return self._spec_to_dict(spec)

    def update_elite_spec(self, spec_key: str, spec_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新精英特长信息"""
        spec = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.spec_key == spec_key
        ).first()
        if not spec:
            return None
        for key, value in spec_data.items():
            if hasattr(spec, key):
                setattr(spec, key, value)
        self.db.commit()
        self.db.refresh(spec)
        return self._spec_to_dict(spec)

    def delete_elite_spec(self, spec_key: str) -> bool:
        """删除精英特长（软删除）"""
        spec = self.db.query(GwEliteSpecialization).filter(
            GwEliteSpecialization.spec_key == spec_key
        ).first()
        if not spec:
            return False
        spec.is_active = 0
        self.db.commit()
        logger.info(f"软删除精英特长 {spec_key}")
        return True

    def create_role_type(self, role_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新角色定义"""
        existing = self.db.query(GwRoleType).filter(
            GwRoleType.role_key == role_data.get("role_key")
        ).first()
        if existing:
            return None
        role = GwRoleType(**role_data)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self._role_type_to_dict(role)

    def update_role_type(self, role_key: str, role_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新角色定位信息"""
        role = self.db.query(GwRoleType).filter(
            GwRoleType.role_key == role_key
        ).first()
        if not role:
            return None
        for key, value in role_data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        self.db.commit()
        self.db.refresh(role)
        return self._role_type_to_dict(role)

    def delete_role_type(self, role_key: str) -> bool:
        """删除角色定位"""
        role = self.db.query(GwRoleType).filter(
            GwRoleType.role_key == role_key
        ).first()
        if not role:
            return False
        self.db.delete(role)
        self.db.commit()
        logger.info(f"删除角色定位 {role_key}")
        return True
