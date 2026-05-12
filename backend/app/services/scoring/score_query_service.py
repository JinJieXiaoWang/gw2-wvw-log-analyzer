# -*- coding: utf-8 -*-
# 模块功能：查询时评分服务（v1.0?# 作者：系统
# 创建日期?2026-05-09
# 说明?#   将评分计算从导入阶段移至查询阶段?#   导入时只保存原始数据，查询时根据当前评分规则实时计算?#   支持评分规则内存缓存（TTL 60s），避免频繁查库?
import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.constants.scoring import DEFAULT_FALLBACK_RULES, RULE_CACHE_TTL_SECONDS
from app.models.log.fight_stats import FightStats
from app.services.game_data.game_data_service import GameDataService
from app.services.scoring.scoring_rule_service import ScoringRuleService
from app.services.wvw.scoring_service import ScoringService
from app.utils.logger import logger

# 评分规则内存缓存: {(role_type, profession): (rules_dict, expire_time)}
_rules_cache: Dict[Tuple[str, Optional[str]], Tuple[Dict[str, float], float]] = {}

# 维度中文标签（向后兼容）
DIMENSION_LABELS = {
    "damage": "总伤?,
    "power_damage": "直伤",
    "condition_damage": "症状伤害",
    "healing": "治疗?,
    "boons": "增益覆盖",
    "alacrity": "敏捷覆盖",
    "quickness": "急速覆?,
    "survival": "生存能力",
    "strips": "破法",
    "cleanses": "净?,
    "kills": "击杀",
    "breakbar": "蔑视?,
    "damage_taken": "承受伤害",
    "blocked_count": "格挡",
    "evaded_count": "闪避",
}


