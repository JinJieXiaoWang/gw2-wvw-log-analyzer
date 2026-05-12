# -*- coding: utf-8 -*-
"""
EI 报告数据服务

功能：
  1. 从 EI HTML/JSON 文件导入完整报告数据
  2. 提取摘要数据存入数据库
  3. 将大体积 JSON 压缩后存入文件系统
  4. 提供按组件读取的查询接口
"""

import gzip
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.log.ei_report import EiReport
from app.models.log.log import Log
from app.utils.logger import logger

EI_REPORT_DIR = Path("uploads/ei_reports")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save_gzip_json(data: Any, path: Path) -> None:
    """将数据以 gzip 压缩 JSON 格式保存到文件"""
    _ensure_dir(path.parent)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def _load_gzip_json(path: Path) -> Any:
    """从 gzip 压缩 JSON 文件读取数据"""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def extract_ei_data_from_html(html_path: str) -> Dict[str, Any]:
    """
    从 EI HTML 文件中提取 _logData 和 _graphData

    Args:
        html_path: EI HTML 文件路径

    Returns:
        dict: {"logData": ..., "graphData": ..., "crData": ...}
    """
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {}

    # 提取 _logData
    log_match = re.search(
        r"const _logData = (.+?);\s*const _crData", content, re.DOTALL
    )
    if log_match:
        result["logData"] = json.loads(log_match.group(1))
    else:
        raise ValueError(f"无法从 {html_path} 中提取 _logData")

    # 提取 _graphData
    graph_match = re.search(
        r"const _graphData = (.+?);\s*const _healingStatsExtension", content, re.DOTALL
    )
    if graph_match:
        result["graphData"] = json.loads(graph_match.group(1))
    else:
        result["graphData"] = None

    # 提取 _crData
    cr_match = re.search(
        r"const _crData = (.+?);\s*const _graphData", content, re.DOTALL
    )
    if cr_match:
        cr_data = cr_match.group(1).strip()
        if cr_data != "null":
            result["crData"] = json.loads(cr_data)
        else:
            result["crData"] = None
    else:
        result["crData"] = None

    return result


