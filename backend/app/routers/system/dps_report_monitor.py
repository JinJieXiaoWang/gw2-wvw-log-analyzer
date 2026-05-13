# -*- coding: utf-8 -*-
# 模块功能：dps.report 队列监控 API
# 说明：提供 dps.report API 请求队列的实时状态和统计信息

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.routers.auth.auth import get_current_admin
from app.schemas.auth.common import ApiResponse
from app.services.system.dps_report_queue import dps_report_queue
from app.services.system.dps_report_service import DpsReportError
from app.utils.logger import logger

router = APIRouter(prefix="/dps-report-queue", tags=["dps.report 队列监控"])


@router.get("", response_model=ApiResponse, summary="获取 dps.report 请求队列状态")
async def get_dps_report_queue_status(
    current_admin=Depends(get_current_admin),
):
    """获取 dps.report API 请求队列的实时统计信息。

    返回字段：
        - queue_size: 等待队列长度
        - is_busy: 当前是否有请求在处理中
        - current_task: 当前正在处理的任务描述
        - current_elapsed_sec: 当前任务已执行秒数
        - submitted: 历史提交总数
        - completed: 历史完成总数
        - failed: 历史失败总数
    """
    try:
        stats = dps_report_queue.get_stats()
        return ApiResponse(
            success=True,
            message="获取队列状态成功",
            data=stats,
        )
    except Exception as e:
        logger.error(f"获取 dps.report 队列状态失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"获取队列状态失败: {e}")
