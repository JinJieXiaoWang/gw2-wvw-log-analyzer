# -*- coding: utf-8 -*-
# 模块功能：游戏数据服务层
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：json, cache, pathlib
# 增强功能：多级缓存机制、Buff中文名动态映射热更新支持

import copy
import hashlib
import json
import threading
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from app.data import DATA_DIR, get_data_version, load_json_file
from app.utils.logger import logger

# =============================================================================
# 缓存键定义
# =============================================================================
CACHE_KEY_PROFESSIONS = "game_data:professions"
CACHE_KEY_BUFFS = "game_data:buffs"
CACHE_KEY_PROFESSION_NAME_CN = "game_data:profession_name_cn"
CACHE_KEY_BUFF_NAME_CN = "game_data:buff_name_cn"
CACHE_KEY_PROFESSION_DETAIL = "game_data:profession_detail"
CACHE_KEY_BUFF_DETAIL = "game_data:buff_detail"

# 缓存过期时间配置（秒）
CACHE_EXPIRE_MEMORY = 300  # 内存缓存5分钟
CACHE_EXPIRE_PERSISTENT = 3600  # 持久化缓存1小时


# =============================================================================
# 缓存条目类
# =============================================================================
class CacheEntry:
    # 功能：缓存条目封装类
    def __init__(self, key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_MEMORY):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.expire_seconds = expire_seconds
        self.access_count = 0
        self.last_accessed = datetime.now()

    def is_expired(self) -> bool:
        # 功能：检查是否过期
        if self.expire_seconds <= 0:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed >= self.expire_seconds

    def get_value(self) -> Any:
        # 功能：获取值（访问时更新统计）
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


# =============================================================================
# 多级缓存管理器
# =============================================================================
class MultiLevelCache:
    # 功能：多级缓存管理器（内存缓存 + 持久化缓存）
    # 增强：添加内存上限和过期条目主动清理，防止无界增长

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
        """LRU驱逐：删除最久未访问的内存缓存条目"""
        if not self._memory_cache:
            return
        oldest_key = min(
            self._memory_cache,
            key=lambda k: self._memory_cache[k].last_accessed
        )
        del self._memory_cache[oldest_key]
        logger.debug(f"MultiLevelCache LRU驱逐: {oldest_key}")

    def clear_expired(self) -> int:
        """主动清理所有过期的内存缓存条目，返回清理数量"""
        with self._lock:
            expired_keys = [
                k for k, entry in self._memory_cache.items()
                if entry.is_expired()
            ]
            for k in expired_keys:
                del self._memory_cache[k]
            if expired_keys:
                logger.info(f"MultiLevelCache 清理 {len(expired_keys)} 个过期条目")
            return len(expired_keys)

    def get(
        self, key: str, loader: Optional[Callable[[], Any]] = None
    ) -> Optional[Any]:
        # 功能：获取缓存值
        # 参数：key - 缓存键；loader - 缓存未命中时的加载器
        # 返回：缓存值或加载器返回值
        with self._lock:
            memory_entry = self._memory_cache.get(key)

            if memory_entry:
                if not memory_entry.is_expired():
                    with self._stats_lock:
                        self._hit_count += 1
                    return memory_entry.get_value()
                else:
                    # 过期条目立即清理
                    del self._memory_cache[key]

            persistent_value = self._load_from_persistent(key)
            if persistent_value is not None:
                self._memory_cache[key] = CacheEntry(
                    key, persistent_value, CACHE_EXPIRE_MEMORY
                )
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

    def set(
        self, key: str, value: Any, expire_seconds: int = CACHE_EXPIRE_MEMORY
    ) -> None:
        # 功能：设置缓存值
        with self._lock:
            # 如果达到内存上限，先LRU驱逐最久未访问的条目
            if len(self._memory_cache) >= self._max_memory_entries and key not in self._memory_cache:
                self._evict_oldest()

            entry = CacheEntry(key, copy.deepcopy(value), expire_seconds)
            self._memory_cache[key] = entry
            self._save_to_persistent(key, value)

    def invalidate(self, key: str) -> None:
        # 功能：使缓存失效
        with self._lock:
            if key in self._memory_cache:
                del self._memory_cache[key]
            self._delete_persistent(key)

    def clear_memory(self) -> None:
        # 功能：清除内存缓存
        with self._lock:
            self._memory_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        # 功能：获取缓存统计信息
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
        # 功能：获取持久化文件路径
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.cache"

    def _save_to_persistent(self, key: str, value: Any) -> None:
        # 功能：保存到持久化缓存（使用JSON序列化替代pickle）
        try:
            path = self._get_persistent_path(key)
            data = {"key": key, "value": value, "saved_at": datetime.now().isoformat()}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"持久化缓存保存失败: {key}, {e}")

    def _load_from_persistent(self, key: str) -> Optional[Any]:
        # 功能：从持久化缓存加载（使用JSON反序列化替代pickle）
        try:
            path = self._get_persistent_path(key)
            if not path.exists():
                return None

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("value")
        except Exception as e:
            logger.warning(f"持久化缓存加载失败: {key}, {e}")
            return None

    def _delete_persistent(self, key: str) -> None:
        # 功能：删除持久化缓存
        try:
            path = self._get_persistent_path(key)
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.warning(f"持久化缓存删除失败: {key}, {e}")