def build_summary_json(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从完整 _logData 中构建摘要 JSON

    摘要包含：
      - 元数据（logName, duration, players 基础信息等）
      - 定义表（skillMap, buffMap, damageModMap, damageIncModMap, mechanicMap）
      - players / targets / enemies / phases 的基础信息（不含 details）
      - boons / conditions / debuffs / buffs 等列表定义
    """
    summary = {}

    # 1. 元数据
    meta_keys = [
        "evtcRecordingDuration",
        "logName",
        "wvw",
        "hasCommander",
        "targetless",
        "lightTheme",
        "noMechanics",
        "singleGroup",
        "hasBreakbarDamage",
        "logErrors",
        "logStart",
        "logEnd",
        "instanceStart",
        "instanceIP",
        "instancePrivacy",
        "arcVersion",
        "evtcBuild",
        "gw2Build",
        "triggerID",
        "logID",
        "mapID",
        "parser",
        "recordedBy",
        "recordedAccountBy",
        "fractalScale",
        "region",
        "uploadLinks",
        "usedExtensions",
        "playersRunningExtensions",
    ]
    for k in meta_keys:
        if k in log_data:
            summary[k] = log_data[k]

    # 2. 定义表
    for key in [
        "skillMap",
        "buffMap",
        "damageModMap",
        "damageIncModMap",
        "mechanicMap",
    ]:
        if key in log_data:
            summary[key] = log_data[key]

    # 3. BUFF/症状/食物等定义列表
    for key in [
        "boons",
        "offBuffs",
        "supBuffs",
        "defBuffs",
        "debuffs",
        "gearBuffs",
        "nourishments",
        "enhancements",
        "otherConsumables",
        "instanceBuffs",
        "conditions",
    ]:
        if key in log_data:
            summary[key] = log_data[key]

    # 4. Players 基础信息（不含 details）
    if "players" in log_data:
        summary["players"] = []
        for p in log_data["players"]:
            player_summary = {k: v for k, v in p.items() if k != "details"}
            summary["players"].append(player_summary)

    # 5. Targets 基础信息（不含 details）
    if "targets" in log_data:
        summary["targets"] = []
        for t in log_data["targets"]:
            target_summary = {k: v for k, v in t.items() if k != "details"}
            summary["targets"].append(target_summary)

    # 6. Enemies 基础信息
    if "enemies" in log_data:
        summary["enemies"] = log_data["enemies"]

    # 7. Phases 基础信息（不含大型统计数组）
    if "phases" in log_data:
        summary["phases"] = []
        for ph in log_data["phases"]:
            phase_summary = {
                "name": ph.get("name"),
                "duration": ph.get("duration"),
                "start": ph.get("start"),
                "end": ph.get("end"),
                "type": ph.get("type"),
                "nameNoMode": ph.get("nameNoMode"),
                "icon": ph.get("icon"),
                "mode": ph.get("mode"),
                "encounterDuration": ph.get("encounterDuration"),
                "startStatus": ph.get("startStatus"),
                "success": ph.get("success"),
                "encounterPhase": ph.get("encounterPhase"),
                "targets": ph.get("targets"),
                "targetPriorities": ph.get("targetPriorities"),
                "breakbarPhase": ph.get("breakbarPhase"),
                "breakbarRecovered": ph.get("breakbarRecovered"),
                "breakbarStart": ph.get("breakbarStart"),
                "subPhases": ph.get("subPhases"),
                "markupLines": ph.get("markupLines"),
                "markupAreas": ph.get("markupAreas"),
            }
            summary["phases"].append(phase_summary)

    # 8. 伤害修饰符定义
    for key in [
        "dmgModifiersItem",
        "dmgIncModifiersItem",
        "dmgModifiersCommon",
        "dmgIncModifiersCommon",
        "dmgModifiersPers",
        "dmgIncModifiersPers",
        "persBuffs",
    ]:
        if key in log_data:
            summary[key] = log_data[key]

    return summary


def import_ei_report_from_html(
    db: Session, log_id: int, html_path: str, report_type: str = "detailed_wvw"
) -> EiReport:
    """
    从 EI HTML 文件导入完整报告数据

    Args:
        db: 数据库会话
        log_id: 关联的日志 ID
        html_path: EI HTML 文件路径
        report_type: 报告类型

    Returns:
        EiReport 实例
    """
    logger.info(f"开始导入 EI 报告 log_id={log_id}, html={html_path}")

    # 1. 提取数据
    ei_data = extract_ei_data_from_html(html_path)
    log_data = ei_data["logData"]
    graph_data = ei_data.get("graphData")
    cr_data = ei_data.get("crData")

    # 2. 构建摘要
    summary = build_summary_json(log_data)

    # 3. 准备文件路径
    report_dir = EI_REPORT_DIR / str(log_id)
    log_data_path = report_dir / "log_data.json.gz"
    graph_data_path = report_dir / "graph_data.json.gz"
    cr_data_path = report_dir / "cr_data.json.gz"

    # 4. 保存压缩文件
    _save_gzip_json(log_data, log_data_path)
    if graph_data:
        _save_gzip_json(graph_data, graph_data_path)
    if cr_data:
        _save_gzip_json(cr_data, cr_data_path)

    # 5. 计算元数据
    duration_ms = 0
    if "phases" in log_data and log_data["phases"]:
        duration_ms = log_data["phases"][0].get("duration", 0)
    elif "evtcRecordingDuration" in log_data:
        # 尝试从字符串解析，如 "06m 07s 295ms"
        dur_str = log_data["evtcRecordingDuration"]
        parts = dur_str.split()
        for part in parts:
            if part.endswith("m"):
                duration_ms += int(part[:-1]) * 60 * 1000
            elif part.endswith("s"):
                duration_ms += int(part[:-1]) * 1000
            elif part.endswith("ms"):
                duration_ms += int(part[:-2])

    player_count = len(log_data.get("players", []))
    target_count = len(log_data.get("targets", []))
    success = "True"
    if "phases" in log_data and log_data["phases"]:
        success = str(log_data["phases"][0].get("success", True))

    # 6. 查询或创建记录
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report:
        report = EiReport(log_id=log_id)
        db.add(report)

    report.report_type = report_type
    report.ei_version = log_data.get("parser", "").replace("Elite Insights ", "")
    report.summary_json = summary
    report.log_data_path = str(log_data_path)
    report.graph_data_path = str(graph_data_path) if graph_data else None
    report.cr_data_path = str(cr_data_path) if cr_data else None
    report.log_name = log_data.get("logName", "")
    report.duration_ms = duration_ms
    report.player_count = player_count
    report.target_count = target_count
    report.success = success
    report.recorded_by = log_data.get("recordedBy", "")
    report.recorded_account_by = log_data.get("recordedAccountBy", "")
    report.map_id = log_data.get("mapID")
    report.region = log_data.get("region", "")
    report.wvw = str(log_data.get("wvw", False))

    db.commit()
    db.refresh(report)

    logger.info(
        f"EI 报告导入完成 log_id={log_id}, "
        f"players={player_count}, targets={target_count}, "
        f"log_data={log_data_path.stat().st_size / 1024 / 1024:.2f}MB"
    )
    return report


def get_ei_report_summary(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """获取 EI 报告摘要数据"""
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report:
        return None
    return report.summary_json


def get_ei_report_meta(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """获取 EI 报告元数据（不含 summary_json 本身）"""
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report:
        return None
    return {
        "log_id": report.log_id,
        "report_type": report.report_type,
        "ei_version": report.ei_version,
        "log_name": report.log_name,
        "duration_ms": report.duration_ms,
        "player_count": report.player_count,
        "target_count": report.target_count,
        "success": report.success,
        "recorded_by": report.recorded_by,
        "recorded_account_by": report.recorded_account_by,
        "map_id": report.map_id,
        "region": report.region,
        "wvw": report.wvw,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "updated_at": report.updated_at.isoformat() if report.updated_at else None,
        "has_log_data": bool(
            report.log_data_path and Path(report.log_data_path).exists()
        ),
        "has_graph_data": bool(
            report.graph_data_path and Path(report.graph_data_path).exists()
        ),
        "has_cr_data": bool(report.cr_data_path and Path(report.cr_data_path).exists()),
    }


def get_full_log_data(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """获取完整的 _logData（从压缩文件读取）"""
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report or not report.log_data_path:
        return None
    path = Path(report.log_data_path)
    if not path.exists():
        return None
    return _load_gzip_json(path)


def get_full_graph_data(db: Session, log_id: int) -> Optional[Dict[str, Any]]:
    """获取完整的 _graphData（从压缩文件读取）"""
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report or not report.graph_data_path:
        return None
    path = Path(report.graph_data_path)
    if not path.exists():
        return None
    return _load_gzip_json(path)


def get_player_detail(
    db: Session, log_id: int, player_index: int
) -> Optional[Dict[str, Any]]:
    """
    获取单个玩家的完整数据（含 details）

    从完整的 _logData 中提取指定玩家的数据
    """
    log_data = get_full_log_data(db, log_id)
    if not log_data or "players" not in log_data:
        return None
    players = log_data["players"]
    if player_index < 0 or player_index >= len(players):
        return None
    return players[player_index]


def get_target_detail(
    db: Session, log_id: int, target_index: int
) -> Optional[Dict[str, Any]]:
    """获取单个目标的完整数据（含 details）"""
    log_data = get_full_log_data(db, log_id)
    if not log_data or "targets" not in log_data:
        return None
    targets = log_data["targets"]
    if target_index < 0 or target_index >= len(targets):
        return None
    return targets[target_index]


def get_phase_detail(
    db: Session, log_id: int, phase_index: int
) -> Optional[Dict[str, Any]]:
    """获取单个阶段的完整数据（含所有统计数组）"""
    log_data = get_full_log_data(db, log_id)
    if not log_data or "phases" not in log_data:
        return None
    phases = log_data["phases"]
    if phase_index < 0 or phase_index >= len(phases):
        return None
    return phases[phase_index]


def get_graph_for_player(
    db: Session, log_id: int, player_index: int
) -> Optional[Dict[str, Any]]:
    """获取指定玩家的图表数据"""
    graph_data = get_full_graph_data(db, log_id)
    if not graph_data or "phases" not in graph_data:
        return None
    # graphData.phases[].players[] 按 player_index 索引
    result = {}
    for phase_idx, phase in enumerate(graph_data["phases"]):
        if "players" in phase and player_index < len(phase["players"]):
            result[f"phase_{phase_idx}"] = phase["players"][player_index]
    return result


def get_graph_for_target(
    db: Session, log_id: int, target_index: int
) -> Optional[Dict[str, Any]]:
    """获取指定目标的图表数据"""
    graph_data = get_full_graph_data(db, log_id)
    if not graph_data or "phases" not in graph_data:
        return None
    result = {}
    for phase_idx, phase in enumerate(graph_data["phases"]):
        if "targets" in phase and target_index < len(phase["targets"]):
            result[f"phase_{phase_idx}"] = phase["targets"][target_index]
    return result


def delete_ei_report(db: Session, log_id: int) -> bool:
    """删除 EI 报告数据（数据库记录 + 文件）"""
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if not report:
        return False

    # 删除文件
    for attr in ["log_data_path", "graph_data_path", "cr_data_path"]:
        path_str = getattr(report, attr)
        if path_str:
            path = Path(path_str)
            if path.exists():
                path.unlink()

    # 删除空目录
    report_dir = EI_REPORT_DIR / str(log_id)
    if report_dir.exists() and not any(report_dir.iterdir()):
        report_dir.rmdir()

    db.delete(report)
    db.commit()
    return True
