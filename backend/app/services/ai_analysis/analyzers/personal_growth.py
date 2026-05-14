# -*- coding: utf-8 -*-
"""个人战力成长档案分析器

功能：基于玩家历史战斗数据，生成个人成长轨迹分析
- 多维度战力雷达图数据
- 公会内百分位排名
- 近期趋势变化
- 可操作的成长建议
"""

import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.services.ai_analysis.data_aggregator import (
    FightStatsAggregator,
)
from app.utils.logger import logger


class PersonalGrowthAnalyzer:
    """个人战力成长档案分析器"""

    # 成长档案核心维度定义
    DIMENSIONS = {
        "damage_output": {
            "label": "输出能力",
            "fields": ["damage", "dps", "power_damage", "condi_damage", "critical_rate"],
            "description": "对敌方造成的总伤害、DPS、直伤/症状伤害占比、暴击率",
        },
        "survival": {
            "label": "生存能力",
            "fields": ["damage_taken", "blocked_count", "evaded_count", "dodge_count", "down_count", "dead_count"],
            "description": "受到伤害、格挡/闪避/翻滚次数、倒地/死亡次数",
        },
        "support": {
            "label": "辅助贡献",
            "fields": ["healing", "resurrects", "condi_cleanse_ally", "boon_strips_ally"],
            "description": "治疗量、复活次数、清除盟友症状、剥离敌方增益",
        },
        "buff_management": {
            "label": "Buff管理",
            "fields": ["might_uptime_active", "quickness_uptime_active", "alacrity_uptime_active", "fury_uptime"],
            "description": "战斗中威能/急速/敏捷/愤怒覆盖率",
        },
        "cc_control": {
            "label": "控制能力",
            "fields": ["applied_cc_duration", "applied_cc_count", "interrupts", "stun_break"],
            "description": "施加CC时长/次数、打断次数、解除昏迷",
        },
        "positioning": {
            "label": "站位意识",
            "fields": ["stack_dist", "dist_to_com", "flanking_rate"],
            "description": "与堆叠点距离、与指挥官距离、侧击率",
        },
    }

    def __init__(self, db: Session, orchestrator=None):
        self.db = db
        self.orchestrator = orchestrator
        self.aggregator = FightStatsAggregator()

    # ==================== 规则分析层 ====================

    async def analyze(self, account: str, fight_count: int = 30) -> Dict[str, Any]:
        """
        主分析入口
        1. 获取历史数据
        2. 计算各维度得分和趋势
        3. 计算公会百分位
        4. 生成规则建议
        5. LLM增强（如果有orchestrator）
        """
        logger.info(f"开始生成个人成长档案: account={account}")

        # 1. 获取历史数据
        history = self.aggregator.get_player_history(self.db, account, fight_count)
        if not history:
            return self._empty_result(account, "该玩家暂无历史战斗数据")

        # 2. 计算维度得分
        dimension_scores = self._calculate_dimension_scores(history)

        # 3. 计算公会百分位
        percentiles = self._calculate_percentiles(account, history)

        # 4. 计算趋势
        trends = self._calculate_trends(history)

        # 5. 规则建议
        suggestions = self._generate_suggestions(dimension_scores, percentiles, trends)

        # 6. 构建结果
        result = {
            "account": account,
            "character_name": history[-1]["character_name"] if history else "",
            "profession": history[-1]["profession"] if history else "",
            "analysis_period": {
                "fight_count": len(history),
                "first_fight": history[0]["start_time"] if history else None,
                "last_fight": history[-1]["start_time"] if history else None,
            },
            "dimension_scores": dimension_scores,
            "percentiles": percentiles,
            "trends": trends,
            "suggestions": suggestions,
            "overall_score": self._calculate_overall_score(dimension_scores),
            "_analysis_mode": "rule_based",
        }

        # 7. LLM增强
        if self.orchestrator:
            llm_result = await self._llm_enhance(result, history)
            if llm_result:
                result["llm_analysis"] = llm_result
                result["_analysis_mode"] = "llm_enhanced"

        return result

    def _calculate_dimension_scores(self, history: List[Dict]) -> Dict[str, Any]:
        """计算各维度得分（0-100）"""
        scores = {}
        for dim_key, dim_config in self.DIMENSIONS.items():
            values = []
            for record in history:
                dim_values = [record.get(f, 0) for f in dim_config["fields"]]
                # 对多字段取平均值作为该战斗的维度值
                if dim_values:
                    values.append(sum(dim_values) / len(dim_values))

            if not values:
                scores[dim_key] = {"score": 0, "label": dim_config["label"], "trend": "stable"}
                continue

            avg = sum(values) / len(values)
            # 将原始值映射到0-100分（使用最近一场的公会平均值作为基准）
            scores[dim_key] = {
                "score": min(100, max(0, round(avg / 10))),  # 简单映射，实际应基于基准
                "label": dim_config["label"],
                "avg_raw": round(avg, 2),
                "trend": self._compute_single_trend(values),
            }
        return scores

    def _compute_single_trend(self, values: List[float]) -> str:
        """计算单维度趋势: improving / declining / stable"""
        if len(values) < 5:
            return "stable"
        # 取前半段和后半段比较
        mid = len(values) // 2
        first_half = sum(values[:mid]) / max(mid, 1)
        second_half = sum(values[mid:]) / max(len(values) - mid, 1)
        diff_pct = (second_half - first_half) / max(first_half, 1)
        if diff_pct > 0.15:
            return "improving"
        elif diff_pct < -0.15:
            return "declining"
        return "stable"

    def _calculate_percentiles(self, account: str, history: List[Dict]) -> Dict[str, int]:
        """计算各维度在公会内的百分位排名"""
        if not history:
            return {}

        profession = history[-1]["profession"]
        percentiles = {}

        for dim_key, dim_config in self.DIMENSIONS.items():
            # 取最近一场的维度代表值
            latest_values = [history[-1].get(f, 0) for f in dim_config["fields"]]
            player_value = sum(latest_values) / max(len(latest_values), 1)

            # 取第一个字段作为百分位计算依据
            guild_values = self.aggregator.get_guild_percentiles(
                self.db, profession, dim_config["fields"][0], days=30
            )
            percentile = self.aggregator.calculate_player_percentile(player_value, guild_values)
            percentiles[dim_key] = percentile

        return percentiles

    def _calculate_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """计算整体趋势"""
        if len(history) < 5:
            return {"overall": "stable", "confidence": 0, "details": "数据不足"}

        # 计算DPS趋势
        dps_values = [r.get("dps", 0) for r in history]
        dps_trend = self._compute_single_trend(dps_values)

        # 计算生存能力趋势（伤害承受越少越好）
        dt_values = [r.get("damage_taken", 0) for r in history]
        # 伤害承受降低是好事，所以反转趋势
        survival_trend_raw = self._compute_single_trend(dt_values)
        survival_trend = "improving" if survival_trend_raw == "declining" else ("declining" if survival_trend_raw == "improving" else "stable")

        # 计算评分趋势
        score_values = [r.get("ai_score", 0) for r in history]
        score_trend = self._compute_single_trend(score_values)

        return {
            "overall": score_trend,
            "dps_trend": dps_trend,
            "survival_trend": survival_trend,
            "score_trend": score_trend,
            "confidence": min(100, len(history) * 3),  # 数据越多置信度越高
        }

    def _generate_suggestions(
        self,
        dimension_scores: Dict,
        percentiles: Dict,
        trends: Dict,
    ) -> List[Dict]:
        """基于规则生成成长建议"""
        suggestions = []

        # 找出最弱的维度
        weak_dims = [
            (k, v["score"]) for k, v in dimension_scores.items()
        ]
        weak_dims.sort(key=lambda x: x[1])

        # 弱维度建议（得分<40）
        for dim_key, score in weak_dims[:2]:
            if score < 40:
                dim_info = self.DIMENSIONS.get(dim_key, {})
                suggestions.append({
                    "category": "priority",
                    "dimension": dim_info.get("label", dim_key),
                    "score": score,
                    "message": f"{dim_info.get('label', dim_key)}较弱（{score}分），建议重点提升",
                    "actions": self._get_dim_actions(dim_key),
                })

        # 百分位低但趋势改善
        for dim_key, perc in percentiles.items():
            dim_score = dimension_scores.get(dim_key, {}).get("score", 0)
            trend = dimension_scores.get(dim_key, {}).get("trend", "stable")
            if perc < 30 and trend == "improving":
                dim_info = self.DIMENSIONS.get(dim_key, {})
                suggestions.append({
                    "category": "encouragement",
                    "dimension": dim_info.get("label", dim_key),
                    "percentile": perc,
                    "message": f"{dim_info.get('label', dim_key)}虽在公会中排名偏低（{perc}%），但近期呈上升趋势，继续努力",
                })

        # 强维度表扬
        for dim_key, perc in percentiles.items():
            if perc >= 70:
                dim_info = self.DIMENSIONS.get(dim_key, {})
                suggestions.append({
                    "category": "strength",
                    "dimension": dim_info.get("label", dim_key),
                    "percentile": perc,
                    "message": f"{dim_info.get('label', dim_key)}是突出优势（公会前{100-perc}%），可指导他人",
                })

        return suggestions

    def _get_dim_actions(self, dim_key: str) -> List[str]:
        """获取维度的具体改进行动"""
        actions_map = {
            "damage_output": [
                "检查武器符文配置是否最优",
                "练习技能循环，减少技能空转",
                "注意在急速覆盖期间爆发输出",
            ],
            "survival": [
                "关注小地图和指挥官标记，提前走位",
                "合理使用翻滚和格挡躲避高伤害技能",
                "保持与堆叠点的适当距离",
            ],
            "support": [
                "关注队友血条，优先保护残血队友",
                "熟悉各职业辅助技能的时机",
                "在团战中寻找复活机会",
            ],
            "buff_management": [
                "与队伍中的增益提供者配合",
                "在增益覆盖期间集中输出",
                "了解自身职业的自增益手段",
            ],
            "cc_control": [
                "在敌方读条时使用打断技能",
                "配合团队CC链，避免重复控制",
                "保留解除昏迷技能应对关键时刻",
            ],
            "positioning": [
                "紧跟指挥官标记移动",
                "保持与队伍堆叠的距离在600码以内",
                "侧击时注意自身安全",
            ],
        }
        return actions_map.get(dim_key, ["持续练习该维度相关技能"])

    def _calculate_overall_score(self, dimension_scores: Dict) -> int:
        """计算综合评分"""
        if not dimension_scores:
            return 0
        scores = [v["score"] for v in dimension_scores.values()]
        return round(sum(scores) / len(scores))

    # ==================== LLM增强层 ====================

    async def _llm_enhance(self, rule_result: Dict, history: List[Dict]) -> Optional[Dict]:
        """使用LLM增强分析结果"""
        if not self.orchestrator:
            return None

        try:
            from app.core.ai_prompt_templates import PromptTemplateRegistry

            template = PromptTemplateRegistry.get("personal_growth_v1")
            if not template:
                return None

            # 构建精简的上下文（避免token过多）
            context = {
                "account": rule_result["account"],
                "profession": rule_result["profession"],
                "fight_count": rule_result["analysis_period"]["fight_count"],
                "dimension_summary": {k: f"{v['label']}:{v['score']}分(趋势:{v['trend']})" for k, v in rule_result["dimension_scores"].items()},
                "percentiles": rule_result["percentiles"],
                "trends": rule_result["trends"],
            }

            optimized, assessment, error = await self.orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.PERSONAL_GROWTH,
                template_id="personal_growth_v1",
                context=context,
            )

            if error or not optimized:
                logger.warning(f"LLM增强失败: {error}")
                return None

            return {
                "narrative": optimized.get("narrative", ""),
                "growth_plan": optimized.get("growth_plan", []),
                "milestones": optimized.get("milestones", []),
                "quality": assessment,
            }
        except Exception as e:
            logger.error(f"LLM增强异常: {e}")
            return None

    def _empty_result(self, account: str, reason: str) -> Dict:
        """空数据返回"""
        return {
            "account": account,
            "error": reason,
            "dimension_scores": {},
            "percentiles": {},
            "trends": {},
            "suggestions": [],
            "overall_score": 0,
        }
