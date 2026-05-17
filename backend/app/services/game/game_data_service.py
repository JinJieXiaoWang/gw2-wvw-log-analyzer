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

from sqlalchemy.orm import Session

from app.data import DATA_DIR, get_data_version
from app.core.initialization import SeedDataLoader
from app.models.game.profession import (
    GwEliteSpecialization,
    GwProfession,
)

# 导入 ProfessionService 进行数据库查询
from app.services.game.profession_service import ProfessionService
from app.services.game.buff_mapper_service import get_global_buff_mapper
from app.utils.logger import logger

# =============================================================================
# 游戏数据服务（增强版）
# =============================================================================
class GameDataService:
    # 功能：游戏数据服务类（增强版，支持多级缓存和热更新）

    def __init__(self, db: Optional[Session] = None):
        self._professions_data: Optional[Dict] = None
        self._buffs_data: Optional[Dict] = None
        self._last_reload: Optional[datetime] = None
        self._buff_mapper = get_global_buff_mapper()
        self._lock = threading.RLock()
        self._db = db  # 数据库会话（可选，用于从数据库读取职业数据）

        self._buff_name_to_id_cache: Dict[str, int] = {}
        self._buff_name_en_to_cn_cache: Dict[str, str] = {}
        self._profession_name_to_data_cache: Dict[str, Dict] = {}

        # 尝试从字典表加载 buff 映射到全局 buff mapper
        self._load_buff_mappings_from_dict()

    def _load_buff_mappings_from_dict(self) -> None:
        """从 gw_buff 表加载 buff 名称映射到全局 BuffNameMapper

        注意：不再从 sys_dict_data 字典表加载，因为字典表数据可能过时。
        gw_buff 表的数据来源于 game_static_buffs 种子数据，是权威数据源。
        """
        try:
            from app.config.database import SessionLocal
            from app.models.game.game_static_data import GwBuff

            db = SessionLocal()
            try:
                buffs = db.query(GwBuff).all()
                if buffs:
                    mappings = {}
                    for buff in buffs:
                        if buff.name:
                            mappings[buff.id] = buff.name
                    if mappings:
                        self._buff_mapper.update_mappings(mappings)
                        logger.debug(f"从 gw_buff 表加载了 {len(mappings)} 条 buff 映射")
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"从 gw_buff 表加载 buff 映射失败: {e}")

    def _get_professions_data(self, force_reload: bool = False) -> Dict:
        # 功能：获取职业数据（内部方法，带缓存） - 从数据库读取
        # 性能优化：使用数据库索引查询，避免全表扫描
        # 错误处理：捕获数据库连接异常，提供详细日志
        if self._professions_data is None or force_reload:
            with self._lock:
                # 双重检查锁定，确保线程安全
                if self._professions_data is None or force_reload:
                    try:
                        if not self._db:
                            # 没有数据库会话，返回空数据（静默处理，不记录错误日志）
                            logger.debug("职业数据加载：未提供数据库会话，返回空数据")
                            self._professions_data = {
                                "version": "2.0.0",
                                "base_professions": {},
                                "elite_specs": {},
                            }
                            return self._professions_data
                        
                        logger.debug("开始从数据库查询职业与精英特长数据...")
                        
                        # 从数据库读取职业数据
                        prof_service = ProfessionService(self._db)
                        
                        # 获取所有职业（使用数据库索引优化查询）
                        logger.debug("查询基础职业数据...")
                        professions = prof_service.get_all_professions(include_specs=False, active_only=False)
                        logger.debug(f"查询到 {len(professions)} 个基础职业")
                        
                        # 获取所有精英特长
                        logger.debug("查询精英特长数据...")
                        specs = prof_service.get_all_specs(active_only=False)
                        logger.debug(f"查询到 {len(specs)} 个精英特长")
                        
                        # 构建兼容的数据结构
                        base_professions = {}
                        elite_specs = {}
                        
                        for prof in professions:
                            base_professions[prof["profession_key"]] = {
                                "name": prof["profession_name_en"],
                                "name_cn": prof["profession_name"],
                                "color": prof["color"],
                                "role_type": prof.get("role_type"),
                                "icon": prof["icon"],
                            }
                        
                        for spec in specs:
                            elite_specs[spec["spec_key"]] = {
                                "name": spec["spec_name_en"],
                                "name_cn": spec["spec_name"],
                                "base_profession": spec["profession_key"],
                                "color": spec["color"],
                                "role_type": spec["role_type"],
                                "icon": spec["icon"],
                                "scoring_config": spec["scoring_config"] or {},
                            }
                        
                        self._professions_data = {
                            "version": "2.0.0",
                            "base_professions": base_professions,
                            "elite_specs": elite_specs,
                        }
                        
                        self._last_reload = datetime.now()
                        self._build_profession_caches()
                        
                        logger.info(
                            f"职业数据从数据库加载成功，版本: 2.0.0，基础职业: {len(base_professions)}，精英特长: {len(elite_specs)}"
                        )
                    
                    except Exception as e:
                        logger.error(f"职业数据加载失败（数据库异常）: {e}", exc_info=True)
                        self._professions_data = {
                            "version": "2.0.0",
                            "base_professions": {},
                            "elite_specs": {},
                        }
        return self._professions_data

    def _get_buffs_data(self, force_reload: bool = False) -> Dict:
        # 功能：获取Buff数据（内部方法，带缓存）
        if self._buffs_data is None or force_reload:
            try:
                self._buffs_data = SeedDataLoader.load("game_static_buffs")
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
            name_en = buff.get("name", "")
            name_cn = buff.get("name_cn", "")
            if buff_id:
                self._buff_name_to_id_cache[name_en] = buff_id
                self._buff_name_to_id_cache[name_cn] = buff_id
            if name_en and name_cn:
                self._buff_name_en_to_cn_cache[name_en.lower()] = name_cn

    def reload_all_data(self) -> Dict[str, Any]:
        # 功能：重新加载所有数据（支持热更新）
        logger.info("开始重新加载所有游戏数据...")
        self._professions_data = None
        self._buffs_data = None

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
        data = self._get_professions_data()
        return data.get("base_professions", {}).get(name)

    def get_elite_spec(self, name: str) -> Optional[Dict]:
        # 功能：获取指定精英特长
        data = self._get_professions_data()
        return data.get("elite_specs", {}).get(name)

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
        spec = self.get_elite_spec(name)
        if spec:
            return spec.get("name_cn", name)
        prof = self.get_profession(name)
        if prof:
            return prof.get("name_cn", name)
        return name

    def get_role_type(self, profession_name: str) -> str:
        # 功能：获取精英特长角色定位
        spec = self.get_elite_spec(profession_name)
        if spec:
            return spec.get("role_type") or "dps"
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
        data = self._get_buffs_data()
        return data.get("buffs", {}).get(str(buff_id))

    def get_buff_name_cn(self, buff_id: int) -> str:
        # 功能：获取Buff中文名
        buff = self.get_buff(buff_id)
        if buff:
            return buff.get("name_cn", f"Buff:{buff_id}")
        # 回退到字典表查找
        from app.utils.db.dict_utils import get_dict_label
        dict_name = get_dict_label("buff", str(buff_id))
        return dict_name if dict_name and dict_name != str(buff_id) else f"Buff:{buff_id}"

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
        return {
            "success": True,
            "updated_count": len(mappings),
            "updated_at": datetime.now().isoformat(),
        }

    def get_buff_name_en(self, buff_id: int) -> str:
        # 功能：获取Buff英文名
        return self._buff_mapper.get_name(buff_id)

    def get_buff_name_cn_by_en(self, name_en: str) -> Optional[str]:
        """通过Buff英文名（不区分大小写）查询中文名。

        数据来源于 gw_buff 种子数据，在 _build_buff_caches 时已预加载到内存。
        若未找到匹配，返回 None。
        """
        if not self._buff_name_en_to_cn_cache:
            self._get_buffs_data()
        return self._buff_name_en_to_cn_cache.get(name_en.lower())

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
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        # 功能：获取缓存统计信息（已废弃，始终返回空）
        return {}


# 全局单例
_game_data_service: Optional[GameDataService] = None


def get_game_data_service(db: Optional[Session] = None) -> GameDataService:
    # 功能：获取游戏数据服务单例（支持传入数据库会话）
    global _game_data_service
    if _game_data_service is None or (db and not _game_data_service._db):
        _game_data_service = GameDataService(db)
    return _game_data_service


def reload_game_data_service() -> Dict[str, Any]:
    # 功能：重新加载游戏数据服务
    global _game_data_service
    if _game_data_service is not None:
        _game_data_service.reload_all_data()
    return get_game_data_service().get_data_info()
