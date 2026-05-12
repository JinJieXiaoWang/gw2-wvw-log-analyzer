# 模块功能：批量解析任务数据验证模型# 作者：系统
# 创建日期：2026-04-29
# 依赖说明：pydantic v2

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BatchParseTaskCreate(BaseModel):
    # 功能：批量解析任务创建模型    task_name: Optional[str] = None
    log_ids: List[int] = Field(..., description="需要解析的日志ID列表")
    overwrite: bool = Field(True, description="是否覆盖已有的解析数据，默认为True")


class BatchParseTaskUpdate(BaseModel):
    # 功能：批量解析任务更新模型    task_name: Optional[str] = None
    status: Optional[str] = None


class BatchParseTaskItemResponse(BaseModel):
    # 功能：批量解析任务项响应模型
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    log_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class BatchParseTaskResponse(BaseModel):
    # 功能：批量解析任务响应模型    model_config = ConfigDict(from_attributes=True)

    id: int
    task_name: Optional[str] = None
    status: str
    total_count: int
    processed_count: int
    success_count: int
    failed_count: int
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None
    error_message: Optional[str] = None
    log_ids: Optional[List[int]] = None


class BatchParseTaskDetailResponse(BatchParseTaskResponse):
    # 功能：批量解析任务详情响应模型    items: List[BatchParseTaskItemResponse] = []


class BatchParseTaskListResponse(BaseModel):
    # 功能：批量解析任务列表响应模型    model_config = ConfigDict(from_attributes=True)

    items: List[BatchParseTaskResponse]
    total: int
    page: int
    page_size: int


class BatchParseProgressResponse(BaseModel):
    # 功能：批量解析进度响应模型    model_config = ConfigDict(from_attributes=True)

    task_id: int
    status: str
    total_count: int
    processed_count: int
    success_count: int
    failed_count: int
    progress_percent: float
    current_log_id: Optional[int] = None
    elapsed_seconds: Optional[float] = None
    estimated_remaining_seconds: Optional[float] = None
    items: List[Dict[str, Any]] = []


class BatchParseResultResponse(BaseModel):
    # 功能：批量解析结果响应模型    model_config = ConfigDict(from_attributes=True)

    task_id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
    success_log_ids: List[int] = []
    failed_log_ids: List[int] = []
    error_details: Dict[int, str] = {}
