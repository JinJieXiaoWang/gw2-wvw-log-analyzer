# -*- coding: utf-8 -*-
# 模块功能：日志解析API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12

import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.auth.sys_user import SysUser
from app.routers.auth.auth import get_current_admin
from app.schemas.auth.common import ApiResponse
from app.services.zevtc import log_service, parser_service
from app.services.zevtc.file_service import FileService
from app.services.zevtc.parse_progress_service import parse_progress_service
from app.utils.error.exceptions import BadRequestException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.post("/{log_id}/parse", response_model=ApiResponse, summary="解析日志文件")
async def parse_log(
    log_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    overwrite: bool = Query(True, description="是否覆盖已有的解析数据"),
    current_admin: SysUser = Depends(get_current_admin),
):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status == "parsing":
        raise BadRequestException("日志正在解析")

    if not FileService.exists(log.file_path):
        raise NotFoundException(f"日志文件不存在 {log.file_path}")

    log_service.update_parse_status(db, log_id, "parsing")

    parse_progress_service.init_progress(
        log_id, os.path.basename(log.file_path)
    )

    background_tasks.add_task(
        log_service.parse_log_background, log_id, db.bind.url, overwrite, current_admin.id
    )

    return ApiResponse(success=True, message="开始解析", data={"log_id": log_id})


@router.get(
    "/{log_id}/parse/progress", response_model=ApiResponse, summary="获取日志解析进度"
)
async def get_parse_progress(log_id: int, db: Session = Depends(get_db)):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    progress = parse_progress_service.get(
        log_id,
        {
            "stage": "未开始",
            "progress": 0,
            "current_file": "",
            "players_found": 0,
            "events_processed": 0,
            "errors": [],
            "warnings": [],
        },
    )

    return ApiResponse(success=True, message="获取解析进度成功", data=progress)


@router.get(
    "/{log_id}/parse/result", response_model=ApiResponse, summary="获取解析结果"
)
async def get_parse_result(log_id: int, db: Session = Depends(get_db)):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    log_service.validate_parse_status_for_result(log)

    result = log_service.get_parse_result_data(db, log_id)

    return ApiResponse(
        success=True,
        message="获取解析结果成功",
        data={
            "log_id": log_id,
            "parse_status": log.parse_status,
            "parse_time": log.parsed_at.isoformat() if log.parsed_at else None,
            "fight_id": result["fight_id"],
            "player_count": result["stats_count"],
            "map_name": result["map_name"],
            "duration_sec": result["duration_sec"],
        },
    )


@router.post("/{log_id}/validate", response_model=ApiResponse, summary="验证解析数据")
async def validate_parsed_data(log_id: int, db: Session = Depends(get_db)):
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status != "completed":
        raise BadRequestException(f"日志未完成解析，当前状态 {log.parse_status}")

    parser = parser_service.LogParser()
    if FileService.exists(log.file_path):
        try:
            parser.parse_file(log.file_path)
            validation = parser.validate_data()
            return ApiResponse(
                success=validation.get("passed", False),
                message="数据验证完成",
                data=validation,
            )
        except Exception as e:
            logger.error(f"数据验证失败: {e}")

    return ApiResponse(success=False, message="无法验证数据", data=None)
