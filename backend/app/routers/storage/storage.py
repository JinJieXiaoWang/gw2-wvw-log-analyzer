# 模块功能：存储管理API路由
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：FastAPI, SQLAlchemy

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.auth.sys_user import SysUser
from app.routers.auth.auth import get_current_admin
from app.schemas.auth.common import ApiResponse
from app.services.system.storage_service import FileCleanupService, StorageMonitorService
from app.utils.logger import logger

router = APIRouter(prefix="/storage", tags=["存储管理"])


def _monitor_record_to_dict(record):
    return {
        "id": record.id,
        "record_time": record.record_time.isoformat() if record.record_time else None,
        "total_size": record.total_size,
        "file_count": record.file_count,
        "log_file_count": record.log_file_count,
        "warning_triggered": record.warning_triggered,
    }


def _cleanup_record_to_dict(record):
    return {
        "id": record.id,
        "cleanup_type": record.cleanup_type,
        "start_time": record.start_time.isoformat() if record.start_time else None,
        "end_time": record.end_time.isoformat() if record.end_time else None,
        "files_deleted": record.files_deleted,
        "space_freed": record.space_freed,
        "status": record.status,
        "triggered_by": record.triggered_by,
        "error_message": record.error_message,
    }


@router.get("/status", response_model=ApiResponse, summary="获取存储状态")
async def get_storage_status(
    db: Session = Depends(get_db), current_admin: SysUser = Depends(get_current_admin)
):
    status = StorageMonitorService.get_storage_status(db)
    return ApiResponse.success_response(
        data=status, message="获取存储状态成功", code=HTTP_200_OK
    )


@router.get("/monitor/records", response_model=ApiResponse, summary="获取监控记录")
async def get_monitor_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    skip = (page - 1) * page_size
    records, total = StorageMonitorService.get_monitor_records(
        db, skip=skip, limit=page_size
    )

    return ApiResponse.success_response(
        data={
            "items": [_monitor_record_to_dict(r) for r in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取监控记录成功",
        code=HTTP_200_OK,
    )


@router.get("/cleanup/records", response_model=ApiResponse, summary="获取清理记录")
async def get_cleanup_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    skip = (page - 1) * page_size
    records, total = FileCleanupService.get_cleanup_records(
        db, skip=skip, limit=page_size
    )

    return ApiResponse.success_response(
        data={
            "items": [_cleanup_record_to_dict(r) for r in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取清理记录成功",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/age", response_model=ApiResponse, summary="按保留天数清理")
async def cleanup_by_age(
    days: Optional[int] = Query(None, ge=1, description="保留天数，默认使用配置值"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    result = FileCleanupService.cleanup_by_age(
        db, days=days, triggered_by=f"admin_{current_admin.id}"
    )
    return ApiResponse.success_response(
        data=result,
        message="清理任务执行完成" if result.get("success") else "清理任务执行失败",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/storage", response_model=ApiResponse, summary="按存储容量清理")
async def cleanup_by_storage(
    max_size_gb: Optional[float] = Query(
        None, ge=0.1, description="最大存储容量GB，默认使用配置值"
    ),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    max_size = None
    if max_size_gb:
        max_size = int(max_size_gb * 1024 * 1024 * 1024)

    result = FileCleanupService.cleanup_by_storage_limit(
        db, max_size=max_size, triggered_by=f"admin_{current_admin.id}"
    )
    return ApiResponse.success_response(
        data=result,
        message="清理任务执行完成" if result.get("success") else "清理任务执行失败",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/parsed", response_model=ApiResponse, summary="清理已解析文件")
async def cleanup_parsed_files(
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    result = FileCleanupService.cleanup_parsed_files(
        db, triggered_by=f"admin_{current_admin.id}"
    )
    return ApiResponse.success_response(
        data=result,
        message="清理任务执行完成" if result.get("success") else "清理任务执行失败",
        code=HTTP_200_OK,
    )


@router.post("/monitor/record", response_model=ApiResponse, summary="手动记录监控数据")
async def record_monitor_data(
    db: Session = Depends(get_db), current_admin: SysUser = Depends(get_current_admin)
):
    record = StorageMonitorService.record_monitor_data(db)
    return ApiResponse.success_response(
        data={
            "record_id": record.id,
            "record_time": (
                record.record_time.isoformat() if record.record_time else None
            ),
        },
        message="监控数据已记录",
        code=HTTP_200_OK,
    )
