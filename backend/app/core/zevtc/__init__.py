# -*- coding: utf-8 -*-
"""
GW2 ZEVTC 核心解析器模块

功能:
    - 读取 ZEVTC (ZIP→EVTC 二进制) 中的全部原始数据提取
    - 提供结构化数据模型 (EvtcHeader, EvtcAgent, EvtcSkill, EvtcEvent)
    - 支持全量解析与流式解析两种模式

使用示例:
    from app.core.zevtc import EvtcParser
    result = EvtcParser(path="path/to/file.zevtc").parse_file()
    print(result.header, result.agent_count, result.event_count)
"""

from .exceptions import (
    DatabaseError,
    DuplicateFileError,
    FileCorruptedError,
    InvalidFileFormatError,
    UnsupportedVersionError,
    ValidationError,
    ZevtcError,
)
from .models import (
    EvtcAgent,
    EvtcEvent,
    EvtcHeader,
    EvtcSkill,
    ImportResult,
    ParseResult,
)
from .parser_core import EvtcByteReader, EvtcParser

__all__ = [
    # Exceptions
    "ZevtcError",
    "InvalidFileFormatError",
    "FileCorruptedError",
    "UnsupportedVersionError",
    "DatabaseError",
    "DuplicateFileError",
    "ValidationError",
    # Models
    "EvtcHeader",
    "EvtcAgent",
    "EvtcSkill",
    "EvtcEvent",
    "ParseResult",
    "ImportResult",
    # Core classes
    "EvtcParser",
    "EvtcByteReader",
]

__version__ = "1.0.0"