# 全局缓存管理器
_global_cache: Optional[MultiLevelCache] = None


def get_global_cache() -> MultiLevelCache:
    # 功能：获取全局缓存管理器
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache


# =============================================================================
# Buff名称映射器（支持热更新）
# =============================================================================
class BuffNameMapper:
    # 功能：Buff名称映射器（支持热更新）
    # 静态映射（内置）+ 动态映射（外部配置）

    STATIC_BUFF_NAMES = {
        717: "Regeneration",
        718: "Swiftness",
        719: "Fury",
        725: "Might",
        726: "Vigor",
        728: "Protection",
        740: "Aegis",
        743: "Stability",
        1122: "Quickness",
        1187: "Resistance",
        26980: "Alacrity",
        30328: "Vigor",
        26981: "Resolution",
        9283: "Empathy",
        110942: "Stone",
        13797: "Geomancy",
    }

    def __init__(self):
        self._dynamic_mappings: Dict[int, str] = {}
        self._last_update: Optional[datetime] = None
        self._lock = threading.RLock()

    def update_mappings(self, mappings: Dict[int, str]) -> None:
        # 功能：更新动态映射
        with self._lock:
            self._dynamic_mappings.update(mappings)
            self._last_update = datetime.now()
            logger.info(f"Buff动态映射已更新，共 {len(mappings)} 条映射")

    def get_name(self, buff_id: int, use_cache: bool = True) -> str:
        # 功能：获取Buff名称（优先动态映射，其次静态映射）
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
        # 功能：获取Buff中文名
        if game_data_service:
            cn_name = game_data_service.get_buff_name_cn(buff_id)
            if cn_name != f"Buff:{buff_id}":
                return cn_name

        return self.get_name(buff_id)

    def reload(self) -> None:
        # 功能：重新加载映射（用于热更新）
        with self._lock:
            self._dynamic_mappings.clear()
            self._last_update = None
        logger.info("Buff名称映射已重置")


# 全局Buff名称映射器
_global_buff_mapper: Optional[BuffNameMapper] = None


def get_global_buff_mapper() -> BuffNameMapper:
    # 功能：获取全局Buff名称映射器
    global _global_buff_mapper
    if _global_buff_mapper is None:
        _global_buff_mapper = BuffNameMapper()
    return _global_buff_mapper


