# -*- coding: utf-8 -*-
# 模块功能：评分规则 Pydantic Schema

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ScoringRuleBase(BaseModel):
    """评分规则基础 Schema"""
    role_type: str = Field(..., description="角色类型: dps/support/tank")
    profession: Optional[str] = Field(None, description="精英特长/职业名称，null表示通用规则")
    dimension: str = Field(..., description="评分维度")
    weight: float = Field(0.0, ge=0.0, le=10.0, description="权重系数")
    min_value: Optional[float] = Field(None, description="最小值阈值")
    max_value: Optional[float] = Field(None, description="最大值上限")
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, max_length=500, description="规则描述")
    sort_order: int = Field(0, description="显示排序")


class ScoringRuleCreate(ScoringRuleBase):
    """创建评分规则"""
    pass


class ScoringRuleUpdate(BaseModel):
    """更新评分规则"""
    weight: Optional[float] = Field(None, ge=0.0, le=10.0, description="权重系数")
    min_value: Optional[float] = Field(None, description="最小值阈值")
    max_value: Optional[float] = Field(None, description="最大值上限")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, max_length=500, description="规则描述")
    sort_order: Optional[int] = Field(None, description="显示排序")


class ScoringRuleResponse(ScoringRuleBase):
    """评分规则响应"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScoringRuleListResponse(BaseModel):
    """评分规则列表响应"""
    items: List[ScoringRuleResponse]
    total: int


class ScoringRuleBatchUpdate(BaseModel):
    """批量更新评分规则"""
    role_type: str = Field(..., description="角色类型")
    profession: Optional[str] = Field(None, description="精英特长/职业名称，null表示更新通用规则")
    rules: List[ScoringRuleCreate] = Field(..., description="规则列表")


class ScoringRulePresetBase(BaseModel):
    """评分规则预设基础 Schema"""
    role_type: str = Field(..., description="角色类型")
    preset_name: str = Field(..., description="预设名称")
    preset_data: str = Field(..., description="预设JSON数据")
    is_default: bool = Field(False, description="是否为系统默认")
    is_active: bool = Field(True, description="是否启用")


class ScoringRulePresetResponse(ScoringRulePresetBase):
    """评分规则预设响应"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleScoringConfig(BaseModel):
    """角色类型评分配置（用于前端展示）"""
    role_type: str = Field(..., description="角色类型")
    role_label: str = Field(..., description="角色类型中文名")
    rules: List[ScoringRuleResponse] = Field(default_factory=list, description="规则列表")
