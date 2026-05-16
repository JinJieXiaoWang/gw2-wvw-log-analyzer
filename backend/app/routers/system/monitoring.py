# -*- coding: utf-8 -*-
# 模块功能：性能监控API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-27
# 依赖说明：FastAPI

from typing import Optional

from fastapi import APIRouter, Depends, Query
from app.schemas.monitoring.monitoring import BenchmarkRequest, BenchmarkResult
from app.core.performance import (
    BenchmarkRunner,
    PerformanceMonitor,
    benchmark_runner,
    performance_monitor,
)
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.services.auth.auth_service import get_current_admin
from app.utils.logger import logger

router = APIRouter(prefix="/monitoring", tags=["性能监控"])


@router.get("/performance", response_model=ApiResponse, summary="获取性能统计信息")
async def get_performance_stats(
    endpoint: Optional[str] = Query(None, description="指定端点")
):
    # 功能：获取性能统计信息
    if endpoint:
        stats = performance_monitor.get_stats(endpoint)
        return ApiResponse.success_response(message="获取性能统计成功", data=stats)
    else:
        all_stats = performance_monitor.get_all_stats()
        summary = performance_monitor.get_summary()
        return ApiResponse.success_response(
            message="获取性能统计成功",
            data={"summary": summary, "endpoints": all_stats},
        )


@router.get("/performance/summary", response_model=ApiResponse, summary="获取性能摘要")
async def get_performance_summary():
    # 功能：获取性能摘要
    summary = performance_monitor.get_summary()
    return ApiResponse.success_response(message="获取性能摘要成功", data=summary)


@router.post("/performance/reset", response_model=ApiResponse, summary="重置性能统计")
async def reset_performance_stats(
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：重置性能统计
    performance_monitor.reset()
    return ApiResponse.success_response(message="性能统计已重?)")


@router.get("/benchmark", response_model=ApiResponse, summary="获取基准测试结果")
async def get_benchmark_results():
    # 功能：获取基准测试结?
    results = benchmark_runner.get_results()
    return ApiResponse.success_response(message="获取基准测试结果成功", data=results)


@router.post("/benchmark/compare", response_model=ApiResponse, summary="比较基准测试")
async def compare_benchmarks(
    name1: str = Query(..., description="测试名称1"),
    name2: str = Query(..., description="测试名称2"),
):
    # 功能：比较两个基准测?
    comparison = benchmark_runner.compare(name1, name2)
    if comparison is None:
        return ApiResponse.error_response(message="未找到指定的基准测试结果", code=404)
    return ApiResponse.success_response(message="获取比较结果成功", data=comparison)


