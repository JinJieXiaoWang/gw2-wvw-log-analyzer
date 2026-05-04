# -*- coding: utf-8 -*-
# 模块功能：设置管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.services.auth_service import get_current_admin
from app.utils.logger import logger

router = APIRouter(prefix="/settings", tags=["设置管理"])

SETTINGS_FILE = "./app_config.json"


# Pydantic模型
class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    default_server: Optional[str] = None
    parse_parallel: Optional[int] = None
    export_format: Optional[str] = None
    auto_backup: Optional[bool] = None
    retention_days: Optional[int] = None


class SettingsResponse(BaseModel):
    theme: str
    default_server: str
    parse_parallel: int
    export_format: str
    auto_backup: bool
    retention_days: int
    updated_at: str


# 默认设置
DEFAULT_SETTINGS = {
    "theme": "light",
    "default_server": "Tarnished Coast",
    "parse_parallel": 1,
    "export_format": "json",
    "auto_backup": True,
    "retention_days": 365,
}


def load_settings() -> Dict[str, Any]:
    # 功能：加载设置
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            result = DEFAULT_SETTINGS.copy()
            result.update(settings)
            return result
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]):
    # 功能：保存设置
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存设置失败: {e}")
        return False


@router.get("", response_model=ApiResponse, summary="获取系统设置")
async def get_settings():
    # 功能：获取系统设置
    settings = load_settings()
    return ApiResponse.success_response(
        code=200,
        message="获取设置成功",
        data={
            "theme": settings["theme"],
            "default_server": settings["default_server"],
            "parse_parallel": settings["parse_parallel"],
            "export_format": settings["export_format"],
            "auto_backup": settings["auto_backup"],
            "retention_days": settings["retention_days"],
            "updated_at": datetime.now().isoformat(),
        },
    )


@router.put("", response_model=ApiResponse, summary="更新系统设置")
async def update_settings(
    settings_update: SettingsUpdate,
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：更新系统设置
    settings = load_settings()

    update_data = settings_update.model_dump(exclude_unset=True)
    settings.update(update_data)

    if save_settings(settings):
        return ApiResponse.success_response(
            message="更新设置成功",
            data={
                "theme": settings["theme"],
                "default_server": settings["default_server"],
                "parse_parallel": settings["parse_parallel"],
                "export_format": settings["export_format"],
                "auto_backup": settings["auto_backup"],
                "retention_days": settings["retention_days"],
                "updated_at": datetime.now().isoformat(),
            },
        )
    else:
        return ApiResponse.error_response(message="更新设置失败", code=500)


@router.post("/reset", response_model=ApiResponse, summary="重置系统设置")
async def reset_settings(current_admin: SysUser = Depends(get_current_admin)):
    # 功能：重置为默认设置
    if save_settings(DEFAULT_SETTINGS):
        return ApiResponse.success_response(
            message="重置设置成功",
            data={
                "theme": DEFAULT_SETTINGS["theme"],
                "default_server": DEFAULT_SETTINGS["default_server"],
                "parse_parallel": DEFAULT_SETTINGS["parse_parallel"],
                "export_format": DEFAULT_SETTINGS["export_format"],
                "auto_backup": DEFAULT_SETTINGS["auto_backup"],
                "retention_days": DEFAULT_SETTINGS["retention_days"],
                "updated_at": datetime.now().isoformat(),
            },
        )
    else:
        return ApiResponse.error_response(message="重置设置失败", code=500)
