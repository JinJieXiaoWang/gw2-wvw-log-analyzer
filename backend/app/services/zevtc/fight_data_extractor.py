# -*- coding: utf-8 -*-
"""战斗数据提取模块"""
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.constants.buffs import BUFF_ID_MAP
from app.utils.logger import logger

from .player_validator import resolve_commander_tag, should_skip_player

# EI 在 targets 中嵌入敌方职业名的正则模式: "Mechanist pl-2994"
_ENEMY_PROF_PATTERN = re.compile(r'^([A-Za-z]+)\s+pl-\d+$')


def resolve_friendly_team_id(ei_json: Dict[str, Any]) -> int:
    """从 EI JSON 中解析友方 teamID。
    
    策略：
    1. 优先从 recordedBy / recordedAccountBy 找到录制者，取其 teamID
    2. 如找不到，返回 players 数组中第一个非 fake 玩家的 teamID
    """
    recorded_by = ei_json.get("recordedBy") or ""
    recorded_account = ei_json.get("recordedAccountBy") or ""
    
    for p in ei_json.get("players", []):
        if p.get("isFake") or p.get("friendlyNPC"):
            continue
        if recorded_by and p.get("name") == recorded_by:
            return p.get("teamID", 0)
        if recorded_account and p.get("account") == recorded_account:
            return p.get("teamID", 0)
    
    # 兜底：取第一个有效玩家的 teamID
    for p in ei_json.get("players", []):
        if not p.get("isFake") and not p.get("friendlyNPC"):
            return p.get("teamID", 0)
    return 0


def extract_enemy_composition(ei_json: Dict[str, Any], friendly_team_id: int) -> tuple:
    """从 EI JSON targets 数组中提取敌方职业统计。
    
    EI 解析器在无法获取敌方 profession 字段时，会将职业名嵌入 target.name：
        "Mechanist pl-2994" -> profession = "Mechanist"
    
    Returns:
        (enemy_count: int, composition_json: str | None)
        composition_json 格式: {"Mechanist": 10, "Herald": 4, ...}
    """
    prof_counts: Dict[str, int] = {}
    enemy_count = 0
    
    for t in ei_json.get("targets", []):
        # 跳过非敌方目标
        if not t.get("enemyPlayer", False):
            continue
        if t.get("isFake", False):
            continue
        
        enemy_count += 1
        name = t.get("name", "")
        
        # 尝试从 name 中提取职业
        match = _ENEMY_PROF_PATTERN.match(name)
        if match:
            prof = match.group(1)
            prof_counts[prof] = prof_counts.get(prof, 0) + 1
            continue
        
        # 备用：尝试 profession 字段（某些日志直接提供）
        prof = t.get("profession")
        if prof:
            prof_counts[prof] = prof_counts.get(prof, 0) + 1
            continue
        
        # 尝试从 players 数组中按 name 匹配（log_id=57 的情况）
        for p in ei_json.get("players", []):
            if p.get("name") == name and p.get("teamID") != friendly_team_id:
                prof = p.get("profession")
                if prof:
                    prof_counts[prof] = prof_counts.get(prof, 0) + 1
                break
    
    if not prof_counts:
        return enemy_count, None
    
    # 按数量降序排列
    sorted_comp = dict(sorted(prof_counts.items(), key=lambda x: -x[1]))
    return enemy_count, json.dumps(sorted_comp, ensure_ascii=False)


def extract_uptime(bu: dict) -> float:
    """兼容多种 buffUptimes 结构提取 uptime"""
    uptime = bu.get("uptime")
    if uptime is not None:
        return uptime
    buff_data = bu.get("buffData")
    if buff_data and isinstance(buff_data, list) and len(buff_data) > 0:
        return buff_data[0].get("uptime", 0)
    return 0


def extract_player_healing(player: Dict) -> int:
    """从EI JSON中提取玩家的治疗量，支持多种格式"""
    support = player.get("support", [{}])
    if support and isinstance(support, list):
        healing = support[0].get("healing")
        if healing is not None:
            return int(healing)

    ext_healing = player.get("extHealingStats")
    if ext_healing:
        outgoing = ext_healing.get("outgoingHealing", [{}])
        if outgoing and isinstance(outgoing, list):
            healing = outgoing[0].get("healing")
            if healing is not None:
                return int(healing)
        healing = ext_healing.get("healing")
        if healing is not None:
            return int(healing)

    return 0


