# -*- coding: utf-8 -*-
# 模块功能：EI 摘要预计算服?# 说明：将前端 computed 中的计算逻辑下沉到后端，
#       返回"即渲?数据，前端零计算直接绑定义
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.log import Log
from app.services.zevtc import fight_service as fight_svc


def build_ei_summary(db: Session, log_id: int, sort_by: str = "damage") -> Dict[str, Any]:
    """构建完整?EI 摘要（含所有预计算衍生字段）?""
    fights = fight_svc.get_fights_by_log_id(db, log_id)
    if not fights:
        return None

    fight = fights[0]
    players = fight_svc.get_log_player_stats(db, log_id, sort_by)
    aggregate = fight_svc.get_fight_aggregate_stats(db, log_id)

    log_record = db.query(Log).filter(Log.id == log_id).first()
    dps_report_permalink = log_record.dps_report_permalink if log_record else None

    prof_dist = _calc_profession_distribution(players)
    groups = _build_groups(players)
    commanders = [p for p in players if p.get("has_commander_tag")]
    ungrouped = [p for p in players if not p.get("group_id")]
    stat_avgs = _calc_stat_averages(players)
    top_dps = sorted(players, key=lambda x: x.get("dps", 0), reverse=True)[:10]
    sorted_players = sorted(players, key=lambda x: x.get(sort_by, 0), reverse=True)
    donut = _build_donut(aggregate)
    percentages = _calc_percentages(aggregate)

    buff_leaders = _calc_buff_leaders(players)
    support_leaders = _calc_support_leaders(players)
    defense_leaders = _calc_defense_leaders(players)

    return {
        "log_id": log_id,
        "fight": _build_fight_info(fight),
        "aggregate": aggregate,
        "players": players,
        "total_players": len(players),
        "enemy_players": fight_svc.get_enemy_players(db, log_id),
        "dps_report_permalink": dps_report_permalink,
        "profession_distribution": prof_dist,
        "groups": groups,
        "commanders": commanders,
        "ungrouped_players": ungrouped,
        "stat_averages": stat_avgs,
        "top_dps_players": top_dps,
        "sorted_players": sorted_players,
        "donut": donut,
        "percentages": percentages,
        "buff_leaders": buff_leaders,
        "support_leaders": support_leaders,
        "defense_leaders": defense_leaders,
    }


def _build_fight_info(fight) -> Dict[str, Any]:
    """构建战斗基本信息字典?""
    return {
        "id": fight.id,
        "map_name": fight.map_name,
        "start_time": fight.start_time.isoformat() if fight.start_time else None,
        "duration_sec": fight.duration_sec,
        "duration_ms": fight.duration_ms,
        "server_name": fight.server_name,
        "recorded_by": fight.recorded_by,
        "recorded_account": fight.recorded_account,
        "total_damage": fight.total_damage,
        "total_healing": fight.total_healing,
        "kill_count": fight.kill_count,
        "death_count": fight.death_count,
        "player_count": fight.player_count,
        "is_wvw": True,
    }


def _calc_profession_distribution(players: List[Dict[str, Any]]) -> Dict[str, int]:
    """计算职业分布?""
    dist: Dict[str, int] = {}
    for p in players:
        prof = p.get("profession", "Unknown")
        dist[prof] = dist.get(prof, 0) + 1
    return dist


def _build_groups(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """构建小队分组（含预计算汇总数据）?""
    group_map: Dict[int, Dict[str, Any]] = {}
    for p in players:
        gid = p.get("group_id")
        if not gid:
            continue
        if gid not in group_map:
            group_map[gid] = {"id": gid, "players": []}
        group_map[gid]["players"].append(p)

    groups = []
    for gid in sorted(group_map.keys()):
        g = group_map[gid]
        players_in_group = g["players"]
        total_damage = sum(p.get("damage", 0) for p in players_in_group)
        avg_dps = round(sum(p.get("dps", 0) for p in players_in_group) / max(len(players_in_group), 1))
        scored = [p for p in players_in_group if p.get("ai_score") is not None]
        avg_score = round(sum(p.get("ai_score", 0) for p in scored) / max(len(scored), 1), 1) if scored else None
        total_dead = sum(p.get("dead_count", 0) for p in players_in_group)
        total_downed = sum(p.get("downed", 0) for p in players_in_group)
        groups.append({
            "id": gid,
            "players": players_in_group,
            "total_damage": total_damage,
            "avg_dps": avg_dps,
            "avg_score": avg_score,
            "total_dead": total_dead,
            "total_downed": total_downed,
        })

    # 计算进度条宽度（基于最大小队伤害）
    max_damage = max((g["total_damage"] for g in groups), default=1)
    for g in groups:
        g["bar_width"] = min((g["total_damage"] / max(max_damage, 1)) * 50, 100)

    return groups


