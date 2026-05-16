# -*- coding: utf-8 -*-
# 模块功能：日志导出API路由
# 作者：系统
# 创建日期?2026-05-12

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.services.zevtc import log_service

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("/export", summary="导出日志数据")
async def export_logs(
    log_ids: Optional[list[int]] = Query(
        None, description="要导出的日志ID列表，不填则导出所?"
    ),
    format: str = Query("json", description="导出格式: json/csv"),
    db: Session = Depends(get_db),
):
    export_data = log_service.get_logs_export_data(db, log_ids=log_ids)

    if format == "csv":
        content = log_service.build_logs_csv(export_data)
        return PlainTextResponse(
            content=content,
            headers={"Content-Disposition": "attachment; filename=logs.csv"},
            media_type="text/csv",
        )

    return ApiResponse(success=True, message="导出成功", data=export_data)
