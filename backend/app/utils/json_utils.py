# -*- coding: utf-8 -*-
"""
JSON 工具模块
提供统一的 JSON 解析接口，支持 orjson 高性能解析，
当 orjson 不可用时自动 fallback 到标准库 json
"""

import json as std_json
from typing import Any, Optional

# 尝试导入 orjson，如果失败则使用标准库
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def loads(data: bytes | str) -> Any:
    """
    解析 JSON 数据
    :param data: JSON 数据（字节或字符串）
    :return: 解析后的 Python 对象
    """
    if HAS_ORJSON:
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            return orjson.loads(data)
        except Exception:
            # orjson 解析失败时 fallback 到标准库
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            return std_json.loads(data)
    else:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return std_json.loads(data)


def dumps(obj: Any, **kwargs) -> bytes | str:
    """
    将 Python 对象序列化为 JSON
    :param obj: 要序列化的对象
    :param kwargs: 额外参数
    :return: JSON 字节串（orjson）或字符串（标准库）
    """
    if HAS_ORJSON:
        return orjson.dumps(obj, **kwargs)
    else:
        return std_json.dumps(obj, **kwargs)


def loads_str(data: str) -> Any:
    """
    解析字符串形式的 JSON
    :param data: JSON 字符串
    :return: 解析后的 Python 对象
    """
    return loads(data)


def loads_bytes(data: bytes) -> Any:
    """
    解析字节形式的 JSON
    :param data: JSON 字节串
    :return: 解析后的 Python 对象
    """
    return loads(data)
