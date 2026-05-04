# -*- coding: utf-8 -*-
# 模块功能：用户数据验证Schema
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：Pydantic v2

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    # 功能：用户基础Schema
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    is_active: bool = Field(True, description="是否激活")
    is_predefined: bool = Field(False, description="是否为预置管理员")
    role: str = Field("operator", description="角色: operator/super_admin/user")


class UserCreate(UserBase):
    # 功能：创建用户请求Schema
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    # 功能：更新用户请求Schema
    model_config = ConfigDict(from_attributes=True)

    email: Optional[str] = Field(None, description="邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")
    role: Optional[str] = Field(None, description="角色")


class PasswordChange(BaseModel):
    # 功能：密码修改请求Schema
    model_config = ConfigDict(from_attributes=True)

    current_password: Optional[str] = Field(None, description="当前密码")
    old_password: Optional[str] = Field(None, description="当前密码（兼容旧字段名）")
    new_password: str = Field(..., min_length=6, description="新密码")
    confirm_password: Optional[str] = Field(None, description="确认新密码")


class UserResponse(UserBase):
    # 功能：用户响应Schema
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_login: Optional[datetime] = None


class UserListResponse(BaseModel):
    # 功能：用户列表响应Schema
    model_config = ConfigDict(from_attributes=True)

    items: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserProfileResponse(BaseModel):
    # 功能：用户资料响应Schema
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    is_predefined: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    stats: Optional[dict] = None


class RoleResponse(BaseModel):
    # 功能：角色响应Schema
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str]


class PermissionResponse(BaseModel):
    # 功能：权限响应Schema
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    resource: str
    action: str
