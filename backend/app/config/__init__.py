# -*- coding: utf-8 -*-
# 模块功能：配置统一入口
# 说明：
#   从各配置模块导出常用配置实例，提供统一的配置访问入口。
#   实际配置逻辑已集中到 app.core.config，本文件保持向后兼容。

from app.core.config import (
    DatabaseType,
    ModelProvider,
    Settings,
    get_settings,
)
from app.core.config import settings as _settings

# 为了向后兼容，重导出旧的变量名
db_settings = _settings
settings = _settings
ai_config = _settings

__all__ = [
    "Settings",
    "get_settings",
    "DatabaseType",
    "ModelProvider",
    "settings",
    "db_settings",
    "ai_config",
]
