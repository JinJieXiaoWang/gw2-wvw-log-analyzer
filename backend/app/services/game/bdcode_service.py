# -*- coding: utf-8 -*-
# 模块功能：激战2 BD码解析服务层
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：json, base64, struct, pathlib, cache
# 核心功能：BD码格式验证、解析、数据匹配、多级缓存
import base64
import json
import struct
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.data import DATA_DIR, load_json_file
from app.services.game.game_data_service import get_global_cache
from app.utils.logger import logger

# =============================================================================
# 职业数字 ID → 英文 ID 映射
# =============================================================================
PROF_NUM_TO_STR = {
    1: "Guardian",
    2: "Warrior",
    3: "Engineer",
    4: "Ranger",
    5: "Thief",
    6: "Elementalist",
    7: "Mesmer",
    8: "Necromancer",
    9: "Revenant",
}

PROF_STR_TO_CN = {
    "Guardian": "守护者",
    "Warrior": "战士",
    "Engineer": "工程师",
    "Ranger": "游侠",
    "Thief": "潜行者",
    "Elementalist": "元素使",
    "Mesmer": "幻术师",
    "Necromancer": "唤灵师",
    "Revenant": "魂武者",
}


# =============================================================================
# 数据类定义
# =============================================================================
@dataclass
class TraitInfo:
    id: int
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    is_selected: bool = False


@dataclass
class SpecializationInfo:
    id: int
    name: str
    name_cn: Optional[str] = None
    icon: Optional[str] = None
    is_elite: bool = False
    selected_traits: List[int] = None
    traits: List[TraitInfo] = None


@dataclass
class SkillInfo:
    id: Optional[int] = None
    palette_id: Optional[int] = None
    name: Optional[str] = None
    name_cn: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    slot: Optional[str] = None
    recharge: int = 0


@dataclass
class BuildInfo:
    bd_code: str
    profession_id: int
    profession: str
    profession_cn: str
    specializations: List[SpecializationInfo]
    skills: Dict[str, Any]


# =============================================================================
# BD码解析器（严格按照原版本实现）
# =============================================================================
class GW2BuildParser:
    """激战2 BD码解析器"""

    SPEC_OFFSET = 2
    SPEC_STRIDE = 2
    SKILL_OFFSET = 8
    SKILL_COUNT = 10  # terrestrial(5) + aquatic(5), interleaved

    @staticmethod
    def parse(code: str, debug: bool = False) -> dict:
        try:
            raw = code.strip().replace("[&", "").replace("]", "")
            rem = len(raw) % 4
            if rem:
                raw += "=" * (4 - rem)
            data = base64.b64decode(raw)

            if debug:
                logger.debug(f"BD码原始字节（共 {len(data)} 字节）")

            result = {
                "profession_num_id": data[1] if len(data) >= 2 else None,
                "specializations": [],
                "skills": {"heal": None, "utility": [], "elite": None},
            }

            # 解析3条特长线
            # 注意：mask字节的低2位=层1选择，中2位=层2选择，高2位=层3选择
            for i in range(3):
                off = GW2BuildParser.SPEC_OFFSET + i * GW2BuildParser.SPEC_STRIDE
                spec_id = data[off] if off < len(data) else 0
                mask = data[off + 1] if off + 1 < len(data) else 0

                t1 = (mask >> 0) & 0x3  # 低2位 = 层1选择
                t2 = (mask >> 2) & 0x3  # 中间2位 = 层2选择
                t3 = (mask >> 4) & 0x3  # 高2位 = 层3选择

                result["specializations"].append(
                    {
                        "id": spec_id,
                        "selected": [t1, t2, t3],
                    }
                )

            # 解析技能
            # GW2 build template v3: 10个skill交错排列
            # 0:Terrestrial Heal, 1:Aquatic Heal,
            # 2:Terrestrial Utility 1, 3:Aquatic Utility 1,
            # 4:Terrestrial Utility 2, 5:Aquatic Utility 2,
            # 6:Terrestrial Utility 3, 7:Aquatic Utility 3,
            # 8:Terrestrial Elite, 9:Aquatic Elite
            all_skills = []
            off = GW2BuildParser.SKILL_OFFSET
            for idx in range(GW2BuildParser.SKILL_COUNT):
                palette_id = None
                if off + 2 <= len(data):
                    val = struct.unpack("<H", data[off : off + 2])[0]
                    palette_id = val if val != 0 else None
                all_skills.append(palette_id)
                off += 2

            # 提取 terrestrial skills（偶数索引）
            result["skills"]["heal"] = all_skills[0]
            result["skills"]["utility"] = [all_skills[2], all_skills[4], all_skills[6]]
            result["skills"]["elite"] = all_skills[8]

            return result
        except Exception as e:
            logger.error(f"BD码解析异常: {e}")
            raise


