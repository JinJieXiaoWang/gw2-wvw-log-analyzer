# -*- coding: utf-8 -*-
"""数据库配置模块

统一入口，所有数据库相关导入应通过 app.config.database
"""

from .database import (
    init_db,
    get_db,
    get_db_context,
    SessionLocal,
    get_base,
    Base,
    test_connection,
    get_current_db_info,
    switch_database,
)

__all__ = [
    "init_db",
    "get_db",
    "get_db_context",
    "SessionLocal",
    "get_base",
    "Base",
    "test_connection",
    "get_current_db_info",
    "switch_database",
]
