# 模块功能：存储管理API路由
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：FastAPI, SQLAlchemy

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.sys_user import SysUser
from app.routers.auth import get_current_admin
from app.schemas.common import ApiResponse
from app.services.system.storage_service import (
    FileCleanupService,
    StorageMonitorService,
)
from app.utils.logger import logger

router = APIRouter(prefix="/storage", tags=["存储管理"])


@router.get("/status", response_model=ApiResponse, summary="获取存储状态")
async def get_storage_status(
    db: Session = Depends(get_db), current_admin: SysUser = Depends(get_current_admin)
):
    # 功能：获取当前存储状态
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
    # 功能：获取存储监控记录
    skip = (page - 1) * page_size
    records, total = StorageMonitorService.get_monitor_records(
        db, skip=skip, limit=page_size
    )

    return ApiResponse.success_response(
        data={
            "items": [
                {
                    "id": r.id,
                    "record_time": r.record_time.isoformat() if r.record_time else None,
                    "total_size_bytes": r.total_size,
                    "total_size_gb": round(r.total_size / (1024 * 1024 * 1024), 2),
                    "file_count": r.file_count,
                    "log_file_count": r.log_file_count,
                    "warning_triggered": r.warning_triggered,
                }
                for r in records
            ],
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
    # 功能：获取清理记录
    skip = (page - 1) * page_size
    records, total = FileCleanupService.get_cleanup_records(
        db, skip=skip, limit=page_size
    )

    return ApiResponse.success_response(
        data={
            "items": [
                {
                    "id": r.id,
                    "cleanup_type": r.cleanup_type,
                    "start_time": r.start_time.isoformat() if r.start_time else None,
                    "end_time": r.end_time.isoformat() if r.end_time else None,
                    "files_deleted": r.files_deleted,
                    "space_freed_bytes": r.space_freed,
                    "space_freed_gb": (
                        round(r.space_freed / (1024 * 1024 * 1024), 2)
                        if r.space_freed
                        else 0
                    ),
                    "status": r.status,
                    "error_message": r.error_message,
                    "triggered_by": r.triggered_by,
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取清理记录成功",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/age", response_model=ApiResponse, summary="按保留天数清理")
async def cleanup_by_age(
    background_tasks: BackgroundTasks,
    days: Optional[int] = Query(None, ge=1, description="保留天数，默认使用配置值"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：按文件保留天数执行清理（后台任务）
    def run_cleanup():
        from app.config.database import SessionLocal

        db_session = SessionLocal()
        try:
            result = FileCleanupService.cleanup_by_age(
                db_session, days=days, triggered_by=f"admin_{current_admin.id}"
            )
            logger.info(f"按天数清理执行完成: {result}")
        finally:
            db_session.close()

    background_tasks.add_task(run_cleanup)

    return ApiResponse.success_response(
        data={"message": "清理任务已提交后台执行"},
        message="清理任务已提交",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/storage", response_model=ApiResponse, summary="按存储容量清理")
async def cleanup_by_storage(
    background_tasks: BackgroundTasks,
    max_size_gb: Optional[float] = Query(
        None, ge=0.1, description="最大存储容量GB，默认使用配置值"
    ),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：按存储容量限制执行清理（后台任务）
    max_size = None
    if max_size_gb:
        max_size = int(max_size_gb * 1024 * 1024 * 1024)

    def run_cleanup():
        from app.config.database import SessionLocal

        db_session = SessionLocal()
        try:
            result = FileCleanupService.cleanup_by_storage_limit(
                db_session, max_size=max_size, triggered_by=f"admin_{current_admin.id}"
            )
            logger.info(f"按容量清理执行完成: {result}")
        finally:
            db_session.close()

    background_tasks.add_task(run_cleanup)

    return ApiResponse.success_response(
        data={"message": "清理任务已提交后台执行"},
        message="清理任务已提交",
        code=HTTP_200_OK,
    )


@router.post("/cleanup/parsed", response_model=ApiResponse, summary="清理已解析文件")
async def cleanup_parsed_files(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：清理已解析日志的原始文件（保留数据库数据）
    def run_cleanup():
        from app.config.database import SessionLocal

        db_session = SessionLocal()
        try:
            result = FileCleanupService.cleanup_parsed_files(
                db_session, triggered_by=f"admin_{current_admin.id}"
            )
            logger.info(f"已解析文件清理执行完成: {result}")
        finally:
            db_session.close()

    background_tasks.add_task(run_cleanup)

    return ApiResponse.success_response(
        data={"message": "清理任务已提交后台执行"},
        message="清理任务已提交",
        code=HTTP_200_OK,
    )


@router.post("/monitor/record", response_model=ApiResponse, summary="手动记录监控数据")
async def record_monitor_data(
    db: Session = Depends(get_db), current_admin: SysUser = Depends(get_current_admin)
):
    # 功能：手动触发监控数据记录
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
