# -*- coding: utf-8 -*-
# 模块功能：评分重算任务 Schema
# 说明：定义重算任务的请求/响应模型

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RecalculateFilters(BaseModel):
    """重算筛选条件"""
    fight_ids: Optional[List[int]] = Field(None, description="指定战斗ID列表")
    date_from: Optional[str] = Field(None, description="起始日期 (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    professions: Optional[List[str]] = Field(None, description="指定职业列表")
    account_names: Optional[List[str]] = Field(None, description="指定账号列表")


class RecalculateRequest(BaseModel):
    """触发评分重算请求"""
    filters: Optional[RecalculateFilters] = Field(
        default_factory=RecalculateFilters,
        description="重算筛选条件，空则表示全量重算",
    )
    description: Optional[str] = Field(
        None,
        description="重算任务描述",
    )


class RecalculateResponse(BaseModel):
    """重算任务创建响应"""
    version_id: int = Field(..., description="版本记录ID")
    version: int = Field(..., description="版本")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="状态说明")


class RecalculateStatusResponse(BaseModel):
    """重算任务进度查询响应"""
    version_id: int = Field(..., description="版本记录ID")
    version: int = Field(..., description="版本")
    status: str = Field(..., description="任务状? pending/processing/completed/failed")
    total_records: int = Field(0, description="需更新的总记录数")
    updated_records: int = Field(0, description="已更新记录数")
    failed_records: int = Field(0, description="失败记录数")
    progress_percent: float = Field(0.0, description="进度百分比")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ScoringRuleVersionResponse(BaseModel):
    """评分规则版本响应"""
    id: int = Field(..., description="版本记录ID")
    version: int = Field(..., description="版本")
    description: Optional[str] = Field(None, description="变更描述")
    status: str = Field(..., description="任务状态")
    total_records: int = Field(0, description="需更新的总记录数")
    updated_records: int = Field(0, description="已更新记录数")
    failed_records: int = Field(0, description="失败记录数")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        from_attributes = True