# =============================================================================
# 游戏数据服务（增强版）
# =============================================================================
class GameDataService:
    # 功能：游戏数据服务类（增强版，支持多级缓存和热更新）

    def __init__(self):
        self._professions_data: Optional[Dict] = None
        self._buffs_data: Optional[Dict] = None
        self._last_reload: Optional[datetime] = None
        self._cache = get_global_cache()
        self._buff_mapper = get_global_buff_mapper()
        self._lock = threading.RLock()

        self._buff_name_to_id_cache: Dict[str, int] = {}
        self._profession_name_to_data_cache: Dict[str, Dict] = {}

    def _get_professions_data(self, force_reload: bool = False) -> Dict:
        # 功能：获取职业数据（内部方法，带缓存）
        if self._professions_data is None or force_reload:
            try:
                self._professions_data = load_json_file("professions.json")
                self._last_reload = datetime.now()
                self._build_profession_caches()
                logger.info(
                    f"职业数据加载成功，版本: {self._professions_data.get('version')}"
                )
            except Exception as e:
                logger.error(f"职业数据加载失败: {e}")
                self._professions_data = {
                    "version": "1.0.0",
                    "base_professions": {},
                    "elite_specs": {},
                }
        return self._professions_data

    def _get_buffs_data(self, force_reload: bool = False) -> Dict:
        # 功能：获取Buff数据（内部方法，带缓存）
        if self._buffs_data is None or force_reload:
            try:
                self._buffs_data = load_json_file("buffs.json")
                self._last_reload = datetime.now()
                self._build_buff_caches()
                logger.info(
                    f"Buff数据加载成功，版本: {self._buffs_data.get('version')}"
                )
            except Exception as e:
                logger.error(f"Buff数据加载失败: {e}")
                self._buffs_data = {"version": "1.0.0", "categories": {}, "buffs": {}}
        return self._buffs_data

    def _build_profession_caches(self) -> None:
        # 功能：构建职业相关缓存
        if not self._professions_data:
            return

        for key, prof in self._professions_data.get("base_professions", {}).items():
            name_en = prof.get("name", key)
            name_cn = prof.get("name_cn", name_en)
            self._profession_name_to_data_cache[name_en] = prof
            self._profession_name_to_data_cache[name_cn] = prof
            self._profession_name_to_data_cache[key] = prof

        for key, spec in self._professions_data.get("elite_specs", {}).items():
            name_en = spec.get("name", key)
            name_cn = spec.get("name_cn", name_en)
            self._profession_name_to_data_cache[name_en] = spec
            self._profession_name_to_data_cache[name_cn] = spec
            self._profession_name_to_data_cache[key] = spec

    def _build_buff_caches(self) -> None:
        # 功能：构建Buff相关缓存
        if not self._buffs_data:
            return

        for key, buff in self._buffs_data.get("buffs", {}).items():
            buff_id = buff.get("id")
            if buff_id:
                self._buff_name_to_id_cache[buff.get("name", "")] = buff_id
                self._buff_name_to_id_cache[buff.get("name_cn", "")] = buff_id

    def reload_all_data(self) -> Dict[str, Any]:
        # 功能：重新加载所有数据（支持热更新）
        logger.info("开始重新加载所有游戏数据...")
        self._professions_data = None
        self._buffs_data = None
        self._cache.clear_memory()

        prof_data = self._get_professions_data(force_reload=True)
        buff_data = self._get_buffs_data(force_reload=True)

        return {
            "success": True,
            "professions_version": prof_data.get("version"),
            "buffs_version": buff_data.get("version"),
            "reloaded_at": datetime.now().isoformat(),
        }

    # ==================== 职业相关方法 ====================

    def get_all_professions(self) -> List[Dict]:
        # 功能：获取所有基础职业列表
        data = self._get_professions_data()
        professions = []
        for key, prof in data.get("base_professions", {}).items():
            professions.append(prof)
        return professions

    def get_all_elite_specs(self) -> List[Dict]:
        # 功能：获取所有精英特长列表
        data = self._get_professions_data()
        specs = []
        for key, spec in data.get("elite_specs", {}).items():
            specs.append(spec)
        return specs

    def get_profession(self, name: str) -> Optional[Dict]:
        # 功能：获取指定基础职业
        cache_key = f"{CACHE_KEY_PROFESSION_DETAIL}:base:{name}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get_professions_data()
        result = data.get("base_professions", {}).get(name)
        if result:
            self._cache.set(cache_key, result)
        return result

    def get_elite_spec(self, name: str) -> Optional[Dict]:
        # 功能：获取指定精英特长
        cache_key = f"{CACHE_KEY_PROFESSION_DETAIL}:elite:{name}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get_professions_data()
        result = data.get("elite_specs", {}).get(name)
        if result:
            self._cache.set(cache_key, result)
        return result

    def get_elite_specs_by_base(self, base_profession: str) -> List[Dict]:
        # 功能：获取某基础职业的所有精英特长
        data = self._get_professions_data()
        specs = []
        for key, spec in data.get("elite_specs", {}).items():
            if spec.get("base_profession") == base_profession:
                specs.append(spec)
        return specs

    def get_profession_name_cn(self, name: str) -> str:
        # 功能：获取职业中文名
        cache_key = f"{CACHE_KEY_PROFESSION_NAME_CN}:{name}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        result = name
        spec = self.get_elite_spec(name)
        if spec:
            result = spec.get("name_cn", name)
        else:
            prof = self.get_profession(name)
            if prof:
                result = prof.get("name_cn", name)

        self._cache.set(cache_key, result)
        return result

    def get_default_role(self, profession_name: str) -> str:
        # 功能：获取职业默认定位
        spec = self.get_elite_spec(profession_name)
        if spec:
            return spec.get("default_role", "dps")

        prof = self.get_profession(profession_name)
        if prof:
            return prof.get("default_role", "dps")

        return "dps"

    def get_scoring_config(self, profession_name: str) -> Optional[Dict[str, int]]:
        # 功能：获取职业评分配置
        spec = self.get_elite_spec(profession_name)
        if spec:
            return spec.get("scoring_config")
        return None

    # ==================== Buff相关方法 ====================

    def get_all_buffs(self) -> List[Dict]:
        # 功能：获取所有Buff列表
        data = self._get_buffs_data()
        buffs = []
        for key, buff in data.get("buffs", {}).items():
            buffs.append(buff)
        return buffs

    def get_buff(self, buff_id: int) -> Optional[Dict]:
        # 功能：获取指定Buff
        cache_key = f"{CACHE_KEY_BUFF_DETAIL}:{buff_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get_buffs_data()
        result = data.get("buffs", {}).get(str(buff_id))
        if result:
            self._cache.set(cache_key, result)
        return result

    def get_buff_name_cn(self, buff_id: int) -> str:
        # 功能：获取Buff中文名
        cache_key = f"{CACHE_KEY_BUFF_NAME_CN}:{buff_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        buff = self.get_buff(buff_id)
        result = buff.get("name_cn", f"Buff:{buff_id}") if buff else f"Buff:{buff_id}"
        self._cache.set(cache_key, result)
        return result

    def get_buffs_by_category(self, category: str) -> List[Dict]:
        # 功能：按分类获取Buff列表
        data = self._get_buffs_data()
        buffs = []
        for key, buff in data.get("buffs", {}).items():
            if buff.get("category") == category:
                buffs.append(buff)
        return buffs

    def get_key_buffs(self) -> List[Dict]:
        # 功能：获取关键Buff列表
        data = self._get_buffs_data()
        buffs = []
        for key, buff in data.get("buffs", {}).items():
            if buff.get("is_key_buff"):
                buffs.append(buff)
        return buffs

    def get_buff_config_for_parser(self, buff_id: int) -> Dict[str, Any]:
        # 功能：获取用于解析器的Buff配置
        buff = self.get_buff(buff_id)
        if buff:
            return {
                "max_stacks": buff.get("max_stacks", 1),
                "stacking_rule": buff.get("stacking", "duration"),
                "effect_type": buff.get("category", "unknown"),
                "intensity_curve": "instant",
                "duration_ms": 30000,
            }
        return {
            "max_stacks": 1,
            "stacking_rule": "duration",
            "effect_type": "unknown",
            "intensity_curve": "instant",
            "duration_ms": 30000,
        }

    # ==================== Buff名称映射热更新接口 ====================

    def update_buff_name_mappings(self, mappings: Dict[int, str]) -> Dict[str, Any]:
        # 功能：更新Buff名称映射（用于热更新）
        self._buff_mapper.update_mappings(mappings)
        self._cache.invalidate(CACHE_KEY_BUFF_NAME_CN)
        return {
            "success": True,
            "updated_count": len(mappings),
            "updated_at": datetime.now().isoformat(),
        }

    def get_buff_name_en(self, buff_id: int) -> str:
        # 功能：获取Buff英文名
        return self._buff_mapper.get_name(buff_id)

    # ==================== 版本和元数据 ====================

    def get_data_info(self) -> Dict[str, Any]:
        # 功能：获取数据版本信息
        version_info = get_data_version()
        prof_data = self._get_professions_data()
        buff_data = self._get_buffs_data()

        return {
            "version": version_info.get("version"),
            "last_updated": version_info.get("last_updated"),
            "professions": {
                "version": prof_data.get("version"),
                "base_count": len(prof_data.get("base_professions", {})),
                "elite_count": len(prof_data.get("elite_specs", {})),
            },
            "buffs": {
                "version": buff_data.get("version"),
                "count": len(buff_data.get("buffs", {})),
                "categories": list(buff_data.get("categories", {}).keys()),
            },
            "cache_stats": self._cache.get_stats(),
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        # 功能：获取缓存统计信息
        return self._cache.get_stats()


# 全局单例
_game_data_service: Optional[GameDataService] = None


def get_game_data_service() -> GameDataService:
    # 功能：获取游戏数据服务单例
    global _game_data_service
    if _game_data_service is None:
        _game_data_service = GameDataService()
    return _game_data_service


def reload_game_data_service() -> Dict[str, Any]:
    # 功能：重新加载游戏数据服务
    global _game_data_service
    if _game_data_service is not None:
        _game_data_service.reload_all_data()
    return get_game_data_service().get_data_info()
