# -*- coding: utf-8 -*-
"""死亡归因与生存分析器

功能：分析玩家死亡原因，识别生存薄弱环节
- 死亡场景分类（集火/走位失误/buff断档/技能未交）
- 死亡前N秒的关键事件时间线
- 生存改进建议
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.services.ai_analysis.data_aggregator import (
    EiJsonExtractor,
    FightStatsAggregator,
)
from app.utils.logger import logger


class DeathAttributionAnalyzer:
    """死亡归因与生存分析器"""

    # 死亡归因分类
    DEATH_CATEGORIES = {
        "focused_fire": {
            "label": "被集火",
            "description": "短时间内受到多个敌方目标的高额伤害",
            "indicators": ["damage_taken极高", "无有效格挡/闪避记录"],
        },
        "positioning_error": {
            "label": "走位失误",
            "description": "脱离团队堆叠点，暴露在敌方火力范围内",
            "indicators": ["dist_to_com过大", "stack_dist异常"],
        },
        "buff_gap": {
            "label": "Buff断档",
            "description": "关键增益（保护/稳固）覆盖率不足",
            "indicators": ["protection_uptime低", "stability_uptime低"],
        },
        "cooldown_mismatch": {
            "label": "技能未交",
            "description": "拥有解控/无敌/翻滚等生存技能但未使用",
            "indicators": ["stun_break未使用", "dodge_count为0"],
        },
        "healing_deficit": {
            "label": "治疗缺口",
            "description": "受到伤害量超过团队治疗能力覆盖",
            "indicators": ["damage_taken持续高于团队平均水平"],
        },
        "cc_chain": {
            "label": "控制链",
            "description": "被连续控制无法操作直至死亡",
            "indicators": ["received_cc_duration长", "removed_stun_duration为0"],
        },
    }

    def __init__(self, db: Session, orchestrator=None):
        self.db = db
        self.orchestrator = orchestrator

    async def analyze(
        self,
        account: str,
        fight_id: Optional[int] = None,
        log_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        主分析入口
        
        Args:
            account: 玩家账号
            fight_id: 指定战斗（可选，不指定则分析最近几场）
            log_id: 对应的EI日志ID（用于获取death_recap）
        """
        logger.info(f"开始死亡归因分析: account={account}, fight_id={fight_id}")

        # 1. 获取历史数据（重点看死亡相关）
        history = FightStatsAggregator.get_player_history(self.db, account, fight_count=20)
        if not history:
            return self._empty_result(account, "暂无战斗数据")

        # 2. 分析死亡统计
        death_stats = self._analyze_death_stats(history)

        # 3. 获取最近一次死亡的EI回放（如果提供了log_id）
        death_recap = None
        if log_id:
            death_recap = EiJsonExtractor.get_death_recap(self.db, log_id, account)

        # 4. 归因分类
        attributions = self._classify_deaths(history, death_recap)

        # 5. 生成建议
        suggestions = self._generate_survival_suggestions(death_stats, attributions)

        # 6. 构建结果
        result = {
            "account": account,
            "death_stats": death_stats,
            "attributions": attributions,
            "death_recap": death_recap,  # 原始EI数据
            "suggestions": suggestions,
            "survival_score": self._calculate_survival_score(history),
            "_analysis_mode": "rule_based",
        }

        # 7. LLM增强
        if self.orchestrator:
            llm_result = await self._llm_enhance(result)
            if llm_result:
                result["llm_analysis"] = llm_result
                result["_analysis_mode"] = "llm_enhanced"

        return result

    def _analyze_death_stats(self, history: List[Dict]) -> Dict[str, Any]:
        """分析死亡统计数据"""
        total_fights = len(history)
        deaths = sum(1 for r in history if r.get("dead_count", 0) > 0)
        downs = sum(1 for r in history if r.get("down_count", 0) > 0)
        total_deaths = sum(r.get("dead_count", 0) for r in history)
        total_downs = sum(r.get("down_count", 0) for r in history)

        avg_damage_taken = sum(r.get("damage_taken", 0) for r in history) / max(total_fights, 1)
        avg_dodge = sum(r.get("dodge_count", 0) for r in history) / max(total_fights, 1)
        avg_block = sum(r.get("blocked_count", 0) for r in history) / max(total_fights, 1)
        avg_evade = sum(r.get("evaded_count", 0) for r in history) / max(total_fights, 1)

        # 查找死亡率最高的战斗
        high_death_fights = [
            {
                "fight_id": r["fight_id"],
                "start_time": r["start_time"],
                "dead_count": r.get("dead_count", 0),
                "down_count": r.get("down_count", 0),
                "damage_taken": r.get("damage_taken", 0),
            }
            for r in history if r.get("dead_count", 0) > 0
        ]
        high_death_fights.sort(key=lambda x: x["dead_count"], reverse=True)

        return {
            "total_fights": total_fights,
            "fights_with_death": deaths,
            "fights_with_down": downs,
            "total_deaths": total_deaths,
            "total_downs": total_downs,
            "death_rate": round(deaths / max(total_fights, 1) * 100, 1),
            "down_rate": round(downs / max(total_fights, 1) * 100, 1),
            "avg_damage_taken": round(avg_damage_taken, 0),
            "avg_dodge_per_fight": round(avg_dodge, 1),
            "avg_block_per_fight": round(avg_block, 1),
            "avg_evade_per_fight": round(avg_evade, 1),
            "high_death_fights": high_death_fights[:5],
        }

    def _classify_deaths(
        self,
        history: List[Dict],
        death_recap: Optional[Dict],
    ) -> List[Dict]:
        """基于规则对死亡进行分类归因"""
        attributions = []

        # 取最近5场有死亡的战斗进行归因
        death_fights = [r for r in history if r.get("dead_count", 0) > 0][:5]

        for record in death_fights:
            reasons = []
            weights = {}

            # 走位失误：距离指挥官过远
            dist = record.get("dist_to_com", 0)
            if dist > 800:
                reasons.append("positioning_error")
                weights["positioning_error"] = min((dist - 800) / 400, 1.0)

            # Buff断档：保护/稳固覆盖率低
            prot = record.get("protection_uptime", 0)
            stab = record.get("stability_uptime", 0)
            if prot < 30 and stab < 20:
                reasons.append("buff_gap")
                weights["buff_gap"] = 1.0 - (float(prot) + float(stab)) / 100

            # 被集火：承伤极高且没有有效防御
            dt = record.get("damage_taken", 0)
            block = record.get("blocked_count", 0)
            evade = record.get("evaded_count", 0)
            dodge = record.get("dodge_count", 0)
            if dt > 500000 and block + evade + dodge < 3:
                reasons.append("focused_fire")
                weights["focused_fire"] = min(dt / 1000000, 1.0)

            # 技能未交：有翻滚但未使用
            if dodge == 0 and record.get("down_count", 0) > 0:
                reasons.append("cooldown_mismatch")
                weights["cooldown_mismatch"] = 0.7

            # 控制链：受到CC时间长
            cc_recv = record.get("received_cc_duration", 0)
            cc_removed = record.get("removed_stun_duration", 0)
            if cc_recv > 5000 and cc_removed < 1000:
                reasons.append("cc_chain")
                weights["cc_chain"] = min(cc_recv / 10000, 1.0)

            # 治疗缺口：承伤过高
            if dt > 800000:
                reasons.append("healing_deficit")
                weights["healing_deficit"] = min((dt - 800000) / 400000, 1.0)

            # 选择权重最高的原因
            primary_reason = max(weights, key=weights.get) if weights else "unknown"

            cat_info = self.DEATH_CATEGORIES.get(primary_reason, {})
            attributions.append({
                "fight_id": record["fight_id"],
                "start_time": record["start_time"],
                "primary_reason": primary_reason,
                "primary_label": cat_info.get("label", "未知"),
                "confidence": round(weights.get(primary_reason, 0.5), 2),
                "all_reasons": reasons,
                "weights": {k: round(v, 2) for k, v in weights.items()},
            })

        return attributions

    def _generate_survival_suggestions(
        self,
        death_stats: Dict,
        attributions: List[Dict],
    ) -> List[Dict]:
        """生成生存改进建议"""
        suggestions = []

        # 统计主要原因
        reason_counts = {}
        for attr in attributions:
            reason = attr["primary_reason"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        # 按频次排序
        sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)

        for reason, count in sorted_reasons:
            cat = self.DEATH_CATEGORIES.get(reason, {})
            if reason == "positioning_error":
                suggestions.append({
                    "priority": "high" if count >= 2 else "medium",
                    "issue": "走位失误",
                    "message": f"{count}次死亡与脱离团队有关，请紧跟指挥官标记",
                    "actions": [
                        "团战时保持与堆叠点600码以内",
                        "使用小地图观察指挥官位置",
                        "撤退时跟随团队移动，不要单独行动",
                    ],
                })
            elif reason == "buff_gap":
                suggestions.append({
                    "priority": "high",
                    "issue": "Buff断档",
                    "message": f"{count}次死亡时保护/稳固覆盖不足",
                    "actions": [
                        "与团队增益提供者保持同步",
                        "携带自身稳固来源（如稳固纹章）",
                        "在敌方爆发前预读保护",
                    ],
                })
            elif reason == "focused_fire":
                suggestions.append({
                    "priority": "medium",
                    "issue": "被集火",
                    "message": f"{count}次被敌方集中火力击杀",
                    "actions": [
                        "被集火时立即使用无敌/格挡技能",
                        "向团队后方/安全位置移动",
                        "注意敌方高伤害技能的预警",
                    ],
                })
            elif reason == "cooldown_mismatch":
                suggestions.append({
                    "priority": "medium",
                    "issue": "生存技能未使用",
                    "message": f"{count}次死亡时未有效使用翻滚/解控",
                    "actions": [
                        "养成见红圈就翻滚的条件反射",
                        "将解控技能放在顺手键位",
                        "不要吝啬生存技能，活着才有输出",
                    ],
                })
            elif reason == "cc_chain":
                suggestions.append({
                    "priority": "high",
                    "issue": "被控制链",
                    "message": f"{count}次被连续控制至死",
                    "actions": [
                        "携带解控/稳定技能",
                        "注意敌方控制技能的CD",
                        "被控制时立即使用解除昏迷",
                    ],
                })

        # 通用建议
        if death_stats["death_rate"] > 50:
            suggestions.append({
                "priority": "high",
                "issue": "整体死亡率过高",
                "message": f"最近{death_stats['total_fights']}场战斗中{death_stats['death_rate']}%有死亡记录",
                "actions": [
                    "优先保证生存再追求输出",
                    "检查Build是否有足够的生存属性",
                    "减少激进走位，稳中求胜",
                ],
            })

        return suggestions

    def _calculate_survival_score(self, history: List[Dict]) -> int:
        """计算生存评分（0-100）"""
        if not history:
            return 0

        total = len(history)
        death_rate = sum(1 for r in history if r.get("dead_count", 0) > 0) / total
        down_rate = sum(1 for r in history if r.get("down_count", 0) > 0) / total

        avg_dt = sum(r.get("damage_taken", 0) for r in history) / total
        avg_defense = sum(
            r.get("blocked_count", 0) + r.get("evaded_count", 0) + r.get("dodge_count", 0)
            for r in history
        ) / total

        # 生存评分 = 100 - 死亡率*30 - 倒地率*20 + 防御动作*2
        score = 100 - death_rate * 30 - down_rate * 20 + min(avg_defense * 2, 20)
        # 承伤过高扣分
        if avg_dt > 1000000:
            score -= 15
        return max(0, min(100, round(score)))

    async def _llm_enhance(self, rule_result: Dict) -> Optional[Dict]:
        """使用LLM增强死亡归因分析"""
        if not self.orchestrator:
            return None

        try:
            from app.core.ai_prompt_templates import PromptTemplateRegistry

            template = PromptTemplateRegistry.get("death_attribution_v1")
            if not template:
                return None

            context = {
                "account": rule_result["account"],
                "death_stats": rule_result["death_stats"],
                "primary_attribution": rule_result["attributions"][0] if rule_result["attributions"] else None,
                "survival_score": rule_result["survival_score"],
            }

            optimized, assessment, error = await self.orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.DEATH_ATTRIBUTION,
                template_id="death_attribution_v1",
                context=context,
            )

            if error or not optimized:
                return None

            return {
                "narrative": optimized.get("narrative", ""),
                "deep_insights": optimized.get("deep_insights", []),
                "personalized_training": optimized.get("personalized_training", []),
                "quality": assessment,
            }
        except Exception as e:
            logger.error(f"死亡归因LLM增强异常: {e}")
            return None

    def _empty_result(self, account: str, reason: str) -> Dict:
        return {
            "account": account,
            "error": reason,
            "death_stats": {},
            "attributions": [],
            "suggestions": [],
            "survival_score": 0,
        }
