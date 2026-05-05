# -*- coding: utf-8 -*-
# 模块功能：评分计算服务（已恢复）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-30
# 更新日期：2026-05-01
# 说明：v2.0 恢复——基于 FightStats 模型计算评分

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fight_stats import FightStats
from app.services.scoring_rule_service import ScoringRuleService
from app.utils.logger import logger


class ScoringService:
    """评分计算服务类（基于 FightStats）"""

    @staticmethod
    def get_scoring_rules(db: Session, role_type: str = "dps") -> Dict[str, float]:
        """从评分规则表获取规则（按角色类型）
        
        Args:
            db: 数据库会话
            role_type: 角色类型 dps/support/tank，默认 dps
        """
        service = ScoringRuleService(db)
        rules = service.get_rules_for_scoring(role_type)

        # 如果表为空，使用默认规则并提示
        if not rules or len(rules) <= 2:  # 只有 min/max 阈值
            logger.warning(f"评分规则表为空或数据不足，使用默认规则 (role_type={role_type})")
            default_fallback = {
                "damage_weight": 0.35,
                "power_damage_weight": 0.15,
                "condition_damage_weight": 0.15,
                "healing_weight": 0.20,
                "boons_weight": 0.10,
                "alacrity_weight": 0.05,
                "quickness_weight": 0.05,
                "survival_weight": 0.10,
                "strips_weight": 0.03,
                "cleanses_weight": 0.02,
                "kills_weight": 0.05,
                "breakbar_weight": 0.03,
                "min_score_threshold": 0.0,
                "max_score_cap": 100.0,
            }
            return default_fallback

        return rules

    @staticmethod
    def calculate_player_score(
        stats: Dict[str, Any],
        rules: Dict[str, float],
        max_values: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """计算单个玩家评分"""
        if not max_values:
            max_values = {}

        damage = stats.get("damage") or 0
        power_damage = stats.get("power_damage") or 0
        condi_damage = stats.get("condi_damage") or 0
        healing = stats.get("healing") or 0
        strips = stats.get("boon_strips") or 0
        cleanses = stats.get("condition_cleanses") or 0
        kills = stats.get("killed") or 0
        breakbar_damage = stats.get("breakbar_damage") or 0

        deaths = stats.get("dead_count") or 0
        survival_score = max(10 - (deaths * 2), 0)

        def normalize(value: float, max_val: float = None) -> float:
            if max_val and max_val > 0:
                return min(100, (value / max_val) * 100)
            return min(100, (value / 1000000) * 100)

        scores = {
            "damage": normalize(damage, max_values.get("damage")),
            "power_damage": normalize(power_damage, max_values.get("power_damage")),
            "condition_damage": normalize(
                condi_damage, max_values.get("condition_damage")
            ),
            "healing": normalize(healing, max_values.get("healing")),
            "boons": 50,  # TODO: 从Buff数据获取
            "alacrity": 50,
            "quickness": 50,
            "survival": survival_score,
            "strips": normalize(strips * 1000, max_values.get("strips")),
            "cleanses": normalize(cleanses * 1000, max_values.get("cleanses")),
            "kills": normalize(kills * 500000, max_values.get("kills")),
            "breakbar": normalize(breakbar_damage, max_values.get("breakbar")),
        }

        total_score = 0
        weight_sum = 0

        for dimension, score in scores.items():
            weight_key = f"{dimension}_weight"
            weight = rules.get(weight_key, 0)
            total_score += score * weight
            weight_sum += weight

        if weight_sum > 0:
            total_score = total_score / weight_sum

        min_score = rules.get("min_score_threshold", 0)
        max_score = rules.get("max_score_cap", 100)
        final_score = max(min_score, min(max_score, total_score))
        grade = ScoringService.get_grade(final_score)

        return {
            "total_score": round(final_score, 2),
            "breakdown": scores,
            "grade": grade,
            "grade_label": ScoringService.get_grade_label(grade),
        }

    @staticmethod
    def get_grade(score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "s"
        elif score >= 80:
            return "a"
        elif score >= 70:
            return "b"
        elif score >= 60:
            return "c"
        elif score >= 40:
            return "d"
        else:
            return "f"

    @staticmethod
    def get_grade_label(grade: str) -> str:
        """根据等级获取中文标签"""
        labels = {
            "s": "S级",
            "a": "A级",
            "b": "B级",
            "c": "C级",
            "d": "D级",
            "f": "F级",
        }
        return labels.get(grade.lower(), grade.upper())

    @staticmethod
    def calculate_all_scores(fight_id: int, db: Session, role_type: str = "dps") -> Dict[str, Any]:
        """计算一场战斗中所有玩家的评分
        
        Args:
            fight_id: 战斗ID
            db: 数据库会话
            role_type: 角色类型 dps/support/tank，默认 dps
        """
        stats_list = db.query(FightStats).filter(FightStats.fight_id == fight_id).all()
        if not stats_list:
            return {
                "fight_id": fight_id,
                "total_players": 0,
                "scores": [],
                "scoring_rules": ScoringService.get_scoring_rules(db, role_type),
            }

        rules = ScoringService.get_scoring_rules(db, role_type)

        # 计算最大值用于归一化
        max_values = {
            "damage": max(s.damage or 0 for s in stats_list),
            "power_damage": max(s.power_damage or 0 for s in stats_list),
            "condition_damage": max(s.condi_damage or 0 for s in stats_list),
            "healing": max(s.healing or 0 for s in stats_list),
            "strips": max(s.boon_strips or 0 for s in stats_list),
            "cleanses": max(s.condition_cleanses or 0 for s in stats_list),
            "kills": max(s.killed or 0 for s in stats_list),
            "breakbar": max(s.breakbar_damage or 0 for s in stats_list),
        }

        scores = []
        for stat in stats_list:
            stat_dict = {
                "damage": stat.damage,
                "power_damage": stat.power_damage,
                "condi_damage": stat.condi_damage,
                "healing": stat.healing,
                "boon_strips": stat.boon_strips,
                "condition_cleanses": stat.condition_cleanses,
                "killed": stat.killed,
                "breakbar_damage": stat.breakbar_damage,
                "dead_count": stat.dead_count,
            }
            result = ScoringService.calculate_player_score(stat_dict, rules, max_values)
            scores.append(
                {
                    "member_id": stat.member_id,
                    "account": stat.account,
                    "character_name": stat.character_name,
                    "profession": stat.profession,
                    **result,
                }
            )

        return {
            "fight_id": fight_id,
            "total_players": len(scores),
            "scores": scores,
            "scoring_rules": rules,
        }
