# -*- coding: utf-8 -*-
# 模块功能：评分规则管理 API 路由
# 说明：提供评分规则的 CRUD 与预设管理

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.schemas.scoring_rule import (
    ScoringRuleBatchUpdate,
    ScoringRuleCreate,
    ScoringRuleResponse,
    ScoringRuleUpdate,
)
from app.services.auth_service import get_current_admin, require_super_admin
from app.services.scoring_rule_service import ScoringRuleService
from app.utils.exceptions import BadRequestException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/scoring-rules", tags=["评分规则管理"])


@router.get("/roles", response_model=ApiResponse, summary="获取所有角色类型配置")
async def get_role_types(
    db: Session = Depends(get_db),
):
    """获取所有支持的角色类型列表"""
    service = ScoringRuleService(db)
    roles = [
        {"type": "dps", "label": "输出", "description": "以伤害输出为主要职责"},
        {"type": "support", "label": "辅助", "description": "以治疗和增益为主要职责"},
        {"type": "tank", "label": "承伤", "description": "以吸收伤害和控制为主要职责"},
    ]
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取角色类型成功", data=roles
    )


@router.get("/rules", response_model=ApiResponse, summary="获取评分规则列表")
async def get_scoring_rules(
    role_type: Optional[str] = Query(None, description="角色类型筛选"),
    active_only: bool = Query(True, description="仅返回启用的规则"),
    db: Session = Depends(get_db),
):
    """获取评分规则，支持按角色类型筛选"""
    service = ScoringRuleService(db)

    if role_type:
        rules = service.get_rules_by_role(role_type, active_only)
        data = {
            "role_type": role_type,
            "role_label": service.get_role_label(role_type),
            "rules": [ScoringRuleResponse.model_validate(r) for r in rules],
        }
    else:
        all_rules = service.get_all_rules(active_only)
        data = {
            role: {
                "role_type": role,
                "role_label": service.get_role_label(role),
                "rules": [ScoringRuleResponse.model_validate(r) for r in rules],
            }
            for role, rules in all_rules.items()
        }

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取评分规则成功", data=data
    )


@router.get("/rules/{rule_id}", response_model=ApiResponse, summary="获取单个评分规则")
async def get_scoring_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """获取指定ID的评分规则详情"""
    service = ScoringRuleService(db)
    rule = service.get_rule_by_id(rule_id)
    if not rule:
        raise NotFoundException(f"评分规则 ID={rule_id} 不存在")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取评分规则成功",
        data=ScoringRuleResponse.model_validate(rule),
    )


@router.post("/rules", response_model=ApiResponse, summary="创建评分规则")
async def create_scoring_rule(
    rule_data: ScoringRuleCreate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """创建新的评分规则"""
    service = ScoringRuleService(db)
    try:
        rule = service.create_rule(rule_data.model_dump())
        return ApiResponse.success_response(
            code=HTTP_200_OK,
            message="创建评分规则成功",
            data=ScoringRuleResponse.model_validate(rule),
        )
    except ValueError as e:
        raise BadRequestException(str(e))


@router.put("/rules/{rule_id}", response_model=ApiResponse, summary="更新评分规则")
async def update_scoring_rule(
    rule_id: int,
    rule_data: ScoringRuleUpdate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """更新评分规则"""
    service = ScoringRuleService(db)
    rule = service.update_rule(rule_id, rule_data.model_dump(exclude_unset=True))
    if not rule:
        raise NotFoundException(f"评分规则 ID={rule_id} 不存在")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="更新评分规则成功",
        data=ScoringRuleResponse.model_validate(rule),
    )


@router.delete("/rules/{rule_id}", response_model=ApiResponse, summary="删除评分规则")
async def delete_scoring_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """删除评分规则"""
    service = ScoringRuleService(db)
    success = service.delete_rule(rule_id)
    if not success:
        raise NotFoundException(f"评分规则 ID={rule_id} 不存在")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除评分规则成功", data=None
    )


@router.post("/rules/batch", response_model=ApiResponse, summary="批量更新评分规则")
async def batch_update_scoring_rules(
    batch_data: ScoringRuleBatchUpdate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """批量更新某个角色类型的所有评分规则（先删后插）"""
    service = ScoringRuleService(db)
    rules_data = [r.model_dump() for r in batch_data.rules]
    result = service.batch_update_rules(batch_data.role_type, rules_data)
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="批量更新评分规则成功", data=result
    )


@router.post("/rules/reset", response_model=ApiResponse, summary="重置为默认规则")
async def reset_scoring_rules(
    role_type: Optional[str] = Query(None, description="指定角色类型，不指定则重置所有"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """重置评分规则为系统默认值"""
    service = ScoringRuleService(db)
    result = service.reset_to_default(role_type)
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="重置评分规则成功", data=result
    )


@router.get("/dimensions", response_model=ApiResponse, summary="获取评分维度列表")
async def get_scoring_dimensions(
    db: Session = Depends(get_db),
):
    """获取所有支持的评分维度及其中文标签"""
    service = ScoringRuleService(db)
    dimensions = [
        {"key": "damage", "label": "总伤害"},
        {"key": "power_damage", "label": "直伤"},
        {"key": "condition_damage", "label": "症状伤害"},
        {"key": "healing", "label": "治疗量"},
        {"key": "boons", "label": "增益覆盖"},
        {"key": "alacrity", "label": "敏捷覆盖"},
        {"key": "quickness", "label": "急速覆盖"},
        {"key": "survival", "label": "生存能力"},
        {"key": "strips", "label": "破法"},
        {"key": "cleanses", "label": "净化"},
        {"key": "kills", "label": "击杀"},
        {"key": "breakbar", "label": "蔑视条"},
        {"key": "damage_taken", "label": "承受伤害"},
        {"key": "blocked_count", "label": "格挡"},
        {"key": "evaded_count", "label": "闪避"},
    ]
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取评分维度成功", data=dimensions
    )
