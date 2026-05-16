# -*- coding: utf-8 -*-
"""GW2 参考数据服务层（内存缓存，不进入数据库）

为 Build 图书馆装备解析提供 gw2_data 数据支撑。
数据来源于 backend/app/data/ref/ 下的精简 mapping 文件。
"""

from typing import Any, Dict, List, Optional

from app.data.ref import REF_DATA_DIR


class GW2RefDataLoader:
    """GW2 参考数据加载器 — 懒加载 + 类级内存缓存"""

    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        """加载指定名称的 JSON 数据文件到内存"""
        import json

        if name not in cls._cache:
            path = REF_DATA_DIR / f"{name}.json"
            if not path.exists():
                raise FileNotFoundError(f"Ref data file not found: {name}.json")
            with open(path, "r", encoding="utf-8") as f:
                cls._cache[name] = json.load(f)
        return cls._cache[name]

    @classmethod
    def get_rune(cls, rune_id: str) -> Optional[Dict[str, Any]]:
        """根据 GW2 API 物品 ID 查询符文"""
        data = cls.load("runes")
        return data.get(str(rune_id))

    @classmethod
    def get_sigil(cls, sigil_id: str) -> Optional[Dict[str, Any]]:
        """根据 GW2 API 物品 ID 查询法印"""
        data = cls.load("sigils")
        return data.get(str(sigil_id))

    @classmethod
    def get_relic(cls, relic_id: str) -> Optional[Dict[str, Any]]:
        """根据 GW2 API 物品 ID 查询古物"""
        data = cls.load("relics")
        return data.get(str(relic_id))

    @classmethod
    def get_food(cls, food_id: str) -> Optional[Dict[str, Any]]:
        """根据 GW2 API 物品 ID 查询食物"""
        data = cls.load("food")
        return data.get(str(food_id))

    @classmethod
    def get_utility(cls, utility_id: str) -> Optional[Dict[str, Any]]:
        """根据 GW2 API 物品 ID 查询扳手/增强"""
        data = cls.load("utilities")
        return data.get(str(utility_id))

    @classmethod
    def list_runes(cls, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出符文，可选搜索过滤"""
        data = cls.load("runes")
        results = []
        for item_id, item in data.items():
            entry = {"id": item_id, "name": item.get("name", ""), "icon": item.get("icon")}
            if search is None or search.lower() in entry["name"].lower():
                results.append(entry)
        return results[:limit]

    @classmethod
    def list_sigils(cls, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出法印，可选搜索过滤"""
        data = cls.load("sigils")
        results = []
        for item_id, item in data.items():
            entry = {"id": item_id, "name": item.get("name", ""), "icon": item.get("icon")}
            if search is None or search.lower() in entry["name"].lower():
                results.append(entry)
        return results[:limit]

    @classmethod
    def list_relics(cls, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出古物，可选搜索过滤"""
        data = cls.load("relics")
        results = []
        for item_id, item in data.items():
            entry = {"id": item_id, "name": item.get("name", ""), "icon": item.get("icon")}
            if search is None or search.lower() in entry["name"].lower():
                results.append(entry)
        return results[:limit]

    @classmethod
    def list_foods(cls, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出食物，可选搜索过滤（仅返回80级Exotic稀有度）"""
        data = cls.load("food")
        results = []
        for item_id, item in data.items():
            # 过滤低等级食物，只保留80级且有icon的
            level = item.get("level", 0)
            rarity = item.get("rarity", "")
            if level < 70 and rarity != "Ascended":
                continue
            entry = {"id": item_id, "name": item.get("name", ""), "icon": item.get("icon")}
            if search is None or search.lower() in entry["name"].lower():
                results.append(entry)
        return results[:limit]

    @classmethod
    def list_utilities(cls, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出扳手/增强，可选搜索过滤（排除区域专用屠戮药剂）"""
        data = cls.load("utilities")
        results = []
        for item_id, item in data.items():
            name = item.get("name", "")
            # 排除区域专用屠戮药剂
            if "屠戮" in name:
                continue
            level = item.get("level", 0)
            if level < 70:
                continue
            entry = {"id": item_id, "name": name, "icon": item.get("icon")}
            if search is None or search.lower() in entry["name"].lower():
                results.append(entry)
        return results[:limit]
