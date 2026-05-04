# -*- coding: utf-8 -*-
"""
WvW 战斗报告服务

从 ZEVTC 同步的 EI 格式表（ei_player/ei_target/ei_phase/ei_skill_map）
中读取数据，组装成适合前端消费的 WvW 战斗分析结构。

设计理念：
  - 不追求 EI 的完整复杂度，聚焦 WvW 场景核心需求
  - 提供 squad composition、performance ranking、timeline 等差异化功能
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.zevtc_data import EiPhase, EiPlayer, EiSkillMap, EiTarget
from app.utils.logger import logger


class WvwReportService:
    """WvW 战斗报告数据服务"""

    # =====================================================================
    # 战斗概览
    # =====================================================================
    @staticmethod
    def get_summary(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
        """获取战斗概览"""
        players = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).all()
        phases = db.query(EiPhase).filter(EiPhase.log_id == log_id).all()
        targets = db.query(EiTarget).filter(EiTarget.log_id == log_id).all()

        if not players:
            return None

        # 总伤害
        total_damage = sum(
            (p.dps_all_json[0]["damage"] if p.dps_all_json else 0) for p in players
        )
        total_power = sum(
            (p.dps_all_json[0]["powerDamage"] if p.dps_all_json else 0) for p in players
        )
        total_condi = sum(
            (p.dps_all_json[0]["condiDamage"] if p.dps_all_json else 0) for p in players
        )

        # 防御统计
        total_down = sum(
            (p.defenses_json[0]["downCount"] if p.defenses_json else 0) for p in players
        )
        total_dead = sum(
            (p.defenses_json[0]["deadCount"] if p.defenses_json else 0) for p in players
        )
        total_taken = sum(
            (p.defenses_json[0]["damageTaken"] if p.defenses_json else 0)
            for p in players
        )

        # 支援统计
        total_cleanse = sum(
            (p.support_json[0]["condiCleanse"] if p.support_json else 0)
            for p in players
        )
        total_heal = sum(
            (p.support_json[0]["healing"] if p.support_json else 0) for p in players
        )

        # 职业分布
        prof_counts = defaultdict(lambda: {"count": 0, "damage": 0})
        for p in players:
            prof = p.profession
            prof_counts[prof]["count"] += 1
            prof_counts[prof]["damage"] += (
                p.dps_all_json[0]["damage"] if p.dps_all_json else 0
            )

        # 小队分布（如果有 group_id）
        group_counts = defaultdict(int)
        for p in players:
            group_counts[p.group_id or 1] += 1

        # Phase 信息
        phase_list = []
        for ph in phases:
            phase_list.append(
                {
                    "phase_index": ph.phase_index,
                    "name": ph.name,
                    "start_ms": ph.start_ms,
                    "end_ms": ph.end_ms,
                    "duration_ms": ph.end_ms - ph.start_ms,
                }
            )

        duration_ms = phase_list[0]["duration_ms"] if phase_list else 0

        # 尝试获取日志基本信息
        log_info = WvwReportService._get_log_info(db, log_id)

        return {
            "log_id": log_id,
            "log_name": log_info.get("log_name", f"Log-{log_id}"),
            "arc_version": log_info.get("arc_version"),
            "duration_ms": duration_ms,
            "duration_sec": duration_ms // 1000,
            "player_count": len(players),
            "target_count": len(targets),
            "uploaded_at": log_info.get("uploaded_at"),
            "damage": {
                "total": total_damage,
                "power": total_power,
                "condi": total_condi,
                "avg_dps": total_damage // max(1, duration_ms // 1000),
            },
            "defenses": {
                "total_down": total_down,
                "total_dead": total_dead,
                "total_damage_taken": total_taken,
            },
            "support": {
                "total_cleanse": total_cleanse,
                "total_healing": total_heal,
            },
            "composition": {
                "professions": [
                    {"name": k, "count": v["count"], "damage": v["damage"]}
                    for k, v in sorted(
                        prof_counts.items(), key=lambda x: x[1]["damage"], reverse=True
                    )
                ],
                "groups": [
                    {"group_id": k, "count": v} for k, v in sorted(group_counts.items())
                ],
            },
            "phases": phase_list,
            "has_synced_data": True,
        }

    @staticmethod
    def _get_log_info(db: Session, log_id: int) -> Dict[str, Any]:
        """获取日志基本信息"""
        from app.models.log import Log

        info = {}
        log = db.query(Log).filter(Log.id == log_id).first()
        if log:
            info["log_name"] = log.filename
            info["uploaded_at"] = (
                log.upload_time.isoformat() if log.upload_time else None
            )

        # 原从 evtc_header 读取 arc_version，该表已废弃删除
        info["arc_version"] = None

        return info

    # =====================================================================
    # 玩家列表与排行榜
    # =====================================================================
    @staticmethod
    def get_players(
        db: Session, log_id: int, sort_by: str = "damage"
    ) -> List[Dict[str, Any]]:
        """获取所有玩家的摘要数据，支持排序"""
        players = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).all()

        result = []
        for p in players:
            dps_data = p.dps_all_json[0] if p.dps_all_json else {}
            stats_data = p.stats_all_json[0] if p.stats_all_json else {}
            defs_data = p.defenses_json[0] if p.defenses_json else {}
            sup_data = p.support_json[0] if p.support_json else {}

            result.append(
                {
                    "player_id": p.player_id,
                    "agent_index": p.agent_index,
                    "account": p.account,
                    "character_name": p.character_name,
                    "profession": p.profession,
                    "group_id": p.group_id or 1,
                    "has_commander_tag": bool(p.has_commander_tag),
                    "damage": dps_data.get("damage", 0),
                    "dps": dps_data.get("dps", 0),
                    "power_damage": dps_data.get("powerDamage", 0),
                    "condi_damage": dps_data.get("condiDamage", 0),
                    "critical_rate": stats_data.get("criticalRate", 0),
                    "flanking_rate": stats_data.get("flankingRate", 0),
                    "missed": stats_data.get("missed", 0),
                    "glance_rate": stats_data.get("glanceRate", 0),
                    "swap_count": stats_data.get("swapCount", 0),
                    "damage_taken": defs_data.get("damageTaken", 0),
                    "down_count": defs_data.get("downCount", 0),
                    "dead_count": defs_data.get("deadCount", 0),
                    "condi_cleanse": sup_data.get("condiCleanse", 0),
                    "healing": sup_data.get("healing", 0),
                    "rotation_length": len(p.rotation_json) if p.rotation_json else 0,
                }
            )

        # 排序
        sort_key = {
            "damage": "damage",
            "dps": "dps",
            "taken": "damage_taken",
            "downs": "down_count",
            "support": "condi_cleanse",
            "healing": "healing",
        }.get(sort_by, "damage")

        result.sort(key=lambda x: x[sort_key], reverse=True)
        return result

    # =====================================================================
    # 单个玩家详情
    # =====================================================================
    @staticmethod
    def get_player_detail(
        db: Session, log_id: int, player_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取单个玩家完整详情"""
        p = (
            db.query(EiPlayer)
            .filter(EiPlayer.log_id == log_id, EiPlayer.player_id == player_id)
            .first()
        )

        if not p:
            return None

        return {
            "player_id": p.player_id,
            "agent_index": p.agent_index,
            "account": p.account,
            "character_name": p.character_name,
            "profession": p.profession,
            "group_id": p.group_id,
            "has_commander_tag": bool(p.has_commander_tag),
            "dps_all": p.dps_all_json or [],
            "stats_all": p.stats_all_json or [],
            "defenses": p.defenses_json or [],
            "support": p.support_json or [],
            "buff_uptimes": p.buff_uptimes_json or [],
            "rotation": p.rotation_json or [],
        }

    # =====================================================================
    # 目标列表
    # =====================================================================
    @staticmethod
    def get_targets(db: Session, log_id: int) -> List[Dict[str, Any]]:
        """获取所有目标数据"""
        targets = db.query(EiTarget).filter(EiTarget.log_id == log_id).all()
        return [
            {
                "target_id": t.target_id,
                "agent_index": t.agent_index,
                "name": t.name,
                "enemy_player": bool(t.enemy_player),
                "total_health": t.total_health,
                "final_health": t.final_health,
                "dps_all": t.dps_all_json or [],
                "defenses": t.defenses_json or [],
            }
            for t in targets
        ]

    # =====================================================================
    # 阶段列表
    # =====================================================================
    @staticmethod
    def get_phases(db: Session, log_id: int) -> List[Dict[str, Any]]:
        """获取所有阶段数据"""
        phases = (
            db.query(EiPhase)
            .filter(EiPhase.log_id == log_id)
            .order_by(EiPhase.phase_index)
            .all()
        )
        return [
            {
                "phase_id": ph.phase_id,
                "phase_index": ph.phase_index,
                "name": ph.name,
                "start_ms": ph.start_ms,
                "end_ms": ph.end_ms,
                "duration_ms": ph.end_ms - ph.start_ms,
                "breakbar_phase": bool(ph.breakbar_phase),
                "targets": ph.targets_json or [],
            }
            for ph in phases
        ]

    # =====================================================================
    # 技能映射
    # =====================================================================
    @staticmethod
    def get_skill_map(db: Session, log_id: int) -> Dict[str, Dict[str, Any]]:
        """获取技能映射表"""
        skills = db.query(EiSkillMap).filter(EiSkillMap.log_id == log_id).all()
        return {
            sk.skill_key: {
                "gw2_skill_id": sk.gw2_skill_id,
                "name": sk.name,
                "auto_attack": bool(sk.auto_attack),
                "can_crit": bool(sk.can_crit),
                "is_swap": bool(sk.is_swap),
                "icon": sk.icon,
            }
            for sk in skills
        }

    # =====================================================================
    # 战斗时间线（evtc_event 表已废弃，当前返回空列表）
    # =====================================================================
    @staticmethod
    def get_timeline(db: Session, log_id: int) -> List[Dict[str, Any]]:
        """
        获取战斗关键事件时间线。
        原从 evtc_event / evtc_agent 读取，该体系已废弃。如需恢复时间线功能，
        可从 fight_stats 的 down_count / dead_count 等字段重构。
        """
        logger.info(f"[WvWReport] timeline 功能已随 evtc_event 表废弃，log_id={log_id}")
        return []

    # =====================================================================
    # 可用报告列表
    # =====================================================================
    @staticmethod
    def list_available_logs(
        db: Session, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """获取已有同步数据的日志列表"""
        from sqlalchemy import func

        from app.models.log import Log

        # Join 查询：只获取有 ei_player 数据的日志
        total = (
            db.query(func.count(Log.id))
            .join(EiPlayer, Log.id == EiPlayer.log_id)
            .scalar()
        )

        logs = (
            db.query(Log)
            .join(EiPlayer, Log.id == EiPlayer.log_id)
            .order_by(Log.upload_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = []
        for log in logs:
            player_count = (
                db.query(func.count(EiPlayer.player_id))
                .filter(EiPlayer.log_id == log.id)
                .scalar()
            )

            phase = db.query(EiPhase).filter(EiPhase.log_id == log.id).first()
            duration_ms = (phase.end_ms - phase.start_ms) if phase else 0

            items.append(
                {
                    "log_id": log.id,
                    "log_name": log.filename,
                    "duration_ms": duration_ms,
                    "duration_sec": duration_ms // 1000,
                    "player_count": player_count,
                    "uploaded_at": (
                        log.upload_time.isoformat() if log.upload_time else None
                    ),
                }
            )

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size,
        }
