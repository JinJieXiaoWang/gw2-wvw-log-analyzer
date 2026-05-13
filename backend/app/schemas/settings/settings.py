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
    system_name: Optional[str] = None
    system_version: Optional[str] = None
    notification_enabled: Optional[bool] = None
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_parse_complete: Optional[bool] = None
    security_two_factor_auth: Optional[bool] = None
    theme_primary_color: Optional[str] = None
    theme_zoom: Optional[int] = None
    export_include_header: Optional[bool] = None
    export_utf8_encoding: Optional[bool] = None
    export_number_format: Optional[str] = None
    parsing_include_overkill: Optional[bool] = None
    parsing_ignore_small_damage: Optional[bool] = None
    parsing_pre_fight_buffer: Optional[int] = None
    parsing_auto_categorize_skills: Optional[bool] = None


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
    system_name: str
    system_version: str
    notification_enabled: bool
    notification_email: bool
    notification_push: bool
    notification_parse_complete: bool
    security_two_factor_auth: bool
    theme_primary_color: str
    theme_zoom: int
    export_include_header: bool
    export_utf8_encoding: bool
    export_number_format: str
    parsing_include_overkill: bool
    parsing_ignore_small_damage: bool
    parsing_pre_fight_buffer: int
    parsing_auto_categorize_skills: bool
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
    """将原始设置字典构建为标准化响应字典"""
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
        "upload_max_file_size": int(defaults.get("upload_max_file_size", 50)),
        "upload_allowed_extensions": defaults.get("upload_allowed_extensions", '[".zevtc", ".evtc"]'),
        "analysis_max_fight_duration": int(defaults.get("analysis_max_fight_duration", 3600)),
        "cache_menu_ttl": int(defaults.get("cache_menu_ttl", 3600)),
        "auto_cleanup_enabled": defaults.get("auto_cleanup_enabled", True),
        "auto_cleanup_retention_days": int(defaults.get("auto_cleanup_retention_days", 30)),
        "system_name": defaults.get("system_name", "GW2 WVW日志分析系统"),
        "system_version": defaults.get("system_version", "1.0.0"),
        "notification_enabled": defaults.get("notification_enabled", True),
        "notification_email": defaults.get("notification_email", True),
        "notification_push": defaults.get("notification_push", False),
        "notification_parse_complete": defaults.get("notification_parse_complete", True),
        "security_two_factor_auth": defaults.get("security_two_factor_auth", False),
        "theme_primary_color": defaults.get("theme_primary_color", "#165DFF"),
        "theme_zoom": int(defaults.get("theme_zoom", 100)),
        "export_include_header": defaults.get("export_include_header", True),
        "export_utf8_encoding": defaults.get("export_utf8_encoding", True),
        "export_number_format": defaults.get("export_number_format", "auto"),
        "parsing_include_overkill": defaults.get("parsing_include_overkill", True),
        "parsing_ignore_small_damage": defaults.get("parsing_ignore_small_damage", True),
        "parsing_pre_fight_buffer": int(defaults.get("parsing_pre_fight_buffer", 5)),
        "parsing_auto_categorize_skills": defaults.get("parsing_auto_categorize_skills", True),
        "updated_at": datetime.now().isoformat(),
    }


def build_settings_response_from_defaults(defaults: Dict[str, str]) -> Dict[str, Any]:
    """从 DEFAULT_CONFIGS 字符串默认值构建响应字典（用于重置设置）"""
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
        "upload_max_file_size": _parse_int(defaults.get("upload_max_file_size", "50"), 50),
        "upload_allowed_extensions": defaults.get("upload_allowed_extensions", '[".zevtc", ".evtc"]'),
        "analysis_max_fight_duration": _parse_int(defaults.get("analysis_max_fight_duration", "3600"), 3600),
        "cache_menu_ttl": _parse_int(defaults.get("cache_menu_ttl", "3600"), 3600),
        "auto_cleanup_enabled": _parse_bool(defaults.get("auto_cleanup_enabled", "true")),
        "auto_cleanup_retention_days": _parse_int(defaults.get("auto_cleanup_retention_days", "30"), 30),
        "system_name": defaults.get("system_name", "GW2 WVW日志分析系统"),
        "system_version": defaults.get("system_version", "1.0.0"),
        "notification_enabled": _parse_bool(defaults.get("notification_enabled", "true")),
        "notification_email": _parse_bool(defaults.get("notification_email", "true")),
        "notification_push": _parse_bool(defaults.get("notification_push", "false")),
        "notification_parse_complete": _parse_bool(defaults.get("notification_parse_complete", "true")),
        "security_two_factor_auth": _parse_bool(defaults.get("security_two_factor_auth", "false")),
        "theme_primary_color": defaults.get("theme_primary_color", "#165DFF"),
        "theme_zoom": _parse_int(defaults.get("theme_zoom", "100"), 100),
        "export_include_header": _parse_bool(defaults.get("export_include_header", "true")),
        "export_utf8_encoding": _parse_bool(defaults.get("export_utf8_encoding", "true")),
        "export_number_format": defaults.get("export_number_format", "auto"),
        "parsing_include_overkill": _parse_bool(defaults.get("parsing_include_overkill", "true")),
        "parsing_ignore_small_damage": _parse_bool(defaults.get("parsing_ignore_small_damage", "true")),
        "parsing_pre_fight_buffer": _parse_int(defaults.get("parsing_pre_fight_buffer", "5"), 5),
        "parsing_auto_categorize_skills": _parse_bool(defaults.get("parsing_auto_categorize_skills", "true")),
        "updated_at": datetime.now().isoformat(),
    }
