# -*- coding: utf-8 -*-
# 模块功能：技能循环分析API路由（简化版）
# 说明：基于现有 fight_stats 数据提供可用分析

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.services.skills.skill_rotation_service import analyze_skill_rotation
from app.utils.decorators import handle_api_errors

router = APIRouter(prefix="/skill-rotation", tags=["技能循环分析"])


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
    """基于 fight_stats 提供简化版技能分析

    请求体:
        - log_id: 日志ID（必填）
        - member_id: 成员ID（必填，用于查找玩家）

    返回完整的技能循环分析数据
    """
    log_id = request.get("log_id")
    member_id = request.get("member_id")

    if not log_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id")

    if not member_id:
        return ApiResponse(
            success=False, message="缺少必要参数: member_id"
        )

    try:
        data = analyze_skill_rotation(int(log_id), str(member_id), db)
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"分析失败: {str(e)}",
            data=None,
        )

    return ApiResponse(
        success=True,
        message="获取技能分析成功",
        data=data,
    )
