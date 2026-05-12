# -*- coding: utf-8 -*-
# 模块功能：出勤统计数据验证模型# 作者：系统
# 创建日期?2026-05-12
# 依赖说明：pydantic v2

from typing import Optional

from pydantic import BaseModel, Field


class AccountFilterParams(BaseModel):
    """账号出勤列表过滤参数"""

    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    search: Optional[str] = Field(None, description="搜索账号或角色名")
    server_name: Optional[str] = Field(None, description="服务器筛?)
    map_name: Optional[str] = Field(None, description="地图筛?)
    profession: Optional[str] = Field(None, description="职业筛?)
    sort_by: str = Field("attendance_count", description="排序字段")
    sort_order: str = Field("desc", description="排序方向 (asc/desc)")
