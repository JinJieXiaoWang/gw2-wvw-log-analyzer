# -*- coding: utf-8 -*-
"""
解析进度存储服务
功能：基于TTL Cache防止无界增长，替代原路由?_ProgressStore
"""

from typing import Any, Dict

from app.utils.cache.cache import Cache


class ParseProgressService:
    """解析进度存储包装器，基于TTL Cache防止无界增长

    原实现使用普?dict，解析崩溃或重启后条目永久残留，导致内存泄漏?
    改用 Cache（LRU + TTL）后，条目会?24 小时后自动过期，
    且最大保?1000 条，超出时淘汰最早的条目?
    """

    def __init__(self):
        self._cache = Cache(max_size=1000, default_ttl=86400)

    def _key(self, log_id: int) -> str:
        return f"parse_progress:{log_id}"

    def __setitem__(self, log_id: int, value: Dict[str, Any]) -> None:
        self._cache.set(self._key(log_id), value, ttl=86400)

    def __getitem__(self, log_id: int) -> Dict[str, Any]:
        val = self._cache.get(self._key(log_id))
        if val is None:
            val = {
                "stage": "未开?,
                "progress": 0,
                "current_file": "",
                "players_found": 0,
                "events_processed": 0,
                "errors": [],
                "warnings": [],
            }
            self._cache.set(self._key(log_id), val, ttl=86400)
        return val

    def get(self, log_id: int, default: Any = None) -> Any:
        val = self._cache.get(self._key(log_id))
        if val is None and default is not None:
            return default
        if val is None:
            val = {
                "stage": "未开?,
                "progress": 0,
                "current_file": "",
                "players_found": 0,
                "events_processed": 0,
                "errors": [],
                "warnings": [],
            }
            self._cache.set(self._key(log_id), val, ttl=86400)
        return val

    def delete(self, log_id: int) -> None:
        self._cache.delete(self._key(log_id))

    def clear_progress(self, log_id: int) -> None:
        self._cache.delete(self._key(log_id))

    def __delitem__(self, log_id: int) -> None:
        self._cache.delete(self._key(log_id))

    def __contains__(self, log_id: int) -> bool:
        return self._cache.get(self._key(log_id)) is not None

    def init_progress(self, log_id: int, filename: str) -> None:
        """初始化解析进度状?""
        from datetime import datetime
        self[log_id] = {
            "stage": "初初始化,
            "progress": 0,
            "current_file": filename,
            "players_found": 0,
            "events_processed": 0,
            "errors": [],
            "warnings": [],
            "start_time": datetime.now().isoformat(),
        }


parse_progress_service = ParseProgressService()
