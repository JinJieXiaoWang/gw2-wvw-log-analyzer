# -*- coding: utf-8 -*-
"""EI 数据存储服务模块"""
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.log.zevtc_data import EiPlayer, EiSkillMap, EiTarget
from app.utils.logger import logger

from .player_validator import resolve_commander_tag, should_skip_player


def insert_ei_players(db: Session, log_id: int, ei_json: Dict[str, Any]):
    """插入/更新 EiPlayer（技能循环、stats、defenses、deathRecap 等）
    过滤假玩家/ NPC，确保 ei_player 中 fight_stats 数据一致
    【优化】使 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值
    """
    db.execute(
        text("DELETE FROM ei_player WHERE log_id = :log_id"), {"log_id": log_id}
    )
    db.flush()

    mappings = []
    for idx, p in enumerate(ei_json.get("players", [])):
        if should_skip_player(p):
            logger.info(f"[import] EiPlayer 跳过假玩家/NPC: {p.get('account')} / {p.get('name')}")
            continue

        has_cmd = resolve_commander_tag(p)

        mappings.append({
            "log_id": log_id,
            "agent_index": idx,
            "account": p.get("account", ""),
            "character_name": p.get("name", ""),
            "profession": p.get("profession", ""),
            "group_id": p.get("group", 1),
            "has_commander_tag": 1 if has_cmd else 0,
            "is_fake": 1 if p.get("isFake") else 0,
            "weapons_json": p.get("weapons") or None,
            "consumables_json": p.get("consumables") or None,
            "dps_all_json": p.get("dpsAll") or None,
            "stats_all_json": p.get("statsAll") or None,
            "defenses_json": p.get("defenses") or None,
            "support_json": p.get("support") or None,
            "buff_uptimes_json": p.get("buffUptimes") or None,
            "rotation_json": p.get("rotation") or None,
            "death_recap_json": p.get("deathRecap") or None,
        })

    if mappings:
        db.bulk_insert_mappings(EiPlayer, mappings)
        db.flush()


def _extract_skill_id_from_key(sk_key: str) -> int:
    """从技能键（如 s12345 或 s-2）提取技能ID"""
    if sk_key.startswith("s"):
        try:
            return int(sk_key[1:])
        except ValueError:
            pass
    return 0


def insert_skill_maps(db: Session, log_id: int, ei_json: Dict[str, Any]):
    """插入/更新 EiSkillMap（技能映射，name 去除双引号）
    【优化】使 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值
    """
    db.execute(
        text("DELETE FROM ei_skill_map WHERE log_id = :log_id"), {"log_id": log_id}
    )
    db.flush()

    mappings = []
    for sk_key, sk in ei_json.get("skillMap", {}).items():
        name = sk.get("name", "")
        if isinstance(name, str):
            name = name.strip('"')
        gw2_skill_id = sk.get("gw2_skill_id")
        if not gw2_skill_id:
            gw2_skill_id = _extract_skill_id_from_key(sk_key)
        mappings.append({
            "log_id": log_id,
            "skill_key": sk_key,
            "gw2_skill_id": gw2_skill_id,
            "name": name,
            "auto_attack": 1 if sk.get("autoAttack") else 0,
            "can_crit": 1 if sk.get("canCrit") else 0,
            "is_swap": 1 if sk.get("isSwap") else 0,
            "is_instant_cast": 1 if sk.get("isInstantCast") else 0,
            "is_trait_proc": 1 if sk.get("isTraitProc") else 0,
            "icon": sk.get("icon", ""),
        })

    if mappings:
        db.bulk_insert_mappings(EiSkillMap, mappings)
        db.flush()


def insert_targets(db: Session, log_id: int, ei_json: Dict[str, Any]):
    """插入/更新 EiTarget（敌方目标等）
    【优化】使 bulk_insert_mappings 绕过 ORM 跟踪，降低内存峰值
    """
    db.execute(
        text("DELETE FROM ei_target WHERE log_id = :log_id"), {"log_id": log_id}
    )
    db.flush()

    mappings = []
    for idx, t in enumerate(ei_json.get("targets", [])):
        mappings.append({
            "log_id": log_id,
            "agent_index": idx,
            "name": t.get("name", ""),
            "enemy_player": 1 if t.get("enemyPlayer") else 0,
            "total_health": t.get("totalHealth", 0),
            "final_health": t.get("finalHealth", 0),
            "health_percent_burned": t.get("healthPercentBurned", 0),
            "dps_all_json": t.get("dpsAll") or None,
            "defenses_json": t.get("defenses") or None,
        })

    if mappings:
        db.bulk_insert_mappings(EiTarget, mappings)
        db.flush()
