# -*- coding: utf-8 -*-
"""
公共配置接口
提供前端应用启动时所需的非敏感公共配置参数据
所有业务配置以后端 Settings 为唯一真相源?
"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.auth.common import ApiResponse

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/public")
def get_public_config():
    """
    获取公共配置（非敏感?

    返回前端应用需要的共享业务配置，确保前后端配置一致性?
    敏感信息（密钥、密码等）不会在此接口中暴露?
    """
    settings = get_settings()
    return ApiResponse.success_response(
        data={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "api_prefix": settings.API_PREFIX,
            "max_upload_size": settings.MAX_UPLOAD_SIZE,
            "ai_enabled": settings.AI_ENABLED,
            "file_retention_days": settings.FILE_RETENTION_DAYS,
            "supported_formats": settings.SUPPORTED_UPLOAD_FORMATS or [".zevtc", ".evtc"],
            "theme_default": settings.DEFAULT_THEME or "dark",
        }
    )
