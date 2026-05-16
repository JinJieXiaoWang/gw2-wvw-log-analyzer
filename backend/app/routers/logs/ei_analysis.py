# -*- coding: utf-8 -*-
# 模块功能：EI分析结果查询（精简版）
# 说明：v2.2 优化——预计算逻辑下沉至 service 层，路由只保留接口入口。

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.schemas.log.ei_analysis import PlayerRotationResponse
from app.services.zevtc.ei_summary_service import build_ei_summary
from app.services.zevtc import fight_service as fight_svc
from app.utils.error.exceptions import NotFoundException
from app.utils.logger import logger


router = APIRouter(prefix="/ei-analysis", tags=["EI分析"])


@router.get("/{log_id}", response_model=ApiResponse, summary="获取日志战斗摘要")
async def get_ei_summary(
    log_id: int,
    sort_by: str = Query("damage", description="排序字段"),
    db: Session = Depends(get_db),
):
    """获取日志的战斗摘要数据（含预计算衍生字段，前端即渲染）。"""
    summary = build_ei_summary(db, log_id, sort_by)
    if summary is None:
        raise NotFoundException("该日志暂无解析结果")
    return ApiResponse.success_response(
        data=summary, message="获取分析摘要成功", code=200
    )


@router.get(
    "/{log_id}/player/{account}/rotation",
    response_model=ApiResponse,
    summary="获取玩家技能循环",
)
async def get_player_rotation(log_id: int, account: str, db: Session = Depends(get_db)):
    """获取指定玩家在指定日志中的技能循环和技能释放次数。"""
    result = fight_svc.get_player_rotation(db, log_id, account)
    if not result:
        raise NotFoundException("该玩家在此日志中没有技能数据")
    return ApiResponse.success_response(data=result, message="获取成功", code=200)


@router.get(
    "/{log_id}/player/{account}",
    response_model=ApiResponse,
    summary="获取玩家在某日志中的详细数据",
)
async def get_player_detail(log_id: int, account: str, db: Session = Depends(get_db)):
    """获取指定玩家在指定日志中的详细统计数据。"""
    players = fight_svc.get_log_player_stats(db, log_id)
    player = next((p for p in players if p.get("account") == account), None)
    if not player:
        raise NotFoundException("该玩家在此日志中不存在")
    return ApiResponse.success_response(data=player, message="获取成功", code=200)
