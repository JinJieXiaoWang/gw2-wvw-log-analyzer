# -*- coding: utf-8 -*-
# 模块功能：日志管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新日期：2026-05-12

import asyncio
import hashlib
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Query,
    Request,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.auth.sys_user import SysUser
from app.routers.auth.auth import get_current_admin
from app.schemas.auth.common import ApiResponse
from app.schemas.log.log import LogResponse, LogUpdate
from app.services.zevtc import log_service
from app.services.zevtc.cache_service import get_ei_json_by_sha256
from app.services.zevtc.file_service import FileService
from app.services.zevtc.log_import_service import LogImportService
from app.services.zevtc.parse_progress_service import parse_progress_service
from app.utils.error.exceptions import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/logs", tags=["日志管理"])

# 挂载批量解析子路由
from .batch_parse import router as batch_parse_router
router.include_router(batch_parse_router)
_upload_semaphore = asyncio.Semaphore(2)

@router.get("", response_model=ApiResponse, summary="获取日志列表")
async def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    parse_status: Optional[str] = Query(None, description="解析状态"),
    search: Optional[str] = Query(None, description="文件名搜索"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    logs, total = log_service.get_logs(
        db, skip=skip, limit=page_size, parse_status=parse_status, search=search
    )
    return ApiResponse.success_response(
        data={
            "items": [LogResponse.model_validate(log) for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取日志列表成功",
        code=HTTP_200_OK,
    )

@router.get("/{log_id}", response_model=ApiResponse, summary="获取日志详情")
async def get_log(log_id: int, db: Session = Depends(get_db)):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")
    return ApiResponse(success=True, message="获取日志成功", data=LogResponse.model_validate(log))

@router.post("", response_model=ApiResponse, summary="上传日志文件")
async def upload_log(
    file: UploadFile = File(...),
    auto_parse: bool = Query(False, description="是否自动解析"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request: Request = None,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    if not file.filename.endswith(".zevtc"):
        raise BadRequestException("只支持 .zevtc 格式的文件")

    async with _upload_semaphore:
        file_path, content = await FileService.save_upload(file)

    file_sha256 = hashlib.sha256(content).hexdigest()

    existing_log = log_service.handle_upload_duplicate(
        db, file_sha256, file.filename, file_path
    )
    if existing_log:
        return ApiResponse(
            success=True,
            message="文件已存在，无需重复上传",
            data=LogResponse.model_validate(existing_log),
        )

    file_size_raw = len(content)

    upload_ip = None
    if request:
        upload_ip = request.headers.get(
            "x-forwarded-for", request.client.host if request.client else None
        )

    log = log_service.create_log(
        db=db,
        log_data={
            "log_uuid": str(uuid.uuid4()),
            "filename": file.filename,
            "file_sha256": file_sha256,
            "file_size_compressed": len(content),
            "file_size_raw": file_size_raw,
            "file_path": file_path,
            "upload_ip": upload_ip,
        },
    )

    if auto_parse:
        background_tasks.add_task(
            log_service.parse_log_background, log.id, db.bind.url, True
        )
        logger.info(f"上传日志成功并自动触发解析，日志ID: {log.id}")
        return ApiResponse(
            success=True,
            message="上传日志成功，已自动开始解析",
            data=LogResponse.model_validate(log),
        )

    logger.info(f"上传日志成功，日志ID: {log.id}")
    return ApiResponse(success=True, message="上传日志成功", data=LogResponse.model_validate(log))

@router.delete("/{log_id}", response_model=ApiResponse, summary="删除日志")
async def delete_log(
    log_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)
):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        logger.warning(f"删除失败：日志ID {log_id} 不存在")
        raise NotFoundException(f"日志ID {log_id} 不存在")

    logger.info(f"用户 {current_admin.username} 请求删除日志: {log.filename}")

    try:
        log_service.delete_log_entry(db, log_id)
        parse_progress_service.clear_progress(log_id)

        logger.info(f"日志删除成功: {log.filename}")
        return ApiResponse(success=True, message="删除日志成功")
    except Exception as e:
        logger.error(f"删除日志异常: {str(e)}", exc_info=True)
        raise InternalServerErrorException(f"删除日志失败: {str(e)}")

@router.put("/{log_id}", response_model=ApiResponse, summary="更新日志")
async def update_log(
    log_id: int,
    log_update: LogUpdate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    log = log_service.update_log(db, log_id, log_update)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")
    return ApiResponse(success=True, message="更新日志成功", data=LogResponse.model_validate(log))


@router.post("/{log_id}/parse", response_model=ApiResponse, summary="解析日志")
async def parse_log(
    log_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status == "parsing":
        raise BadRequestException("日志正在解析中，请稍后")

    if not log.file_path or not log.file_path.endswith(".zevtc"):
        raise BadRequestException("日志文件无效或不存在")

    logger.info(f"用户 {current_admin.username} 请求解析日志: {log.filename}")

    try:
        # 更新状态为解析中
        log_service.update_parse_status(db, log_id, "parsing")

        # 提交后台解析任务，接口立即返回
        background_tasks.add_task(
            log_service.parse_log_background,
            log_id,
            str(db.bind.url),
            True,
        )

        return ApiResponse(
            success=True,
            message="解析任务已提交",
            data=LogResponse.model_validate(log),
        )

    except Exception as e:
        logger.error(f"提交解析任务异常: {str(e)}", exc_info=True)
        log_service.update_parse_status(db, log_id, "failed", str(e))
        raise InternalServerErrorException(f"提交解析任务失败: {str(e)}")


@router.post("/check-sha256", response_model=ApiResponse, summary="SHA256 预检（检查缓存与重复）")
async def check_sha256(
    sha256: str,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    """上传前预检：通过 SHA256 检查文件是否已上传且是否有 EI JSON 缓存。"""
    from app.models.log.log import Log

    log = db.query(Log).filter(Log.file_sha256 == sha256).first()
    if not log:
        return ApiResponse(success=True, message="未找到记录", data={"exists": False})

    # 检查是否有有效的 EI JSON 缓存
    has_cache = bool(log.ei_json_cache and log.ei_json_cached_at)
    data = {
        "exists": True,
        "log_id": log.id,
        "parse_status": log.parse_status,
        "dps_report_permalink": log.dps_report_permalink,
        "has_ei_json_cache": has_cache,
        "ei_json_cached_at": log.ei_json_cached_at.isoformat() if log.ei_json_cached_at else None,
    }
    return ApiResponse(success=True, message="找到已有记录", data=data)


@router.post("/batch-delete", response_model=ApiResponse, summary="批量删除日志")
async def batch_delete_logs(
    log_ids: list[int],
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    result = log_service.batch_delete_logs(db, log_ids, user_id=current_admin.id)

    return ApiResponse(
        success=True,
        message=f"批量删除完成: 删除 {result['deleted_count']} 个，失败 {len(result['failed_ids'])} 个",
        data=result,
    )