def extract_fight_data(ei_json: Dict[str, Any], friendly_team_id: int = 0) -> Dict[str, Any]:
    """提取战斗级标量数据（直接从EI JSON）
    
    Args:
        ei_json: EI解析后的JSON数据
        friendly_team_id: 友方teamID，用于区分敌我玩家统计
    """
    ei_duration_ms = ei_json.get("durationMS", 0)
    duration_sec = max(1, int(ei_duration_ms / 1000))

    ei_start = ei_json.get("timeStartStd") or ei_json.get("timeStart")
    ei_end = ei_json.get("timeEndStd") or ei_json.get("timeEnd")

    ei_players = ei_json.get("players", [])
    total_damage = 0
    total_kills = 0
    total_deaths = 0
    friendly_count = 0
    enemy_count = 0
    
    for p in ei_players:
        if p.get("isFake") or p.get("friendlyNPC"):
            continue
        
        team_id = p.get("teamID", 0)
        is_friendly = (team_id == friendly_team_id) if friendly_team_id else True
        
        dps_all = p.get("dpsAll", [{}])[0]
        stats_all = p.get("statsAll", [{}])[0]
        defenses = p.get("defenses", [{}])[0]
        
        # 总伤害/击杀/死亡统计（包含双方，用于战斗总览）
        total_damage += dps_all.get("damage", 0)
        total_kills += stats_all.get("killed", 0)
        total_deaths += defenses.get("deadCount", 0)
        
        if is_friendly:
            friendly_count += 1
        else:
            enemy_count += 1

    # 提取敌方职业统计（从 targets 数组）
    extracted_enemy_count, enemy_comp_json = extract_enemy_composition(ei_json, friendly_team_id)
    
    # 如果 targets 中没统计到敌方，但 players 中有，用 players 中的计数兜底
    if extracted_enemy_count == 0 and enemy_count > 0:
        extracted_enemy_count = enemy_count

    parsed_start = parse_ei_time(ei_start)
    parsed_end = parse_ei_time(ei_end)

    if not parsed_start:
        logger.warning(f"[import] 无法解析开始时间 {ei_start}，使用当前时间")
        parsed_start = datetime.now(timezone.utc)
    if not parsed_end:
        parsed_end = parsed_start

    return {
        "start_time": parsed_start,
        "end_time": parsed_end,
        "duration_sec": duration_sec,
        "duration_ms": ei_duration_ms,
        "map_name": ei_json.get("fightName"),
        "server_name": "Unknown",
        "recorded_by": ei_json.get("recordedBy"),
        "recorded_account": ei_json.get("recordedAccountBy"),
        "total_damage": total_damage,
        "total_healing": sum(
            extract_player_healing(p) for p in ei_json.get("players", [])
            if not p.get("isFake") and not p.get("friendlyNPC")
        ),
        "kill_count": total_kills,
        "death_count": total_deaths,
        "player_count": friendly_count + enemy_count,  # 总玩家数（向后兼容）
        "friendly_player_count": friendly_count,
        "enemy_player_count": extracted_enemy_count,
        "enemy_composition": enemy_comp_json,
    }


