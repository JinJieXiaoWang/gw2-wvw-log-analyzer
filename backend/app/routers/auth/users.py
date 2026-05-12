# -*- coding: utf-8 -*-
# 模块功能：用户管理API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-27
# 更新日期?2026-05-12
# 依赖说明：FastAPI, JWT认证

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.constants.roles import ROLES
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.schemas.auth.user import UserCreate, UserProfileResponse, UserResponse, UserUpdate
from app.services.auth.auth_service import (
    get_current_admin,
    get_user_permissions,
    require_super_admin,
)
from app.services.auth.user_service import (
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)
from app.utils.error.exceptions import NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="获取用户列表",
    description="获取系统用户列表，仅超级管理员可访问",
)
async def get_users_route(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="活跃状态过?),
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    result = get_users(db, page=page, page_size=page_size, role=role, is_active=is_active)
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取用户列表成功",
        data={
            "items": [UserResponse.model_validate(u) for u in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        },
    )


@router.get(
    "/profile",
    response_model=ApiResponse,
    summary="获取当前用户资料",
    description="获取当前登录用户的详细信?,
)
async def get_user_profile(current_admin=Depends(get_current_admin)):
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取用户资料成功",
        data={
            "user": UserProfileResponse.model_validate(current_admin).model_dump(),
            "permissions": get_user_permissions(current_admin.role),
        },
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse,
    summary="获取指定用户",
    description="获取指定用户的详细信息，仅超级管理员可访?,
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存?)
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取用户成功", data=UserResponse.model_validate(user)
    )


@router.post(
    "",
    response_model=ApiResponse,
    summary="创建用户",
    description="创建新用户，仅超级管理员可访?,
)
async def create_user_route(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = create_user(db, user_data)
    logger.info(f"管理?{admin.username} 创建了新用户 {user.username}")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="创建用户成功", data=UserResponse.model_validate(user)
    )


@router.put(
    "/{user_id}",
    response_model=ApiResponse,
    summary="更新用户",
    description="更新用户信息，仅超级管理员可访问",
)
async def update_user_route(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = update_user(db, user_id, user_data)
    logger.info(f"管理?{admin.username} 更新了用?{user.username}")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="更新用户成功", data=UserResponse.model_validate(user)
    )


@router.delete(
    "/{user_id}",
    response_model=ApiResponse,
    summary="删除用户",
    description="删除指定用户，仅超级管理员可访问，不能删除自己，预置管理员禁止删?,
)
async def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存?)
    username = user.username
    delete_user(db, user_id, admin.id)
    logger.info(f"管理?{admin.username} 删除了用?{username}")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除用户成功", data=None
    )


@router.get(
    "/roles/list",
    response_model=ApiResponse,
    summary="获取角色列表",
    description="获取系统角色列表",
)
async def get_roles():
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取角色列表成功", data=ROLES
    )