def _calc_stat_averages(players: List[Dict[str, Any]]) -> Dict[str, float]:
    """计算各项统计平均值（一次遍历）?""
    if not players:
        return {"protection": 0, "stability": 0, "hitRate": 100, "skillCastUptime": 0, "stackDist": 0, "distToCom": 0}

    prot_sum = prot_cnt = 0
    stab_sum = stab_cnt = 0
    skill_sum = skill_cnt = 0
    stack_sum = stack_cnt = 0
    dist_sum = dist_cnt = 0
    missed = crit = flank = glance = 0

    for p in players:
        if p.get("protection_uptime", 0) > 0:
            prot_sum += p["protection_uptime"]
            prot_cnt += 1
        if p.get("stability_uptime", 0) > 0:
            stab_sum += p["stability_uptime"]
            stab_cnt += 1
        if p.get("skill_cast_uptime", 0) > 0:
            skill_sum += p["skill_cast_uptime"]
            skill_cnt += 1
        if p.get("stack_dist", 0) > 0:
            stack_sum += p["stack_dist"]
            stack_cnt += 1
        if p.get("dist_to_com", 0) > 0:
            dist_sum += p["dist_to_com"]
            dist_cnt += 1
        missed += p.get("missed", 0)
        crit += p.get("critical_rate", 0)
        flank += p.get("flanking_rate", 0)
        glance += p.get("glance_rate", 0)

    total_hits = missed + crit + flank + glance + 1
    hit_rate = max(0, min(100, 100 - (missed / total_hits) * 100))

    return {
        "protection": round(prot_sum / prot_cnt, 1) if prot_cnt else 0,
        "stability": round(stab_sum / stab_cnt, 1) if stab_cnt else 0,
        "hitRate": round(hit_rate, 1),
        "skillCastUptime": round(skill_sum / skill_cnt, 1) if skill_cnt else 0,
        "stackDist": round(stack_sum / stack_cnt, 1) if stack_cnt else 0,
        "distToCom": round(dist_sum / dist_cnt, 1) if dist_cnt else 0,
    }


def _build_donut(aggregate: Dict[str, Any]) -> Dict[str, Any]:
    """构建环形?SVG 参数据""
    total = aggregate.get("total_damage", 0)
    if not total:
        return {"pd": "0 264", "cd": "0 264", "bd": "0 264", "co": 0, "bo": 0, "total": 0, "p": 0, "c": 0, "b": 0}

    circumference = 264
    pd = aggregate.get("total_power_damage", 0)
    cd = aggregate.get("total_condi_damage", 0)
    bd = aggregate.get("total_breakbar_damage", 0)
    p_arc = (pd / total) * circumference
    c_arc = (cd / total) * circumference
    b_arc = (bd / total) * circumference

    return {
        "pd": f"{p_arc} {circumference}",
        "cd": f"{c_arc} {circumference}",
        "bd": f"{b_arc} {circumference}",
        "co": -p_arc,
        "bo": -(p_arc + c_arc),
        "total": total,
        "p": round((pd / total) * 100),
        "c": round((cd / total) * 100),
        "b": round((bd / total) * 100),
    }


def _calc_percentages(aggregate: Dict[str, Any]) -> Dict[str, int]:
    """计算伤害占比百分比?""
    total = aggregate.get("total_damage", 0)
    if not total:
        return {"power": 0, "condi": 0, "breakbar": 0}
    return {
        "power": round((aggregate.get("total_power_damage", 0) / total) * 100),
        "condi": round((aggregate.get("total_condi_damage", 0) / total) * 100),
        "breakbar": round((aggregate.get("total_breakbar_damage", 0) / total) * 100),
    }


def _calc_buff_leaders(players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """计算 Buff 排行榜?""
    return {
        "might": sorted(players, key=lambda x: x.get("might_uptime", 0), reverse=True)[:5],
        "quickness": sorted(players, key=lambda x: x.get("quickness_uptime", 0), reverse=True)[:5],
        "alacrity": sorted(players, key=lambda x: x.get("alacrity_uptime", 0), reverse=True)[:5],
        "fury": sorted(players, key=lambda x: x.get("fury_uptime", 0), reverse=True)[:5],
        "stability": sorted(players, key=lambda x: x.get("stability_uptime", 0), reverse=True)[:5],
    }


def _calc_support_leaders(players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """计算支援排行榜?""
    return {
        "boon_strips": sorted(players, key=lambda x: x.get("boon_strips", 0), reverse=True)[:5],
        "condition_cleanses": sorted(players, key=lambda x: x.get("condition_cleanses", 0), reverse=True)[:5],
        "resurrects": sorted(players, key=lambda x: x.get("resurrects", 0), reverse=True)[:5],
    }


def _calc_defense_leaders(players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """计算防御排行榜?""
    return {
        "damage_taken": sorted(players, key=lambda x: x.get("damage_taken", 0), reverse=True)[:5],
        "dodge_count": sorted(players, key=lambda x: x.get("dodge_count", 0), reverse=True)[:5],
    }
