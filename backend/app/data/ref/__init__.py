# -*- coding: utf-8 -*-
"""
GW2 参考数据模块

存放从 gw2_data 复制的装备参考数据，用于 Build 图书馆等场景的装备查询。
数据以扁平 JSON mapping 格式存储，运行时懒加载到内存。

与 seeds/ 目录的区别：
- seeds/: 数据库初始化数据，有 _meta + data 结构，通过 SeedDataLoader 加载到 DB
- ref/:   内存参考数据，无结构约束，通过 GW2RefDataLoader 懒加载到内存
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.utils.logger import logger

REF_DATA_DIR = Path(__file__).parent


class GW2RefDataLoader:
    """GW2 参考数据懒加载器

    按需加载 ref/ 目录下的 JSON 文件，首次访问时加载到内存缓存。
    所有数据为只读，不支持热重载（数据变更频率极低）。
    """

    _cache: Dict[str, Any] = {}

    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        """加载指定参考数据文件

        Args:
            name: 数据名（如 "runes", "sigils", "relics", "food", "utilities"）

        Returns:
            dict: 解析后的 JSON 数据。文件不存在时返回空字典。
        """
        if name in cls._cache:
            return cls._cache[name]

        path = REF_DATA_DIR / f"{name}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._cache[name] = data
            logger.debug(f"[GW2RefDataLoader] 加载成功: {name}.json ({len(data)} entries)")
            return data
        except FileNotFoundError:
            logger.warning(f"[GW2RefDataLoader] 文件不存在: {path}")
            cls._cache[name] = {}
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"[GW2RefDataLoader] JSON 解析失败: {path}, {e}")
            cls._cache[name] = {}
            return {}

    @classmethod
    def get_names(cls, name: str) -> List[str]:
        """获取指定数据类型的所有名称列表"""
        data = cls.load(name)
        names = []
        for entry in data.values():
            if isinstance(entry, dict):
                item_name = entry.get("name")
                if item_name:
                    names.append(item_name)
            elif isinstance(entry, str):
                names.append(entry)
        return sorted(set(names))

    @classmethod
    def search_by_name(cls, name: str, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """按名称关键字搜索参考数据

        Args:
            name: 数据类型（如 "food"）
            keyword: 搜索关键字
            limit: 最大返回数量

        Returns:
            list: 匹配结果列表，每项包含 name, icon 等字段
        """
        data = cls.load(name)
        keyword_lower = keyword.lower()
        results = []
        for key, entry in data.items():
            if isinstance(entry, dict):
                item_name = entry.get("name", "")
                if keyword_lower in item_name.lower():
                    results.append({"id": key, **entry})
                    if len(results) >= limit:
                        break
        return results

    @classmethod
    def get_by_id(cls, name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """按 ID 获取参考数据条目"""
        data = cls.load(name)
        entry = data.get(str(item_id))
        if isinstance(entry, dict):
            return {"id": str(item_id), **entry}
        return None

    @classmethod
    def clear_cache(cls) -> None:
        """清空内存缓存（用于测试或数据更新后）"""
        cls._cache.clear()
        logger.info("[GW2RefDataLoader] 内存缓存已清空")
