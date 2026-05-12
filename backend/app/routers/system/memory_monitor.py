
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
from app.utils.cache.enhanced_cache import get_cache
from app.schemas.auth.common import ApiResponse

router = APIRouter(prefix="/memory", tags=["memory-monitor"])


@router.get("/status", response_model=ApiResponse)
async def get_memory_status():
    """获取当前内存状?""
    memory_stats = get_memory_stats()
    cache = get_cache()
    cache_stats = cache.get_stats()
    
    return ApiResponse.success_response(
        data={"memory": memory_stats, "cache": cache_stats}
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


@router.get("/cache/stats", response_model=ApiResponse)
async def get_cache_statistics():
    """获取缓存统计信息"""
    cache = get_cache()
    return ApiResponse.success_response(data=cache.get_stats())


@router.post("/cache/clear", response_model=ApiResponse)
async def clear_all_cache():
    """清空所有缓?""
    cache = get_cache()
    item_count = cache.size()
    cache.clear()
    
    return ApiResponse.success_response(
        data={"cleared_items": item_count}
    )


@router.delete("/cache/{key_pattern}", response_model=ApiResponse)
async def delete_cache_by_pattern(key_pattern: str):
    """按模式删除缓?""
    from app.utils.cache.enhanced_cache import delete_cache
    deleted_count = delete_cache(key_pattern)
    
    return ApiResponse.success_response(
        data={"deleted_count": deleted_count}
    )


@router.get("/check", response_model=ApiResponse)
async def check_memory_status():
    """检查内存是否超?""
    is_over_limit = check_memory_limit(action="api_check")
    
    return ApiResponse.success_response(
        data={
            "is_over_limit": is_over_limit,
            "current_mb": round(get_memory_mb(), 2),
        }
    )

