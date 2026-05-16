# -*- coding: utf-8 -*-
# 模块功能：职业数据API路由
# 作者：System
# 创建日期：2026-05-11
# 依赖说明：FastAPI
# 说明：提供职业、精英特长、角色定位的查询接口
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.services.auth.auth_service import get_current_admin, require_permission
from app.services.game.profession_service import ProfessionService

router = APIRouter(tags=["职业数据"])

@router.get("/", response_model=ApiResponse, summary="获取所有职业列表")
async def get_professions(
    include_specs: bool = False,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    获取所有职业列表
    - **include_specs**: 是否包含精英特长信息
    - **active_only**: 是否只返回启用状态的数据
    """
    service = ProfessionService(db)
    professions = service.get_all_professions(include_specs=include_specs, active_only=active_only)
    return ApiResponse.success_response(
        message="获取职业列表成功",
        data={
            "professions": professions,
            "total": len(professions),
        },
    )

@router.get("/cascade", response_model=ApiResponse, summary="获取职业-精英特长级联数据")
async def get_profession_cascade(db: Session = Depends(get_db)):
    """
    获取职业-精英特长级联数据
    用于前端级联选择器组件
    """
    service = ProfessionService(db)
    cascade_data = service.get_profession_spec_cascade()
    return ApiResponse.success_response(
        message="获取级联数据成功",
        data=cascade_data,
    )

@router.get("/role-mapping", response_model=ApiResponse, summary="获取角色定位-精英特长映射")
async def get_role_spec_mapping(db: Session = Depends(get_db)):
    """
    获取角色定位到精英特长的映射
    用于评分规则页面职业归类展示
    """
    service = ProfessionService(db)
    mapping = service.get_role_spec_mapping()
    return ApiResponse.success_response(
        message="获取角色映射成功",
        data=mapping,
    )

@router.get("/role-types", response_model=ApiResponse, summary="获取所有角色定义")
async def get_role_types(db: Session = Depends(get_db)):
    """获取所有角色定位类型"""
    service = ProfessionService(db)
    role_types = service.get_all_role_types()
    return ApiResponse.success_response(
        message="获取角色定位成功",
        data=role_types,
    )

@router.get("/elite-specs", response_model=ApiResponse, summary="获取所有精英特长列表")
async def get_all_elite_specs(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    获取所有精英特长列表
    - **active_only**: 是否只返回启用状态的数据
    """
    service = ProfessionService(db)
    specs = service.get_all_specs(active_only=active_only)
    return ApiResponse.success_response(
        message="获取精英特长列表成功",
        data={
            "elite_specs": specs,
            "total": len(specs),
        },
    )

@router.get("/elite-specs/{profession_key}", response_model=ApiResponse, summary="获取职业的精英特长列表")
async def get_profession_elite_specs(
    profession_key: str,
    db: Session = Depends(get_db),
):
    """获取指定职业的所有精英特长列表"""
    service = ProfessionService(db)
    specs = service.get_specs_by_profession(profession_key)
    return ApiResponse.success_response(
        message=f"获取 {profession_key} 的精英特长成功",
        data={
            "profession_key": profession_key,
            "elite_specs": specs,
            "total": len(specs),
        },
    )

@router.get("/profession/{profession_key}", response_model=ApiResponse, summary="获取职业详情")
async def get_profession_detail(
    profession_key: str,
    db: Session = Depends(get_db),
):
    """
    获取职业详细信息
    - **profession_key**: 职业英文键（Guardian, Warrior 等）
    """
    service = ProfessionService(db)
    profession = service.get_profession(profession_key, include_specs=True)
    if not profession:
        return ApiResponse.fail_response(message=f"职业 {profession_key} 不存在")
    return ApiResponse.success_response(
        message="获取职业详情成功",
        data=profession,
    )

@router.get("/elite-spec/{spec_key}", response_model=ApiResponse, summary="获取精英特长详情")
async def get_elite_spec_detail(
    spec_key: str,
    db: Session = Depends(get_db),
):
    """
    获取精英特长详细信息
    - **spec_key**: 精英特长英文键（Dragonhunter, Firebrand 等）
    """
    service = ProfessionService(db)
    spec = service.get_spec_by_key(spec_key)
    if not spec:
        return ApiResponse.fail_response(message=f"精英特长 {spec_key} 不存在")
    return ApiResponse.success_response(
        message="获取精英特长详情成功",
        data=spec,
    )

@router.get("/statistics", response_model=ApiResponse, summary="获取职业数据统计")
async def get_statistics(db: Session = Depends(get_db)):
    """获取职业数据统计信息"""
    service = ProfessionService(db)
    stats = service.get_statistics()
    return ApiResponse.success_response(
        message="获取统计成功",
        data=stats,
    )

@router.get("/color/{profession_key}", response_model=ApiResponse, summary="获取职业颜色")
async def get_profession_color(
    profession_key: str,
    db: Session = Depends(get_db),
):
    """获取职业颜色"""
    service = ProfessionService(db)
    color = service.get_profession_color(profession_key)
    return ApiResponse.success_response(
        message="获取职业颜色成功",
        data={"profession_key": profession_key, "color": color},
    )

@router.get("/name/{profession_key}", response_model=ApiResponse, summary="获取职业中文名称")
async def get_profession_name(
    profession_key: str,
    db: Session = Depends(get_db),
):
    """获取职业中文名称"""
    service = ProfessionService(db)
    name = service.get_profession_name(profession_key)
    return ApiResponse.success_response(
        message="获取职业名称成功",
        data={"profession_key": profession_key, "name": name},
    )

@router.get("/spec-role/{spec_key}", response_model=ApiResponse, summary="获取精英特长角色定位")
async def get_spec_role_type(
    spec_key: str,
    db: Session = Depends(get_db),
):
    """获取精英特长的角色定位"""
    service = ProfessionService(db)
    role = service.get_spec_role_type(spec_key)
    return ApiResponse.success_response(
        message="获取角色定位成功",
        data={"spec_key": spec_key, "role_type": role},
    )
