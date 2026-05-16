# -*- coding: utf-8 -*-
# 模块功能：设置管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新日期：2026-05-05 - 持久化层从 app_config.json 迁移到 sys_config 表
# 依赖说明：FastAPI

from app.config.database import get_db
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.schemas.settings.settings import (
    SettingsUpdate,
    build_settings_response,
    build_settings_response_from_defaults,
)
from app.services.auth.auth_service import get_current_admin
from app.services.system.sys_config_service import SysConfigService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/settings", tags=["设置管理"])


@router.get("", response_model=ApiResponse, summary="获取系统设置")
async def get_settings(db: Session = Depends(get_db)):
    """获取系统设置（从 sys_config 表读取）"""
    service = SysConfigService(db)
    settings = service.get_all_settings()
    return ApiResponse.success_response(
        code=200,
        message="获取设置成功",
        data=build_settings_response(settings),
    )


@router.put("", response_model=ApiResponse, summary="更新系统设置")
async def update_settings(
    settings_update: SettingsUpdate,
    current_admin: SysUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """更新系统设置（写入 sys_config 表）"""
    service = SysConfigService(db)
    update_data = settings_update.model_dump(exclude_unset=True)

    if service.update_settings(update_data):
        settings = service.get_all_settings()
        return ApiResponse.success_response(
            message="更新设置成功",
            data=build_settings_response(settings),
        )
    else:
        return ApiResponse.error_response(message="更新设置失败", code=500)


@router.post("/reset", response_model=ApiResponse, summary="重置系统设置")
async def reset_settings(
    current_admin: SysUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """重置为默认设置"""
    from app.services.system.sys_config_service import DEFAULT_CONFIGS

    service = SysConfigService(db)
    defaults = {cfg["config_key"]: cfg["config_value"] for cfg in DEFAULT_CONFIGS}

    if service.update_settings(defaults):
        return ApiResponse.success_response(
            message="重置设置成功",
            data=build_settings_response_from_defaults(defaults),
        )
    else:
        return ApiResponse.error_response(message="重置设置失败", code=500)
