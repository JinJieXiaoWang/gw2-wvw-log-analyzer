# -*- coding: utf-8 -*-
# 模块功能：评分规则管?API 路由
# 说明：提供评分规则的 CRUD、职业特定规则管理与版本管理

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.scoring.scoring_rule_version import ScoringRuleVersion
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.schemas.scoring.scoring_recalculation import ScoringRuleVersionResponse
from app.schemas.scoring.scoring_rule import (
    ScoringRuleBatchUpdate,
    ScoringRuleCreate,
    ScoringRuleResponse,
    ScoringRuleUpdate,
)
from app.services.auth.auth_service import get_current_admin, require_super_admin
from app.constants.scoring import SCORING_DIMENSIONS
from app.services.scoring.scoring_rule_service import ScoringRuleService
from app.utils.error.exceptions import BadRequestException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/scoring-rules", tags=["评分规则管理"])


@router.get("/roles", response_model=ApiResponse, summary="获取所有启用的角色类型配置")
async def get_role_types(
    db: Session = Depends(get_db),
):
    """获取所有启用的角色类型列表（从职业管理模块 gw_role_type 表读取，确保与职业管理数据一致）"""
    service = ScoringRuleService(db)
    roles = service.get_role_types_data()

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取角色类型成功", data=roles
    )


@router.get("/rules", response_model=ApiResponse, summary="获取评分规则列表")
async def get_scoring_rules(
    role_type: Optional[str] = Query(None, description="角色类型筛?),
    profession: Optional[str] = Query(None, description="职业特定规则筛?),
    active_only: bool = Query(True, description="仅返回启用的规则"),
    db: Session = Depends(get_db),
):
    """获取评分规则，支持按角色类型和职业筛?
    
    - ?profession ?null 或不传时，返回通用规则
    - ?profession 有值时，返回该职业的特定规则（如不存在则返回空列表?
    """
    service = ScoringRuleService(db)
    data = service.get_scoring_rules_data(
        role_type=role_type, profession=profession, active_only=active_only
    )

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取评分规则成功", data=data
    )


@router.get("/rules/{rule_id}", response_model=ApiResponse, summary="获取单个评分规则")
async def get_scoring_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    """获取指定ID的评分规则详?""
    service = ScoringRuleService(db)
    rule = service.get_rule_by_id(rule_id)
    if not rule:
        raise NotFoundException(f"评分规则 ID={rule_id} 不存?)

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
        raise NotFoundException(f"评分规则 ID={rule_id} 不存?)

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
        raise NotFoundException(f"评分规则 ID={rule_id} 不存?)

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除评分规则成功", data=None
    )


@router.post("/rules/batch", response_model=ApiResponse, summary="批量更新评分规则")
async def batch_update_scoring_rules(
    batch_data: ScoringRuleBatchUpdate,
    auto_bump_version: bool = Query(True, description="是否自动递增规则版本),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """批量更新某个角色类型的所有评分规则（先删后插?
    
    - 支持更新通用规则（profession=null）或职业特定规则（profession有值）
    - 批量更新后自动递增规则版本号（可通过 auto_bump_version 控制?
    """
    service = ScoringRuleService(db)
    rules_data = [r.model_dump() for r in batch_data.rules]
    result = service.batch_update_rules(
        batch_data.role_type, rules_data, profession=batch_data.profession
    )

    # 自动递增版本
    version_info = None
    if auto_bump_version:
        prof_desc = f"职业 {batch_data.profession} " if batch_data.profession else "通用 "
        version = service.bump_version(
            description=f"批量更新 {batch_data.role_type} {prof_desc}评分规则"
        )
        version_info = {"version_id": version.id, "version": version.version}

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="批量更新评分规则成功",
        data={**result, "version": version_info},
    )


@router.post("/rules/reset", response_model=ApiResponse, summary="重置为默认规则)
async def reset_scoring_rules(
    role_type: Optional[str] = Query(None, description="指定角色类型，不指定则重置所?),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """重置评分规则为系统默认值（仅重置通用规则，保留职业特定规则）"""
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
    dimensions = SCORING_DIMENSIONS
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取评分维度成功", data=dimensions
    )


# ==================== 职业特定规则接口 ====================

@router.post(
    "/rules/profession/{profession}",
    response_model=ApiResponse,
    summary="创建/更新职业特定规则?,
)
async def upsert_profession_rules(
    profession: str,
    batch_data: ScoringRuleBatchUpdate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """为指定职业创建或更新完整规则?
    
    - 如果该职业已有规则，先删除旧规则再插入新规则
    - 自动递增规则版本
    """
    service = ScoringRuleService(db)
    rules_data = [r.model_dump() for r in batch_data.rules]
    result = service.batch_update_rules(
        batch_data.role_type, rules_data, profession=profession
    )

    # 递增版本
    version = service.bump_version(
        description=f"更新职业 {profession} ?{batch_data.role_type} 评分规则"
    )

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message=f"职业 {profession} 评分规则更新成功",
        data={**result, "version_id": version.id, "version": version.version},
    )


@router.delete(
    "/rules/profession/{profession}",
    response_model=ApiResponse,
    summary="删除职业特定规则",
)
async def delete_profession_rules(
    profession: str,
    role_type: Optional[str] = Query(None, description="指定角色类型，不指定则删除该职业所有规则),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """删除指定职业的所有特定规则""
    service = ScoringRuleService(db)
    count = service.delete_profession_rules(profession, role_type)
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message=f"已删除职?{profession} ?{count} 条特定规则,
        data={"profession": profession, "deleted_count": count},
    )


@router.get("/professions", response_model=ApiResponse, summary="获取已配置职业规则列?)
async def get_professions_with_rules(
    role_type: Optional[str] = Query(None, description="按角色类型筛?),
    db: Session = Depends(get_db),
):
    """获取已配置职业特定规则的职业列表"""
    service = ScoringRuleService(db)
    professions = service.get_professions_with_rules(role_type)
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取职业规则列表成功",
        data={"professions": professions, "count": len(professions)},
    )


# ==================== 版本管理接口 ====================

@router.get("/versions", response_model=ApiResponse, summary="获取规则版本历史")
async def get_rule_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取评分规则版本历史列表"""
    service = ScoringRuleService(db)
    versions = service.get_versions(skip=skip, limit=limit)
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取版本历史成功",
        data=[
            ScoringRuleVersionResponse.model_validate(v).model_dump()
            for v in versions
        ],
    )


@router.get("/versions/{version_id}", response_model=ApiResponse, summary="获取版本详情")
async def get_rule_version(
    version_id: int,
    db: Session = Depends(get_db),
):
    """获取指定版本的详情和重算进度"""
    service = ScoringRuleService(db)
    data = service.get_version_with_progress(version_id)
    if not data:
        raise NotFoundException(f"版本记录 ID={version_id} 不存?)

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取版本详情成功", data=data
    )


@router.post("/versions/bump", response_model=ApiResponse, summary="手动递增规则版本")
async def bump_rule_version(
    description: Optional[str] = Query(None, description="版本变更描述"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(require_super_admin),
):
    """手动递增评分规则版本""
    service = ScoringRuleService(db)
    version = service.bump_version(description or "手动版本递增")
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="版本递增成功",
        data={"version_id": version.id, "version": version.version},
    )
