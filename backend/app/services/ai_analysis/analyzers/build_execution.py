# -*- coding: utf-8 -*-
"""Build执行效能验证分析器

功能：验证玩家实际战斗表现与Build设计意图的匹配度
- Build理论性能 vs 实际表现差距分析
- 关键装备/技能是否有效利用
- 符文/食物等配置建议
"""

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.models.game.build import Build
from app.services.ai_analysis.data_aggregator import (
    EiJsonExtractor,
    FightStatsAggregator,
)
from app.constants.dict_values import AiBuildType, CheckStatus
from app.utils.db.dict_utils import get_dict_label
from app.utils.logger import logger


class BuildExecutionAnalyzer:
    """Build执行效能验证分析器"""

    # Build类型与期望指标的映射（启发式基准）
    # label 从 AiBuildType Enum 读取，不硬编码中文
    BUILD_EXPECTATIONS = {
        AiBuildType.POWER.value: {
            "expected_power_ratio": 0.7,  # 直伤应占总伤害70%+
            "expected_crit_rate": 0.6,  # 暴击率60%+
            "expected_dps_per_1k_stats": 800,  # 每1k攻击力对应800DPS
        },
        AiBuildType.CONDI.value: {
            "expected_condi_ratio": 0.7,  # 症状应占总伤害70%+
            "expected_avg_conditions": 10,  # 平均症状层数
        },
        AiBuildType.SUPPORT.value: {
            "expected_healing_per_min": 500000,  # 每分钟治疗量
            "expected_boon_uptime": 0.6,  # 增益覆盖率60%+
        },
        AiBuildType.TANK.value: {
            "expected_damage_taken_per_min": 800000,  # 每分钟承伤（拉仇恨）
            "expected_block_evade_rate": 0.3,  # 格挡/闪避率
        },
    }

    def __init__(self, db: Session, orchestrator=None):
        self.db = db
        self.orchestrator = orchestrator

    async def analyze(
        self,
        account: str,
        build_id: Optional[int] = None,
        fight_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        主分析入口

        Args:
            account: 玩家账号
            build_id: 指定Build ID（用于理论性能对比）
            fight_id: 指定战斗ID（用于获取该场表现）
        """
        logger.info(f"开始Build执行验证: account={account}, build_id={build_id}")

        # 1. 获取玩家最近数据
        history = FightStatsAggregator.get_player_history(self.db, account, fight_count=10)
        if not history:
            return self._empty_result(account, "暂无战斗数据")

        # 取最新一场数据
        latest = history[-1]

        # 2. 获取Build信息
        build_info = None
        if build_id:
            build = self.db.query(Build).filter(Build.id == build_id).first()
            if build:
                build_info = self._extract_build_info(build)

        # 3. 识别Build类型
        build_type = self._infer_build_type(latest, build_info)
        expectations = self.BUILD_EXPECTATIONS.get(build_type, self.BUILD_EXPECTATIONS[AiBuildType.POWER.value])

        # 4. 执行效能验证
        execution_check = self._validate_execution(latest, build_type, expectations)

        # 5. 装备/消耗品检查
        equipment_check = self._check_equipment(latest.get("fight_id"), account)

        # 6. 将装备检查转换为checks格式并合并
        execution_check = self._merge_equipment_checks(execution_check, equipment_check, latest, build_info)

        # 7. 构建结果
        result = {
            "account": account,
            "profession": latest.get("profession", ""),
            "build_type": build_type,
            "build_info": build_info,
            "latest_fight": {
                "fight_id": latest["fight_id"],
                "start_time": latest["start_time"],
            },
            "execution_check": execution_check,
            "equipment_check": equipment_check,
            "execution_score": execution_check.get("overall_score", 0),
            "_analysis_mode": "rule_based",
        }

        # 7. LLM增强
        if self.orchestrator:
            llm_result = await self._llm_enhance(result, latest)
            if llm_result:
                result["llm_analysis"] = llm_result
                result["_analysis_mode"] = "llm_enhanced"

        return result

    def _extract_build_info(self, build: Build) -> Dict[str, Any]:
        """从Build模型提取关键信息"""
        return {
            "id": build.id,
            "name": build.name,
            "profession": build.profession,
            "specialization": getattr(build, "specialization", ""),
            "weapons": getattr(build, "weapons", ""),
            "stats": getattr(build, "stats", ""),
            "traits": getattr(build, "traits", ""),
            "runes": getattr(build, "runes", ""),
            "sigils": getattr(build, "sigils", ""),
            "food": getattr(build, "food", ""),
            "description": getattr(build, "description", ""),
        }

    def _infer_build_type(
        self,
        latest: Dict,
        build_info: Optional[Dict],
    ) -> str:
        """推断Build类型"""
        # 优先从Build信息推断
        if build_info:
            desc = (build_info.get("description", "") + build_info.get("name", "")).lower()
            if any(k in desc for k in ["condi", "症状", " Condition"]):
                return AiBuildType.CONDI.value
            if any(k in desc for k in ["support", "辅助", " heal"]):
                return AiBuildType.SUPPORT.value
            if any(k in desc for k in ["tank", "坦克", " frontline"]):
                return AiBuildType.TANK.value

        # 从数据推断
        total_damage = latest.get("damage", 1)
        power_ratio = latest.get("power_damage", 0) / max(total_damage, 1)
        condi_ratio = latest.get("condi_damage", 0) / max(total_damage, 1)
        healing = latest.get("healing", 0)

        if healing > 500000:
            return AiBuildType.SUPPORT.value
        if condi_ratio > 0.6:
            return AiBuildType.CONDI.value
        if power_ratio > 0.6:
            return AiBuildType.POWER.value

        return AiBuildType.POWER.value

    def _validate_execution(
        self,
        latest: Dict,
        build_type: str,
        expectations: Dict,
    ) -> Dict[str, Any]:
        """验证实际执行与期望的差距"""
        checks = []
        total_damage = max(latest.get("damage", 1), 1)
        duration = max(latest.get("duration_sec", 60), 60)

        if build_type == AiBuildType.POWER.value:
            # 直伤占比检查
            power_ratio = latest.get("power_damage", 0) / total_damage
            expected = expectations.get("expected_power_ratio", 0.7)
            checks.append({
                "check": "power_damage_ratio",
                "label": get_dict_label("ai_check_item", "power_damage_ratio"),
                "actual": round(power_ratio * 100, 1),
                "expected": round(expected * 100, 1),
                "status": CheckStatus.PASS.value if power_ratio >= expected * 0.8 else CheckStatus.FAIL.value,
                "gap": round((expected - power_ratio) * 100, 1),
            })

            # 暴击率检查
            crit_rate = latest.get("critical_rate", 0)
            expected_crit = expectations.get("expected_crit_rate", 0.6)
            checks.append({
                "check": "critical_rate",
                "label": get_dict_label("ai_check_item", "critical_rate"),
                "actual": round(crit_rate * 100, 1),
                "expected": round(expected_crit * 100, 1),
                "status": CheckStatus.PASS.value if crit_rate >= expected_crit * 0.8 else CheckStatus.FAIL.value,
                "gap": round((expected_crit - crit_rate) * 100, 1),
            })

        elif build_type == AiBuildType.CONDI.value:
            # 症状占比检查
            condi_ratio = latest.get("condi_damage", 0) / total_damage
            expected = expectations.get("expected_condi_ratio", 0.7)
            checks.append({
                "check": "condi_damage_ratio",
                "label": get_dict_label("ai_check_item", "condi_damage_ratio"),
                "actual": round(condi_ratio * 100, 1),
                "expected": round(expected * 100, 1),
                "status": CheckStatus.PASS.value if condi_ratio >= expected * 0.8 else CheckStatus.FAIL.value,
                "gap": round((expected - condi_ratio) * 100, 1),
            })

        elif build_type == AiBuildType.SUPPORT.value:
            # 治疗量检查
            healing_per_min = latest.get("healing", 0) / (duration / 60)
            expected = expectations.get("expected_healing_per_min", 500000)
            checks.append({
                "check": "healing_output",
                "label": get_dict_label("ai_check_item", "healing_output"),
                "actual": round(healing_per_min, 0),
                "expected": expected,
                "status": CheckStatus.PASS.value if healing_per_min >= expected * 0.6 else CheckStatus.FAIL.value,
                "gap": round(expected - healing_per_min, 0),
            })

            # Buff覆盖检查
            boon_uptime = latest.get("might_uptime_active", 0) + latest.get("quickness_uptime_active", 0)
            expected_boon = expectations.get("expected_boon_uptime", 0.6)
            checks.append({
                "check": "boon_uptime",
                "label": get_dict_label("ai_check_item", "boon_uptime"),
                "actual": round(boon_uptime, 1),
                "expected": round(expected_boon * 100, 1),
                "status": CheckStatus.PASS.value if boon_uptime >= expected_boon * 80 else CheckStatus.FAIL.value,
                "gap": round(expected_boon * 100 - boon_uptime, 1),
            })

        # 通用检查：DPS效率
        dps = latest.get("dps", 0)
        checks.append({
            "check": "dps_efficiency",
            "label": get_dict_label("ai_check_item", "dps_efficiency"),
            "actual": dps,
            "expected": "根据Build类型而异",
            "status": "info",
        })

        # 通用检查：技能施放（swap_count反映武器切换频率）
        swaps = latest.get("swap_count", 0)
        skill_uptime = latest.get("skill_cast_uptime", 0)
        checks.append({
            "check": "skill_engagement",
            "label": get_dict_label("ai_check_item", "skill_engagement"),
            "actual": f"武器切换{swaps}次, 技能施放率{round(skill_uptime, 1)}%",
            "expected": "高活跃度",
            "status": CheckStatus.PASS.value if skill_uptime > 60 else CheckStatus.WARN.value,
        })

        # 计算总分
        pass_count = sum(1 for c in checks if c["status"] == CheckStatus.PASS.value)
        fail_count = sum(1 for c in checks if c["status"] == CheckStatus.FAIL.value)
        total_scored = pass_count + fail_count
        score = round((pass_count / max(total_scored, 1)) * 100) if total_scored > 0 else 50

        return {
            "checks": checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "overall_score": score,
        }

    def _check_equipment(self, fight_id: int, account: str) -> Dict[str, Any]:
        """检查装备/消耗品配置"""
        # 从EI数据获取武器和消耗品
        weapons_raw = EiJsonExtractor.get_weapons(self.db, fight_id, account)
        consumables_raw = EiJsonExtractor.get_consumables(self.db, fight_id, account)
        weapons = weapons_raw if isinstance(weapons_raw, list) else (json.loads(weapons_raw) if weapons_raw else None)
        consumables = consumables_raw if isinstance(consumables_raw, list) else (json.loads(consumables_raw) if consumables_raw else None)

        issues = []
        if not weapons:
            issues.append("无法获取武器配置数据")
        if not consumables:
            issues.append("未检测到食物/扳手消耗品")

        # 检查是否有常用消耗品
        has_food = False
        has_util = False
        if consumables:
            for c in consumables:
                name = c.get("name", "").lower() if isinstance(c, dict) else str(c).lower()
                if any(k in name for k in ["food", "食物", "stew", "pie", "cake"]):
                    has_food = True
                if any(k in name for k in ["oil", "sharpening", "tuning", "扳手", "油"]):
                    has_util = True

        if not has_food:
            issues.append("未使用食物（Food），建议携带适合的WvW食物")
        if not has_util:
            issues.append("未使用扳手/磨刀石（Utility），建议携带")

        return {
            "weapons": weapons,
            "consumables": consumables,
            "has_food": has_food,
            "has_utility": has_util,
            "issues": issues,
            "equipment_score": 100 - len(issues) * 20,
        }

    def _merge_equipment_checks(
        self,
        execution_check: Dict[str, Any],
        equipment_check: Dict[str, Any],
        latest: Dict,
        build_info: Optional[Dict],
    ) -> Dict[str, Any]:
        """将装备/消耗品/职业匹配检查合并到execution_check"""
        checks = list(execution_check.get("checks", []))

        # 武器非空检查
        weapons = equipment_check.get("weapons")
        has_weapons = bool(weapons and (isinstance(weapons, list) and len(weapons) > 0))
        checks.append({
            "check": "weapon_presence",
            "label": get_dict_label("ai_check_item", "weapon_presence"),
            "actual": "已装备" if has_weapons else "未获取",
            "expected": "主副手武器齐全",
            "status": CheckStatus.PASS.value if has_weapons else CheckStatus.WARN.value,
        })

        # 食物检查
        has_food = equipment_check.get("has_food", False)
        checks.append({
            "check": "food_consumable",
            "label": get_dict_label("ai_check_item", "food_consumable"),
            "actual": "已使用" if has_food else "未检测",
            "expected": "使用WvW食物",
            "status": CheckStatus.PASS.value if has_food else CheckStatus.WARN.value,
        })

        # 增强道具检查
        has_util = equipment_check.get("has_utility", False)
        checks.append({
            "check": "utility_consumable",
            "label": get_dict_label("ai_check_item", "utility_consumable"),
            "actual": "已使用" if has_util else "未检测",
            "expected": "使用磨刀石/油/调谐",
            "status": CheckStatus.PASS.value if has_util else CheckStatus.WARN.value,
        })

        # 职业匹配检查
        if build_info:
            actual_prof = latest.get("profession", "")
            expected_prof = build_info.get("profession", "")
            prof_match = actual_prof.lower() == expected_prof.lower() if expected_prof else True
            checks.append({
                "check": "profession_match",
                "label": get_dict_label("ai_check_item", "profession_match"),
                "actual": actual_prof,
                "expected": expected_prof or "任意",
                "status": CheckStatus.PASS.value if prof_match else CheckStatus.FAIL.value,
            })

        # 重新计算总分
        pass_count = sum(1 for c in checks if c["status"] == CheckStatus.PASS.value)
        fail_count = sum(1 for c in checks if c["status"] == CheckStatus.FAIL.value)
        total_scored = pass_count + fail_count
        score = round((pass_count / max(total_scored, 1)) * 100) if total_scored > 0 else 50

        return {
            "checks": checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "overall_score": score,
        }

    async def _llm_enhance(self, rule_result: Dict, latest: Dict) -> Optional[Dict]:
        """使用LLM增强Build验证分析"""
        if not self.orchestrator:
            return None

        try:
            from app.core.ai_prompt_templates import PromptTemplateRegistry

            template = PromptTemplateRegistry.get("build_execution_v1")
            if not template:
                return None

            context = {
                "account": rule_result["account"],
                "profession": rule_result["profession"],
                "build_type": rule_result["build_type"],
                "execution_score": rule_result["execution_score"],
                "failed_checks": [c for c in rule_result["execution_check"]["checks"] if c["status"] == CheckStatus.FAIL.value],
                "equipment_issues": rule_result["equipment_check"]["issues"],
            }

            optimized, assessment, error = await self.orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.BUILD_EXECUTION,
                template_id="build_execution_v1",
                context=context,
            )

            if error or not optimized:
                return None

            return {
                "narrative": optimized.get("narrative", ""),
                "optimization_path": optimized.get("optimization_path", []),
                "alternative_builds": optimized.get("alternative_builds", []),
                "quality": assessment,
            }
        except Exception as e:
            logger.error(f"Build验证LLM增强异常: {e}")
            return None

    def _empty_result(self, account: str, reason: str) -> Dict:
        return {
            "account": account,
            "error": reason,
            "execution_check": {},
            "equipment_check": {},
            "execution_score": 0,
        }
