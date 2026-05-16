# 模块功能：管理员数据验证模式
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-28
# 依赖说明：pydantic v2

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminBase(BaseModel):
    # 功能：管理员基础模型
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=3, max_length=50, description="用户名")


class AdminCreate(AdminBase):
    # 功能：创建管理员请求模型
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class AdminLogin(BaseModel):
    # 功能：管理员登录请求模型
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class AdminResponse(BaseModel):
    # 功能：管理员响应模型
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="管理员ID")
    username: str = Field(..., description="用户名")
    role: str = Field("operator", description="用户角色")
    is_active: bool = Field(True, description="是否启用")
    is_predefined: bool = Field(False, description="是否为预置管理员")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")


class LoginResponse(BaseModel):
    # 功能：登录响应模型
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(7200, description="令牌有效期（秒），默认2小时")
    user: AdminResponse = Field(..., description="用户信息")
    permissions: list = Field(
        ["read", "write", "upload", "delete"], description="权限列表"
    )
    menus: list = Field([], description="用户可用菜单树形结构")
