# -*- coding: utf-8 -*-
"""
Build 图书馆数据初始化?

功能说明?
- 应用启动时自动检?builds 表是否为?
- 若为空，则从种子数据包读取配置数据并自动入库
- 直接调用 BDCodeService（无需 HTTP API），确保启动阶段可用

作? System
创建日期: 22026-05-06
更新日期: 22026-05-12 - ?JSON 文件迁移?seed_data 模块
"""

from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.data import seed_data
from app.models.game_data.build import Build
from app.services.game_data.build_service import create_build
from app.services.game_data.bdcode_service import get_bdcode_service
from app.utils.logger import logger


class BuildDataInitializer:
    """Build 数据初始化器"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.bdcode_service = get_bdcode_service()

    def init_builds(self) -> Dict[str, Any]:
        """
        初初始化builds 数据
        - ?builds 表已有数据，则跳?
        - 若为空，则从种子数据包读取并导入

        Returns:
            {"initialized": bool, "count": int, "errors": List[str]}
        """
        try:
            existing = self.db.query(Build).count()
            if existing > 0:
                logger.info(f"Builds 表已?{existing} 条数据，跳过自动初初始化)
                return {"initialized": False, "count": 0, "errors": []}

            logger.info("Builds 表为空，开始从种子数据包自动导入配置数据..")
            builds_data = seed_data.get_builds_initial()
            logger.info(f"成功从种子数据包加载 {len(builds_data)} 条配置数据)
            success, failure, errors = self._import_builds(builds_data)

            if failure == 0:
                logger.info(f"Build 数据自动初始化完成 成功导入 {success} 条配置)
            else:
                logger.warning(f"Build 数据初始化完成 {success} 成功, {failure} 失败")

            return {"initialized": True, "count": success, "errors": errors}

        except Exception as e:
            logger.error(f"Build 数据初始化异? {e}")
            return {"initialized": False, "count": 0, "errors": [str(e)]}
        finally:
            if self.db:
                self.db.close()

    # ------------------------------------------------------------------
    # 内部方法：数据导入
    # ------------------------------------------------------------------

    def _parse_bd_code(self, bd_code: str) -> Optional[Dict[str, Any]]:
        """直接调用 BDCodeService 解析（无需 HTTP API?""
        try:
            result = self.bdcode_service.parse_bdcode(bd_code, include_icons=False)
            if result.get("success"):
                return result.get("data")
        except Exception as e:
            logger.warning(f"BD Code 解析失败 [{bd_code[:30]}...]: {e}")
        return None

    def _build_data_to_db_format(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ?JSON 数据转换为数据库格式
        JSON 文件已经与数据库表结构兼容，只需确保字段完整
        """
        # 基础字段（直接从 JSON 获取?
        result = {
            "slug": raw_data.get("slug", ""),
            "title": raw_data.get("title", ""),
            "profession": raw_data.get("profession", ""),
            "profession_color": raw_data.get("profession_color"),
            "elite_spec": raw_data.get("elite_spec"),
            "role": raw_data.get("role", "dps"),
            "sub_roles": raw_data.get("sub_roles", []),
            "armor_type": raw_data.get("armor_type", ""),
            "weapons": raw_data.get("weapons", []),
            "relic": raw_data.get("relic", ""),
            "rune": raw_data.get("rune", ""),
            "food": raw_data.get("food", ""),
            "wrench": raw_data.get("wrench", ""),
            "infusion": raw_data.get("infusion", ""),
            "attr_requirements": raw_data.get("attr_requirements", []),
            "bd_code": raw_data.get("bd_code", ""),
            "trait_lines": raw_data.get("trait_lines", []),
            "rotation_commands": raw_data.get("rotation_commands", []),
            "mechanics": raw_data.get("mechanics", []),
            "videos": raw_data.get("videos", []),
            "author": raw_data.get("author", ""),
            "word_count": raw_data.get("word_count", 0),
            "is_meta": raw_data.get("is_meta", False),
        }

        # 如果没有解析特性线且有 BD Code，尝试解?
        if not result["trait_lines"] and result["bd_code"]:
            api_data = self._parse_bd_code(result["bd_code"])
            if api_data:
                # 更新职业信息（如?JSON 中未设置?
                if not result["profession"]:
                    result["profession"] = api_data.get("profession", "")

                # 更新职业颜色（如?JSON 中未设置?
                if not result["profession_color"]:
                    color_map = {
                        "Warrior": "#E85D04", "Guardian": "#FAA307", "Revenant": "#9D4EDD",
                        "Ranger": "#06D6A0", "Engineer": "#7B8FA1", "Necromancer": "#8D0801",
                        "Mesmer": "#4361EE", "Elementalist": "#FF6B6B", "Thief": "#C0363D",
                    }
                    result["profession_color"] = color_map.get(result["profession"], "#888888")

                # 更新精英特长（如?JSON 中未设置?
                if not result["elite_spec"]:
                    specs = api_data.get("specializations", [])
                    elite = next((s for s in specs if s.get("is_elite")), None)
                    if elite:
                        result["elite_spec"] = elite.get("name_cn") or elite.get("name")

                # 解析特性线
                result["trait_lines"] = []
                for s in api_data.get("specializations", []):
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
                db_data = self._build_data_to_db_format(raw)

                # 验证必填字段
                if not db_data["title"] or not db_data["bd_code"] or not db_data["profession"]:
                    raise ValueError("缺少必填字段（title/bd_code/profession?)

                build = create_build(self.db, db_data)
                logger.info(f"[{idx}/{len(builds_data)}] 导入成功: {build.title} (id={build.id})")
                success_count += 1
            except Exception as e:
                err_msg = f"[{idx}/{len(builds_data)}] 导入失败: {raw.get('title', 'Unknown')} - {e}"
                logger.error(err_msg)
                errors.append(err_msg)
                failure_count += 1

        return success_count, failure_count, errors
