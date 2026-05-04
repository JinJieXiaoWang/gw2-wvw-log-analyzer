# -*- coding: utf-8 -*-
# 模块功能：游戏数据API路由
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：FastAPI
# 说明：大部分接口已迁移至字典模块（dictionary），请使用字典接口获取游戏数据

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services.game_data.game_data_service import get_game_data_service

router = APIRouter(prefix="/game-data", tags=["游戏数据"])


@router.get(
    "/info",
    response_model=ApiResponse,
    summary="获取数据版本信息",
    description="获取游戏数据的版本信息",
)
async def get_data_info():
    # 功能：获取数据版本信息
    service = get_game_data_service()
    data_info = service.get_data_info()

    return ApiResponse(success=True, message="获取数据版本信息成功", data=data_info)
