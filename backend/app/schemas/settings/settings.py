from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    """设置更新请求"""
    theme: Optional[str] = None
    default_server: Optional[str] = None
    parse_parallel: Optional[int] = None
    export_format: Optional[str] = None
    auto_backup: Optional[bool] = None
    retention_days: Optional[int] = None
    scoring_mode: Optional[str] = None
    watermark_enabled: Optional[bool] = None
    watermark_text: Optional[str] = None
    watermark_screenshot_enabled: Optional[bool] = None
    upload_max_file_size: Optional[int] = None
    upload_allowed_extensions: Optional[str] = None
    analysis_max_fight_duration: Optional[int] = None
    cache_menu_ttl: Optional[int] = None
    auto_cleanup_enabled: Optional[bool] = None
    auto_cleanup_retention_days: Optional[int] = None


class SettingsResponse(BaseModel):
    """设置响应"""
    theme: str
    default_server: str
    parse_parallel: int
    export_format: str
    auto_backup: bool
    retention_days: int
    scoring_mode: str
    watermark_enabled: bool
    watermark_text: str
    watermark_screenshot_enabled: bool
    upload_max_file_size: int
    upload_allowed_extensions: str
    analysis_max_fight_duration: int
    cache_menu_ttl: int
    auto_cleanup_enabled: bool
    auto_cleanup_retention_days: int
    updated_at: str


# 默认设置常量（集中管理，避免在路由层重复硬编码）
DEFAULT_SETTINGS = {
    "theme": "light",
    "default_server": "Tarnished Coast",
    "parse_parallel": 1,
    "export_format": "json",
    "auto_backup": True,
    "retention_days": 365,
    "scoring_mode": "role_based",
    "watermark_enabled": False,
    "watermark_text": "",
    "watermark_screenshot_enabled": True,
    "upload_max_file_size": 50,
    "upload_allowed_extensions": '[".zevtc", ".evtc"]',
    "analysis_max_fight_duration": 3600,
    "cache_menu_ttl": 3600,
    "auto_cleanup_enabled": True,
    "auto_cleanup_retention_days": 30,
}


def build_settings_response(settings: Dict[str, Any]) -> Dict[str, Any]:
    """将原始设置字典构建为标准化响应字?""
    defaults = DEFAULT_SETTINGS.copy()
    defaults.update(settings)
    return {
        "theme": defaults.get("theme", "light"),
        "default_server": defaults.get("default_server", "Tarnished Coast"),
        "parse_parallel": int(defaults.get("parse_parallel", 1)),
        "export_format": defaults.get("export_format", "json"),
        "auto_backup": defaults.get("auto_backup", True),
        "retention_days": int(defaults.get("retention_days", 365)),
        "scoring_mode": defaults.get("scoring_mode", "role_based"),
        "watermark_enabled": defaults.get("watermark_enabled", False),
        "watermark_text": defaults.get("watermark_text", ""),
        "watermark_screenshot_enabled": defaults.get("watermark_screenshot_enabled", True),
        "upload_max_file_size": int(defaults.get("upload.max_file_size", 50)),
        "upload_allowed_extensions": defaults.get("upload.allowed_extensions", '[".zevtc", ".evtc"]'),
        "analysis_max_fight_duration": int(defaults.get("analysis.max_fight_duration", 3600)),
        "cache_menu_ttl": int(defaults.get("cache.menu_ttl", 3600)),
        "auto_cleanup_enabled": defaults.get("auto_cleanup.enabled", True),
        "auto_cleanup_retention_days": int(defaults.get("auto_cleanup.retention_days", 30)),
        "updated_at": datetime.now().isoformat(),
    }


def build_settings_response_from_defaults(defaults: Dict[str, str]) -> Dict[str, Any]:
    """?DEFAULT_CONFIGS 字符串默认值构建响应字典（用于重置设置?""
    def _parse_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"

    def _parse_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    return {
        "theme": defaults.get("theme", "light"),
        "default_server": defaults.get("default_server", "Tarnished Coast"),
        "parse_parallel": _parse_int(defaults.get("parse_parallel", "1"), 1),
        "export_format": defaults.get("export_format", "json"),
        "auto_backup": _parse_bool(defaults.get("auto_backup", "true")),
        "retention_days": _parse_int(defaults.get("retention_days", "365"), 365),
        "scoring_mode": defaults.get("scoring_mode", "role_based"),
        "watermark_enabled": _parse_bool(defaults.get("watermark_enabled", "false")),
        "watermark_text": defaults.get("watermark_text", ""),
        "watermark_screenshot_enabled": _parse_bool(defaults.get("watermark_screenshot_enabled", "true")),
        "upload_max_file_size": _parse_int(defaults.get("upload.max_file_size", "50"), 50),
        "upload_allowed_extensions": defaults.get("upload.allowed_extensions", '[".zevtc", ".evtc"]'),
        "analysis_max_fight_duration": _parse_int(defaults.get("analysis.max_fight_duration", "3600"), 3600),
        "cache_menu_ttl": _parse_int(defaults.get("cache.menu_ttl", "3600"), 3600),
        "auto_cleanup_enabled": _parse_bool(defaults.get("auto_cleanup.enabled", "true")),
        "auto_cleanup_retention_days": _parse_int(defaults.get("auto_cleanup.retention_days", "30"), 30),
        "updated_at": datetime.now().isoformat(),
    }
