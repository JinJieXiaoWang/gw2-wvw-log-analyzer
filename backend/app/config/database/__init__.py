# -*- coding: utf-8 -*-
"""数据库配置模块 (DEPRECATED)

警告：本目录下的模块为历史遗留，内容与上级目录的 database.py 存在重复且可能不同步。
新代码请直接从 app.config.database 导入，而非本目录。
计划在未来版本中移除本目录。
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
