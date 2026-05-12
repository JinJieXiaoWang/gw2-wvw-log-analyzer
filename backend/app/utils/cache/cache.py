# 模块功能：缓存工?# 作者：帅妹妹丶.8297
# 创建日期?2026-04-27
# 依赖说明：functools, time

import functools
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional


# 简单的内存缓存实现
class Cache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        功能：初始化缓存
        参数据            max_size: 缓存最大容?            default_ttl: 默认缓存过期时间（秒?        """
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        功能：获取缓存?        参数：key - 缓存?        返回：缓存值，如果不存在或已过期则返回None
        """
        if key not in self.cache:
            return None

        item = self.cache[key]
        if time.time() > item["expire_time"]:
            del self.cache[key]
            return None

        self.cache.move_to_end(key)
        return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        功能：设置缓存?        参数据            key: 缓存?            value: 缓存?            ttl: 缓存过期时间（秒），如果为None则使用默认?        """
        if key in self.cache:
            del self.cache[key]
        elif len(self.cache) >= self.max_size:
            # O(1) LRU 驱逐：删除最久未访问的项
            self.cache.popitem(last=False)

        expire_time = time.time() + (ttl or self.default_ttl)
        self.cache[key] = {
            "value": value,
            "expire_time": expire_time,
        }
        self.cache.move_to_end(key)

    def delete(self, key: str) -> None:
        """
        功能：删除缓存?        参数：key - 缓存?        """
        self.cache.pop(key, None)

    def clear(self) -> None:
        """
        功能：清空缓?        """
        self.cache.clear()

    def size(self) -> int:
        """
        功能：获取缓存大?        返回：缓存项数量
        """
        return len(self.cache)


# 创建全局缓存实例
cache = Cache()


def cache_result(ttl: Optional[int] = None):
    """
    功能：缓存函数结果的装饰?    参数：ttl - 缓存过期时间（秒?    返回：装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存?            key_parts = [func.__name__]
            for arg in args:
                if hasattr(arg, "__dict__"):
                    # 对于对象，使用其id
                    key_parts.append(str(id(arg)))
                else:
                    key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            cache_key = "_".join(key_parts)

            # 尝试从缓存获?            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 缓存结果
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def clear_cache():
    """
    功能：清空所有缓?    """
    cache.clear()


def delete_cache(key_pattern: str) -> int:
    """
    功能：删除匹配模式的缓存
    参数：key_pattern - 缓存键模型    返回：删除的缓存项数据    """
    deleted = 0
    keys_to_delete = []
    for key in cache.cache:
        if key_pattern in key:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        cache.delete(key)
        deleted += 1
    return deleted
