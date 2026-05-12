# -*- coding: utf-8 -*-
# 模块功能：用户密码与状态管理API路由
# 作者：系统
# 创建日期?2026-05-12

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.schemas.auth.user import PasswordChange
from app.services.auth.auth_service import get_current_admin, require_super_admin
from app.services.auth.user_service import (
    change_user_password,
    get_user_by_id,
    reset_user_password,
    toggle_user_active,
)
from app.utils.error.exceptions import NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["用户管理"])


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
    current_password = password_data.current_password or password_data.old_password
    change_user_password(
        db=db,
        user_id=current_admin.id,
        old_password=current_password,
        new_password=password_data.new_password,
        confirm_password=password_data.confirm_password,
    )
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
async def reset_user_password_route(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存在")
    username = user.username
    new_password = reset_user_password(db, user_id)
    logger.warning(
        f"管理?{admin.username} 重置了用?{username} 的密码，"
        f"临时密码: {new_password}"
    )
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="密码重置成功，临时密码已输出到服务器日志",
        data=None,
    )


@router.post(
    "/{user_id}/toggle-active",
    response_model=ApiResponse,
    summary="切换用户活跃状态",
    description="切换指定用户的活跃状态，仅超级管理员可访问",
)
async def toggle_user_active_route(
    user_id: int,
    db: Session = Depends(get_db),
    admin: SysUser = Depends(require_super_admin),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存在")
    username = user.username
    is_active = toggle_user_active(db, user_id, admin.id)
    status = "激活" if is_active else "禁用"
    logger.info(f"管理?{admin.username} {status}了用?{username}")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message=f"用户已{status}", data={"is_active": is_active}
    )