# =============================================================================
# 本地数据加载器
# =============================================================================
class GW2LocalDataLoader:
    """本地游戏数据加载器"""

    def __init__(self):
        self._skills: Optional[List[Dict]] = None
        self._specializations: Optional[List[Dict]] = None
        self._traits: Optional[List[Dict]] = None
        self._skill_idx: Optional[Dict[int, Dict]] = None
        self._spec_idx: Optional[Dict[int, Dict]] = None
        self._trait_idx: Optional[Dict[int, Dict]] = None
        self._palette_map: Optional[Dict[str, Dict[int, int]]] = None

    def _load_all_data(self) -> None:
        # 加载所有数据（懒加载）
        if self._skills is not None:
            return

        try:
            self._skills = load_json_file("bdcode_skills.json")
            self._specializations = load_json_file("bdcode_specializations.json")
            self._traits = load_json_file("bdcode_traits.json")
            palette_list = load_json_file("skill_palettes.json")

            # 构建索引
            self._skill_idx = {s["id"]: s for s in self._skills}
            self._spec_idx = {s["id"]: s for s in self._specializations}
            self._trait_idx = {t["id"]: t for t in self._traits}

            # 构建调色板映射（按职业分组，避免不同职业palette_id冲突）
            self._palette_map = {}
            for entry in palette_list:
                p_id = entry.get("palette_id")
                s_id = entry.get("skill_id")
                prof = entry.get("profession", "Unknown")
                if p_id and s_id:
                    if prof not in self._palette_map:
                        self._palette_map[prof] = {}
                    self._palette_map[prof][p_id] = s_id

            logger.info(f"本地数据加载完成:")
            logger.info(f"  技能: {len(self._skill_idx)}")
            logger.info(f"  特长线: {len(self._spec_idx)}")
            logger.info(f"  特性: {len(self._trait_idx)}")
            logger.info(f"  调色板映射: {len(self._palette_map)}")

        except Exception as e:
            logger.error(f"数据加载异常: {e}")
            self._skills = []
            self._specializations = []
            self._traits = []
            self._skill_idx = {}
            self._spec_idx = {}
            self._trait_idx = {}
            self._palette_map = {}

    def get_skill(
        self, palette_id: Optional[int], profession: Optional[str] = None
    ) -> Optional[Dict]:
        """根据调色板ID获取技能信息

        Args:
            palette_id: 调色板ID
            profession: 职业英文名称，用于区分不同职业的palette_id
        """
        self._load_all_data()
        if palette_id is None:
            return None

        # 优先按职业查找，避免palette_id冲突
        if profession and profession in self._palette_map:
            skill_id = self._palette_map[profession].get(palette_id, palette_id)
        else:
            # 回退：在所有职业中查找（取第一个匹配）
            skill_id = palette_id
            for prof_map in self._palette_map.values():
                if palette_id in prof_map:
                    skill_id = prof_map[palette_id]
                    break
        return self._skill_idx.get(skill_id)

    def get_spec(self, spec_id: int) -> Dict:
        """获取特长线信息"""
        self._load_all_data()
        empty = {"name": "未选择", "icon": "", "elite": False}
        if not spec_id:
            return empty
        return self._spec_idx.get(
            spec_id, {"name": f"特长[ID:{spec_id}]", "icon": "", "elite": False}
        )

    def get_spec_traits(
        self, spec_id: int, selected: List[int]
    ) -> Dict[str, List[Dict]]:
        """获取特长线的特性数据"""
        self._load_all_data()
        spec = self._spec_idx.get(spec_id, {})
        major_ids = spec.get("major_traits", [])
        minor_ids = spec.get("minor_traits", [])

        return {
            "major": [self._trait_idx.get(tid, {}) for tid in major_ids],
            "minor": [self._trait_idx.get(tid, {}) for tid in minor_ids],
        }


