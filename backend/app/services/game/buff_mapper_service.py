# -*- coding: utf-8 -*-
"""Buff 名称映射器（支持热更新）"""

import threading
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from app.constants.buffs import STATIC_BUFF_NAMES
from app.services.game.cache_service import get_global_cache
from app.utils.logger import logger

if TYPE_CHECKING:
    from app.services.game.game_data_service import GameDataService

CACHE_KEY_BUFF_NAME_CN = "game_data:buff_name_cn"


class BuffNameMapper:
    """Buff名称映射器（支持热更新）
    静态映射（内置? 动态映射（外部配置?    """

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
        cache_key = f"{CACHE_KEY_BUFF_NAME_CN}:{buff_id}"
        cache = get_global_cache()

        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        with self._lock:
            if buff_id in self._dynamic_mappings:
                name = self._dynamic_mappings[buff_id]
            elif buff_id in self.STATIC_BUFF_NAMES:
                name = self.STATIC_BUFF_NAMES[buff_id]
            else:
                name = f"Buff:{buff_id}"

            if use_cache:
                cache.set(cache_key, name)
            return name

    def get_name_cn(
        self, buff_id: int, game_data_service: Optional["GameDataService"] = None
    ) -> str:
        if game_data_service:
            cn_name = game_data_service.get_buff_name_cn(buff_id)
            if cn_name != f"Buff:{buff_id}":
                return cn_name
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
