# -*- coding: utf-8 -*-
"""
解析进度存储服务
功能：使用普通dict存储实时解析进度，解析完成后清理，无TTL机制
"""

from typing import Any, Dict
from datetime import datetime

from app.utils.db.dict_utils import get_dict_label


class ParseProgressService:
    """解析进度存储包装器

    使用普通内存字典存储解析过程中的实时状态。
    应用重启后丢失，解析完成后由调用方清理。
    不涉及持久化缓存或TTL机制。
    """

    def __init__(self):
        self._progress: Dict[int, Dict[str, Any]] = {}

    def _key(self, log_id: int) -> str:
        return f"parse_progress:{log_id}"

    def __setitem__(self, log_id: int, value: Dict[str, Any]) -> None:
        self._progress[log_id] = value

    def __getitem__(self, log_id: int) -> Dict[str, Any]:
        val = self._progress.get(log_id)
        if val is None:
            val = {
                "stage": get_dict_label("parse_stage", "pending") or "未开始",
                "progress": 0,
                "current_file": "",
                "players_found": 0,
                "events_processed": 0,
                "errors": [],
                "warnings": [],
            }
            self._progress[log_id] = val
        return val

    def get(self, log_id: int, default: Any = None) -> Any:
        val = self._progress.get(log_id)
        if val is None and default is not None:
            return default
        if val is None:
            val = {
                "stage": get_dict_label("parse_stage", "pending") or "未开始",
                "progress": 0,
                "current_file": "",
                "players_found": 0,
                "events_processed": 0,
                "errors": [],
                "warnings": [],
            }
            self._progress[log_id] = val
        return val

    def delete(self, log_id: int) -> None:
        self._progress.pop(log_id, None)

    def clear_progress(self, log_id: int) -> None:
        self._progress.pop(log_id, None)

    def __delitem__(self, log_id: int) -> None:
        self._progress.pop(log_id, None)

    def __contains__(self, log_id: int) -> bool:
        return log_id in self._progress

    def init_progress(self, log_id: int, filename: str) -> None:
        """初始化解析进度状态"""
        self[log_id] = {
            "stage": get_dict_label("parse_stage", "initializing") or "初始化",
            "progress": 0,
            "current_file": filename,
            "players_found": 0,
            "events_processed": 0,
            "errors": [],
            "warnings": [],
            "start_time": datetime.now().isoformat(),
        }


parse_progress_service = ParseProgressService()