# =============================================================================
# BD码解析服务
# =============================================================================
class BDCodeService:
    """BD码解析服务"""

    def __init__(self):
        self._parser = GW2BuildParser()
        self._loader = GW2LocalDataLoader()
        self._cache = get_global_cache()

    def validate_bdcode(self, bd_code: str) -> Dict[str, Any]:
        """
        验证BD码格式
        返回: {'is_valid': bool, 'error': str}
        """
        try:
            bd_code = bd_code.strip()
            if not bd_code:
                return {"is_valid": False, "error": "BD码不能为空"}

            if not (bd_code.startswith("[&") and bd_code.endswith("]")):
                return {"is_valid": False, "error": "BD码格式不正确，应为 [&...]"}

            raw = bd_code.replace("[&", "").replace("]", "")
            if len(raw) < 5:
                return {"is_valid": False, "error": "BD码内容过短"}

            rem = len(raw) % 4
            if rem:
                raw += "=" * (4 - rem)
            try:
                base64.b64decode(raw)
            except Exception as e:
                return {"is_valid": False, "error": f"BD码编码格式错误: {str(e)}"}

            return {"is_valid": True, "error": None}
        except Exception as e:
            return {"is_valid": False, "error": f"BD码验证失败: {str(e)}"}

    def parse_bdcode(self, bd_code: str, include_icons: bool = True) -> Dict[str, Any]:
        """
        解析BD码
        参数:
            bd_code: BD码字符串
            include_icons: 是否包含图标URL
        返回:
            完整的Build信息
        """
        cache_key = f"bdcode:parse:{hash(bd_code)}:{include_icons}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        validation = self.validate_bdcode(bd_code)
        if not validation["is_valid"]:
            result = {
                "success": False,
                "error": validation["error"],
                "bd_code": bd_code,
            }
            self._cache.set(cache_key, result)
            return result

        try:
            parse_result = self._parser.parse(bd_code)
            build_info = self._build_full_info(bd_code, parse_result, include_icons)

            result = {"success": True, "data": asdict(build_info), "bd_code": bd_code}
            self._cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"BD码解析异常: {e}")
            result = {
                "success": False,
                "error": f"解析失败: {str(e)}",
                "bd_code": bd_code,
            }
            return result

    def _build_full_info(
        self, bd_code: str, parse_result: Dict, include_icons: bool
    ) -> BuildInfo:
        """构建完整的Build信息"""
        prof_num = parse_result.get("profession_num_id", 0)
        prof_str = PROF_NUM_TO_STR.get(prof_num, "Unknown")
        prof_cn = PROF_STR_TO_CN.get(prof_str, "未知职业")

        # 构建特长线信息
        specs = []
        for spec_data in parse_result.get("specializations", []):
            spec_id = spec_data["id"]
            spec_info = self._loader.get_spec(spec_id)
            selected = spec_data["selected"]

            if spec_id > 0:
                # 获取特性
                traits_data = self._loader.get_spec_traits(spec_id, selected)
                major = traits_data.get("major", [])
                minor = traits_data.get("minor", [])

                trait_list = []
                for i in range(3):
                    if selected[i] > 0:
                        idx = i * 3 + (selected[i] - 1)
                        if idx < len(major) and major[idx]:
                            trait = TraitInfo(
                                id=major[idx].get("id", 0),
                                name=major[idx].get("name", ""),
                                icon=major[idx].get("icon") if include_icons else None,
                                description=major[idx].get("description"),
                                is_selected=True,
                            )
                            trait_list.append(trait)

                specs.append(
                    SpecializationInfo(
                        id=spec_id,
                        name=spec_info.get("name", ""),
                        name_cn=spec_info.get("name", ""),
                        icon=spec_info.get("icon") if include_icons else None,
                        is_elite=spec_info.get("elite", False),
                        selected_traits=selected,
                        traits=trait_list,
                    )
                )
            else:
                specs.append(
                    SpecializationInfo(
                        id=0,
                        name="未选择",
                        name_cn="未选择",
                        selected_traits=[0, 0, 0],
                        traits=[],
                    )
                )

        # 构建技能信息
        skills_data = parse_result.get("skills", {})
        skills = {
            "heal": self._get_skill_info(
                skills_data.get("heal"), include_icons, prof_str
            ),
            "utility": [
                self._get_skill_info(p, include_icons, prof_str)
                for p in skills_data.get("utility", [])
            ],
            "elite": self._get_skill_info(
                skills_data.get("elite"), include_icons, prof_str
            ),
        }

        return BuildInfo(
            bd_code=bd_code,
            profession_id=prof_num,
            profession=prof_str,
            profession_cn=prof_cn,
            specializations=specs,
            skills=skills,
        )

    def _get_skill_info(
        self,
        palette_id: Optional[int],
        include_icons: bool,
        profession: Optional[str] = None,
    ) -> Optional[SkillInfo]:
        """获取技能信息"""
        if palette_id is None:
            return None

        skill_data = self._loader.get_skill(palette_id, profession)
        if skill_data is None:
            return SkillInfo(palette_id=palette_id, name=f"技能[ID:{palette_id}]")

        recharge = 0
        for fact in skill_data.get("facts") or []:
            if fact.get("type") == "Recharge":
                recharge = fact.get("value", 0)
                break

        return SkillInfo(
            id=skill_data.get("id"),
            palette_id=palette_id,
            name=skill_data.get("name"),
            name_cn=skill_data.get("name"),
            icon=skill_data.get("icon") if include_icons else None,
            description=skill_data.get("description"),
            slot=skill_data.get("slot"),
            recharge=recharge,
        )


# 全局单例
_bdcode_service: Optional[BDCodeService] = None


def get_bdcode_service() -> BDCodeService:
    """获取BD码解析服务单例"""
    global _bdcode_service
    if _bdcode_service is None:
        _bdcode_service = BDCodeService()
    return _bdcode_service
