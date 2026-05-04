# -*- coding: utf-8 -*-
"""
ZEVTC 解析器异常层次结构

所有异常均继承自 ZevtcError，便于调用方统一捕获。
"""

from typing import Any, Dict, Optional


class ZevtcError(Exception):
    """所有 ZEVTC 相关异常的基类"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class InvalidFileFormatError(ZevtcError):
    """文件格式无效（非 EVTC Magic、ZIP 损坏等）"""

    pass


class FileCorruptedError(ZevtcError):
    """文件数据损坏（截断、CRC 错误、读取越界等）"""

    pass


class UnsupportedVersionError(ZevtcError):
    """EVTC 版本不支持（revision > 1 等）"""

    pass


class DatabaseError(ZevtcError):
    """数据库操作失败"""

    pass


class DuplicateFileError(ZevtcError):
    """文件 SHA-256 已存在于指纹表中（可选择更新模式）"""

    pass


class ValidationError(ZevtcError):
    """数据验证失败（如 Agent 数量与 Header 声明不符）"""

    pass
