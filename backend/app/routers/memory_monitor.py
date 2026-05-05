
# -*- coding: utf-8 -*-
# 模块功能：内存监控API路由
# 作者：系统
# 创建日期：2026-05-06
# 说明：
#   - 内存状态查询
#   - 手动GC触发
#   - 缓存统计
#   - 内存限制配置

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import logger
from app.middleware.enhanced_memory_monitor import (
    get_memory_mb,
    get_memory_stats,
    trigger_gc,
    check_memory_limit,
)
from app.utils.enhanced_cache import get_cache

router = APIRouter(prefix="/api/memory", tags=["memory-monitor"])


@router.get("/status", response_model=Dict[str, Any])
async def get_memory_status():
    """获取当前内存状态"""
    memory_stats = get_memory_stats()
    cache = get_cache()
    cache_stats = cache.get_stats()
    
    return {
        "memory": memory_stats,
        "cache": cache_stats,
    }


@router.post("/gc", response_model=Dict[str, Any])
async def force_gc():
    """强制触发垃圾回收"""
    freed_mb = trigger_gc(action="api_manual_trigger", force=True)
    
    return {
        "success": True,
        "freed_mb": round(freed_mb, 2),
        "current_mb": round(get_memory_mb(), 2),
    }


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_statistics():
    """获取缓存统计信息"""
    cache = get_cache()
    return cache.get_stats()


@router.post("/cache/clear", response_model=Dict[str, Any])
async def clear_all_cache():
    """清空所有缓存"""
    cache = get_cache()
    item_count = cache.size()
    cache.clear()
    
    return {
        "success": True,
        "cleared_items": item_count,
    }


@router.delete("/cache/{key_pattern}", response_model=Dict[str, Any])
async def delete_cache_by_pattern(key_pattern: str):
    """按模式删除缓存"""
    from app.utils.enhanced_cache import delete_cache
    deleted_count = delete_cache(key_pattern)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
    }


@router.get("/check", response_model=Dict[str, Any])
async def check_memory_status():
    """检查内存是否超限"""
    is_over_limit = check_memory_limit(action="api_check")
    
    return {
        "is_over_limit": is_over_limit,
        "current_mb": round(get_memory_mb(), 2),
    }

