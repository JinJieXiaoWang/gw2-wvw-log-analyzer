# -*- coding: utf-8 -*-
"""
WvW 战斗分析报告 API 路由

提供从 ZEVTC 原始数据同步生成的 EI 格式分析结果。
聚焦 WvW 场景核心需求：
  - 战斗概览与 squad composition
  - 玩家表现排行榜
  - 战斗时间线
  - 阶段分析

设计理念：
  - 不复制 EI 的完整复杂度
  - 提供清晰、前端友好的 JSON 结构
  - 支持 WvW 特有的分析维度（指挥官标记、小队分组等）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.wvw_report import (
    WvwPhasesResponse,
    WvwPlayerDetailResponse,
    WvwPlayersResponse,
    WvwReportListResponse,
    WvwSkillMapResponse,
    WvwSummaryResponse,
    WvwTargetsResponse,
    WvwTimelineResponse,
)
from app.services.wvw.report_service import WvwReportService

router = APIRouter(prefix="/wvw-report", tags=["WvW 战斗报告"])


# =====================================================================
# 1. 报告列表
# =====================================================================
@router.get(
    "/logs", response_model=WvwReportListResponse, summary="获取有同步数据的日志列表"
)
async def list_wvw_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取已有 ZEVTC→EI 同步数据的日志列表"""
    result = WvwReportService.list_available_logs(db, page, page_size)
    return WvwReportListResponse(
        success=True,
        message="获取成功",
        data=result,
    )


# =====================================================================
# 2. 战斗概览
# =====================================================================
@router.get(
    "/logs/{log_id}/summary", response_model=WvwSummaryResponse, summary="获取战斗概览"
)
async def get_wvw_summary(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回战斗概览，包含：
      - 基础信息（时长、人数、目标数）
      - 伤害统计（总伤害、直伤、症状、平均DPS）
      - 防御统计（倒地、死亡、承伤）
      - 支援统计（症状清除、治疗）
      - 小队构成（职业分布、小队分配）
      - 阶段列表
    """
    summary = WvwReportService.get_summary(db, log_id)
    if not summary:
        return WvwSummaryResponse(
            success=False, message="未找到该日志的同步数据", code=404, data=None
        )
    return WvwSummaryResponse(success=True, message="获取成功", data=summary)


# =====================================================================
# 3. 玩家排行榜
# =====================================================================
@router.get(
    "/logs/{log_id}/players",
    response_model=WvwPlayersResponse,
    summary="获取玩家排行榜",
)
async def get_wvw_players(
    log_id: int = Path(..., description="日志ID"),
    sort_by: str = Query(
        "damage", description="排序字段: damage/dps/taken/downs/support/healing"
    ),
    db: Session = Depends(get_db),
):
    """
    返回所有玩家的摘要数据，支持多种排序方式：
      - damage: 按总伤害排序
      - dps: 按 DPS 排序
      - taken: 按承受伤害排序
      - downs: 按倒地次数排序
      - support: 按症状清除排序
      - healing: 按治疗量排序
    """
    players = WvwReportService.get_players(db, log_id, sort_by)
    return WvwPlayersResponse(
        success=True,
        message="获取成功",
        data={"count": len(players), "players": players},
    )


# =====================================================================
# 4. 单个玩家详情
# =====================================================================
@router.get(
    "/logs/{log_id}/players/{player_id}",
    response_model=WvwPlayerDetailResponse,
    summary="获取单个玩家详情",
)
async def get_wvw_player_detail(
    log_id: int = Path(..., description="日志ID"),
    player_id: int = Path(..., description="玩家ID（ei_player.player_id）"),
    db: Session = Depends(get_db),
):
    """返回单个玩家的完整数据（含 DPS、防御、支援、技能循环等）"""
    player = WvwReportService.get_player_detail(db, log_id, player_id)
    if not player:
        return WvwPlayerDetailResponse(
            success=False, message="未找到该玩家", code=404, data=None
        )
    return WvwPlayerDetailResponse(success=True, message="获取成功", data=player)


# =====================================================================
# 5. 目标列表
# =====================================================================
@router.get(
    "/logs/{log_id}/targets", response_model=WvwTargetsResponse, summary="获取目标列表"
)
async def get_wvw_targets(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """返回所有目标（NPC/敌方玩家）的摘要数据"""
    targets = WvwReportService.get_targets(db, log_id)
    return WvwTargetsResponse(
        success=True,
        message="获取成功",
        data={"count": len(targets), "targets": targets},
    )


# =====================================================================
# 6. 阶段列表
# =====================================================================
@router.get(
    "/logs/{log_id}/phases", response_model=WvwPhasesResponse, summary="获取阶段列表"
)
async def get_wvw_phases(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """返回所有阶段的统计数据"""
    phases = WvwReportService.get_phases(db, log_id)
    return WvwPhasesResponse(
        success=True,
        message="获取成功",
        data={"count": len(phases), "phases": phases},
    )


# =====================================================================
# 7. 战斗时间线
# =====================================================================
@router.get(
    "/logs/{log_id}/timeline",
    response_model=WvwTimelineResponse,
    summary="获取战斗时间线",
)
async def get_wvw_timeline(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """
    返回战斗关键事件时间线：
      - 进入/退出战斗
      - 倒地/起身
      - Despawn 事件
    """
    timeline = WvwReportService.get_timeline(db, log_id)
    return WvwTimelineResponse(
        success=True,
        message="获取成功",
        data={"count": len(timeline), "events": timeline},
    )


# =====================================================================
# 8. 技能映射
# =====================================================================
@router.get(
    "/logs/{log_id}/skill-map",
    response_model=WvwSkillMapResponse,
    summary="获取技能映射表",
)
async def get_wvw_skill_map(
    log_id: int = Path(..., description="日志ID"), db: Session = Depends(get_db)
):
    """返回技能 ID 到名称的映射表"""
    skill_map = WvwReportService.get_skill_map(db, log_id)
    return WvwSkillMapResponse(
        success=True,
        message="获取成功",
        data={"count": len(skill_map), "skills": skill_map},
    )