def _get_cached_rules(db: Session, role_type: str, profession: Optional[str]) -> Dict[str, float]:
    """获取评分规则，优先使用内存缓?""
    global _rules_cache
    cache_key = (role_type, profession)
    now = time.time()

    cached = _rules_cache.get(cache_key)
    if cached and cached[1] > now:
        return cached[0]

    # 缓存未命中或过期，查?    service = ScoringRuleService(db)
    rules = service.get_rules_for_scoring(role_type, profession)

    # 如果表为空，使用默认兜底规则
    if not rules or len(rules) <= 2:
        rules = DEFAULT_FALLBACK_RULES.copy()

    _rules_cache[cache_key] = (rules, now + RULE_CACHE_TTL_SECONDS)
    return rules


def _clear_rules_cache():
    """清空规则缓存（规则更新后调用?""
    global _rules_cache
    _rules_cache.clear()
    logger.info("[score_query] 评分规则缓存已清?)


def _fight_stats_to_dict(stat: FightStats) -> Dict[str, Any]:
    """?FightStats ORM 对象转为原始数据字典（用于评分计算）"""
    return {
        "damage": stat.damage or 0,
        "power_damage": stat.power_damage or 0,
        "condi_damage": stat.condi_damage or 0,
        "healing": stat.healing or 0,
        "boon_strips": stat.boon_strips or 0,
        "condition_cleanses": stat.condition_cleanses or 0,
        "killed": stat.killed or 0,
        "breakbar_damage": stat.breakbar_damage or 0,
        "dead_count": stat.dead_count or 0,
        "might_uptime": float(stat.might_uptime or 0),
        "fury_uptime": float(stat.fury_uptime or 0),
        "quickness_uptime": float(stat.quickness_uptime or 0),
        "alacrity_uptime": float(stat.alacrity_uptime or 0),
        "protection_uptime": float(stat.protection_uptime or 0),
        "stability_uptime": float(stat.stability_uptime or 0),
    }


class PlayerScoreService:
    """玩家评分查询服务

    设计原则?    - 原始数据 immutable，评分规则可?    - 每次查询都用当前规则实时计算，保证规则更新立即可?    - 同一场战斗内共享 max_values，减少重复计?    """

    @staticmethod
    def calculate_single_score(
        db: Session,
        stat: FightStats,
        max_values: Optional[Dict[str, Any]] = None,
        role_type: Optional[str] = None,
        profession: Optional[str] = None,
    ) -> Dict[str, Any]:
        """为单?FightStats 计算评分

        Args:
            db: 数据库会?            stat: FightStats 记录
            max_values: 同场最大值（可选，不传则使?stat 自身值作?max?            role_type: 强制指定角色类型（None 则按职业自动判断?            profession: 强制指定职业（None 则使?stat.profession?
        Returns:
            {"total_score": float, "grade": str, "grade_label": str, "breakdown": dict}
        """
        player_profession = profession or stat.profession
        player_role = role_type

        if player_role is None and player_profession:
            player_role = GameDataService().get_default_role(player_profession)
        if player_role is None:
            player_role = "dps"

        rules = _get_cached_rules(db, player_role, player_profession)
        stat_dict = _fight_stats_to_dict(stat)

        # 如果未提供同场最大值，使用自身值（单条查询时）
        effective_max = max_values or {
            "damage": stat_dict["damage"],
            "power_damage": stat_dict["power_damage"],
            "condition_damage": stat_dict["condi_damage"],
            "healing": stat_dict["healing"],
            "strips": stat_dict["boon_strips"],
            "cleanses": stat_dict["condition_cleanses"],
            "kills": stat_dict["killed"],
            "breakbar": stat_dict["breakbar_damage"],
            "boons": 100,
            "alacrity": 100,
            "quickness": 100,
        }

        result = ScoringService.calculate_player_score(stat_dict, rules, effective_max)
        return {
            "total_score": result["total_score"],
            "grade": result["grade"],
            "grade_label": result["grade_label"],
            "breakdown": result["breakdown"],
            "role_type": player_role,
            "profession_rule": player_profession,
        }

    @staticmethod
    def calculate_fight_scores(
        db: Session,
        fight_id: int,
        role_type: Optional[str] = None,
        profession: Optional[str] = None,
    ) -> Dict[str, Any]:
        """计算一场战斗中所有玩家的评分（查询接口主入口?
        Args:
            db: 数据库会?            fight_id: 战斗ID
            role_type: 强制指定角色类型
            profession: 强制指定职业

        Returns:
            {
                "fight_id": int,
                "total_players": int,
                "scores": [{
                    "member_id", "account", "character_name", "profession",
                    "total_score", "grade", "grade_label", "breakdown", ...
                }],
                "max_values": dict,
            }
        """
        stats_list = db.query(FightStats).filter(FightStats.fight_id == fight_id).all()
        if not stats_list:
            return {
                "fight_id": fight_id,
                "total_players": 0,
                "scores": [],
                "max_values": {},
            }

        # 计算同场最大值（用于归一化）
        max_values = {
            "damage": max((s.damage or 0) for s in stats_list),
            "power_damage": max((s.power_damage or 0) for s in stats_list),
            "condition_damage": max((s.condi_damage or 0) for s in stats_list),
            "healing": max((s.healing or 0) for s in stats_list),
            "strips": max((s.boon_strips or 0) for s in stats_list),
            "cleanses": max((s.condition_cleanses or 0) for s in stats_list),
            "kills": max((s.killed or 0) for s in stats_list),
            "breakbar": max((s.breakbar_damage or 0) for s in stats_list),
            "boons": 100,
            "alacrity": 100,
            "quickness": 100,
        }

        scores = []
        for stat in stats_list:
            result = PlayerScoreService.calculate_single_score(
                db, stat, max_values=max_values, role_type=role_type, profession=profession
            )
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
            "max_values": max_values,
        }

    @staticmethod
    def attach_scores_to_stats(
        db: Session,
        stats_list: List[FightStats],
    ) -> List[Dict[str, Any]]:
        """为一?FightStats 附加评分字段（列表查询用?
        优化：按 fight_id 分组，同一场战斗共?max_values?
        Args:
            db: 数据库会?            stats_list: FightStats 列表（可能来自多场战斗）

        Returns:
            带评分字段的字典列表
        """
        if not stats_list:
            return []

        # ?fight_id 分组
        fight_groups: Dict[int, List[FightStats]] = {}
        for stat in stats_list:
            fight_groups.setdefault(stat.fight_id, []).append(stat)

        # 预计算每场的 max_values
        fight_max_values: Dict[int, Dict[str, Any]] = {}
        for fight_id, group in fight_groups.items():
            fight_max_values[fight_id] = {
                "damage": max((s.damage or 0) for s in group),
                "power_damage": max((s.power_damage or 0) for s in group),
                "condition_damage": max((s.condi_damage or 0) for s in group),
                "healing": max((s.healing or 0) for s in group),
                "strips": max((s.boon_strips or 0) for s in group),
                "cleanses": max((s.condition_cleanses or 0) for s in group),
                "kills": max((s.killed or 0) for s in group),
                "breakbar": max((s.breakbar_damage or 0) for s in group),
                "boons": 100,
                "alacrity": 100,
                "quickness": 100,
            }

        results = []
        for stat in stats_list:
            max_values = fight_max_values.get(stat.fight_id)
            score_result = PlayerScoreService.calculate_single_score(
                db, stat, max_values=max_values
            )

            # ?ORM 对象转为 dict，并附加评分字段
            stat_dict = {
                c.name: getattr(stat, c.name)
                for c in stat.__table__.columns
            }
            stat_dict["ai_score"] = score_result["total_score"]
            stat_dict["score_grade"] = score_result["grade"]
            stat_dict["score_breakdown"] = score_result["breakdown"]
            stat_dict["role_type"] = score_result["role_type"]
            stat_dict["grade_label"] = score_result["grade_label"]
            results.append(stat_dict)

        return results
