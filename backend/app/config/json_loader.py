# -*- coding: utf-8 -*-
# 模块功能：集中式 JSON 配置加载器
# 说明：统一加载 backend/app/config/json/ 目录下的所有 JSON 配置文件
#   - 使用 orjson 解析（项目已有依赖，速度更快）
#   - 支持开发模式热检测（文件修改后自动重载）
#   - 加载失败时回退到内存默认值并记录告警日志

import os
import time
from typing import Any, Dict, Optional

from app.utils.logger import logger

# 优先使用 orjson，回退到标准库 json
try:
    import orjson as json_lib

    def _load_json(path: str) -> Dict[str, Any]:
        with open(path, "rb") as f:
            return json_lib.loads(f.read())
except ImportError:
    import json as json_lib  # type: ignore[no-redef]

    def _load_json(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json_lib.load(f)

_JSON_DIR = os.path.join(os.path.dirname(__file__), "json")

# 内存缓存: {name: {"data": dict, "mtime": float, "path": str}}
_cache: Dict[str, Dict[str, Any]] = {}

# 开发模式热检测开关（可通过环境变量控制）
_HOT_RELOAD = os.environ.get("JSON_CONFIG_HOT_RELOAD", "false").lower() in ("1", "true", "yes")

# 各配置的内存默认回退值（加载失败时使用）
_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "scoring_rules": {},
    "parsing_config": {
        "parsing_strategy": "api",
        "local_parser": {"enabled": False, "experimental": True},
        "cache": {"ei_json_cache_ttl_hours": 720, "compress_algorithm": "gzip"},
        "dps_report": {"upload_timeout_seconds": 300, "json_fetch_timeout_seconds": 60},
        "validation": {"verify_permalink_on_insert": True},
    },
    "rate_limit_config": {
        "dps_report_api": {
            "token_bucket": {"max_requests_per_window": 25, "window_seconds": 60},
            "request_queue": {"max_concurrent_requests": 1},
        },
        "batch_parse": {"max_concurrent_tasks": 1, "streaming_batch_size": 10},
    },
}


def _resolve_path(name: str) -> str:
    """将配置名解析为完整文件路径。支持 'name' 或 'name.json'。"""
    if not name.endswith(".json"):
        name = f"{name}.json"
    return os.path.join(_JSON_DIR, name)


def _is_stale(name: str, path: str) -> bool:
    """检查缓存是否过期（文件被修改）"""
    if name not in _cache:
        return True
    try:
        current_mtime = os.path.getmtime(path)
        return current_mtime > _cache[name]["mtime"]
    except OSError:
        return True


def load_json_config(name: str, use_cache: bool = True) -> Dict[str, Any]:
    """加载 JSON 配置文件。

    Args:
        name: 配置文件名（如 'scoring_rules' 或 'parsing_config.json'）
        use_cache: 是否使用内存缓存（生产环境建议 True）

    Returns:
        dict: 解析后的 JSON 数据。加载失败时返回默认空结构并记录告警。
    """
    path = _resolve_path(name)

    if use_cache and not _HOT_RELOAD and name in _cache:
        return _cache[name]["data"]

    if use_cache and _HOT_RELOAD and not _is_stale(name, path):
        return _cache[name]["data"]

    try:
        data = _load_json(path)
        _cache[name] = {"data": data, "mtime": os.path.getmtime(path), "path": path}
        logger.debug(f"[json_loader] 加载配置成功: {name}")
        return data
    except FileNotFoundError:
        logger.warning(f"[json_loader] 配置文件不存在: {path}，使用默认值")
        fallback = _DEFAULTS.get(name.replace(".json", ""), {})
        _cache[name] = {"data": fallback, "mtime": 0, "path": path}
        return fallback
    except Exception as e:
        logger.error(f"[json_loader] 加载配置失败: {path}，错误: {e}")
        fallback = _DEFAULTS.get(name.replace(".json", ""), {})
        _cache[name] = {"data": fallback, "mtime": 0, "path": path}
        return fallback


def reload_json_config(name: str) -> Dict[str, Any]:
    """强制重新加载指定 JSON 配置文件（忽略缓存）"""
    return load_json_config(name, use_cache=False)


def get_json_config_names() -> list:
    """获取 json/ 目录下所有可用的配置文件名（不含扩展名）"""
    names = []
    try:
        for fname in os.listdir(_JSON_DIR):
            if fname.endswith(".json"):
                names.append(fname[:-5])
    except OSError:
        pass
    return names


def get_json_config_path(name: str) -> str:
    """获取配置文件的绝对路径（用于外部工具或日志记录）"""
    return os.path.abspath(_resolve_path(name))
