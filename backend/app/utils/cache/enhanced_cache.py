
# -*- coding: utf-8 -*-
#模块功能：增强型内存缓存
#作者：系统
#创建日期?2026-05-06
#说明：具有大小限制的内存跟踪LRU缓存

import time
import os
from collections import OrderedDict

from app.utils.logger import logger

# Config
CACHE_MAX_ITEMS = int(os.environ.get("CACHE_MAX_ITEMS", 1000))
CACHE_MAX_SIZE_MB = int(os.environ.get("CACHE_MAX_SIZE_MB", 200))
CACHE_DEFAULT_TTL_SECONDS = int(os.environ.get("CACHE_DEFAULT_TTL_SECONDS", 3600))
CACHE_MAX_SIZE_BYTES = CACHE_MAX_SIZE_MB * 1024 * 1024


def _get_object_size(obj):
    """Estimate object memory size in bytes"""
    import sys
    size = sys.getsizeof(obj)
    
    # Recursively estimate container sizes
    if isinstance(obj, dict):
        size += sum(_get_object_size(k) + _get_object_size(v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        size += sum(_get_object_size(item) for item in obj)
    
    return size


class MemoryTrackedCache:
    """LRU cache with memory size tracking"""
    
    def __init__(
        self,
        max_items=CACHE_MAX_ITEMS,
        max_size_bytes=CACHE_MAX_SIZE_BYTES,
        default_ttl=CACHE_DEFAULT_TTL_SECONDS,
    ):
        self._cache = OrderedDict()
        self._expiry = {}
        self._sizes = {}
        
        self.max_items = max_items
        self.max_size_bytes = max_size_bytes
        self.default_ttl = default_ttl
        
        self._total_size = 0
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def get(self, key):
        """Get cached item"""
        if key not in self._cache:
            self._misses += 1
            return None
        
        # Check expiry
        if key in self._expiry and time.time() > self._expiry[key]:
            self.delete(key)
            self._misses += 1
            return None
        
        # Update access order
        self._cache.move_to_end(key)
        self._hits += 1
        return self._cache[key]
    
    def set(self, key, value, ttl=None):
        """Set cached item"""
        # Subtract old size if exists
        if key in self._cache:
            self._total_size -= self._sizes.get(key, 0)
        
        # Calculate new object size
        size = _get_object_size(value)
        
        # Evict first to make space
        self._evict_if_needed(additional_size=size)
        
        # Set cache
        self._cache[key] = value
        self._sizes[key] = size
        self._total_size += size
        
        if ttl is None:
            ttl = self.default_ttl
        self._expiry[key] = time.time() + ttl
        
        # Check again and evict
        self._evict_if_needed()
    
    def delete(self, key):
        """Delete cached item"""
        if key in self._cache:
            self._total_size -= self._sizes.get(key, 0)
            del self._cache[key]
            del self._sizes[key]
            if key in self._expiry:
                del self._expiry[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        self._sizes.clear()
        self._total_size = 0
    
    def size(self):
        """Get cache item count"""
        return len(self._cache)
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            "items": len(self._cache),
            "total_size_bytes": self._total_size,
            "total_size_mb": self._total_size / (1024 * 1024),
            "max_items": self.max_items,
            "max_size_bytes": self.max_size_bytes,
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0,
            "evictions": self._evictions,
        }
    
    def _evict_if_needed(self, additional_size=0):
        """Evict expired or LRU items as needed"""
        # Clean expired first
        now = time.time()
        expired_keys = [k for k, exp in self._expiry.items() if exp < now]
        for key in expired_keys:
            self.delete(key)
        
        # Check limits
        while (
            (len(self._cache) >= self.max_items)
            or (self._total_size + additional_size > self.max_size_bytes)
        ):
            if not self._cache:
                break
            
            # Evict oldest
            oldest_key = next(iter(self._cache))
            self.delete(oldest_key)
            self._evictions += 1
    
    def cache_result(self, ttl=None):
        """Decorator: Cache function results"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = "%s.%s:%s:%s" % (func.__module__, func.__name__, repr(args), repr(kwargs))
                cached = self.get(key)
                if cached is not None:
                    return cached
                result = func(*args, **kwargs)
                self.set(key, result, ttl=ttl)
                return result
            return wrapper
        return decorator


# Global singleton
_global_cache = None


def get_cache():
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MemoryTrackedCache()
        logger.info(
            "[cache] Enhanced memory cache initialized max_items=%d max_size_mb=%.0f",
            _global_cache.max_items,
            _global_cache.max_size_bytes / (1024 * 1024)
        )
    return _global_cache


def delete_cache(pattern):
    """Delete cache by pattern, return count"""
    cache = get_cache()
    import re
    keys = list(cache._cache.keys())
    count = 0
    for key in keys:
        if re.search(pattern, key):
            cache.delete(key)
            count += 1
    if count > 0:
        logger.info("[cache] Deleted %d items by pattern: %s", count, pattern)
    return count

