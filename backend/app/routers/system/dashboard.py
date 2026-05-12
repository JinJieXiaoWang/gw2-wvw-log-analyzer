# -*- coding: utf-8 -*-
# 模块功能：数据看板API路由 v2.0
# 作者：系统
# 创建日期?2026-04-27
# 更新日期?2026-05-12
# 说明：基?fights / fight_stats / members / evtc_log 真实数据模型重构

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.services.system import dashboard_service
from app.utils.decorators import handle_api_errors

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


# =====================================================================
# 1. 核心 KPI 概览
# =====================================================================

@router.get("/overview", response_model=ApiResponse, summary="获取核心KPI概览")
@handle_api_errors
async def get_overview(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取数据看板核心KPI概览

    返回指标?
    - total_fights: 总战斗场?
    - total_participations: 总参与人?
    - total_damage: 总伤?
    - total_healing: 总治?
    - active_accounts: 活跃账号?
    - total_characters: 角色总数
    - parsed_logs: 解析日志?
    - avg_ai_score: 平均AI评分
    - change: 环比变化（fights/damage/healing/accounts?
    """
    data = dashboard_service.get_overview(db, days)
    return ApiResponse(success=True, message="获取概览成功", data=data)


# =====================================================================
# 2. 时间趋势
# =====================================================================

@router.get("/trends", response_model=ApiResponse, summary="获取时间趋势数据")
@handle_api_errors
async def get_trends(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    metric: str = Query(
        "damage",
        description="指标类型: fights / damage / healing / kills / active_accounts",
    ),
    db: Session = Depends(get_db),
):
    """获取时间趋势数据（折线图用）

    Args:
        metric: 指标类型
            - fights: 每日战斗场次
            - damage: 每日总伤?
            - healing: 每日总治?
            - kills: 每日击杀?
            - active_accounts: 每日活跃账号?

    Returns:
        dates: 日期列表
        values: 对应数值列?
    """
    data = dashboard_service.get_trends(db, days, metric)
    return ApiResponse(success=True, message="获取趋势成功", data=data)


# =====================================================================
# 3. 职业分布
# =====================================================================

@router.get(
    "/profession-distribution",
    response_model=ApiResponse,
    summary="获取职业分布",
)
@handle_api_errors
async def get_profession_distribution(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取职业分布数据（饼?柱状图用?

    按角色最新战斗的职业统计，不因转职而拆分同一角色?
    返回每个职业的出场角色数和总伤害?
    """
    data = dashboard_service.get_profession_distribution(db, days)
    return ApiResponse(success=True, message="获取职业分布成功", data=data)


# =====================================================================
# 4. 地图统计
# =====================================================================

@router.get("/map-stats", response_model=ApiResponse, summary="获取地图统计")
@handle_api_errors
async def get_map_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取地图统计（出场热度）

    返回各地图的?
    - fight_count: 战斗场次
    - avg_duration_sec: 平均时长
    - total_damage: 总伤?
    - avg_player_count: 平均参与人数
    """
    data = dashboard_service.get_map_stats(db, days)
    return ApiResponse(success=True, message="获取地图统计成功", data=data)


# =====================================================================
# 5. 玩家排行
# =====================================================================

@router.get("/top-players", response_model=ApiResponse, summary="获取玩家排行")
@handle_api_errors
async def get_top_players(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    sort_by: str = Query(
        "damage",
        description="排序字段: damage / dps / healing / killed / ai_score / "
        "damage_taken / boon_strips / condition_cleanses / resurrects",
    ),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
):
    """获取玩家排行（按 account 维度聚合?

    返回每个账号的：
    - fight_count: 参与战斗?
    - total_damage: 总伤?
    - avg_dps: 平均DPS
    - total_healing: 总治?
    - total_kills: 击杀?
    - total_deaths: 死亡?
    - kd_ratio: K/D?
    - avg_ai_score: 平均AI评分
    """
    data = dashboard_service.get_top_players(db, days, sort_by, limit)
    return ApiResponse(success=True, message="获取排行成功", data=data)


# =====================================================================
# 6. 最近战?
# =====================================================================

@router.get("/recent-fights", response_model=ApiResponse, summary="获取最近战?)
@handle_api_errors
async def get_recent_fights(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db),
):
    """获取最近战斗记?

    返回最近的上传日志中的战斗记录?
    """
    data = dashboard_service.get_recent_fights(db, limit)
    return ApiResponse(success=True, message="获取最近战斗成?, data=data)


# =====================================================================
# 7. 解析状态分?
# =====================================================================

@router.get(
    "/parse-status", response_model=ApiResponse, summary="获取解析状态分?
)
@handle_api_errors
async def get_parse_status(db: Session = Depends(get_db)):
    """获取日志解析状态分?

    返回各解析状态（pending/parsing/completed/failed/partial）的占比?
    """
    data = dashboard_service.get_parse_status_distribution(db)
    return ApiResponse(success=True, message="获取解析状态成?, data=data)


# =====================================================================
# 8. AI 评分分布
# =====================================================================

@router.get(
    "/ai-score-distribution",
    response_model=ApiResponse,
    summary="获取AI评分分布",
)
@handle_api_errors
async def get_ai_score_distribution(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取AI评分分布

    ?S(90-100) / A(80-90) / B(70-80) / C(60-70) / D(0-60) 分段统计?
    """
    data = dashboard_service.get_ai_score_distribution(db, days)
    return ApiResponse(success=True, message="获取评分分布成功", data=data)


# =====================================================================
# 9. Buff 概览
# =====================================================================

@router.get("/buff-overview", response_model=ApiResponse, summary="获取Buff覆盖率概?)
@handle_api_errors
async def get_buff_overview(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    """获取平均 Buff 覆盖率概?

    返回 might / fury / quickness / alacrity / protection / stability 的平均覆盖率?
    """
    data = dashboard_service.get_buff_overview(db, days)
    return ApiResponse(success=True, message="获取Buff概览成功", data=data)
