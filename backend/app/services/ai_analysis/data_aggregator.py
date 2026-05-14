# -*- coding: utf-8 -*-
# 模块功能：AI分析数据聚合层
# 说明：从数据库提取并聚合原始数据，为各分析器提供结构化输入

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.models.log.zevtc_data import EiPlayer
from app.utils.logger import logger


# ==================== FightStats 聚合器 ====================


class FightStatsAggregator:
    """战斗统计数据聚合器"""

    # 可用于AI分析的核心维度字段
    DIMENSION_FIELDS = [
        "damage", "dps", "power_damage", "condi_damage", "breakbar_damage",
        "healing", "resurrects", "condi_cleanse_ally", "boon_strips_ally",
        "might_uptime", "fury_uptime", "quickness_uptime", "alacrity_uptime",
        "protection_uptime", "stability_uptime",
        "might_uptime_active", "quickness_uptime_active", "alacrity_uptime_active",
        "damage_taken", "blocked_count", "evaded_count", "dodge_count",
        "down_count", "dead_count", "boon_strips", "condition_cleanses",
        "critical_rate", "flanking_rate", "glance_rate", "missed",
        "killed", "downed", "interrupts", "swap_count",
        "applied_cc_duration", "applied_cc_count",
        "barrier_damage_absorbed", "condition_damage_taken", "power_damage_taken",
        "received_cc_duration", "avg_boons", "avg_conditions",
        "wasted", "saved", "skill_cast_uptime",
        "stack_dist", "dist_to_com",
        "downed_damage_taken", "interrupted_count",
        "down_duration", "dead_duration", "dc_count", "dc_duration",
        "stun_break", "removed_stun_duration",
    ]

    @staticmethod
    def get_player_history(
        db: Session,
        account: str,
        fight_count: int = 30,
        profession_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取指定玩家的历史战斗数据

        返回按时间排序的战斗记录列表
        """
        query = (
            db.query(FightStats, Fight)
            .join(Fight, FightStats.fight_id == Fight.id)
            .filter(FightStats.account == account)
            .filter(FightStats.is_deleted == 0 if hasattr(FightStats, 'is_deleted') else True)
        )

        if profession_filter:
            query = query.filter(FightStats.profession == profession_filter)

        results = (
            query.order_by(Fight.start_time.desc())
            .limit(fight_count)
            .all()
        )

        records = []
        for stats, fight in results:
            record = {
                "fight_id": fight.id,
                "start_time": fight.start_time.isoformat() if fight.start_time else None,
                "map_name": fight.map_name,
                "duration_sec": fight.duration_sec,
                "profession": stats.profession,
                "character_name": stats.character_name,
                "group_id": stats.group_id,
                "has_commander_tag": bool(stats.has_commander_tag),
            }
            for field in FightStatsAggregator.DIMENSION_FIELDS:
                record[field] = getattr(stats, field, 0) or 0
            # 评分数据
            record["ai_score"] = float(stats.ai_score) if stats.ai_score else 0
            record["score_grade"] = stats.score_grade or ""
            records.append(record)

        # 按时间正序排列（ oldest -> newest ）
        records.reverse()
        return records

    @staticmethod
    def get_guild_averages(
        db: Session,
        profession: Optional[str] = None,
        days: int = 30,
    ) -> Dict[str, float]:
        """
        获取公会成员在指定时间范围内的平均水平
        """
        start_date = datetime.now() - timedelta(days=days)

        query = (
            db.query(FightStats)
            .join(Fight, FightStats.fight_id == Fight.id)
            .filter(Fight.start_time >= start_date)
        )

        if profession:
            query = query.filter(FightStats.profession == profession)

        stats_list = query.all()
        if not stats_list:
            return {}

        averages = {}
        for field in FightStatsAggregator.DIMENSION_FIELDS:
            values = [getattr(s, field, 0) or 0 for s in stats_list]
            averages[field] = sum(values) / max(len(values), 1)

        return averages

    @staticmethod
    def get_guild_percentiles(
        db: Session,
        profession: str,
        dimension: str,
        days: int = 30,
    ) -> List[float]:
        """
        获取指定职业某维度的所有值，用于计算百分位
        """
        start_date = datetime.now() - timedelta(days=days)
        stats_list = (
            db.query(FightStats)
            .join(Fight, FightStats.fight_id == Fight.id)
            .filter(FightStats.profession == profession)
            .filter(Fight.start_time >= start_date)
            .all()
        )
        return sorted([getattr(s, dimension, 0) or 0 for s in stats_list])

    @staticmethod
    def calculate_player_percentile(
        player_value: float,
        guild_values: List[float],
    ) -> int:
        """
        计算玩家在某维度上的公会百分位排名 (0-100)
        """
        if not guild_values:
            return 50
        count = len(guild_values)
        below = sum(1 for v in guild_values if v < player_value)
        return int((below / count) * 100)


# ==================== EI JSON 提取器 ====================


class EiJsonExtractor:
    """EI原始JSON数据提取器"""

    @staticmethod
    def get_death_recap(
        db: Session,
        log_id: int,
        account: str,
    ) -> Optional[Dict]:
        """
        获取指定玩家的死亡回放数据
        """
        player = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id)
            .filter(EiPlayer.account == account)
            .first()
        )
        if not player or not player.death_recap_json:
            return None
        try:
            return json.loads(player.death_recap_json)
        except json.JSONDecodeError:
            logger.warning(f"死亡回放JSON解析失败: log_id={log_id}, account={account}")
            return None

    @staticmethod
    def get_rotation(
        db: Session,
        log_id: int,
        account: str,
    ) -> Optional[List]:
        """
        获取指定玩家的技能循环数据
        """
        player = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id)
            .filter(EiPlayer.account == account)
            .first()
        )
        if not player or not player.rotation_json:
            return None
        if isinstance(player.rotation_json, list):
            return player.rotation_json
        try:
            return json.loads(player.rotation_json)
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def get_buff_uptimes(
        db: Session,
        log_id: int,
        account: str,
    ) -> Optional[List]:
        """
        获取指定玩家的Buff覆盖率详情
        """
        player = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id)
            .filter(EiPlayer.account == account)
            .first()
        )
        if not player or not player.buff_uptimes_json:
            return None
        if isinstance(player.buff_uptimes_json, list):
            return player.buff_uptimes_json
        try:
            return json.loads(player.buff_uptimes_json)
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def get_weapons(
        db: Session,
        log_id: int,
        account: str,
    ) -> Optional[List]:
        """
        获取指定玩家的武器配置
        """
        player = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id)
            .filter(EiPlayer.account == account)
            .first()
        )
        if not player or not player.weapons_json:
            return None
        if isinstance(player.weapons_json, list):
            return player.weapons_json
        try:
            return json.loads(player.weapons_json)
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def get_consumables(
        db: Session,
        log_id: int,
        account: str,
    ) -> Optional[List]:
        """
        获取指定玩家的食物/扳手配置
        """
        player = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id)
            .filter(EiPlayer.account == account)
            .first()
        )
        if not player or not player.consumables_json:
            return None
        if isinstance(player.consumables_json, list):
            return player.consumables_json
        try:
            return json.loads(player.consumables_json)
        except (json.JSONDecodeError, TypeError):
            return None


# ==================== 小队数据聚合器 ====================


class SquadAggregator:
    """小队数据聚合器"""

    @staticmethod
    def get_fight_squads(
        db: Session,
        fight_id: int,
    ) -> Dict[int, List[FightStats]]:
        """
        获取某场战斗按group_id分组的小队数据
        返回 {group_id: [FightStats, ...]}
        """
        stats_list = (
            db.query(FightStats)
            .filter(FightStats.fight_id == fight_id)
            .all()
        )

        squads: Dict[int, List[FightStats]] = {}
        for stats in stats_list:
            gid = stats.group_id or 1
            if gid not in squads:
                squads[gid] = []
            squads[gid].append(stats)

        return squads

    @staticmethod
    def get_fight_averages(
        db: Session,
        fight_id: int,
    ) -> Dict[str, float]:
        """
        获取某场战斗的全局平均值
        """
        stats_list = (
            db.query(FightStats)
            .filter(FightStats.fight_id == fight_id)
            .all()
        )

        if not stats_list:
            return {}

        averages = {}
        for field in FightStatsAggregator.DIMENSION_FIELDS:
            values = [getattr(s, field, 0) or 0 for s in stats_list]
            averages[field] = sum(values) / max(len(values), 1)

        return averages
