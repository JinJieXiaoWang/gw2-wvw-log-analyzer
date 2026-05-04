# -*- coding: utf-8 -*-
# 模块功能：用户管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI, JWT认证

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.schemas.user import (
    PasswordChange,
    PermissionResponse,
    RoleResponse,
    UserCreate,
    UserListResponse,
    UserProfileResponse,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import (
    delete_admin,
    get_current_admin,
    get_password_hash,
    get_user_permissions,
    require_super_admin,
    verify_password,
)
from app.utils.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="获取用户列表",
    description="获取系统用户列表，仅超级管理员可访问",
)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="活跃状态过滤"),
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    query = db.query(SysUser)

    if role:
        query = query.filter(SysUser.role == role)
    if is_active is not None:
        query = query.filter(SysUser.is_active == is_active)

    total = query.count()
    skip = (page - 1) * page_size
    users = query.offset(skip).limit(page_size).all()

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取用户列表成功",
        data={
            "items": [UserResponse.model_validate(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get(
    "/profile",
    response_model=ApiResponse,
    summary="获取当前用户资料",
    description="获取当前登录用户的详细信息",
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
    description="获取指定用户的详细信息，仅超级管理员可访问",
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise NotFoundException(f"用户ID {user_id} 不存在")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取用户成功", data=UserResponse.model_validate(user)
    )


@router.post(
    "",
    response_model=ApiResponse,
    summary="创建用户",
    description="创建新用户，仅超级管理员可访问",
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    existing = db.query(SysUser).filter(SysUser.username == user_data.username).first()
    if existing:
        raise BadRequestException(f"用户名 {user_data.username} 已存在")

    user = SysUser(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        is_active=user_data.is_active,
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"管理员 {admin.username} 创建了新用户 {user.username}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="创建用户成功", data=UserResponse.model_validate(user)
    )


@router.put(
    "/{user_id}",
    response_model=ApiResponse,
    summary="更新用户",
    description="更新用户信息，仅超级管理员可访问",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise NotFoundException(f"用户ID {user_id} 不存在")

    if user_data.email is not None:
        user.email = user_data.email
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.role is not None:
        user.role = user_data.role

    db.commit()
    db.refresh(user)

    logger.info(f"管理员 {admin.username} 更新了用户 {user.username}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="更新用户成功", data=UserResponse.model_validate(user)
    )


@router.delete(
    "/{user_id}",
    response_model=ApiResponse,
    summary="删除用户",
    description="删除指定用户，仅超级管理员可访问，不能删除自己，预置管理员禁止删除",
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    if admin.id == user_id:
        raise BadRequestException(detail="不能删除自己的账户")

    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存在")

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止删除")

    username = user.username
    success = delete_admin(db, user_id)

    if not success:
        raise BadRequestException(detail="删除用户失败")

    logger.info(f"管理员 {admin.username} 删除了用户 {username}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除用户成功", data=None
    )


@router.post(
    "/change-password",
    response_model=ApiResponse,
    summary="修改密码",
    description="修改当前登录用户的密码",
)
async def change_password(
    password_data: PasswordChange,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    # 兼容 old_password 字段名
    current_password = password_data.current_password or password_data.old_password
    if not current_password:
        raise BadRequestException(detail="请提供当前密码")

    # confirm_password 可选验证
    if password_data.confirm_password is not None and password_data.new_password != password_data.confirm_password:
        raise BadRequestException(detail="两次输入的密码不一致")

    if len(password_data.new_password) < 6:
        raise BadRequestException(detail="新密码长度至少6位")

    if not verify_password(current_password, current_admin.password_hash):
        raise BadRequestException(detail="当前密码错误")

    current_admin.password_hash = get_password_hash(password_data.new_password)
    current_admin.token_version = (current_admin.token_version or 0) + 1
    db.commit()

    logger.info(f"用户 {current_admin.username} 修改了密码")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="密码修改成功", data=None
    )


@router.post(
    "/{user_id}/reset-password",
    response_model=ApiResponse,
    summary="重置用户密码",
    description="重置指定用户的密码，仅超级管理员可访问",
)
async def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存在")

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止重置密码")

    # 安全改进：生成随机临时密码，避免硬编码
    import secrets

    new_password = secrets.token_urlsafe(12)
    user.password_hash = get_password_hash(new_password)
    user.token_version = (user.token_version or 0) + 1
    db.commit()

    logger.info(f"管理员 {admin.username} 重置了用户 {user.username} 的密码")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message=f"密码重置成功，新密码为: {new_password}",
        data={"temp_password": new_password},
    )


@router.post(
    "/{user_id}/toggle-active",
    response_model=ApiResponse,
    summary="切换用户活跃状态",
    description="切换指定用户的活跃状态，仅超级管理员可访问，不能修改自己，预置管理员禁止禁用",
)
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    if admin.id == user_id:
        raise BadRequestException(detail="不能修改自己的活跃状态")

    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存在")

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止禁用")

    user.is_active = not user.is_active
    db.commit()

    status = "激活" if user.is_active else "禁用"
    logger.info(f"管理员 {admin.username} {status}了用户 {user.username}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message=f"用户已{status}", data={"is_active": user.is_active}
    )


@router.get(
    "/roles/list",
    response_model=ApiResponse,
    summary="获取角色列表",
    description="获取系统角色列表",
)
async def get_roles():
    roles = [
        {
            "id": 1,
            "name": "super_admin",
            "description": "超级管理员",
            "permissions": ["read", "write", "upload", "delete", "manage_users"],
        },
        {
            "id": 2,
            "name": "operator",
            "description": "操作员",
            "permissions": ["read", "write", "upload", "delete"],
        },
        {"id": 3, "name": "user", "description": "普通用户", "permissions": ["read"]},
        {"id": 4, "name": "guest", "description": "游客", "permissions": ["read"]},
    ]

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取角色列表成功", data=roles
    )
