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
        - member_id: 成员ID（可选，与 account 二选一）
        - account: 玩家账号（可选，与 member_id 二选一）

    返回指标:
        - fight_count: 参与战斗数
        - total_damage: 总伤害
        - avg_dps: 平均DPS
        - total_healing: 总治疗
        - skill_cast_uptime: 技能施法占比
        - buffs: Buff平均覆盖率
        - survival: 生存数据
        - combat: 战斗贡献数据
    """
    log_id = request.get("log_id")
    member_id = request.get("member_id")
    account = request.get("account")

    if not log_id:
        return ApiResponse(success=False, message="缺少必要参数: log_id")

    if member_id is None and not account:
        return ApiResponse(
            success=False, message="缺少必要参数: member_id 或 account 至少提供一个"
        )

    data = analyze_skill_rotation(
        db,
        int(log_id),
        int(member_id) if member_id is not None else None,
        account,
    )

    if data is None:
        return ApiResponse(
            success=True,
            message="未找到该玩家的战斗数据",
            data=None,
        )

    return ApiResponse(
        success=True,
        message="获取技能分析成功",
        data=data,
    )