def extract_player_stats(ei_json: Dict[str, Any], friendly_team_id: int = 0) -> List[Dict[str, Any]]:
    """提取每个玩家的标量统计（直接从EI JSON），仅提取友方玩家。
    
    Args:
        ei_json: EI解析后的JSON数据
        friendly_team_id: 友方teamID，用于过滤敌方玩家
    """
    results = []

    for ei_p in ei_json.get("players", []):
        if should_skip_player(ei_p):
            continue
        
        # 排除敌方玩家（teamID不同）
        if friendly_team_id:
            player_team_id = ei_p.get("teamID", 0)
            if player_team_id != friendly_team_id:
                logger.debug(
                    f"[import] 跳过敌方玩家: {ei_p.get('account')} "
                    f"(teamID={player_team_id} != friendly={friendly_team_id})"
                )
                continue

        dps_all = ei_p.get("dpsAll", [{}])[0]
        stats_all = ei_p.get("statsAll", [{}])[0]
        defenses = ei_p.get("defenses", [{}])[0]
        support = ei_p.get("support", [{}])[0]

        buff_uptimes = {}
        for bu in ei_p.get("buffUptimes", []):
            buff_id = bu.get("id")
            name = bu.get("name", "")
            uptime = extract_uptime(bu)
            if buff_id and buff_id in BUFF_ID_MAP:
                buff_uptimes[BUFF_ID_MAP[buff_id]] = uptime
            elif name:
                buff_uptimes[name.lower()] = uptime

        buff_uptimes_active = {}
        for bu in ei_p.get("buffUptimesActive", []):
            buff_id = bu.get("id")
            name = bu.get("name", "")
            uptime = extract_uptime(bu)
            if buff_id and buff_id in BUFF_ID_MAP:
                buff_uptimes_active[BUFF_ID_MAP[buff_id]] = uptime
            elif name:
                buff_uptimes_active[name.lower()] = uptime

        has_cmd = resolve_commander_tag(ei_p)

        player = {
            "account": ei_p.get("account", ""),
            "character_name": ei_p.get("name", ""),
            "profession": ei_p.get("profession", ""),
            "group_id": ei_p.get("group", 0),
            "team_id": ei_p.get("teamID", 0),
            "has_commander_tag": has_cmd,
            "damage": dps_all.get("damage", 0),
            "dps": dps_all.get("dps", 0),
            "power_damage": dps_all.get("powerDamage", 0),
            "condi_damage": dps_all.get("condiDamage", 0),
            "breakbar_damage": int(dps_all.get("breakbarDamage", 0) or 0),
            "critical_rate": stats_all.get("criticalRate", 0),
            "flanking_rate": stats_all.get("flankingRate", 0),
            "glance_rate": stats_all.get("glanceRate", 0),
            "missed": stats_all.get("missed", 0),
            "interrupts": stats_all.get("interrupts", 0),
            "swap_count": stats_all.get("swapCount", 0),
            "blocked_count": defenses.get("blockedCount", 0),
            "evaded_count": defenses.get("evadedCount", 0),
            "dodge_count": defenses.get("dodgeCount", 0),
            "down_count": defenses.get("downCount", 0),
            "dead_count": defenses.get("deadCount", 0),
            "boon_strips": support.get("boonStrips", 0),
            "condition_cleanses": support.get("condiCleanse", 0),
            "resurrects": support.get("resurrects", 0),
            "condi_cleanse_ally": max(
                0, support.get("condiCleanse", 0) - support.get("condiCleanseSelf", 0)
            ),
            "boon_strips_ally": support.get("boonStrips", 0),
            "might_uptime": buff_uptimes.get("might", 0),
            "fury_uptime": buff_uptimes.get("fury", 0),
            "quickness_uptime": buff_uptimes.get("quickness", 0),
            "alacrity_uptime": buff_uptimes.get("alacrity", 0),
            "protection_uptime": buff_uptimes.get("protection", 0),
            "stability_uptime": buff_uptimes.get("stability", 0),
            "healing": extract_player_healing(ei_p),
            "killed": stats_all.get("killed", 0),
            "downed": stats_all.get("downed", 0),
            "damage_taken": defenses.get("damageTaken", 0),
            "down_contribution": dps_all.get("downContribution", 0),
            "against_downed_damage": dps_all.get("againstDownedDamage", 0),
            "applied_cc_duration": support.get("appliedCcDuration", 0),
            "barrier_damage_absorbed": defenses.get("damageBarrier", 0),
            "condition_damage_taken": defenses.get("conditionDamageTaken", 0),
            "power_damage_taken": defenses.get("powerDamageTaken", 0),
            "received_cc_duration": support.get("receivedCcDuration", 0),
            "might_uptime_active": buff_uptimes_active.get("might", 0),
            "quickness_uptime_active": buff_uptimes_active.get("quickness", 0),
            "alacrity_uptime_active": buff_uptimes_active.get("alacrity", 0),
            "avg_boons": stats_all.get("avgBoons", 0),
            "avg_conditions": stats_all.get("avgConditions", 0),
            "wasted": stats_all.get("wasted", 0),
            "saved": stats_all.get("saved", 0),
            "skill_cast_uptime": stats_all.get("skillCastUptime", 0),
            "stack_dist": stats_all.get("stackDist", 0),
            "dist_to_com": stats_all.get("distToCom", 0),
            "downed_damage_taken": defenses.get("downedDamageTaken", 0),
            "interrupted_count": defenses.get("interruptedCount", 0),
            "down_duration": defenses.get("downDuration", 0),
            "dead_duration": defenses.get("deadDuration", 0),
            "dc_count": defenses.get("dcCount", 0),
            "dc_duration": defenses.get("dcDuration", 0),
            "stun_break": support.get("stunBreak", 0),
            "removed_stun_duration": support.get("removedStunDuration", 0),
            "applied_cc_count": stats_all.get("appliedCrowdControl", 0),
        }
        results.append(player)

    return results


def parse_ei_time(time_str: str) -> datetime:
    """将 EI 时间字符串解析为 datetime

    支持格式:
        - ISO 8601: 22026-04-14T11:29:53.1234567-04:00
        - EI 自定义 22026-04-14 11:29:53 +00:00
        - 纯日期 22026-04-14
    """
    if not time_str:
        return None
    ts = str(time_str).strip()
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        pass
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(
            ts.replace(" +", "+").replace(" -", "-")
        )
    except ValueError:
        pass
    try:
        return datetime.strptime(ts, "%Y-%m-%d")
    except ValueError:
        pass
    logger.warning(f"[import] 无法解析时间字符? {time_str}")
    return None


