# 模块功能：AI分析报告数据验证模式
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：pydantic v2

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AIReportBase(BaseModel):
    # 功能：AI报告基础模型
    model_config = ConfigDict(from_attributes=True)

    report_type: str = Field(..., description="报告类型: fight/skill/build/trend")
    target_type: str = Field(..., description="目标类型: fight/member/build")
    target_id: int


class AIReportCreate(AIReportBase):
    # 功能：AI报告创建模型
    content: dict
    summary: Optional[str] = None
    ai_score: Optional[float] = None
    is_public: bool = True


class AIReportResponse(AIReportBase):
    # 功能：AI报告响应模型
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    summary: Optional[str] = None
    ai_score: Optional[float] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    is_public: bool


class AIReportDetailResponse(AIReportResponse):
    # 功能：AI报告详情响应模型
    parsed_content: Optional[dict] = None


class FightAnalysisContent(BaseModel):
    # 功能：战斗分析内容模型
    model_config = ConfigDict(from_attributes=True)

    summary: str
    team_strengths: List[str]
    team_weaknesses: List[str]
    buff_analysis: List[str]
    cc_analysis: List[str]
    skill_rotation_notes: List[str]
    recommendations: List[str]


class SkillAnalysisContent(BaseModel):
    # 功能：技能循环分析内容模型
    model_config = ConfigDict(from_attributes=True)

    ideal_rotation: List[dict]
    actual_rotation: List[dict]
    mistakes: List[dict]
    optimization_suggestions: List[str]
    rotation_score: float


class BuildAnalysisContent(BaseModel):
    # 功能：Build分析内容模型
    model_config = ConfigDict(from_attributes=True)

    current_build: dict
    suggestions: List[dict]
    wvw_appropriateness: float
    alternative_builds: List[dict]


class TrendAnalysisContent(BaseModel):
    # 功能：趋势分析内容模型
    model_config = ConfigDict(from_attributes=True)

    trend_data: List[dict]
    predictions: List[str]
    anomalies: List[str]
    insights: List[str]


class AIReportListResponse(BaseModel):
    # 功能：AI报告列表响应模型
    model_config = ConfigDict(from_attributes=True)

    items: List[AIReportResponse]
    total: int
    page: int
    page_size: int


class AIAnalyzeRequest(BaseModel):
    # 功能：AI分析请求模型
    model_config = ConfigDict(from_attributes=True)

    options: Optional[dict] = None


class AISuggestionResponse(BaseModel):
    # 功能：AI建议响应模型
    model_config = ConfigDict(from_attributes=True)

    suggestions: List[str]
    priority: List[str]
