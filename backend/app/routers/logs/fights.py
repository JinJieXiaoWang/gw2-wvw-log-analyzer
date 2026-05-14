# 模块功能：战斗数据API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新说明：v2.0 改造为从 fight_stats 表读取，不再返回完整 EI JSON

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.schemas.auth.common import ApiResponse
from app.schemas.log.fight import FightListResponse, FightResponse, FightStatsResponse
from app.services.zevtc import fight_service as fight_svc
from app.utils.error.exceptions import NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/fights", tags=["战斗数据"])


@router.get("", response_model=ApiResponse, summary="获取战斗列表")
async def get_fights(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    map_name: Optional[str] = Query(None, description="地图名称"),
    server_name: Optional[str] = Query(None, description="服务器"),
    db: Session = Depends(get_db),
):
    """获取战斗列表"""
    skip = (page - 1) * page_size
    fights, total = fight_svc.get_fights(
        db, skip=skip, limit=page_size, map_name=map_name, server_name=server_name
    )

    return ApiResponse.success_response(
        data={
            "items": [FightResponse.model_validate(f) for f in fights],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取战斗列表成功",
        code=HTTP_200_OK,
    )


@router.get("/{fight_id}", response_model=ApiResponse, summary="获取战斗详情")
async def get_fight(fight_id: int, db: Session = Depends(get_db)):
    """获取战斗详情（含玩家统计）"""
    fight = fight_svc.get_fight_with_stats(db, fight_id)
    if not fight:
        raise NotFoundException(f"战斗ID {fight_id} 不存在")

    fight_data = FightResponse.model_validate(fight)
    stats_data = fight_svc.build_fight_stats_data(fight)

    return ApiResponse.success_response(
        data={"fight": fight_data, "stats": stats_data},
        message="获取战斗成功",
        code=HTTP_200_OK,
    )


@router.get("/{fight_id}/stats", response_model=ApiResponse, summary="获取战斗统计数据")
async def get_fight_stats(fight_id: int, db: Session = Depends(get_db)):
    """获取战斗统计数据"""
    fight = fight_svc.get_fight_by_id(db, fight_id)
    if not fight:
        raise NotFoundException(f"战斗ID {fight_id} 不存在")

    stats = fight_svc.get_fight_stats(db, fight_id)

    return ApiResponse.success_response(
        data=[FightStatsResponse.model_validate(s) for s in stats],
        message="获取战斗统计成功",
        code=HTTP_200_OK,
    )


# =====================================================================
# 新增：按日志 ID 查询玩家排行榜（用于 /logs/3 页面）
# =====================================================================
@router.get(
    "/by-log/{log_id}/players", response_model=ApiResponse, summary="获取日志玩家排行榜"
)
async def get_log_players(
    log_id: int,
    sort_by: str = Query("damage", description="排序字段"),
    db: Session = Depends(get_db),
):
    """
    获取指定日志的玩家排行榜。
    这是 /logs/{log_id} 页面的核心数据源。
    """
    result = fight_svc.get_log_players_with_distribution(db, log_id, sort_by)

    return ApiResponse.success_response(
        data=result,
        message="获取成功",
        code=HTTP_200_OK,
    )
