# -*- coding: utf-8 -*-
"""
数据初始化管理 API

功能：
- 手动触发数据初始化（超级管理员权限）
- 查询初始化状态和版本信息
- 强制重新初始化

作者：帅妹妹丶.8297
创建日期：2026-05-15
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.initialization import DataVersionManager, InitializationError, RetryConfig
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.services.auth.auth_service import require_super_admin
from app.services.system.initialization_service import InitializationService
from app.utils.logger import logger

router = APIRouter(prefix="/initialization", tags=["数据初始化管理"])


@router.post("/run", response_model=ApiResponse, summary="手动触发数据初始化")
async def run_initialization(
    force: bool = Query(False, description="强制重新初始化（忽略版本记录）"),
    max_attempts: int = Query(5, ge=1, le=20, description="最大重试次数"),
    admin: SysUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    手动触发种子数据初始化（应急方案入口）

    需要超级管理员权限。
    如果初始化失败，返回详细的错误诊断信息。
    """
    logger.info(f"[API] 管理员 {admin.username} 手动触发数据初始化, force={force}")

    try:
        retry_config = RetryConfig(max_attempts=max_attempts)
        service = InitializationService(db, retry_config=retry_config, force=force)
        summary = service.run()
        return ApiResponse.success_response(
            data=summary,
            message="数据初始化成功",
        )
    except InitializationError as e:
        logger.error(f"[API] 手动初始化失败: {e}")
        return ApiResponse.error_response(
            message=str(e),
            code=500,
            data={
                "step": e.step,
                "error_type": e.error_type,
                "suggestion": e.suggestion,
                "timestamp": e.timestamp,
            },
        )
    except Exception as e:
        logger.error(f"[API] 手动初始化发生未预料错误: {e}", exc_info=True)
        return ApiResponse.error_response(
            message=f"初始化失败: {str(e)}",
            code=500,
        )


@router.get("/status", response_model=ApiResponse, summary="查询初始化状态")
async def get_initialization_status(
    admin: SysUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    查询当前数据版本和初始化状态
    """
    try:
        version_manager = DataVersionManager(db)
        applied = version_manager.get_applied_version()
        should_apply, reason = version_manager.check_version(force=False)

        return ApiResponse.success_response(
            data={
                "current_version": DataVersionManager.CURRENT_VERSION,
                "applied_version": applied,
                "needs_initialization": should_apply,
                "reason": reason,
            },
            message="获取初始化状态成功",
        )
    except Exception as e:
        logger.error(f"[API] 查询初始化状态失败: {e}")
        return ApiResponse.error_response(message=f"查询失败: {str(e)}", code=500)


@router.post("/clear-version", response_model=ApiResponse, summary="清除版本记录")
async def clear_version_record(
    admin: SysUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    清除数据版本记录（下次启动将重新初始化）

    ⚠️ 危险操作：仅用于数据修复场景
    """
    try:
        version_manager = DataVersionManager(db)
        version_manager.clear_version()
        return ApiResponse.success_response(
            data={"version": DataVersionManager.CURRENT_VERSION},
            message="版本记录已清除，下次启动将重新初始化",
        )
    except Exception as e:
        logger.error(f"[API] 清除版本记录失败: {e}")
        return ApiResponse.error_response(message=f"清除失败: {str(e)}", code=500)
