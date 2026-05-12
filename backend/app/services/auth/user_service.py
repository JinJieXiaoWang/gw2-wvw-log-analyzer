# -*- coding: utf-8 -*-
# 模块功能：用户业务逻辑服务
# 作者：系统
# 创建日期?2026-05-12

import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app.models.auth.sys_user import SysUser
from app.schemas.auth.user import UserCreate, UserUpdate
from app.services.auth.auth_service import delete_admin, get_password_hash, verify_password
from app.utils.error.exceptions import BadRequestException, NotFoundException


def get_user_by_id(db: Session, user_id: int) -> Optional[SysUser]:
    return db.query(SysUser).filter(SysUser.id == user_id).first()


def get_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> dict:
    query = db.query(SysUser)

    if role:
        query = query.filter(SysUser.role == role)
    if is_active is not None:
        query = query.filter(SysUser.is_active == is_active)

    total = query.count()
    skip = (page - 1) * page_size
    users = query.offset(skip).limit(page_size).all()

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def create_user(db: Session, user_data: UserCreate) -> SysUser:
    existing = db.query(SysUser).filter(SysUser.username == user_data.username).first()
    if existing:
        raise BadRequestException(f"用户?{user_data.username} 已存?)

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
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> SysUser:
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"用户ID {user_id} 不存?)

    if user_data.email is not None:
        user.email = user_data.email
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.role is not None:
        user.role = user_data.role

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, admin_id: int) -> bool:
    if admin_id == user_id:
        raise BadRequestException(detail="不能删除自己的账?)

    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存?)

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止删?)

    success = delete_admin(db, user_id)
    if not success:
        raise BadRequestException(detail="删除用户失败")
    return True


def change_user_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str,
    confirm_password: Optional[str] = None,
) -> bool:
    if not old_password:
        raise BadRequestException(detail="请提供当前密?)

    if confirm_password is not None and new_password != confirm_password:
        raise BadRequestException(detail="两次输入的密码不一?)

    if len(new_password) < 6:
        raise BadRequestException(detail="新密码长度至??)

    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail="用户不存?)

    if not verify_password(old_password, user.password_hash):
        raise BadRequestException(detail="当前密码错误")

    user.password_hash = get_password_hash(new_password)
    user.token_version = (user.token_version or 0) + 1
    db.commit()
    return True


def reset_user_password(db: Session, user_id: int) -> str:
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存?)

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止重置密?)

    new_password = secrets.token_urlsafe(12)
    user.password_hash = get_password_hash(new_password)
    user.token_version = (user.token_version or 0) + 1
    db.commit()
    return new_password


def toggle_user_active(db: Session, user_id: int, admin_id: int) -> bool:
    if admin_id == user_id:
        raise BadRequestException(detail="不能修改自己的活跃状?)

    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail=f"用户ID {user_id} 不存?)

    if user.is_predefined:
        raise BadRequestException(detail="预置管理员账号禁止禁?)

    user.is_active = not user.is_active
    db.commit()
    return user.is_active
