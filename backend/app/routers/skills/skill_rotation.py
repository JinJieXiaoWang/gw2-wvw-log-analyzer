# -*- coding: utf-8 -*-
# 模块功能：技能循环分析API路由
# 说明：基于 EI 同步数据提供真实技能循环分析

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.services.skills.skill_rotation_service import (
    analyze_skill_rotation,
    compare_rotations,
    export_rotation_report,
    get_ideal_rotations,
    get_player_rotation,
    health_check,
    ERROR_CODES,
)
from app.utils.decorators import handle_api_errors

router = APIRouter(prefix="/skill-rotation", tags=["技能循环分析"])


# ==================== 健康检查 ====================

@router.get(
    "/health",
    response_model=ApiResponse,
    summary="服务健康检查",
)
@handle_api_errors
async def skill_rotation_health(db: Session = Depends(get_db)):
    """检查技能循环分析服务状态"""
    result = health_check(db)
    return ApiResponse(
        success=result["status"] == "healthy",
        message="服务运行正常" if result["status"] == "healthy" else "服务异常",
        data=result,
    )


# ==================== 玩家技能循环 ====================

@router.get(
    "/player/{member_account}",
    response_model=ApiResponse,
    summary="获取玩家技能循环",
)
@handle_api_errors
async def get_player_skill_rotation(
    member_account: str,
    log_id: int = Query(..., description="日志ID"),
    db: Session = Depends(get_db),
):
    """获取指定玩家在指定日志中的技能循环数据

    参数:
        - member_account: 玩家账号（如 xxx.1234）
        - log_id: 日志ID（必填）

    返回:
        包含 events(事件列表), cycles(循环分割), stats(统计), mistakes(失误), optimizations(优化建议)
    """
    if not log_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id")

    data = get_player_rotation(log_id, member_account, db)
    if not data.get("found"):
        return ApiResponse(
            success=False,
            message=f"找不到该玩家在日志 {log_id} 中的数据",
            data={"account": member_account, "log_id": log_id},
        )

    return ApiResponse(
        success=True,
        message="获取技能循环成功",
        data=data,
    )


# ==================== 分析接口（兼容旧版） ====================

@router.post(
    "/analyze",
    response_model=ApiResponse,
    summary="分析技能循环",
)
@handle_api_errors
async def analyze_rotation(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """基于 EI 数据提供技能循环分析

    请求体:
        - log_id: 日志ID（必填）
        - member_id: 成员账号（必填，用于查找玩家）

    返回完整的技能循环分析数据
    """
    log_id = request.get("log_id")
    member_id = request.get("member_id")

    if not log_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id")

    if not member_id:
        return ApiResponse(success=False, message="缺少必要参数: member_id")

    data = analyze_skill_rotation(int(log_id), str(member_id), db)
    if not data.get("found"):
        return ApiResponse(
            success=False,
            message=f"找不到该玩家在日志 {log_id} 中的数据",
            data={"account": member_id, "log_id": log_id},
        )

    return ApiResponse(
        success=True,
        message="获取技能分析成功",
        data=data,
    )


# ==================== 循环对比 ====================

@router.get(
    "/compare/{member_account}",
    response_model=ApiResponse,
    summary="对比技能循环",
)
@handle_api_errors
async def compare_skill_rotation(
    member_account: str,
    benchmark_account: str = Query(..., description="对比基准账号"),
    log_id: int = Query(..., description="日志ID"),
    db: Session = Depends(get_db),
):
    """对比两个玩家在同一日志中的技能循环

    参数:
        - member_account: 被对比玩家账号
        - benchmark_account: 基准玩家账号（Query参数）
        - log_id: 日志ID（Query参数）

    返回:
        包含 actual(实际玩家数据), benchmark(基准玩家数据), comparisons(对比指标)
    """
    if not log_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id")
    if not benchmark_account:
        return ApiResponse(success=False, message="缺少必要参数: benchmark_account")

    data = compare_rotations(log_id, member_account, benchmark_account, db)
    if not data.get("success"):
        return ApiResponse(
            success=False,
            message=data.get("message", "对比失败"),
            data=data,
        )

    return ApiResponse(
        success=True,
        message="循环对比成功",
        data=data,
    )


# ==================== 导出报告 ====================

@router.post(
    "/export-report",
    response_model=ApiResponse,
    summary="导出分析报告",
)
@handle_api_errors
async def export_report(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """导出技能循环分析报告

    请求体:
        - log_id: 日志ID（必填）
        - member_id: 成员账号（必填）
        - format: 导出格式，json 或 pdf（默认 json）

    返回:
        报告数据结构，前端可基于此生成文件下载
    """
    log_id = request.get("log_id")
    member_id = request.get("member_id")
    fmt = request.get("format", "json")

    if not log_id or not member_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id 或 member_id")

    rotation_data = get_player_rotation(int(log_id), str(member_id), db)
    if not rotation_data.get("found"):
        return ApiResponse(
            success=False,
            message=f"找不到该玩家在日志 {log_id} 中的数据",
        )

    report = export_rotation_report(rotation_data)
    report["format"] = fmt

    return ApiResponse(
        success=True,
        message="报告生成成功",
        data=report,
    )


# ==================== 理想循环模板 ====================

@router.get(
    "/ideal-rotations",
    response_model=ApiResponse,
    summary="获取理想循环模板",
)
@handle_api_errors
async def ideal_rotations(
    profession: Optional[str] = Query(None, description="职业名称，如 Troubadour"),
):
    """获取理想技能循环模板

    参数:
        - profession: 职业名称（可选），不提供则返回通用模板

    返回:
        理想循环步骤列表
    """
    templates = get_ideal_rotations(profession)
    return ApiResponse(
        success=True,
        message="获取模板成功",
        data={"templates": templates, "profession": profession},
    )


# ==================== 错误码 ====================

@router.get(
    "/errors",
    response_model=ApiResponse,
    summary="错误码说明",
)
@handle_api_errors
async def error_codes():
    """获取技能循环分析相关的错误码说明"""
    return ApiResponse(
        success=True,
        message="获取错误码成功",
        data={"error_codes": list(ERROR_CODES.values())},
    )
