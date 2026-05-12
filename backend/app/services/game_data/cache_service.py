# -*- coding: utf-8 -*-
"""多级缓存服务（内存缓?+ 持久化缓存）"""

import copy
import hashlib
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from app.utils.logger import logger

DATA_DIR = Path(__file__).parent.parent.parent / "data"
CACHE_EXPIRE_MEMORY = 300
CACHE_EXPIRE_PERSISTENT = 3600


class CacheEntry:
    """缓存条目封装?""

    def __init__(self, key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_MEMORY):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.expire_seconds = expire_seconds
        self.access_count = 0
        self.last_accessed = datetime.now()

    def is_expired(self) -> bool:
        if self.expire_seconds <= 0:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed >= self.expire_seconds

    def get_value(self) -> Any:
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


class MultiLevelCache:
    """多级缓存管理器（内存缓存 + 持久化缓存）"""

    def __init__(self, cache_dir: Optional[Path] = None, max_memory_entries: int = 2000):
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._cache_dir = cache_dir or (DATA_DIR / ".cache")
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_memory_entries = max_memory_entries
        self._lock = threading.RLock()
        self._hit_count = 0
        self._miss_count = 0
        self._stats_lock = threading.Lock()

    def _evict_oldest(self) -> None:
        if not self._memory_cache:
            return
        oldest_key = min(self._memory_cache, key=lambda k: self._memory_cache[k].last_accessed)
        del self._memory_cache[oldest_key]
        logger.debug(f"MultiLevelCache LRU驱? {oldest_key}")

    def clear_expired(self) -> int:
        with self._lock:
            expired_keys = [k for k, entry in self._memory_cache.items() if entry.is_expired()]
            for k in expired_keys:
                del self._memory_cache[k]
            if expired_keys:
                logger.info(f"MultiLevelCache 清理 {len(expired_keys)} 个过期条?)
            return len(expired_keys)

    def get(self, key: str, loader: Optional[Callable[[], Any]] = None) -> Optional[Any]:
        with self._lock:
            memory_entry = self._memory_cache.get(key)
            if memory_entry:
                if not memory_entry.is_expired():
                    with self._stats_lock:
                        self._hit_count += 1
                    return memory_entry.get_value()
                else:
                    del self._memory_cache[key]

            persistent_value = self._load_from_persistent(key)
            if persistent_value is not None:
                self._memory_cache[key] = CacheEntry(key, persistent_value, CACHE_EXPIRE_MEMORY)
                with self._stats_lock:
                    self._hit_count += 1
                return persistent_value

            if loader:
                value = loader()
                self.set(key, value)
                with self._stats_lock:
                    self._miss_count += 1
                return value

            with self._stats_lock:
                self._miss_count += 1
            return None

    def set(self, key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_MEMORY) -> None:
        with self._lock:
            if len(self._memory_cache) >= self._max_memory_entries and key not in self._memory_cache:
                self._evict_oldest()
            entry = CacheEntry(key, copy.deepcopy(value), expire_seconds)
            self._memory_cache[key] = entry
            self._save_to_persistent(key, value)

    def invalidate(self, key: str) -> None:
        with self._lock:
            if key in self._memory_cache:
                del self._memory_cache[key]
            self._delete_persistent(key)

    def clear_memory(self) -> None:
        with self._lock:
            self._memory_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        with self._stats_lock:
            total = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total * 100) if total > 0 else 0
            return {
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "total_requests": total,
                "hit_rate_percent": round(hit_rate, 2),
                "memory_cache_size": len(self._memory_cache),
                "max_memory_entries": self._max_memory_entries,
            }

    def _get_persistent_path(self, key: str) -> Path:
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.cache"

    def _save_to_persistent(self, key: str, value: Any) -> None:
        try:
            path = self._get_persistent_path(key)
            data = {"key": key, "value": value, "saved_at": datetime.now().isoformat()}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"持久化缓存保存失败 {key}, {e}")

    def _load_from_persistent(self, key: str) -> Optional[Any]:
        try:
            path = self._get_persistent_path(key)
            if not path.exists():
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("value")
        except Exception as e:
            logger.warning(f"持久化缓存加载失败 {key}, {e}")
            return None

    def _delete_persistent(self, key: str) -> None:
        try:
            path = self._get_persistent_path(key)
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.warning(f"持久化缓存删除失败 {key}, {e}")


_global_cache: Optional[MultiLevelCache] = None


def get_global_cache() -> MultiLevelCache:
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache
