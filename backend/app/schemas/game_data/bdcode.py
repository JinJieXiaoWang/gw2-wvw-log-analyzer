# -*- coding: utf-8 -*-
# 模块功能：BDCode解析相关的Schema定义
# 作者：系统
# 创建日期?2026-04-27

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ==================== 基础请求/响应模型 ====================
class BDCodeParseRequest(BaseModel):
    """BDCode解析请求"""

    bd_code: str = Field(..., description="BDCode字符串，格式 [&...]")
    include_icons: bool = Field(default=True, description="是否包含图标URL")


class BDCodeValidationRequest(BaseModel):
    """BDCode验证请求"""

    bd_code: str = Field(..., description="BDCode字符?)


class BDCodeValidationResponse(BaseModel):
    """BDCode验证响应"""

    is_valid: bool = Field(..., description="是否有效")
    error: Optional[str] = Field(None, description="错误信息")


# ==================== 详细数据模型 ====================
class TraitInfoResponse(BaseModel):
    """特性信?""

    id: int = Field(0, description="特性ID")
    name: str = Field("", description="特性名?)
    icon: Optional[str] = Field(None, description="图标URL")
    description: Optional[str] = Field(None, description="描述")
    is_selected: bool = Field(False, description="是否被选中")


class SpecializationInfoResponse(BaseModel):
    """专精线信?""

    id: int = Field(0, description="专精线ID")
    name: str = Field("", description="专精线名?)
    name_cn: Optional[str] = Field(None, description="中文名称")
    icon: Optional[str] = Field(None, description="图标URL")
    is_elite: bool = Field(False, description="是否为精英专?)
    selected_traits: List[int] = Field([0, 0, 0], description="选中的特性位?)
    traits: List[TraitInfoResponse] = Field([], description="特性列?)


class SkillInfoResponse(BaseModel):
    """技能信?""

    id: Optional[int] = Field(None, description="技能ID")
    palette_id: Optional[int] = Field(None, description="调色盘ID")
    name: Optional[str] = Field(None, description="技能名?)
    name_cn: Optional[str] = Field(None, description="中文名称")
    icon: Optional[str] = Field(None, description="图标URL")
    description: Optional[str] = Field(None, description="描述")
    slot: Optional[str] = Field(None, description="技能槽")
    recharge: int = Field(0, description="冷却时间（秒?)


class BuildInfoResponse(BaseModel):
    """Build完整信息"""

    bd_code: str = Field(..., description="原始BDCode")
    profession_id: int = Field(..., description="职业数字ID")
    profession: str = Field(..., description="职业英文名称")
    profession_cn: str = Field(..., description="职业中文名称")
    specializations: List[SpecializationInfoResponse] = Field(
        [], description="专精线列?
    )
    skills: Dict[str, Any] = Field({}, description="技能列?heal, utility, elite")


class BDCodeParseResponse(BaseModel):
    """BDCode解析响应"""

    success: bool = Field(..., description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")
    data: Optional[BuildInfoResponse] = Field(None, description="Build数据")
    bd_code: str = Field(..., description="原始BDCode")


# ==================== 批量处理模型 ====================
class BDCodeBatchRequest(BaseModel):
    """BDCode批量解析请求"""

    bd_codes: List[str] = Field(..., description="BDCode列表")
    include_icons: bool = Field(default=True, description="是否包含图标URL")


class BDCodeBatchItem(BaseModel):
    """批量解析单项结果"""

    bd_code: str = Field(..., description="原始BDCode")
    success: bool = Field(..., description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")
    data: Optional[BuildInfoResponse] = Field(None, description="Build数据")


class BDCodeBatchResponse(BaseModel):
    """BDCode批量解析响应"""

    total_count: int = Field(..., description="总数")
    success_count: int = Field(..., description="成功数量")
    error_count: int = Field(..., description="失败数量")
    results: List[BDCodeBatchItem] = Field([], description="解析结果列表")


class BDCodeStatsResponse(BaseModel):
    """BDCode统计信息"""

    skill_palettes_count: int = Field(..., description="技能调色盘数量")
    skills_count: int = Field(..., description="技能数据)
    specializations_count: int = Field(..., description="专精线数据)
    traits_count: int = Field(..., description="特性数据)
    cache_stats: Dict[str, Any] = Field({}, description="缓存统计")
