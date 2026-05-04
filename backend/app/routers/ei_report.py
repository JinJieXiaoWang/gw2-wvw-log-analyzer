# -*- coding: utf-8 -*-
"""
EI 完整报告 API 路由

功能：
  提供 Elite Insights 完整报告数据的分层查询接口。
  由于 _logData 体积巨大（可达 100MB+），采用按需加载策略：
    - /summary        → 返回摘要（元数据 + 导航结构 + 定义表，~1-5MB）
    - /data           → 流式返回完整 _logData（gzip 压缩传输）
    - /graph          → 流式返回 _graphData（gzip 压缩传输）
    - /players/{idx}  → 返回单个玩家完整数据
    - /targets/{idx}  → 返回单个目标完整数据
    - /phases/{idx}   → 返回单个阶段完整数据
"""

import gzip
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.sys_user import SysUser
from app.schemas.ei_report import (
    EiFullDataResponse,
    EiGraphDataResponse,
    EiImportRequest,
    EiImportResponse,
    EiPhaseDetailResponse,
    EiPlayerDetailResponse,
    EiPlayerGraphResponse,
    EiReportListItem,
    EiReportListResponse,
    EiReportMeta,
    EiSummaryResponse,
    EiTargetDetailResponse,
    EiTargetGraphResponse,
)
from app.services.ei.report_service import (
    EiReport,
    delete_ei_report,
    get_ei_report_meta,
    get_ei_report_summary,
    get_full_graph_data,
    get_full_log_data,
    get_graph_for_player,
    get_graph_for_target,
    get_phase_detail,
    get_player_detail,
    get_target_detail,
    import_ei_report_from_html,
)
from app.services.auth_service import get_current_admin
from app.services.ei.unified_service import get_unified_ei_data
from app.utils.logger import logger

router = APIRouter(prefix="/ei-report", tags=["EI 完整报告"])


# =====================================================================
# 1. 报告列表与元数据
# =====================================================================
@router.get(
    "/logs", response_model=EiReportListResponse, summary="获取已导入的 EI 报告列表"
)
async def list_ei_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取已导入的 EI 报告列表（分页）"""
    from sqlalchemy import func

    total = db.query(func.count(EiReport.report_id)).scalar()

    # 避免加载巨大的 summary_json 列导致 sort buffer 溢出
    # 使用 with_entities 只选择列表需要的标量列
    rows = (
        db.query(
            EiReport.log_id,
            EiReport.log_name,
            EiReport.report_type,
            EiReport.ei_version,
            EiReport.duration_ms,
            EiReport.player_count,
            EiReport.target_count,
            EiReport.recorded_by,
            EiReport.created_at,
        )
        .order_by(EiReport.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for r in rows:
        items.append(
            EiReportListItem(
                log_id=r.log_id,
                log_name=r.log_name,
                report_type=r.report_type,
                ei_version=r.ei_version,
                duration_ms=r.duration_ms,
                player_count=r.player_count,
                target_count=r.target_count,
                recorded_by=r.recorded_by,
                created_at=r.created_at.isoformat() if r.created_at else None,
            )
        )

    return EiReportListResponse(
        success=True,
        message="获取成功",
        total=total,
        items=items,
    )


@router.get(
    "/logs/{log_id}/meta",
    response_model=EiSummaryResponse,
    summary="获取 EI 报告元数据",
)
async def get_report_meta(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回 EI 报告的元数据（不含 summary_json 本身）。
    用于前端判断报告是否存在、有哪些数据可用。
    """
    meta = get_ei_report_meta(db, log_id)
    if not meta:
        return EiSummaryResponse(
            success=False, message="未找到该日志的 EI 报告", code=404, data=None
        )
    return EiSummaryResponse(success=True, message="获取成功", data=meta)


