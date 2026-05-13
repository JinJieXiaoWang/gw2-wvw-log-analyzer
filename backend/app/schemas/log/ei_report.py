# -*- coding: utf-8 -*-
"""
EI 报告 API Schema 定义

说明?  EI (_logData + _graphData) 格式 的数据结构极其复杂且版本间可能变化，
  因此本模块采用 顶层结构 + 深层宽松的策略：
  - 顶层字段（如元数据、定义表）使用显?Pydantic 字段
  - 深层嵌套结构（如 player details, phase stats）使?Dict[str, Any] / List[Any]
  这样既保持 API 文档可读性，又避免因 EI 版本变化导致解析失败 """

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =====================================================================
# 基础响应
# =====================================================================
class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    code: int = 200


# =====================================================================
# EI 报告元数据# =====================================================================
class EiReportMeta(BaseModel):
    log_id: int
    report_type: str = "detailed_wvw"
    ei_version: Optional[str] = None
    log_name: Optional[str] = None
    duration_ms: Optional[int] = None
    player_count: Optional[int] = None
    target_count: Optional[int] = None
    success: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_account_by: Optional[str] = None
    map_id: Optional[int] = None
    region: Optional[str] = None
    wvw: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    has_log_data: bool = False
    has_graph_data: bool = False
    has_cr_data: bool = False


# =====================================================================
# EI 摘要数据结构（直接来自 summary_json）
# =====================================================================
class EiSummaryResponse(ApiResponse):
    """EI 报告摘要响应"""

    data: Optional[Dict[str, Any]] = None


# =====================================================================
# 完整数据响应
# =====================================================================
class EiFullDataResponse(ApiResponse):
    """EI 完整 _logData 响应"""

    data: Optional[Dict[str, Any]] = None


class EiGraphDataResponse(ApiResponse):
    """EI 完整 _graphData 响应"""

    data: Optional[Dict[str, Any]] = None


# =====================================================================
# 导入请求/响应
# =====================================================================
class EiImportRequest(BaseModel):
    html_path: str = Field(..., description="EI HTML 文件路径（服务器本地路径）")
    report_type: str = Field("detailed_wvw", description="报告类型")


class EiImportResponse(ApiResponse):
    report_id: Optional[int] = None
    meta: Optional[EiReportMeta] = None


# =====================================================================
# 玩家/目标/阶段详情响应
# =====================================================================
class EiPlayerDetailResponse(ApiResponse):
    """单个玩家完整数据（含 details 字段）"""

    player_index: int = 0
    data: Optional[Dict[str, Any]] = None


class EiTargetDetailResponse(ApiResponse):
    """单个目标完整数据（含 details 字段）"""

    target_index: int = 0
    data: Optional[Dict[str, Any]] = None


class EiPhaseDetailResponse(ApiResponse):
    """单个阶段完整数据（含所有统计数组）"""

    phase_index: int = 0
    data: Optional[Dict[str, Any]] = None


class EiPlayerGraphResponse(ApiResponse):
    """玩家图表数据"""

    player_index: int = 0
    data: Optional[Dict[str, Any]] = None


class EiTargetGraphResponse(ApiResponse):
    """目标图表数据"""

    target_index: int = 0
    data: Optional[Dict[str, Any]] = None


# =====================================================================
# 报告列表
# =====================================================================
class EiReportListItem(BaseModel):
    log_id: int
    log_name: Optional[str] = None
    report_type: str = ""
    ei_version: Optional[str] = None
    duration_ms: Optional[int] = None
    player_count: Optional[int] = None
    target_count: Optional[int] = None
    recorded_by: Optional[str] = None
    created_at: Optional[str] = None


class EiReportListResponse(ApiResponse):
    total: int = 0
    items: List[EiReportListItem] = []
