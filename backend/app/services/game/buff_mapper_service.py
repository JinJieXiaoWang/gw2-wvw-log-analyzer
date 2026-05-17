# -*- coding: utf-8 -*-
"""Buff 名称映射器（支持热更新）

数据来源优先级：
1. 动态映射（外部配置热更新）
2. GameDataService（gw_buff 种子数据）
3. 回退：Buff:{id}
"""

import threading
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from app.utils.logger import logger

if TYPE_CHECKING:
    from app.services.game.game_data_service import GameDataService


class BuffNameMapper:
    """Buff名称映射器（支持热更新）
    动态映射（外部配置）+ GameDataService 种子数据
    """

    def __init__(self):
        self._dynamic_mappings: Dict[int, str] = {}
        self._last_update: Optional[datetime] = None
        self._lock = threading.RLock()

    def update_mappings(self, mappings: Dict[int, str]) -> None:
        with self._lock:
            self._dynamic_mappings.update(mappings)
            self._last_update = datetime.now()
            logger.info(f"Buff动态映射已更新，共 {len(mappings)} 条映射")

    def get_name(self, buff_id: int, use_cache: bool = True) -> str:
        """获取Buff英文名（优先动态映射，其次 gw_buff 种子数据）"""
        with self._lock:
            if buff_id in self._dynamic_mappings:
                return self._dynamic_mappings[buff_id]
        # 回退到 GameDataService（gw_buff 种子数据）
        try:
            from app.services.game.game_data_service import get_game_data_service
            gs = get_game_data_service()
            buff = gs.get_buff(buff_id)
            if buff and buff.get("name"):
                return buff["name"]
        except Exception:
            pass
        return f"Buff:{buff_id}"

    def get_name_cn(
        self, buff_id: int, game_data_service: Optional["GameDataService"] = None
    ) -> str:
        """获取Buff中文名"""
        if game_data_service:
            cn_name = game_data_service.get_buff_name_cn(buff_id)
            if cn_name != f"Buff:{buff_id}":
                return cn_name
        # 回退到全局 GameDataService
        try:
            from app.services.game.game_data_service import get_game_data_service
            gs = get_game_data_service()
            cn_name = gs.get_buff_name_cn(buff_id)
            if cn_name != f"Buff:{buff_id}":
                return cn_name
        except Exception:
            pass
        return self.get_name(buff_id)

    def reload(self) -> None:
        with self._lock:
            self._dynamic_mappings.clear()
            self._last_update = None
        logger.info("Buff名称映射已重加载")


_global_buff_mapper: Optional[BuffNameMapper] = None


def get_global_buff_mapper() -> BuffNameMapper:
    global _global_buff_mapper
    if _global_buff_mapper is None:
        _global_buff_mapper = BuffNameMapper()
    return _global_buff_mapper