# =====================================================================
# 2. 摘要数据（快速加载，1-5MB）
# =====================================================================
@router.get(
    "/logs/{log_id}/summary",
    response_model=EiSummaryResponse,
    summary="获取 EI 报告摘要",
)
async def get_report_summary(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回 EI 报告摘要数据，包含：
      - 元数据（logName, duration, players 基础信息, 等）
      - 定义表（skillMap, buffMap, damageModMap, mechanicMap）
      - players / targets / phases 基础信息（不含 details）
      - boons / conditions / debuffs 等定义列表

    体积约 1-5MB，可直接从数据库 JSON 列读取。
    """
    summary = get_ei_report_summary(db, log_id)
    if not summary:
        return EiSummaryResponse(
            success=False, message="未找到该日志的 EI 报告", code=404, data=None
        )
    return EiSummaryResponse(success=True, message="获取成功", data=summary)


# =====================================================================
# 3. 完整数据（流式传输，支持 gzip）
# =====================================================================
def _gzip_json_stream(data: dict):
    """生成 gzip 压缩的 JSON 字节流"""
    import io

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    buf.seek(0)
    yield buf.read()


@router.get("/logs/{log_id}/data", summary="获取完整 _logData（流式 gzip）")
async def get_report_data(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回完整的 _logData JSON（gzip 压缩流式传输）。
    体积可能达 30-100MB，建议前端在需要完整数据时调用，并配合流式解压。
    """
    log_data = get_full_log_data(db, log_id)
    if not log_data:
        raise HTTPException(status_code=404, detail="未找到该日志的 EI 报告数据")

    return StreamingResponse(
        _gzip_json_stream(log_data),
        media_type="application/gzip",
        headers={
            "Content-Disposition": f'attachment; filename="ei_logdata_{log_id}.json.gz"',
            "Content-Encoding": "gzip",
        },
    )


@router.get("/logs/{log_id}/graph", summary="获取完整 _graphData（流式 gzip）")
async def get_report_graph(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回完整的 _graphData JSON（gzip 压缩流式传输）。
    包含每秒伤害、血量状态、BUFF 状态等时间序列数据，用于绘制图表。
    """
    graph_data = get_full_graph_data(db, log_id)
    if not graph_data:
        raise HTTPException(status_code=404, detail="未找到该日志的图表数据")

    return StreamingResponse(
        _gzip_json_stream(graph_data),
        media_type="application/gzip",
        headers={
            "Content-Disposition": f'attachment; filename="ei_graphdata_{log_id}.json.gz"',
            "Content-Encoding": "gzip",
        },
    )


# =====================================================================
# 4. 按需加载：Player / Target / Phase 详情
# =====================================================================
@router.get(
    "/logs/{log_id}/players/{player_index}",
    response_model=EiPlayerDetailResponse,
    summary="获取单个玩家完整数据",
)
async def get_player_full_data(
    log_id: int = Path(..., description="日志ID"),
    player_index: int = Path(..., ge=0, description="玩家在列表中的索引"),
    db: Session = Depends(get_db),
):
    """
    返回单个玩家的完整数据（含 details）：
      - 基础信息（name, profession, group, 等）
      - dmgDistributions / dmgDistributionsTargets / dmgDistributionsTaken
      - rotation（技能循环）
      - boonGraph（BUFF 时间线）
      - deathRecap, minions, food 等
    """
    player = get_player_detail(db, log_id, player_index)
    if not player:
        return EiPlayerDetailResponse(
            success=False,
            message="未找到该玩家",
            code=404,
            player_index=player_index,
            data=None,
        )
    return EiPlayerDetailResponse(
        success=True, message="获取成功", player_index=player_index, data=player
    )


@router.get(
    "/logs/{log_id}/targets/{target_index}",
    response_model=EiTargetDetailResponse,
    summary="获取单个目标完整数据",
)
async def get_target_full_data(
    log_id: int = Path(..., description="日志ID"),
    target_index: int = Path(..., ge=0, description="目标在列表中的索引"),
    db: Session = Depends(get_db),
):
    """返回单个目标的完整数据（含 details）"""
    target = get_target_detail(db, log_id, target_index)
    if not target:
        return EiTargetDetailResponse(
            success=False,
            message="未找到该目标",
            code=404,
            target_index=target_index,
            data=None,
        )
    return EiTargetDetailResponse(
        success=True, message="获取成功", target_index=target_index, data=target
    )


@router.get(
    "/logs/{log_id}/phases/{phase_index}",
    response_model=EiPhaseDetailResponse,
    summary="获取单个阶段完整统计",
)
async def get_phase_full_data(
    log_id: int = Path(..., description="日志ID"),
    phase_index: int = Path(..., ge=0, description="阶段索引"),
    db: Session = Depends(get_db),
):
    """
    返回单个阶段的完整统计数据：
      - dpsStats, dpsStatsTargets, offensiveStats, gameplayStats
      - defStats, supportStats
      - buffsStatContainer（所有 BUFF 统计）
      - dmgModifiers, mechanicStats
    """
    phase = get_phase_detail(db, log_id, phase_index)
    if not phase:
        return EiPhaseDetailResponse(
            success=False,
            message="未找到该阶段",
            code=404,
            phase_index=phase_index,
            data=None,
        )
    return EiPhaseDetailResponse(
        success=True, message="获取成功", phase_index=phase_index, data=phase
    )


# =====================================================================
# 5. 图表数据（按 player / target）
# =====================================================================
@router.get(
    "/logs/{log_id}/players/{player_index}/graph",
    response_model=EiPlayerGraphResponse,
    summary="获取玩家图表数据",
)
async def get_player_graph_data(
    log_id: int = Path(..., description="日志ID"),
    player_index: int = Path(..., ge=0, description="玩家索引"),
    db: Session = Depends(get_db),
):
    """
    返回指定玩家的图表数据（来自 _graphData）：
      - damage / powerDamage / conditionDamage / breakbarDamage 时间序列
      - healthStates / barrierStates
    """
    data = get_graph_for_player(db, log_id, player_index)
    if not data:
        return EiPlayerGraphResponse(
            success=False,
            message="未找到该玩家的图表数据",
            code=404,
            player_index=player_index,
            data=None,
        )
    return EiPlayerGraphResponse(
        success=True, message="获取成功", player_index=player_index, data=data
    )


@router.get(
    "/logs/{log_id}/targets/{target_index}/graph",
    response_model=EiTargetGraphResponse,
    summary="获取目标图表数据",
)
async def get_target_graph_data(
    log_id: int = Path(..., description="日志ID"),
    target_index: int = Path(..., ge=0, description="目标索引"),
    db: Session = Depends(get_db),
):
    """返回指定目标的图表数据（来自 _graphData）"""
    data = get_graph_for_target(db, log_id, target_index)
    if not data:
        return EiTargetGraphResponse(
            success=False,
            message="未找到该目标的图表数据",
            code=404,
            target_index=target_index,
            data=None,
        )
    return EiTargetGraphResponse(
        success=True, message="获取成功", target_index=target_index, data=data
    )


# =====================================================================
# 6. 数据导入与管理
# =====================================================================
@router.post(
    "/logs/{log_id}/import",
    response_model=EiImportResponse,
    summary="从 EI HTML 导入报告",
)
async def import_report(
    log_id: int = Path(..., description="日志ID"),
    req: EiImportRequest = ...,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    """
    从 EI HTML 文件导入完整报告数据。

    流程：
      1. 读取 HTML 文件，提取 _logData / _graphData / _crData
      2. 构建摘要 JSON 存入数据库
      3. 将完整数据 gzip 压缩后存入文件系统
      4. 更新 ei_report 表记录
    """
    try:
        report = import_ei_report_from_html(db, log_id, req.html_path, req.report_type)
        meta = get_ei_report_meta(db, log_id)
        return EiImportResponse(
            success=True,
            message="导入成功",
            report_id=report.report_id,
            meta=EiReportMeta(**meta) if meta else None,
        )
    except FileNotFoundError:
        logger.error(f"EI HTML 文件不存在: {req.html_path}")
        return EiImportResponse(
            success=False, message=f"文件不存在: {req.html_path}", code=404
        )
    except Exception as e:
        logger.error(f"导入 EI 报告失败 log_id={log_id}: {e}", exc_info=True)
        return EiImportResponse(success=False, message=f"导入失败: {str(e)}", code=500)


@router.get(
    "/logs/{log_id}/unified",
    response_model=EiSummaryResponse,
    summary="获取统一 EI 数据（自动选择数据源）",
)
async def get_unified_report(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回统一的 EI 格式数据，自动选择最佳数据源：
      1. 优先从 ei_report 表返回完整的 EI _logData（如果已通过 HTML 导入）
      2. 如果没有 HTML 数据，从 ei_player/ei_target/ei_phase 等 ZEVTC 同步表组装 EI 格式数据

    返回结构兼容 EiDetailView 的期望格式。
    """
    data = get_unified_ei_data(db, log_id)
    if not data:
        return EiSummaryResponse(
            success=False,
            message="未找到该日志的 EI 报告或同步数据",
            code=404,
            data=None,
        )
    return EiSummaryResponse(success=True, message="获取成功", data=data)


@router.delete(
    "/logs/{log_id}", response_model=EiSummaryResponse, summary="删除 EI 报告"
)
async def delete_report(
    log_id: int = Path(..., description="日志ID"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    """删除指定日志的 EI 报告（数据库记录 + 压缩文件）"""
    deleted = delete_ei_report(db, log_id)
    if not deleted:
        return EiSummaryResponse(
            success=False, message="未找到该日志的 EI 报告", code=404
        )
    return EiSummaryResponse(success=True, message="删除成功")
