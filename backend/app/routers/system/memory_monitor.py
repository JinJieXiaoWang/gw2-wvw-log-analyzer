
# -*- coding: utf-8 -*-
# 模块功能：内存监控API路由
# 作者：系统
# 创建日期?2026-05-06
# 说明?
#   - 内存状态查?
#   - 手动GC触发
#   - 缓存统计
#   - 内存限制配置

from fastapi import APIRouter

from app.middleware.enhanced_memory_monitor import (
    get_memory_mb,
    get_memory_stats,
    trigger_gc,
    check_memory_limit,
)
from app.schemas.auth.common import ApiResponse

router = APIRouter(prefix="/memory", tags=["memory-monitor"])


@router.get("/status", response_model=ApiResponse)
async def get_memory_status():
    """获取当前内存状态"""
    memory_stats = get_memory_stats()
    return ApiResponse.success_response(
        data={"memory": memory_stats}
    )


@router.post("/gc", response_model=ApiResponse)
async def force_gc():
    """强制触发垃圾回收"""
    freed_mb = trigger_gc(action="api_manual_trigger", force=True)
    return ApiResponse.success_response(
        data={
            "freed_mb": round(freed_mb, 2),
            "current_mb": round(get_memory_mb(), 2),
        }
    )


@router.get("/check", response_model=ApiResponse)
async def check_memory_status():
    """检查内存是否超限"""
    is_over_limit = check_memory_limit(action="api_check")
    return ApiResponse.success_response(
        data={
            "is_over_limit": is_over_limit,
            "current_mb": round(get_memory_mb(), 2),
        }
    )

