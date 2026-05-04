# -*- coding: utf-8 -*-
"""
Build 图书馆数据初始化器

功能说明：
- 应用启动时自动检测 builds 表是否为空
- 若为空，则从 tests/GW2.txt 解析配置数据并自动入库
- 直接调用 BDCodeService（无需 HTTP API），确保启动阶段可用
- author 字段统一设为空字符串

作者: System
创建日期: 2026-05-05
"""

import os
import re
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.build import Build
from app.services.build_service import create_build
from app.services.game_data.bdcode_service import get_bdcode_service
from app.utils.logger import logger

# GW2.txt 路径（相对 backend 根目录）
GW2_TXT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tests", "GW2.txt"
)


class BuildDataInitializer:
    """Build 数据初始化器"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.bdcode_service = get_bdcode_service()

    def init_builds(self) -> Dict[str, Any]:
        """
        初始化 builds 数据
        - 若 builds 表已有数据，则跳过
        - 若为空，则解析 GW2.txt 并导入

        Returns:
            {"initialized": bool, "count": int, "errors": List[str]}
        """
        try:
            existing = self.db.query(Build).count()
            if existing > 0:
                logger.info(f"Builds 表已有 {existing} 条数据，跳过自动初始化")
                return {"initialized": False, "count": 0, "errors": []}

            if not os.path.exists(GW2_TXT_PATH):
                logger.warning(f"GW2.txt 数据文件不存在: {GW2_TXT_PATH}")
                return {"initialized": False, "count": 0, "errors": ["数据文件不存在"]}

            logger.info("Builds 表为空，开始从 GW2.txt 自动导入配置数据...")
            builds_data = self._parse_gw2_txt(GW2_TXT_PATH)
            success, failure, errors = self._import_builds(builds_data)

            if failure == 0:
                logger.info(f"Build 数据自动初始化完成: 成功导入 {success} 条配置")
            else:
                logger.warning(f"Build 数据初始化完成: {success} 成功, {failure} 失败")

            return {"initialized": True, "count": success, "errors": errors}

        except Exception as e:
            logger.error(f"Build 数据初始化异常: {e}")
            return {"initialized": False, "count": 0, "errors": [str(e)]}
        finally:
            if self.db:
                self.db.close()

    # ------------------------------------------------------------------
    # 内部方法：GW2.txt 解析
    # ------------------------------------------------------------------

    def _extract_weapons(self, text: str) -> List[Dict[str, Any]]:
        """从描述文本中提取武器配置"""
        weapons = []

        weapon_prefix = re.search(r'武器[\s:：]+(.+?)(?:符文|古物|宠物|$)', text)
        if weapon_prefix:
            weapon_text = weapon_prefix.group(1)
        else:
            weapon_text = text

        weapon_pattern = re.compile(r'([\u4e00-\u9fa5a-zA-Z]+(?:\d)?)[\s]*(?:（|\()([^）)]+)(?:）|\))')
        matches = list(weapon_pattern.finditer(weapon_text))

        if len(matches) >= 2:
            for i in range(0, len(matches), 2):
                if i + 1 < len(matches):
                    between = weapon_text[matches[i].end():matches[i+1].start()]
                    if '+' in between or '＋' in between or '、' in between or len(between.strip()) < 5:
                        for j in [i, i+1]:
                            m = matches[j]
                            w_name = m.group(1).strip()
                            sigils_raw = m.group(2)
                            sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                            weapons.append({"set": len(weapons) + 1, "name": w_name, "sigils": sigils})
                        break
            else:
                for i, m in enumerate(matches):
                    w_name = m.group(1).strip()
                    sigils_raw = m.group(2)
                    sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
                    weapons.append({"set": i + 1, "name": w_name, "sigils": sigils})
        elif len(matches) == 1:
            m = matches[0]
            w_name = m.group(1).strip()
            sigils_raw = m.group(2)
            sigils = [s.strip() for s in re.split(r'[、/,]', sigils_raw) if s.strip()]
            weapons.append({"set": 1, "name": w_name, "sigils": sigils})

        return weapons

    def _parse_gw2_txt(self, path: str) -> List[Dict[str, Any]]:
        """解析 GW2.txt 文件"""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        builds = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("=") or line.startswith("-"):
                i += 1
                continue

            bd_match = re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', line)
            if bd_match:
                bd_code = bd_match.group(1)

                # 向前找标题
                title = None
                j = i - 1
                while j >= 0:
                    prev = lines[j].strip()
                    if prev and not prev.startswith("=") and not prev.startswith("-"):
                        if not re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', prev):
                            title = prev
                            break
                    j -= 1

                title = (title or "未命名配置").rstrip("：:").strip()

                # 向后找描述
                desc_lines = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if next_line.startswith("=") or next_line.startswith("-"):
                        break
                    if re.match(r'^(\[&[A-Za-z0-9+/=]+\])$', next_line):
                        break
                    if next_line.startswith("循环"):
                        j += 1
                        while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("="):
                            j += 1
                        break
                    desc_lines.append(next_line)
                    j += 1

                description = " ".join(desc_lines)
                build = {"title": title, "bd_code": bd_code, "description": description}

                # 护甲类型
                for pattern in [r'([^（\s]*?套)', r'(全[\u4e00-\u9fa5]+)', r'([^\s]*混搭)', r'([^\s]*者套)']:
                    armor_match = re.search(pattern, description)
                    if armor_match:
                        build["armor_type"] = armor_match.group(1).strip()
                        break

                # 武器、符文、古物
                build["weapons"] = self._extract_weapons(description)
                rune_match = re.search(r'(?:[^\u4e00-\u9fa5]|^)([\u4e00-\u9fa5]+符文)', description)
                if rune_match:
                    build["rune"] = rune_match.group(1).strip()
                relic_match = re.search(r'古物[：:\s]+([\u4e00-\u9fa5]+(?:[/|\\][\u4e00-\u9fa5]+)?)', description)
                if relic_match:
                    build["relic"] = relic_match.group(1).strip()

                builds.append(build)
                i = j
            else:
                i += 1

        return builds

    # ------------------------------------------------------------------
    # 内部方法：数据导入
    # ------------------------------------------------------------------

    def _parse_bd_code(self, bd_code: str) -> Optional[Dict[str, Any]]:
        """直接调用 BDCodeService 解析（无需 HTTP API）"""
        try:
            result = self.bdcode_service.parse_bdcode(bd_code, include_icons=False)
            if result.get("success"):
                return result.get("data")
        except Exception as e:
            logger.warning(f"BD Code 解析失败 [{bd_code[:30]}...]: {e}")
        return None

    def _build_data_to_db_format(self, parsed: Dict[str, Any], api_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """将解析数据组合为数据库格式"""
        result = {
            "title": parsed["title"],
            "bd_code": parsed["bd_code"],
            "author": "",
            "armor_type": parsed.get("armor_type", ""),
            "weapons": parsed.get("weapons", []),
            "rune": parsed.get("rune", ""),
            "relic": parsed.get("relic", ""),
            "food": "",
            "wrench": "",
            "infusion": "",
            "attr_requirements": [],
            "trait_lines": [],
            "rotation_commands": [],
            "mechanics": [],
            "videos": [],
            "sub_roles": [],
            "is_meta": False,
            "profession": "",
            "profession_color": None,
            "elite_spec": None,
            "role": "dps",
        }

        if api_data:
            profession = api_data.get("profession")
            if profession:
                result["profession"] = profession
                color_map = {
                    "Warrior": "#E85D04", "Guardian": "#FAA307", "Revenant": "#9D4EDD",
                    "Ranger": "#06D6A0", "Engineer": "#7B8FA1", "Necromancer": "#8D0801",
                    "Mesmer": "#4361EE", "Elementalist": "#FF6B6B", "Thief": "#C0363D",
                }
                result["profession_color"] = color_map.get(profession, "#888888")

            specs = api_data.get("specializations", [])
            elite = next((s for s in specs if s.get("is_elite")), None)
            if elite:
                result["elite_spec"] = elite.get("name_cn") or elite.get("name")

            result["trait_lines"] = []
            for s in specs:
                traits = s.get("selected_traits", [])
                if len(traits) == 3:
                    result["trait_lines"].append({
                        "name": s.get("name_cn") or s.get("name") or "",
                        "choices": [int(t) for t in traits]
                    })

        return result

    def _import_builds(self, builds_data: List[Dict[str, Any]]) -> tuple:
        """导入配置数据到数据库"""
        success_count = 0
        failure_count = 0
        errors = []

        for idx, raw in enumerate(builds_data, 1):
            try:
                api_data = self._parse_bd_code(raw["bd_code"])
                if api_data:
                    logger.info(f"[{idx}/{len(builds_data)}] BD解析成功: {raw['title']} -> {api_data.get('profession', 'Unknown')}")
                else:
                    logger.warning(f"[{idx}/{len(builds_data)}] BD解析失败或跳过: {raw['title']}")

                db_data = self._build_data_to_db_format(raw, api_data)
                build = create_build(self.db, db_data)
                logger.info(f"[{idx}/{len(builds_data)}] 导入成功: {build.title} (id={build.id})")
                success_count += 1
            except Exception as e:
                err_msg = f"[{idx}/{len(builds_data)}] 导入失败: {raw.get('title', 'Unknown')} - {e}"
                logger.error(err_msg)
                errors.append(err_msg)
                failure_count += 1

        return success_count, failure_count, errors
