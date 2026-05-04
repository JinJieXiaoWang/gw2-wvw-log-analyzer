# -*- coding: utf-8 -*-
"""
系统监控API
提供错误统计、性能监控等功能
"""

from fastapi import APIRouter, Depends

from app.config.database import get_db
from app.models.sys_user import SysUser
from app.routers.auth import get_current_admin
from app.schemas.common import ApiResponse
from app.utils.error_monitor import (
    ErrorMonitor,
    export_errors_to_file,
    get_error_report,
)
from app.utils.logger import logger

router = APIRouter(prefix="/monitor", tags=["系统监控"])


@router.get("/errors/stats", response_model=ApiResponse, summary="获取错误统计")
async def get_error_stats(current_admin: SysUser = Depends(get_current_admin)):
    """获取系统错误统计信息"""
    try:
        stats = ErrorMonitor.get_error_stats()
        return ApiResponse(success=True, message="获取错误统计成功", data=stats)
    except Exception as e:
        logger.error(f"获取错误统计失败: {e}")
        raise


@router.get("/errors/report", response_model=ApiResponse, summary="获取完整错误报告")
async def get_error_report_api(current_admin: SysUser = Depends(get_current_admin)):
    """获取详细的错误报告"""
    try:
        report = get_error_report()
        return ApiResponse(success=True, message="获取错误报告成功", data=report)
    except Exception as e:
        logger.error(f"获取错误报告失败: {e}")
        raise


@router.post("/errors/clear", response_model=ApiResponse, summary="清空错误统计")
async def clear_error_stats(current_admin: SysUser = Depends(get_current_admin)):
    """清空所有错误统计"""
    try:
        ErrorMonitor.clear_stats()
        logger.info(f"管理员 {current_admin.username} 清空了错误统计")
        return ApiResponse(success=True, message="错误统计已清空")
    except Exception as e:
        logger.error(f"清空错误统计失败: {e}")
        raise


@router.post("/errors/export", response_model=ApiResponse, summary="导出错误")
async def export_errors(
    limit: int = 100, current_admin: SysUser = Depends(get_current_admin)
):
    """导出错误到文件"""
    try:
        import os
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"errors_export_{timestamp}.json"
        filepath = os.path.join(os.getcwd(), filename)

        success = export_errors_to_file(filepath, limit)

        if success:
            logger.info(f"管理员 {current_admin.username} 导出了错误记录")
            return ApiResponse(
                success=True,
                message="错误导出成功",
                data={"file": filename, "file_path": filepath, "errors_count": limit},
            )
        else:
            return ApiResponse(success=False, message="错误导出失败")
    except Exception as e:
        logger.error(f"导出错误失败: {e}")
        raise


@router.get("/health", response_model=ApiResponse, summary="健康检查")
async def health_check():
    """简单的健康检查端点"""
    return ApiResponse(
        success=True,
        message="系统运行正常",
        data={"status": "healthy", "timestamp": "current"},
    )
