# -*- coding: utf-8 -*-
"""
EI 统一数据服务

功能：为 EiDetailView 提供统一的后端接口，自动选择最佳数据源：
  1. 优先从 ei_report 表返回完整的 EI _logData（如果已通过 HTML 导入）
  2. 如果没有 HTML 数据，从 ei_player/ei_target/ei_phase 等 ZEVTC 同步表组装 EI 格式数据

设计理念：
  - 前端只需调用一个接口，后端自动处理数据源选择
  - 组装逻辑尽量还原 EI 数据结构，让 EiDetailView 能够正常渲染
  - 对于 ZEVTC 数据无法提供的字段（如 damage1S 时间序列），使用合理的默认值或空数组
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ei_report import EiReport
from app.models.log import Log
from app.models.zevtc_data import EiPhase, EiPlayer, EiSkillMap, EiTarget
from app.services.ei.report_service import get_full_graph_data, get_full_log_data
from app.utils.logger import logger


def _parse_weapons(weapons_json: Optional[Any]) -> List[str]:
    """解析 weapons_json 为 EI 格式的武器数组"""
    if not weapons_json:
        return []
    try:
        if isinstance(weapons_json, str):
            import json

            weapons_json = json.loads(weapons_json)
        # weapons_json format: [{"l1Set": ["Mace"], "l2Set": ["Shield"], ...}]
        if isinstance(weapons_json, list) and len(weapons_json) > 0:
            ws = weapons_json[0]
            l1 = ws.get("l1Set", []) or []
            l2 = ws.get("l2Set", []) or []
            # EI format: [weapon1_main, weapon1_off, weapon2_main, weapon2_off]
            result = []
            result.extend(l1[:2])  # max 2 weapons for set 1
            while len(result) < 2:
                result.append("")
            result.extend(l2[:2])  # max 2 weapons for set 2
            while len(result) < 4:
                result.append("")
            return result
    except Exception:
        pass
    return []


def get_unified_ei_data(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """
    获取统一的 EI 格式数据，自动选择最佳数据源

    返回结构兼容 EiDetailView 的期望格式：
    {
        "log_id": int,
        "source": "ei_report" | "zevtc_sync",
        "fight_name": str,
        "duration_ms": int,
        "duration_str": str,
        "recorder": {"name": str, "account": str},
        "versions": {"eliteInsights": str, "arc": str, "gw2": str},
        "log_data": {...},  // EI _logData 格式
        "players": [...],    // 完整玩家数组
        "targets": [...],    // 目标数组
        "phases": [...],     // 阶段数组
        "skill_map": {...},  // 技能映射
    }
    """
    # 策略1：优先检查 ei_report（HTML 导入的完整数据）
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if report and report.summary_json:
        data = _from_ei_report(db, log_id, report)
        if data:
            return data

    # 策略2：从 ZEVTC 同步表组装
    has_synced = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).first()
    if has_synced:
        return _from_zevtc_sync(db, log_id)

    return None


def _from_ei_report(
    db: Session, log_id: int, report: EiReport
) -> Optional[Dict[str, Any]]:
    """从 ei_report 表构建统一数据"""
    try:
        summary = report.summary_json or {}
        full_log = get_full_log_data(db, log_id) or {}

        # 构建 logData 结构
        log_data = {
            "duration": report.duration_ms or 0,
            "evtcRecordingDuration": report.duration_ms or 0,
            "logStart": summary.get("logStart", ""),
            "logEnd": summary.get("logEnd", ""),
            "instanceStart": summary.get("instanceStart", ""),
            "instanceIP": summary.get("instanceIP", ""),
            "region": summary.get("region", ""),
            "arcVersion": summary.get("arcVersion", ""),
            "gw2Build": str(summary.get("gw2Build", "")),
            "triggerID": str(summary.get("triggerID", "")),
            "logID": str(summary.get("logID", "")),
            "mapID": str(summary.get("mapID", "")),
            "parser": summary.get("parser", "Elite Insights"),
            "wvw": summary.get("wvw", False),
            "hasCommander": summary.get("hasCommander", False),
            "recordedBy": summary.get("recordedBy", ""),
            "recordedAccountBy": summary.get("recordedAccountBy", ""),
        }

        players = full_log.get("players", []) if full_log else []
        targets = full_log.get("targets", []) if full_log else []
        phases = summary.get("phases", [])
        skill_map = summary.get("skillMap", {})

        return {
            "log_id": log_id,
            "source": "ei_report",
            "fight_name": report.log_name or f"Log-{log_id}",
            "duration_ms": report.duration_ms or 0,
            "duration_str": _format_duration(report.duration_ms or 0),
            "player_count": report.player_count or 0,
            "target_count": report.target_count or 0,
            "recorder": {
                "name": summary.get("recordedBy", "Unknown"),
                "account": summary.get("recordedAccountBy", "Unknown"),
            },
            "versions": {
                "eliteInsights": report.ei_version or "Unknown",
                "arc": summary.get("arcVersion", "Unknown"),
                "gw2": str(summary.get("gw2Build", "")),
            },
            "log_data": log_data,
            "players": players,
            "targets": targets,
            "phases": phases,
            "skill_map": skill_map,
            "has_graph_data": bool(report.graph_data_path),
            "has_cr_data": bool(report.cr_data_path),
        }
    except Exception as e:
        logger.error(f"从 ei_report 构建统一数据失败 log_id={log_id}: {e}")
        return None


def _from_zevtc_sync(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """从 ZEVTC 同步表组装 EI 格式数据"""
    try:
        # 获取基础信息
        log = db.query(Log).filter(Log.id == log_id).first()
        phase = db.query(EiPhase).filter(EiPhase.log_id == log_id).first()

        # 获取所有玩家
        players = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).all()
        targets = db.query(EiTarget).filter(EiTarget.log_id == log_id).all()
        phases = (
            db.query(EiPhase)
            .filter(EiPhase.log_id == log_id)
            .order_by(EiPhase.phase_index)
            .all()
        )
        skills = db.query(EiSkillMap).filter(EiSkillMap.log_id == log_id).all()

        duration_ms = (phase.end_ms - phase.start_ms) if phase else 0

        # 构建 logData
        log_data = {
            "duration": duration_ms,
            "evtcRecordingDuration": duration_ms,
            "logStart": "",
            "logEnd": "",
            "instanceStart": "",
            "instanceIP": "",
            "region": "",
            "arcVersion": "N/A",
            "gw2Build": "",
            "triggerID": str(log_id),
            "logID": str(log_id),
            "mapID": "",
            "parser": "ZEVTC Sync",
            "wvw": True,
            "hasCommander": any(p.has_commander_tag for p in players),
            "recordedBy": "",
            "recordedAccountBy": "",
        }

        # 组装玩家数据为 EI 格式（按伤害降序）
        sorted_players = sorted(
            players,
            key=lambda p: (p.dps_all_json[0].get("damage", 0) if p.dps_all_json else 0),
            reverse=True,
        )
        ei_players = [_build_ei_player(p, duration_ms) for p in sorted_players]

        # 组装目标数据（包含敌方玩家和NPC）
        # WvW日志中：敌方玩家prof在1-9但没有account_name
        enemy_players = [p for p in players if not p.account]
        ei_targets = [_build_ei_target_from_player(p) for p in enemy_players]
        ei_targets += [_build_ei_target(t) for t in targets]

        # 组装阶段数据
        ei_phases = [_build_ei_phase(ph) for ph in phases]

        # 组装技能映射
        skill_map = {
            sk.skill_key: {"name": sk.name, "id": sk.gw2_skill_id} for sk in skills
        }

        return {
            "log_id": log_id,
            "source": "zevtc_sync",
            "fight_name": log.filename if log else f"Log-{log_id}",
            "duration_ms": duration_ms,
            "duration_str": _format_duration(duration_ms),
            "player_count": len(players),
            "target_count": len(targets),
            "recorder": {"name": "Unknown", "account": "Unknown"},
            "versions": {
                "eliteInsights": "N/A",
                "arc": "N/A",
                "gw2": "N/A",
            },
            "log_data": log_data,
            "players": ei_players,
            "targets": ei_targets,
            "phases": ei_phases,
            "skill_map": skill_map,
            "has_graph_data": False,
            "has_cr_data": False,
        }
    except Exception as e:
        logger.error(
            f"从 ZEVTC 同步表组装 EI 数据失败 log_id={log_id}: {e}", exc_info=True
        )
        return None


def _build_ei_player(p: EiPlayer, duration_ms: int) -> Dict[str, Any]:
    """将 ei_player 记录转换为 EI 格式的玩家数据"""
    dps_data = p.dps_all_json[0] if p.dps_all_json else {}
    stats_data = p.stats_all_json[0] if p.stats_all_json else {}
    defs_data = p.defenses_json[0] if p.defenses_json else {}
    sup_data = p.support_json[0] if p.support_json else {}

    duration_sec = max(1, duration_ms // 1000)

    # 构建 EI 格式的玩家对象
    return {
        "instanceID": p.player_id,
        "name": p.character_name,
        "profession": p.profession,
        "account": p.account or "",
        "group": p.group_id or 1,
        "hasCommanderTag": bool(p.has_commander_tag),
        "friendlyNPC": False,
        "notInSquad": False,
        "isFake": bool(p.is_fake),
        "dps": dps_data.get("dps", 0),
        "total_score": 0,  # ZEVTC 同步不计算评分
        "cc": 0,
        "downs": defs_data.get("downCount", 0),
        "deaths": defs_data.get("deadCount", 0),
        "cleanses": sup_data.get("condiCleanse", 0),
        "strips": sup_data.get("boonStrips", 0),
        "weapons": _parse_weapons(p.weapons_json),
        "consumables": p.consumables_json or {"food": [], "utility": []},
        "role": "Unknown",
        "hps": sup_data.get("healing", 0),
        "critRate": stats_data.get("criticalRate", 0),
        "critDamage": 0,
        "dpsAll": [
            {
                "dps": dps_data.get("dps", 0),
                "damage": dps_data.get("damage", 0),
                "powerDamage": dps_data.get("powerDamage", 0),
                "condiDamage": dps_data.get("condiDamage", 0),
                "breakbarDamage": dps_data.get("breakbarDamage", 0),
                "actorDps": dps_data.get("actorDps", 0),
                "actorDamage": dps_data.get("actorDamage", 0),
                "actorCondiDps": dps_data.get("condiDps", 0),
                "actorCondiDamage": dps_data.get("condiDamage", 0),
                "actorPowerDps": dps_data.get("powerDps", 0),
                "actorPowerDamage": dps_data.get("powerDamage", 0),
                "actorBreakbarDamage": dps_data.get("breakbarDamage", 0),
            }
        ],
        "defenses": [
            {
                "damageTaken": defs_data.get("damageTaken", 0),
                "downedDamageTaken": 0,
                "breakbarDamageTaken": 0,
                "blockedCount": 0,
                "evadedCount": 0,
                "missedCount": stats_data.get("missed", 0),
                "dodgeCount": 0,
                "invulnedCount": 0,
                "damageBarrier": 0,
                "interruptedCount": 0,
                "downCount": defs_data.get("downCount", 0),
                "downDuration": 0,
                "deadCount": defs_data.get("deadCount", 0),
                "deadDuration": 0,
                "dcCount": 0,
                "dcDuration": 0,
                "boonStrips": sup_data.get("boonStrips", 0),
                "boonStripsTime": 0,
                "conditionCleanses": sup_data.get("condiCleanse", 0),
                "conditionCleansesTime": 0,
            }
        ],
        "statsAll": [
            {
                "wasted": 0,
                "timeWasted": 0,
                "saved": 0,
                "timeSaved": 0,
                "stackDist": 0,
                "distToCom": 0,
                "avgBoons": 0,
                "avgActiveBoons": 0,
                "avgConditions": 0,
                "avgActiveConditions": 0,
                "swapCount": stats_data.get("swapCount", 0),
                "skillCastUptime": 0,
                "skillCastUptimeNoAA": 0,
                "totalDamageCount": stats_data.get("totalDamageCount", 0),
                "totalDmg": dps_data.get("damage", 0),
                "directDamageCount": stats_data.get("directDamageCount", 0),
                "directDmg": dps_data.get("powerDamage", 0),
                "connectedDirectDamageCount": stats_data.get(
                    "connectedDirectDamageCount", 0
                ),
                "connectedDirectDmg": 0,
                "connectedDamageCount": 0,
                "connectedDmg": 0,
                "critableDirectDamageCount": 0,
                "criticalRate": (stats_data.get("criticalRate", 0) or 0) / 100,
                "criticalDmg": 0,
                "flankingRate": (stats_data.get("flankingRate", 0) or 0) / 100,
                "againstMovingRate": 0,
                "glanceRate": (stats_data.get("glanceRate", 0) or 0) / 100,
                "missed": stats_data.get("missed", 0),
                "evaded": 0,
                "blocked": 0,
                "interrupts": stats_data.get("interrupts", 0),
                "invulned": 0,
                "killed": 0,
                "downed": defs_data.get("downCount", 0),
                "downContribution": 0,
                "connectedPowerCount": 0,
                "connectedPowerAbove90HPCount": 0,
                "connectedConditionCount": 0,
                "connectedConditionAbove90HPCount": 0,
                "againstDownedCount": 0,
                "againstDownedDamage": 0,
            }
        ],
        "support": [
            {
                "condiCleanse": sup_data.get("condiCleanse", 0),
                "boonStrips": sup_data.get("boonStrips", 0),
            }
        ],
        "buffUptimes": [],
        "damage1S": [[]],
        "powerDamage1S": [[]],
        "conditionDamage1S": [[]],
        "rotation": p.rotation_json or [[]],
        "damageModifiers": [[]],
        "totalDamageDist": [],
        "totalDamageTaken": [],
        "targetDamageDist": [],
        "statsTargets": [[]],
        "activeTimes": [],
        "selfBuffs": [],
        "buffUptimesActive": [],
        "selfBuffsActive": [],
        "healthPercents": [],
        "barrierPercents": [],
        "dpsTargets": [[]],
        "targetDamage1S": [[]],
        "targetPowerDamage1S": [[]],
        "targetConditionDamage1S": [[]],
        "totalHealth": 0,
        "condition": 0,
        "concentration": 0,
        "healing": 0,
        "toughness": 0,
        "hitboxHeight": 0,
        "hitboxWidth": 0,
        "teamID": 0,
    }


def _build_ei_target_from_player(p: EiPlayer) -> Dict[str, Any]:
    """将敌方玩家（ei_player）转换为 EI 格式的目标数据"""
    dps_data = p.dps_all_json[0] if p.dps_all_json else {}
    defs_data = p.defenses_json[0] if p.defenses_json else {}
    return {
        "instanceID": p.player_id,
        "name": p.character_name,
        "icon": "",
        "finalHealth": 0,
        "firstAware": 0,
        "lastAware": 0,
        "statsAll": [{"totalDmg": dps_data.get("damage", 0)}],
        "dpsAll": [{"damage": dps_data.get("damage", 0)}],
        "enemyPlayer": True,
        "totalHealth": -1,
        "healthPercentBurned": 100,
        "id": p.player_id,
        "condition": 0,
        "concentration": 0,
        "healing": 0,
        "toughness": 0,
        "hitboxHeight": 0,
        "hitboxWidth": 0,
        "teamID": 0,
        "isFake": False,
        "buffs": [],
        "breakbarPercents": [],
        "defenses": [],
        "totalDamageDist": [],
        "totalDamageTaken": [],
        "damage1S": [],
        "powerDamage1S": [],
        "conditionDamage1S": [],
    }


def _build_ei_target(t: EiTarget) -> Dict[str, Any]:
    """将 ei_target 记录转换为 EI 格式的目标数据"""
    dps_data = t.dps_all_json[0] if t.dps_all_json else {}
    return {
        "instanceID": t.target_id,
        "name": t.name,
        "icon": "",
        "finalHealth": t.final_health or 0,
        "firstAware": 0,
        "lastAware": 0,
        "statsAll": [{"totalDmg": dps_data.get("damageTaken", 0)}],
        "dpsAll": [{"damage": dps_data.get("damageTaken", 0)}],
        "enemyPlayer": bool(t.enemy_player),
        "totalHealth": t.total_health or -1,
        "healthPercentBurned": t.health_percent_burned or 0,
        "id": t.target_id,
        "condition": 0,
        "concentration": 0,
        "healing": 0,
        "toughness": 0,
        "hitboxHeight": 0,
        "hitboxWidth": 0,
        "teamID": 0,
        "isFake": False,
        "buffs": [],
        "breakbarPercents": [],
        "defenses": [],
        "totalDamageDist": [],
        "totalDamageTaken": [],
        "damage1S": [],
        "powerDamage1S": [],
        "conditionDamage1S": [],
    }


def _build_ei_phase(ph: EiPhase) -> Dict[str, Any]:
    """将 ei_phase 记录转换为 EI 格式的阶段数据"""
    targets = ph.targets_json or []
    target_ids = [t.get("address", 0) for t in targets]
    return {
        "name": ph.name,
        "duration": ph.end_ms - ph.start_ms,
        "start": ph.start_ms / 1000,
        "end": ph.end_ms / 1000,
        "type": 0,
        "nameNoMode": ph.name,
        "icon": "",
        "mode": "",
        "encounterDuration": ph.end_ms - ph.start_ms,
        "startStatus": "",
        "success": True,
        "encounterPhase": False,
        "targets": target_ids,
        "targetPriorities": {},
        "breakbarPhase": bool(ph.breakbar_phase),
        "breakbarRecovered": 0,
        "breakbarStart": 0,
        "subPhases": [],
        "markupLines": [],
        "markupAreas": [],
    }


def _format_duration(ms: int) -> str:
    """将毫秒格式化为 mm:ss 字符串"""
    total_sec = ms // 1000
    min_ = total_sec // 60
    sec = total_sec % 60
    return f"{min_:02d}:{sec:02d}"
