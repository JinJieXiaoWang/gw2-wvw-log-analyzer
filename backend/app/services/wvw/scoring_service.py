# -*- coding: utf-8 -*-
# 模块功能：评分计算服务（v3.0）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-30
# 更新日期：2026-05-07
# 说明：v3.0 — 支持职业特定规则、Buff 覆盖率参与评分、历史数据重算

from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.services.scoring.scoring_rule_service import ScoringRuleService
from app.services.system.sys_config_service import SysConfigService
from app.constants.dict_values import RoleType, get_grade, get_grade_label
from app.utils.logger import logger


class ScoringService:
    """评分计算服务类（基于 FightStats）"""

    @staticmethod
    def _get_scoring_mode(db: Session) -> str:
        """从 sys_config 读取当前评分模式"""
        config_service = SysConfigService(db)
        return config_service.get_config("scoring_mode", "role_based")

    @staticmethod
    def get_scoring_rules(
        db: Session, role_type: str = RoleType.DPS, profession: Optional[str] = None
    ) -> Dict[str, float]:
        """从评分规则表获取规则（按角色类型和职业）
        
        Args:
            db: 数据库会话
            role_type: 角色类型 dps/support/tank
            profession: 精英特长/职业名称，None 表示使用通用规则
        """
        scoring_mode = ScoringService._get_scoring_mode(db)
        service = ScoringRuleService(db)

        if scoring_mode == "profession_based" and profession:
            # profession_based 模式：查找该职业的所有规则并合并
            prof_rules = service.get_profession_rules(profession, active_only=True)
            rules = {}
            for role_rules in prof_rules.values():
                for rule in role_rules:
                    weight_key = f"{rule.dimension}_weight"
                    rules[weight_key] = rule.weight
            rules.setdefault("min_score_threshold", 0.0)
            rules.setdefault("max_score_cap", 100.0)
            if rules and len(rules) > 2:
                return rules
            # 如果该职业没有规则，回退到 role_based 逻辑

        rules = service.get_rules_for_scoring(role_type, profession)

        # 如果表为空，从 JSON 配置加载兜底规则
        if not rules or len(rules) <= 2:
            from app.services.scoring.score_query_service import _get_default_fallback_rules
            rules = _get_default_fallback_rules(role_type)
            logger.warning(
                f"评分规则表为空或数据不足，已使用 JSON 兜底规则 "
                f"(role_type={role_type}, profession={profession})"
            )

        return rules

    @staticmethod
    def calculate_player_score(
        stats: Dict[str, Any],
        rules: Dict[str, float],
        max_values: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """计算单个玩家评分
        
        Args:
            stats: 玩家统计数据字典
            rules: 评分规则权重字典
            max_values: 同场最大值字典（用于归一化）
        """
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

        # 从 stats 读取 Buff 覆盖率（v3.0 修复硬编码问题）
        might = float(stats.get("might_uptime") or 0)
        fury = float(stats.get("fury_uptime") or 0)
        protection = float(stats.get("protection_uptime") or 0)
        stability = float(stats.get("stability_uptime") or 0)
        quickness = float(stats.get("quickness_uptime") or 0)
        alacrity = float(stats.get("alacrity_uptime") or 0)

        # 综合增益覆盖率 = 关键增益平均值
        boons_score = min(100.0, (might + fury + protection + stability) / 4)

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
            "boons": boons_score,
            "alacrity": min(100.0, alacrity),
            "quickness": min(100.0, quickness),
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
        return get_grade(score)

    @staticmethod
    def get_grade_label(grade: str) -> str:
        """根据等级获取中文标签"""
        return get_grade_label(grade)

    @staticmethod
    def calculate_all_scores(
        fight_id: int, db: Session, role_type: str = RoleType.DPS, profession: Optional[str] = None
    ) -> Dict[str, Any]:
        """计算一场战斗中所有玩家的评分
        
        Args:
            fight_id: 战斗ID
            db: 数据库会话
            role_type: 角色类型 dps/support/tank
            profession: 指定职业（用于预览），None 则按各玩家实际职业计算
        """
        stats_list = db.query(FightStats).filter(FightStats.fight_id == fight_id).all()
        if not stats_list:
            return {
                "fight_id": fight_id,
                "total_players": 0,
                "scores": [],
                "scoring_rules": ScoringService.get_scoring_rules(db, role_type, profession),
            }

        # 计算最大值用于归一化（Buff 覆盖率固定上限100）
        max_values = {
            "damage": max(s.damage or 0 for s in stats_list),
            "power_damage": max(s.power_damage or 0 for s in stats_list),
            "condition_damage": max(s.condi_damage or 0 for s in stats_list),
            "healing": max(s.healing or 0 for s in stats_list),
            "strips": max(s.boon_strips or 0 for s in stats_list),
            "cleanses": max(s.condition_cleanses or 0 for s in stats_list),
            "kills": max(s.killed or 0 for s in stats_list),
            "breakbar": max(s.breakbar_damage or 0 for s in stats_list),
            "boons": 100,
            "alacrity": 100,
            "quickness": 100,
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
                "might_uptime": float(stat.might_uptime or 0),
                "fury_uptime": float(stat.fury_uptime or 0),
                "quickness_uptime": float(stat.quickness_uptime or 0),
                "alacrity_uptime": float(stat.alacrity_uptime or 0),
                "protection_uptime": float(stat.protection_uptime or 0),
                "stability_uptime": float(stat.stability_uptime or 0),
            }

            # 如果未指定 profession，按玩家实际职业获取规则
            player_profession = profession or stat.profession
            player_role_type = role_type
            if not profession and player_profession:
                from app.services.game.game_data_service import GameDataService
                player_role_type = GameDataService().get_role_type(player_profession)

            rules = ScoringService.get_scoring_rules(db, player_role_type, player_profession)
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
            "scoring_rules": ScoringService.get_scoring_rules(db, role_type, profession),
        }

    # ==================== 历史数据重算 ====================

    @staticmethod
    def recalculate_fight_scores(
        fight_id: int, db: Session, version: Optional[int] = None
    ) -> Dict[str, int]:
        """重新计算一场战斗中所有玩家的评分
        
        Args:
            fight_id: 战斗ID
            db: 数据库会话
            version: 新的规则版本号（写入 fight_stats）
            
        Returns:
            {"updated_count": 更新记录数}
        """
        stats_list = db.query(FightStats).filter(FightStats.fight_id == fight_id).all()
        if not stats_list:
            return {"updated_count": 0}

        from app.services.game.game_data_service import GameDataService
        game_data = GameDataService(db)

        # 计算同场最大值
        max_values = {
            "damage": max(s.damage or 0 for s in stats_list),
            "power_damage": max(s.power_damage or 0 for s in stats_list),
            "condition_damage": max(s.condi_damage or 0 for s in stats_list),
            "healing": max(s.healing or 0 for s in stats_list),
            "strips": max(s.boon_strips or 0 for s in stats_list),
            "cleanses": max(s.condition_cleanses or 0 for s in stats_list),
            "kills": max(s.killed or 0 for s in stats_list),
            "breakbar": max(s.breakbar_damage or 0 for s in stats_list),
            "boons": 100,
            "alacrity": 100,
            "quickness": 100,
        }

        updated_count = 0
        for stat in stats_list:
            profession = stat.profession
            role_type = game_data.get_role_type(profession) if profession else RoleType.DPS
            rules = ScoringService.get_scoring_rules(db, role_type, profession)

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
                "might_uptime": float(stat.might_uptime or 0),
                "fury_uptime": float(stat.fury_uptime or 0),
                "quickness_uptime": float(stat.quickness_uptime or 0),
                "alacrity_uptime": float(stat.alacrity_uptime or 0),
                "protection_uptime": float(stat.protection_uptime or 0),
                "stability_uptime": float(stat.stability_uptime or 0),
            }

            result = ScoringService.calculate_player_score(stat_dict, rules, max_values)

            stat.ai_score = result["total_score"]
            stat.score_grade = result["grade"][:10]
            stat.score_breakdown = result["breakdown"]
            stat.role_type = role_type
            if version is not None:
                stat.rule_version = version
            stat.scoring_profession_rule = profession if profession else None
            updated_count += 1

        db.commit()
        return {"updated_count": updated_count}

    @staticmethod
    def recalculate_scores_by_filters(
        db: Session,
        filters: Dict[str, Any],
        version: int,
        batch_size: int = 1000,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ) -> Dict[str, int]:
        """根据筛选条件批量重算评分
        
        Args:
            db: 数据库会话
            filters: 筛选条件，支持 fight_ids, date_from, date_to, professions, account_names
            version: 新的规则版本号
            batch_size: 每批处理记录数
            progress_callback: 进度回调函数(batch_idx, total_batches, updated_count)
            
        Returns:
            {"updated_count": 总更新记录数}
        """
        from app.services.game.game_data_service import GameDataService
        game_data = GameDataService()

        # 构建基础查询
        query = db.query(FightStats)

        # 应用筛选条件
        if filters.get("fight_ids"):
            query = query.filter(FightStats.fight_id.in_(filters["fight_ids"]))

        if filters.get("professions"):
            query = query.filter(FightStats.profession.in_(filters["professions"]))

        if filters.get("account_names"):
            query = query.filter(FightStats.account.in_(filters["account_names"]))

        if filters.get("date_from") or filters.get("date_to"):
            query = query.join(Fight, FightStats.fight_id == Fight.id)
            if filters.get("date_from"):
                query = query.filter(func.date(Fight.start_time) >= filters["date_from"])
            if filters.get("date_to"):
                query = query.filter(func.date(Fight.start_time) <= filters["date_to"])

        # 统计总数
        total_count = query.count()
        if total_count == 0:
            return {"updated_count": 0}

        total_batches = (total_count + batch_size - 1) // batch_size
        updated_total = 0

        for batch_idx in range(total_batches):
            batch_records = query.offset(batch_idx * batch_size).limit(batch_size).all()
            if not batch_records:
                break

            # 按 fight_id 分组，计算每场的 max_values
            fight_groups = {}
            for stat in batch_records:
                fight_groups.setdefault(stat.fight_id, []).append(stat)

            for fight_id, stats_list in fight_groups.items():
                max_values = {
                    "damage": max(s.damage or 0 for s in stats_list),
                    "power_damage": max(s.power_damage or 0 for s in stats_list),
                    "condition_damage": max(s.condi_damage or 0 for s in stats_list),
                    "healing": max(s.healing or 0 for s in stats_list),
                    "strips": max(s.boon_strips or 0 for s in stats_list),
                    "cleanses": max(s.condition_cleanses or 0 for s in stats_list),
                    "kills": max(s.killed or 0 for s in stats_list),
                    "breakbar": max(s.breakbar_damage or 0 for s in stats_list),
                    "boons": 100,
                    "alacrity": 100,
                    "quickness": 100,
                }

                for stat in stats_list:
                    profession = stat.profession
                    role_type = game_data.get_role_type(profession) if profession else RoleType.DPS
                    rules = ScoringService.get_scoring_rules(db, role_type, profession)

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
                        "might_uptime": float(stat.might_uptime or 0),
                        "fury_uptime": float(stat.fury_uptime or 0),
                        "quickness_uptime": float(stat.quickness_uptime or 0),
                        "alacrity_uptime": float(stat.alacrity_uptime or 0),
                        "protection_uptime": float(stat.protection_uptime or 0),
                        "stability_uptime": float(stat.stability_uptime or 0),
                    }

                    result = ScoringService.calculate_player_score(stat_dict, rules, max_values)

                    stat.ai_score = result["total_score"]
                    stat.score_grade = result["grade"][:10]
                    stat.score_breakdown = result["breakdown"]
                    stat.role_type = role_type
                    stat.rule_version = version
                    stat.scoring_profession_rule = profession if profession else None
                    updated_total += 1

            db.commit()

            if progress_callback:
                progress_callback(batch_idx + 1, total_batches, updated_total)

            logger.info(
                f"评分重算进度: {batch_idx + 1}/{total_batches} 批次完成, "
                f"已更新 {updated_total}/{total_count} 条记录"
            )

        return {"updated_count": updated_total}
