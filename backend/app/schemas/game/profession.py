# -*- coding: utf-8 -*-
# 模块功能：职业数据相关的 Pydantic 模型
# 作者：System
# 创建日期?2026-05-12

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# === 角色定位模型 ===

class RoleTypeBase(BaseModel):
    role_key: str = Field(..., description="角色定位键")
    role_name: str = Field(..., description="角色定位名称")
    color: Optional[str] = Field(None, description="颜色")
    icon: Optional[str] = Field(None, description="图标")
    sort_order: Optional[int] = Field(0, description="排序")


class RoleTypeCreate(RoleTypeBase):
    pass


class RoleTypeUpdate(BaseModel):
    role_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


# === 职业模型 ===

class ProfessionBase(BaseModel):
    profession_key: str = Field(..., description="职业键")
    profession_name: str = Field(..., description="职业中文名称")
    profession_name_en: Optional[str] = Field(None, description="职业英文名称")
    color: Optional[str] = Field(None, description="颜色")
    icon: Optional[str] = Field(None, description="图标")
    default_role: Optional[str] = Field("dps", description="默认角色定位")
    possible_roles: Optional[List[str]] = Field(None, description="可能的角色定义")
    is_active: Optional[int] = Field(1, description="是否启用")
    sort_order: Optional[int] = Field(0, description="排序")


class ProfessionCreate(ProfessionBase):
    pass


class ProfessionUpdate(BaseModel):
    profession_name: Optional[str] = None
    profession_name_en: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    default_role: Optional[str] = None
    possible_roles: Optional[List[str]] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None


class ProfessionRoleUpdate(BaseModel):
    role_key: str = Field(..., description="角色定位键")


# === 精英特长模型 ===

class EliteSpecBase(BaseModel):
    spec_key: str = Field(..., description="精英特长键")
    spec_name: str = Field(..., description="精英特长中文名称")
    spec_name_en: Optional[str] = Field(None, description="精英特长英文名称")
    profession_key: str = Field(..., description="所属职业键")
    color: Optional[str] = Field(None, description="颜色")
    icon: Optional[str] = Field(None, description="图标")
    default_role: Optional[str] = Field("dps", description="默认角色定位")
    dps_type: Optional[str] = Field(None, description="DPS类型")
    scoring_config: Optional[Dict[str, Any]] = Field(None, description="评分配置")
    is_key_support: Optional[int] = Field(0, description="是否关键辅助")
    is_active: Optional[int] = Field(1, description="是否启用")
    sort_order: Optional[int] = Field(0, description="排序")


class EliteSpecCreate(EliteSpecBase):
    pass


class EliteSpecUpdate(BaseModel):
    spec_name: Optional[str] = None
    spec_name_en: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    default_role: Optional[str] = None
    dps_type: Optional[str] = None
    scoring_config: Optional[Dict[str, Any]] = None
    is_key_support: Optional[int] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None


class EliteSpecRoleUpdate(BaseModel):
    role_key: str = Field(..., description="角色定位键")
