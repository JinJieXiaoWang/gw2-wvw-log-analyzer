# -*- coding: utf-8 -*-
# 模块功能：GW2 参考数据 API（装备下拉列表）
# 说明：数据来自 gw2_data 精简 mapping，内存缓存，不进入数据库

from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.auth.common import ApiResponse
from app.services.game.ref_data_service import GW2RefDataLoader
from app.utils.logger import logger

router = APIRouter(prefix="/ref-data", tags=["GW2参考数据"])


@router.get("/runes", response_model=ApiResponse, summary="获取符文列表")
async def list_runes(
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=500, description="返回数量上限"),
):
    """获取符文下拉列表数据（用于 Build 图书馆装备选择）"""
    try:
        items = GW2RefDataLoader.list_runes(search=search, limit=limit)
        return ApiResponse.success_response(data={"items": items, "total": len(items)})
    except Exception as e:
        logger.error(f"获取符文列表失败: {e}")
        return ApiResponse.fail_response(message=f"获取符文列表失败: {e}")


@router.get("/sigils", response_model=ApiResponse, summary="获取法印列表")
async def list_sigils(
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=500, description="返回数量上限"),
):
    """获取法印下拉列表数据（用于 Build 图书馆装备选择）"""
    try:
        items = GW2RefDataLoader.list_sigils(search=search, limit=limit)
        return ApiResponse.success_response(data={"items": items, "total": len(items)})
    except Exception as e:
        logger.error(f"获取法印列表失败: {e}")
        return ApiResponse.fail_response(message=f"获取法印列表失败: {e}")


@router.get("/relics", response_model=ApiResponse, summary="获取古物列表")
async def list_relics(
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=500, description="返回数量上限"),
):
    """获取古物下拉列表数据（用于 Build 图书馆装备选择）"""
    try:
        items = GW2RefDataLoader.list_relics(search=search, limit=limit)
        return ApiResponse.success_response(data={"items": items, "total": len(items)})
    except Exception as e:
        logger.error(f"获取古物列表失败: {e}")
        return ApiResponse.fail_response(message=f"获取古物列表失败: {e}")


@router.get("/foods", response_model=ApiResponse, summary="获取食物列表")
async def list_foods(
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=500, description="返回数量上限"),
):
    """获取食物下拉列表数据（用于 Build 图书馆装备选择）"""
    try:
        items = GW2RefDataLoader.list_foods(search=search, limit=limit)
        return ApiResponse.success_response(data={"items": items, "total": len(items)})
    except Exception as e:
        logger.error(f"获取食物列表失败: {e}")
        return ApiResponse.fail_response(message=f"获取食物列表失败: {e}")


@router.get("/utilities", response_model=ApiResponse, summary="获取增强剂列表")
async def list_utilities(
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, ge=1, le=500, description="返回数量上限"),
):
    """获取扳手/保养油等增强剂下拉列表数据"""
    try:
        items = GW2RefDataLoader.list_utilities(search=search, limit=limit)
        return ApiResponse.success_response(data={"items": items, "total": len(items)})
    except Exception as e:
        logger.error(f"获取增强剂列表失败: {e}")
        return ApiResponse.fail_response(message=f"获取增强剂列表失败: {e}")
