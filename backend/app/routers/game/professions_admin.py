# -*- coding: utf-8 -*-
# 模块功能：职业管理API路由（管理员操作）
# 作者：System
# 创建日期：2026-05-12

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.schemas.game.profession import (
    ProfessionCreate,
    ProfessionUpdate,
    ProfessionRoleUpdate,
    EliteSpecCreate,
    EliteSpecUpdate,
    EliteSpecRoleUpdate,
    RoleTypeCreate,
    RoleTypeUpdate,
)
from app.services.auth.auth_service import get_current_admin, require_permission
from app.services.game.profession_service import ProfessionService

router = APIRouter(tags=["职业管理"])


@router.put("/profession/{profession_key}/role", response_model=ApiResponse, summary="更新职业默认角色定位")
async def update_profession_role(
    profession_key: str,
    role_update: ProfessionRoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """更新职业的默认角色定义"""
    service = ProfessionService(db)
    success = service.update_profession_role(profession_key, role_update.role_key)
    if success:
        return ApiResponse.success_response(
            message=f"职业 {profession_key} 的默认角色定位已更新为 {role_update.role_key}",
        )
    else:
        return ApiResponse.fail_response(message=f"更新失败，职业 {profession_key} 不存在")


@router.put("/elite-spec/{spec_key}/role", response_model=ApiResponse, summary="更新精英特长默认角色定位")
async def update_spec_role(
    spec_key: str,
    role_update: EliteSpecRoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """更新精英特长的默认角色定义"""
    service = ProfessionService(db)
    success = service.update_spec_role_type(spec_key, role_update.role_key)
    if success:
        return ApiResponse.success_response(
            message=f"精英特长 {spec_key} 的默认角色定位已更新为 {role_update.role_key}",
        )
    else:
        return ApiResponse.fail_response(message=f"更新失败，精英特长 {spec_key} 不存在")


@router.post("/profession", response_model=ApiResponse, summary="创建新职业")
async def create_profession(
    profession_data: ProfessionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """创建新职业"""
    service = ProfessionService(db)
    profession = service.create_profession(profession_data.model_dump())
    if profession:
        return ApiResponse.success_response(
            message="职业创建成功",
            data=profession,
        )
    else:
        return ApiResponse.fail_response(message="职业创建失败，可能已存在")


@router.put("/profession/{profession_key}", response_model=ApiResponse, summary="更新职业信息")
async def update_profession(
    profession_key: str,
    profession_data: ProfessionUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """更新职业信息"""
    service = ProfessionService(db)
    profession = service.update_profession(
        profession_key, 
        profession_data.model_dump(exclude_unset=True)
    )
    if profession:
        return ApiResponse.success_response(
            message="职业更新成功",
            data=profession,
        )
    else:
        return ApiResponse.fail_response(message=f"更新失败，职业 {profession_key} 不存在")


@router.delete("/profession/{profession_key}", response_model=ApiResponse, summary="删除职业")
async def delete_profession(
    profession_key: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """删除职业（软删除，设置is_active=0）"""
    service = ProfessionService(db)
    success = service.delete_profession(profession_key)
    if success:
        return ApiResponse.success_response(message=f"职业 {profession_key} 已删除")
    else:
        return ApiResponse.fail_response(message=f"删除失败，职业 {profession_key} 不存在")


@router.post("/elite-spec", response_model=ApiResponse, summary="创建新精英特长")
async def create_elite_spec(
    spec_data: EliteSpecCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """创建新精英特长"""
    service = ProfessionService(db)
    spec = service.create_elite_spec(spec_data.model_dump())
    if spec:
        return ApiResponse.success_response(
            message="精英特长创建成功",
            data=spec,
        )
    else:
        return ApiResponse.fail_response(message="精英特长创建失败，可能已存在")


@router.put("/elite-spec/{spec_key}", response_model=ApiResponse, summary="更新精英特长信息")
async def update_elite_spec(
    spec_key: str,
    spec_data: EliteSpecUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """更新精英特长信息"""
    service = ProfessionService(db)
    spec = service.update_elite_spec(
        spec_key, 
        spec_data.model_dump(exclude_unset=True)
    )
    if spec:
        return ApiResponse.success_response(
            message="精英特长更新成功",
            data=spec,
        )
    else:
        return ApiResponse.fail_response(message=f"更新失败，精英特长 {spec_key} 不存在")


@router.delete("/elite-spec/{spec_key}", response_model=ApiResponse, summary="删除精英特长")
async def delete_elite_spec(
    spec_key: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """删除精英特长（软删除，设置is_active=0）"""
    service = ProfessionService(db)
    success = service.delete_elite_spec(spec_key)
    if success:
        return ApiResponse.success_response(message=f"精英特长 {spec_key} 已删除")
    else:
        return ApiResponse.fail_response(message=f"删除失败，精英特长 {spec_key} 不存在")


@router.post("/role-type", response_model=ApiResponse, summary="创建新角色定义")
async def create_role_type(
    role_data: RoleTypeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """创建新角色定义"""
    service = ProfessionService(db)
    role = service.create_role_type(role_data.model_dump())
    if role:
        return ApiResponse.success_response(
            message="角色定位创建成功",
            data=role,
        )
    else:
        return ApiResponse.fail_response(message="角色定位创建失败，可能已存在")


@router.put("/role-type/{role_key}", response_model=ApiResponse, summary="更新角色定位")
async def update_role_type(
    role_key: str,
    role_data: RoleTypeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """更新角色定位信息"""
    service = ProfessionService(db)
    role = service.update_role_type(
        role_key, 
        role_data.model_dump(exclude_unset=True)
    )
    if role:
        return ApiResponse.success_response(
            message="角色定位更新成功",
            data=role,
        )
    else:
        return ApiResponse.fail_response(message=f"更新失败，角色定义 {role_key} 不存在")


@router.delete("/role-type/{role_key}", response_model=ApiResponse, summary="删除角色定位")
async def delete_role_type(
    role_key: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission("write")),
):
    """删除角色定位"""
    service = ProfessionService(db)
    success = service.delete_role_type(role_key)
    if success:
        return ApiResponse.success_response(message=f"角色定位 {role_key} 已删除")
    else:
        return ApiResponse.fail_response(message=f"删除失败，角色定义 {role_key} 不存在")
