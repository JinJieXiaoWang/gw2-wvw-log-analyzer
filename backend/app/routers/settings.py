# -*- coding: utf-8 -*-
# 模块功能：设置管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新日期：2026-05-05 - 持久化层从 app_config.json 迁移到 sys_config 表
# 依赖说明：FastAPI

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.services.auth_service import get_current_admin
from app.services.sys_config_service import SysConfigService

router = APIRouter(prefix="/settings", tags=["设置管理"])


# Pydantic模型
class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    default_server: Optional[str] = None
    parse_parallel: Optional[int] = None
    export_format: Optional[str] = None
    auto_backup: Optional[bool] = None
    retention_days: Optional[int] = None
    watermark_enabled: Optional[bool] = None
    watermark_text: Optional[str] = None
    watermark_screenshot_enabled: Optional[bool] = None


class SettingsResponse(BaseModel):
    theme: str
    default_server: str
    parse_parallel: int
    export_format: str
    auto_backup: bool
    retention_days: int
    watermark_enabled: bool
    watermark_text: str
    watermark_screenshot_enabled: bool
    updated_at: str


@router.get("", response_model=ApiResponse, summary="获取系统设置")
async def get_settings(db: Session = Depends(get_db)):
    """获取系统设置（从 sys_config 表读取）"""
    service = SysConfigService(db)
    settings = service.get_all_settings()

    return ApiResponse.success_response(
        code=200,
        message="获取设置成功",
        data={
            "theme": settings.get("theme", "light"),
            "default_server": settings.get("default_server", "Tarnished Coast"),
            "parse_parallel": settings.get("parse_parallel", 1),
            "export_format": settings.get("export_format", "json"),
            "auto_backup": settings.get("auto_backup", True),
            "retention_days": settings.get("retention_days", 365),
            "watermark_enabled": settings.get("watermark_enabled", False),
            "watermark_text": settings.get("watermark_text", ""),
            "watermark_screenshot_enabled": settings.get("watermark_screenshot_enabled", True),
            "updated_at": datetime.now().isoformat(),
        },
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
            data={
                "theme": settings.get("theme", "light"),
                "default_server": settings.get("default_server", "Tarnished Coast"),
                "parse_parallel": settings.get("parse_parallel", 1),
                "export_format": settings.get("export_format", "json"),
                "auto_backup": settings.get("auto_backup", True),
                "retention_days": settings.get("retention_days", 365),
                "watermark_enabled": settings.get("watermark_enabled", False),
                "watermark_text": settings.get("watermark_text", ""),
                "watermark_screenshot_enabled": settings.get("watermark_screenshot_enabled", True),
                "updated_at": datetime.now().isoformat(),
            },
        )
    else:
        return ApiResponse.error_response(message="更新设置失败", code=500)


@router.post("/reset", response_model=ApiResponse, summary="重置系统设置")
async def reset_settings(
    current_admin: SysUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """重置为默认设置"""
    from app.services.sys_config_service import DEFAULT_CONFIGS

    service = SysConfigService(db)
    defaults = {cfg["config_key"]: cfg["config_value"] for cfg in DEFAULT_CONFIGS}

    if service.update_settings(defaults):
        return ApiResponse.success_response(
            message="重置设置成功",
            data={
                "theme": defaults.get("theme", "light"),
                "default_server": defaults.get("default_server", "Tarnished Coast"),
                "parse_parallel": int(defaults.get("parse_parallel", 1)),
                "export_format": defaults.get("export_format", "json"),
                "auto_backup": defaults.get("auto_backup", "true").lower() == "true",
                "retention_days": int(defaults.get("retention_days", 365)),
                "watermark_enabled": defaults.get("watermark_enabled", "false").lower() == "true",
                "watermark_text": defaults.get("watermark_text", ""),
                "watermark_screenshot_enabled": defaults.get("watermark_screenshot_enabled", "true").lower() == "true",
                "updated_at": datetime.now().isoformat(),
            },
        )
    else:
        return ApiResponse.error_response(message="重置设置失败", code=500)