def build_fight_stats_mappings(
    fight_id: int, member_map: Dict[str, Any], account_to_player: Dict[str, Dict]
) -> List[Dict[str, Any]]:
    """根据 member_map 和 player_map 数据构建 fight_stats 批量插入映射"""
    mappings = []
    for account, member in member_map.items():
        if account not in account_to_player:
            continue
        p = account_to_player[account]
        mappings.append({
            "fight_id": fight_id,
            "member_id": member.id,
            "account": account,
            "character_name": p.get("character_name", "").strip()[:100],
            "profession": p.get("profession", "").strip()[:50],
            "group_id": p.get("group_id", 1),
            "team_id": p.get("team_id", 0),
            "has_commander_tag": 1 if p.get("has_commander_tag") else 0,
            "damage": p.get("damage", 0),
            "dps": p.get("dps", 0),
            "power_damage": p.get("power_damage", 0),
            "condi_damage": p.get("condi_damage", 0),
            "breakbar_damage": p.get("breakbar_damage", 0),
            "critical_rate": p.get("critical_rate", 0),
            "flanking_rate": p.get("flanking_rate", 0),
            "glance_rate": p.get("glance_rate", 0),
            "missed": p.get("missed", 0),
            "interrupts": p.get("interrupts", 0),
            "swap_count": p.get("swap_count", 0),
            "blocked_count": p.get("blocked_count", 0),
            "evaded_count": p.get("evaded_count", 0),
            "dodge_count": p.get("dodge_count", 0),
            "down_count": p.get("down_count", 0),
            "dead_count": p.get("dead_count", 0),
            "boon_strips": p.get("boon_strips", 0),
            "condition_cleanses": p.get("condition_cleanses", 0),
            "resurrects": p.get("resurrects", 0),
            "condi_cleanse_ally": p.get("condi_cleanse_ally", 0),
            "boon_strips_ally": p.get("boon_strips_ally", 0),
            "might_uptime": p.get("might_uptime", 0),
            "fury_uptime": p.get("fury_uptime", 0),
            "quickness_uptime": p.get("quickness_uptime", 0),
            "alacrity_uptime": p.get("alacrity_uptime", 0),
            "protection_uptime": p.get("protection_uptime", 0),
            "stability_uptime": p.get("stability_uptime", 0),
            "healing": p.get("healing", 0),
            "killed": p.get("killed", 0),
            "downed": p.get("downed", 0),
            "damage_taken": p.get("damage_taken", 0),
            "down_contribution": p.get("down_contribution", 0),
            "against_downed_damage": p.get("against_downed_damage", 0),
            "applied_cc_duration": p.get("applied_cc_duration", 0),
            "barrier_damage_absorbed": p.get("barrier_damage_absorbed", 0),
            "condition_damage_taken": p.get("condition_damage_taken", 0),
            "power_damage_taken": p.get("power_damage_taken", 0),
            "received_cc_duration": p.get("received_cc_duration", 0),
            "might_uptime_active": p.get("might_uptime_active", 0),
            "quickness_uptime_active": p.get("quickness_uptime_active", 0),
            "alacrity_uptime_active": p.get("alacrity_uptime_active", 0),
            "avg_boons": p.get("avg_boons", 0),
            "avg_conditions": p.get("avg_conditions", 0),
            "wasted": p.get("wasted", 0),
            "saved": p.get("saved", 0),
            "skill_cast_uptime": p.get("skill_cast_uptime", 0),
            "stack_dist": p.get("stack_dist", 0),
            "dist_to_com": p.get("dist_to_com", 0),
            "downed_damage_taken": p.get("downed_damage_taken", 0),
            "interrupted_count": p.get("interrupted_count", 0),
            "down_duration": p.get("down_duration", 0),
            "dead_duration": p.get("dead_duration", 0),
            "dc_count": p.get("dc_count", 0),
            "dc_duration": p.get("dc_duration", 0),
            "stun_break": p.get("stun_break", 0),
            "removed_stun_duration": p.get("removed_stun_duration", 0),
            "applied_cc_count": p.get("applied_cc_count", 0),
            "ai_score": 0,
            "score_grade": "",
            "score_breakdown": None,
            "role_type": None,
            "rule_version": 0,
            "scoring_profession_rule": None,
        })
    return mappings
