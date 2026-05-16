# -*- coding: utf-8 -*-
"""战斗关键片段复盘分析器

功能：识别战斗中的关键片段（爆发期/团灭前/逆转点）
- 基于时间线数据识别关键时刻
- 关键片段中的玩家表现评估
- 关键时刻的决策建议
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.models.log.fight import Fight
from app.services.ai_analysis.data_aggregator import SquadAggregator
from app.constants.dict_values import AiRating, ImportanceLevel
from app.utils.logger import logger


class CriticalMomentsAnalyzer:
    """战斗关键片段复盘分析器"""

    def __init__(self, db: Session, orchestrator=None):
        self.db = db
        self.orchestrator = orchestrator

    async def analyze(
        self,
        fight_id: int,
        account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        主分析入口

        Args:
            fight_id: 战斗ID
            account: 指定玩家（可选，None则分析全队关键时刻）
        """
        logger.info(f"开始关键片段分析: fight_id={fight_id}, account={account}")

        # 1. 获取战斗基础信息
        fight = self.db.query(Fight).filter(Fight.id == fight_id).first()
        if not fight:
            return self._empty_result("战斗不存在")

        # 2. 获取小队数据
        squads = SquadAggregator.get_fight_squads(self.db, fight_id)
        all_members = []
        for members in squads.values():
            all_members.extend(members)

        if not all_members:
            return self._empty_result("该战斗无成员数据")

        # 3. 识别关键时刻
        moments = self._identify_critical_moments(fight, all_members, account)

        # 4. 评估关键时刻表现
        moment_evaluations = []
        for moment in moments:
            eval_result = self._evaluate_moment(moment, all_members, account)
            moment_evaluations.append(eval_result)

        # 5. 构建结果
        result = {
            "fight_id": fight_id,
            "fight_info": {
                "map_name": fight.map_name,
                "duration_sec": fight.duration_sec,
                "start_time": fight.start_time.isoformat() if fight.start_time else None,
            },
            "moments": moment_evaluations,
            "moment_count": len(moment_evaluations),
            "_analysis_mode": "rule_based",
        }

        # 6. LLM增强
        if self.orchestrator and moment_evaluations:
            llm_result = await self._llm_enhance(result)
            if llm_result:
                result["llm_analysis"] = llm_result
                result["_analysis_mode"] = "llm_enhanced"

        return result

    def _identify_critical_moments(
        self,
        fight: Fight,
        members: List[Any],
        account: Optional[str],
    ) -> List[Dict]:
        """识别战斗中的关键时刻"""
        moments = []
        duration = max(fight.duration_sec or 60, 1)

        # 关键片段1: 开场爆发（前20%时间）
        moments.append({
            "type": "opening_burst",
            "label": "开场爆发期",
            "time_start": 0,
            "time_end": duration * 0.2,
            "description": "战斗开始后的开场爆发阶段，决定先手优势",
            "importance": "high",
        })

        # 关键片段2: 团灭风险期（死亡集中时段）
        # 基于成员的down/dead时间点推断（fight_stats没有精确时间，用启发式）
        dead_members = [m for m in members if (m.dead_count or 0) > 0]
        down_members = [m for m in members if (m.down_count or 0) > 0]
        if dead_members or down_members:
            moments.append({
                "type": "crisis_moment",
                "label": "危机时刻",
                "time_start": duration * 0.4,
                "time_end": duration * 0.7,
                "description": f"团队出现{len(down_members)}次倒地、{len(dead_members)}次死亡的关键时段",
                "importance": ImportanceLevel.CRITICAL.value,
            })

        # 关键片段3: 收尾阶段（最后15%时间）
        moments.append({
            "type": "climax",
            "label": "收尾决战",
            "time_start": duration * 0.85,
            "time_end": duration,
            "description": "战斗收尾阶段，决定最终战果",
            "importance": "high",
        })

        # 关键片段4: 高输出窗口（如果有成员DPS特别高）
        top_dps_member = max(members, key=lambda m: m.dps or 0, default=None)
        if top_dps_member and (top_dps_member.dps or 0) > 5000:
            moments.append({
                "type": "damage_spike",
                "label": "输出峰值",
                "time_start": duration * 0.3,
                "time_end": duration * 0.5,
                "description": f"{top_dps_member.character_name}打出峰值DPS {top_dps_member.dps}",
                "importance": "medium",
                "highlight_player": top_dps_member.account,
            })

        # 关键片段5: 辅助高光时刻（治疗/复活特别突出）
        top_healer = max(members, key=lambda m: m.healing or 0, default=None)
        if top_healer and (top_healer.healing or 0) > 1000000:
            moments.append({
                "type": "support_highlight",
                "label": "辅助高光",
                "time_start": duration * 0.3,
                "time_end": duration * 0.7,
                "description": f"{top_healer.character_name}提供了{top_healer.healing}治疗量",
                "importance": "medium",
                "highlight_player": top_healer.account,
            })

        return moments

    def _evaluate_moment(
        self,
        moment: Dict,
        members: List[Any],
        account: Optional[str],
    ) -> Dict[str, Any]:
        """评估特定关键时刻的玩家表现"""
        moment_type = moment["type"]
        evaluations = []

        # 如果指定了account，只评估该玩家
        target_members = [m for m in members if m.account == account] if account else members

        for member in target_members:
            eval_entry = {
                "account": member.account,
                "character_name": member.character_name,
                "profession": member.profession,
            }

            if moment_type == "opening_burst":
                # 开场评估：DPS启动速度和buff利用
                dps = member.dps or 0
                might = member.might_uptime_active or 0
                eval_entry["performance"] = {
                    "dps": dps,
                    "might_uptime": might,
                    "rating": AiRating.EXCELLENT.value if dps > 4000 and might > 60 else (AiRating.GOOD.value if dps > 2500 else AiRating.NEEDS_IMPROVEMENT.value),
                }
                eval_entry["note"] = "开场爆发期应全力输出并确保吃到团队增益"

            elif moment_type == "crisis_moment":
                # 危机评估：生存和辅助表现
                dt = member.damage_taken or 0
                dead = member.dead_count or 0
                res = member.resurrects or 0
                eval_entry["performance"] = {
                    "damage_taken": dt,
                    "deaths": dead,
                    "resurrects": res,
                    "rating": AiRating.EXCELLENT.value if dead == 0 and res > 2 else (AiRating.GOOD.value if dead == 0 else AiRating.CRITICAL.value),
                }
                eval_entry["note"] = "危机时刻优先保证生存，有余力时支援队友"

            elif moment_type == "climax":
                # 收尾评估：持续输出能力和技能保留
                swap = member.swap_count or 0
                skill_uptime = member.skill_cast_uptime or 0
                eval_entry["performance"] = {
                    "weapon_swaps": swap,
                    "skill_uptime": skill_uptime,
                    "rating": AiRating.EXCELLENT.value if skill_uptime > 70 else AiRating.GOOD.value if skill_uptime > 50 else AiRating.NEEDS_IMPROVEMENT.value,
                }
                eval_entry["note"] = "收尾阶段保持输出节奏，保留关键技能应对变数"

            elif moment_type == "damage_spike":
                eval_entry["performance"] = {
                    "dps": member.dps or 0,
                    "rating": AiRating.EXCELLENT.value if (member.dps or 0) > 5000 else AiRating.GOOD.value,
                }
                eval_entry["note"] = "输出峰值期应最大化伤害输出"

            elif moment_type == "support_highlight":
                eval_entry["performance"] = {
                    "healing": member.healing or 0,
                    "cleanses": member.condi_cleanse_ally or 0,
                    "rating": AiRating.EXCELLENT.value if (member.healing or 0) > 1000000 else AiRating.GOOD.value,
                }
                eval_entry["note"] = "辅助高光时刻确保团队生存能力"

            evaluations.append(eval_entry)

        moment["evaluations"] = evaluations
        return moment

    async def _llm_enhance(self, rule_result: Dict) -> Optional[Dict]:
        """使用LLM增强关键片段分析"""
        if not self.orchestrator:
            return None

        try:
            from app.core.ai_prompt_templates import PromptTemplateRegistry

            template = PromptTemplateRegistry.get("critical_moments_v1")
            if not template:
                return None

            # 选取最重要的2个时刻给LLM分析
            top_moments = sorted(
                rule_result["moments"],
                key=lambda m: {ImportanceLevel.CRITICAL.value: 3, ImportanceLevel.HIGH.value: 2, ImportanceLevel.MEDIUM.value: 1}.get(m.get("importance", ""), 0),
                reverse=True,
            )[:2]

            context = {
                "fight_id": rule_result["fight_id"],
                "map_name": rule_result["fight_info"]["map_name"],
                "duration": rule_result["fight_info"]["duration_sec"],
                "moments": [
                    {
                        "type": m["type"],
                        "label": m["label"],
                        "importance": m["importance"],
                    }
                    for m in top_moments
                ],
            }

            optimized, assessment, error = await self.orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.CRITICAL_MOMENTS,
                template_id="critical_moments_v1",
                context=context,
            )

            if error or not optimized:
                return None

            return {
                "narrative": optimized.get("narrative", ""),
                "key_decisions": optimized.get("key_decisions", []),
                "what_if_analysis": optimized.get("what_if_analysis", []),
                "quality": assessment,
            }
        except Exception as e:
            logger.error(f"关键片段LLM增强异常: {e}")
            return None

    def _empty_result(self, reason: str) -> Dict:
        return {
            "error": reason,
            "moments": [],
            "moment_count": 0,
        }
