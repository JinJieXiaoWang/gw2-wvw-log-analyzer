# -*- coding: utf-8 -*-
"""小队协同效能诊断分析器

功能：分析小队（Group/Squad）内部的协同效能
- 小队Buff覆盖互补性
- 输出/辅助/控制角色配比合理性
- 关键技能协同时机
- 小队整体改进建议
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.services.ai_analysis.data_aggregator import SquadAggregator
from app.utils.logger import logger


class SquadSynergyAnalyzer:
    """小队协同效能诊断分析器"""

    # WvW常见角色定位（基于职业和数据的启发式判断）
    ROLE_HEURISTICS = {
        "damage": {
            "professions": [" Weaver", " Berserker", " Holosmith", " Soulbeast", " Renegade"],
            "priority_fields": ["damage", "dps", "power_damage", "condi_damage"],
        },
        "support": {
            "professions": [" Firebrand", " Scrapper", " Tempest", " Druid"],
            "priority_fields": ["healing", "resurrects", "condi_cleanse_ally", "boon_strips_ally"],
        },
        "control": {
            "professions": [" Spellbreaker", " Chronomancer", " Scourge", " Herald"],
            "priority_fields": ["applied_cc_duration", "applied_cc_count", "boon_strips"],
        },
        "tank": {
            "professions": [" Spellbreaker", " Firebrand", " Scrapper"],
            "priority_fields": ["damage_taken", "blocked_count", "barrier_damage_absorbed"],
        },
    }

    def __init__(self, db: Session, orchestrator=None):
        self.db = db
        self.orchestrator = orchestrator

    async def analyze(self, fight_id: int, group_id: Optional[int] = None) -> Dict[str, Any]:
        """
        主分析入口

        Args:
            fight_id: 战斗ID
            group_id: 指定小队编号（None则分析所有小队）
        """
        logger.info(f"开始小队协同分析: fight_id={fight_id}, group_id={group_id}")

        # 1. 获取小队数据
        squads = SquadAggregator.get_fight_squads(self.db, fight_id)
        if not squads:
            return self._empty_result("该战斗暂无小队数据")

        # 2. 如果指定了group_id，只分析该小队
        target_squads = {group_id: squads[group_id]} if group_id else squads

        # 3. 分析每个小队
        squad_analyses = []
        for gid, members in target_squads.items():
            analysis = self._analyze_single_squad(gid, members)
            squad_analyses.append(analysis)

        # 4. 计算全局对比
        global_avg = SquadAggregator.get_fight_averages(self.db, fight_id)

        # 5. 构建结果
        result = {
            "fight_id": fight_id,
            "squad_count": len(squads),
            "squads": squad_analyses,
            "global_averages": {k: round(v, 1) for k, v in list(global_avg.items())[:10]},
            "_analysis_mode": "rule_based",
        }

        # 6. LLM增强
        if self.orchestrator:
            llm_result = await self._llm_enhance(result)
            if llm_result:
                result["llm_analysis"] = llm_result
                result["_analysis_mode"] = "llm_enhanced"

        return result

    def _analyze_single_squad(self, group_id: int, members: List[Any]) -> Dict[str, Any]:
        """分析单个小队"""
        if not members:
            return {"group_id": group_id, "member_count": 0, "error": "空小队"}

        # 1. 角色识别
        roles = self._identify_roles(members)

        # 2. 计算小队指标
        squad_metrics = self._calculate_squad_metrics(members)

        # 3. Buff互补分析
        buff_analysis = self._analyze_buff_complement(members)

        # 4. 协同评分
        synergy_score = self._calculate_synergy_score(roles, buff_analysis, squad_metrics)

        # 5. 生成建议
        suggestions = self._generate_squad_suggestions(roles, buff_analysis, squad_metrics)

        return {
            "group_id": group_id,
            "member_count": len(members),
            "members": [
                {
                    "account": m.account,
                    "character_name": m.character_name,
                    "profession": m.profession,
                    "role": roles.get(m.account, "unknown"),
                }
                for m in members
            ],
            "role_distribution": self._summarize_roles(roles),
            "squad_metrics": squad_metrics,
            "buff_analysis": buff_analysis,
            "synergy_score": synergy_score,
            "suggestions": suggestions,
        }

    def _identify_roles(self, members: List[Any]) -> Dict[str, str]:
        """基于数据启发式识别成员角色"""
        roles = {}
        for member in members:
            prof = member.profession or ""
            account = member.account

            # 计算各角色匹配度
            scores = {}
            for role, config in self.ROLE_HEURISTICS.items():
                score = 0
                # 职业匹配
                if any(p in prof for p in config["professions"]):
                    score += 30

                # 数据匹配
                for field in config["priority_fields"]:
                    val = getattr(member, field, 0) or 0
                    if role in ["damage", "support"]:
                        score += min(val / 10000, 20)
                    elif role == "control":
                        score += min(val / 1000, 20)
                    elif role == "tank":
                        score += min(val / 50000, 20)

                scores[role] = score

            # 选择最高分的角色
            if scores:
                best_role = max(scores, key=scores.get)
                roles[account] = best_role
            else:
                roles[account] = "unknown"

        return roles

    def _calculate_squad_metrics(self, members: List[Any]) -> Dict[str, Any]:
        """计算小队综合指标"""
        total_damage = sum(m.damage or 0 for m in members)
        total_healing = sum(m.healing or 0 for m in members)
        total_cc = sum(m.applied_cc_duration or 0 for m in members)
        total_res = sum(m.resurrects or 0 for m in members)
        total_cleanses = sum(m.condi_cleanse_ally or 0 for m in members)

        # 平均buff覆盖
        avg_might = sum(m.might_uptime_active or 0 for m in members) / max(len(members), 1)
        avg_quick = sum(m.quickness_uptime_active or 0 for m in members) / max(len(members), 1)
        avg_alac = sum(m.alacrity_uptime_active or 0 for m in members) / max(len(members), 1)

        return {
            "total_damage": total_damage,
            "total_healing": total_healing,
            "total_cc_duration": total_cc,
            "total_resurrects": total_res,
            "total_cleanses": total_cleanses,
            "avg_might_uptime": round(avg_might, 1),
            "avg_quickness_uptime": round(avg_quick, 1),
            "avg_alacrity_uptime": round(avg_alac, 1),
        }

    def _analyze_buff_complement(self, members: List[Any]) -> Dict[str, Any]:
        """分析小队Buff互补性"""
        # 检查是否有增益提供者（高急速/敏捷覆盖的成员）
        has_quickness_provider = any(
            (m.quickness_uptime_active or 0) > 50 for m in members
        )
        has_alacrity_provider = any(
            (m.alacrity_uptime_active or 0) > 50 for m in members
        )
        has_might_stacker = any(
            (m.might_uptime_active or 0) > 80 for m in members
        )
        has_healer = any(
            (m.healing or 0) > 500000 for m in members
        )
        has_cleanser = any(
            (m.condi_cleanse_ally or 0) > 50 for m in members
        )

        missing = []
        if not has_quickness_provider:
            missing.append("急速提供者")
        if not has_alacrity_provider:
            missing.append("敏捷提供者")
        if not has_might_stacker:
            missing.append("威能堆叠者")
        if not has_healer:
            missing.append("治疗者")
        if not has_cleanser:
            missing.append("症状清除者")

        return {
            "has_quickness_provider": has_quickness_provider,
            "has_alacrity_provider": has_alacrity_provider,
            "has_might_stacker": has_might_stacker,
            "has_healer": has_healer,
            "has_cleanser": has_cleanser,
            "missing_roles": missing,
            "complement_score": max(0, 100 - len(missing) * 20),
        }

    def _calculate_synergy_score(
        self,
        roles: Dict[str, str],
        buff_analysis: Dict,
        squad_metrics: Dict,
    ) -> int:
        """计算小队协同评分（0-100）"""
        score = 50  # 基础分

        # 角色分布加分（理想：2-3输出，1-2辅助，1控制）
        role_counts = self._summarize_roles(roles)
        if 2 <= role_counts.get("damage", 0) <= 4:
            score += 15
        if 1 <= role_counts.get("support", 0) <= 2:
            score += 15
        if role_counts.get("control", 0) >= 1:
            score += 10

        # Buff互补加分
        score += buff_analysis.get("complement_score", 0) * 0.1

        # 团队指标加分
        if squad_metrics.get("avg_might_uptime", 0) > 70:
            score += 5
        if squad_metrics.get("avg_quickness_uptime", 0) > 50:
            score += 5

        return min(100, round(score))

    def _summarize_roles(self, roles: Dict[str, str]) -> Dict[str, int]:
        """汇总角色分布"""
        counts = {}
        for role in roles.values():
            counts[role] = counts.get(role, 0) + 1
        return counts

    def _generate_squad_suggestions(
        self,
        roles: Dict[str, str],
        buff_analysis: Dict,
        squad_metrics: Dict,
    ) -> List[Dict]:
        """生成小队改进建议"""
        suggestions = []
        role_counts = self._summarize_roles(roles)

        # 缺少关键角色
        for missing in buff_analysis.get("missing_roles", []):
            suggestions.append({
                "priority": "high",
                "category": "role_composition",
                "issue": f"缺少{missing}",
                "message": f"小队中缺少{missing}，建议补充",
                "actions": [f"邀请一名能够提供{missing}功能的职业加入小队"],
            })

        # 输出不足
        if role_counts.get("damage", 0) < 2:
            suggestions.append({
                "priority": "medium",
                "category": "role_composition",
                "issue": "输出不足",
                "message": "小队输出职业偏少，可能导致团战输出不够",
                "actions": ["至少保证2-3名输出职业"],
            })

        # Buff覆盖低
        if squad_metrics.get("avg_might_uptime", 0) < 50:
            suggestions.append({
                "priority": "high",
                "category": "buff_coverage",
                "issue": "威能覆盖过低",
                "message": "小队平均威能覆盖率不足50%，严重影响输出",
                "actions": [
                    "确保有战士或魂武提供小队威能",
                    "使用威能食物和符文",
                ],
            })

        if squad_metrics.get("avg_quickness_uptime", 0) < 40:
            suggestions.append({
                "priority": "high",
                "category": "buff_coverage",
                "issue": "急速覆盖不足",
                "message": "急速覆盖率偏低，影响全队输出节奏",
                "actions": [
                    "确保有燃火或时空提供急速",
                    "检查增益是否覆盖到所有小队成员",
                ],
            })

        # 治疗不足
        if not buff_analysis.get("has_healer", False):
            suggestions.append({
                "priority": "high",
                "category": "survival",
                "issue": "无治疗者",
                "message": "小队中缺少治疗职业，生存能力堪忧",
                "actions": [
                    "建议至少配置1名治疗职业（燃火/暴风/德鲁伊）",
                ],
            })

        return suggestions

    async def _llm_enhance(self, rule_result: Dict) -> Optional[Dict]:
        """使用LLM增强小队协同分析"""
        if not self.orchestrator:
            return None

        try:
            from app.core.ai_prompt_templates import PromptTemplateRegistry

            template = PromptTemplateRegistry.get("squad_synergy_v1")
            if not template:
                return None

            context = {
                "fight_id": rule_result["fight_id"],
                "squad_count": rule_result["squad_count"],
                "best_squad": max(rule_result["squads"], key=lambda s: s.get("synergy_score", 0)) if rule_result["squads"] else None,
                "worst_squad": min(rule_result["squads"], key=lambda s: s.get("synergy_score", 0)) if rule_result["squads"] else None,
            }

            optimized, assessment, error = await self.orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.SQUAD_SYNERGY,
                template_id="squad_synergy_v1",
                context=context,
            )

            if error or not optimized:
                return None

            return {
                "narrative": optimized.get("narrative", ""),
                "tactical_suggestions": optimized.get("tactical_suggestions", []),
                "quality": assessment,
            }
        except Exception as e:
            logger.error(f"小队协同LLM增强异常: {e}")
            return None

    def _empty_result(self, reason: str) -> Dict:
        return {
            "error": reason,
            "squads": [],
            "synergy_score": 0,
        }
