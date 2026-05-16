# 模块功能：菜单管理数据验证模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-11
# 依赖说明：pydantic v2

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SysMenuBase(BaseModel):
    """菜单基础模型"""
    model_config = ConfigDict(from_attributes=True)
    
    menu_name: str = Field(..., min_length=1, max_length=50, description="菜单名称")
    parent_id: int = Field(0, ge=0, description="父菜单ID")
    order_num: int = Field(0, ge=0, description="显示顺序")
    path: str = Field("", max_length=200, description="路由地址")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    query: Optional[str] = Field(None, max_length=255, description="路由参数")
    route_name: str = Field("", max_length=50, description="路由名称")
    is_frame: int = Field(1, ge=0, le=1, description="是否为外链（0是 1否）")
    is_cache: int = Field(0, ge=0, le=1, description="是否缓存（0缓存 1不缓存）")
    menu_type: str = Field("", max_length=1, description="菜单类型（M目录 C菜单 F按钮）")
    visible: str = Field("0", max_length=1, description="菜单状态（0显示 1隐藏）")
    status: str = Field("0", max_length=1, description="菜单状态（0正常 1停用）")
    perms: Optional[str] = Field(None, max_length=100, description="权限标识")
    icon: str = Field("#", max_length=100, description="菜单图标")
    remark: str = Field("", max_length=500, description="备注")


class SysMenuCreate(SysMenuBase):
    """创建菜单请求模型"""
    create_by: str = Field("", max_length=64, description="创建人")


class SysMenuUpdate(SysMenuBase):
    """更新菜单请求模型"""
    update_by: str = Field("", max_length=64, description="更新人")
    menu_name: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单名称")


class SysMenuResponse(BaseModel):
    """菜单响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    menu_id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    parent_id: int = Field(..., description="父菜单ID")
    order_num: int = Field(..., description="显示顺序")
    path: str = Field(..., description="路由地址")
    component: Optional[str] = Field(None, description="组件路径")
    query: Optional[str] = Field(None, description="路由参数")
    route_name: str = Field(..., description="路由名称")
    is_frame: int = Field(..., description="是否为外链")
    is_cache: int = Field(..., description="是否缓存")
    menu_type: str = Field(..., description="菜单类型")
    visible: str = Field(..., description="显示状态")
    status: str = Field(..., description="菜单状态")
    perms: Optional[str] = Field(None, description="权限标识")
    icon: str = Field(..., description="菜单图标")
    create_by: str = Field(..., description="创建人")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_by: str = Field(..., description="更新人")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    remark: str = Field(..., description="备注")


class SysMenuTreeResponse(SysMenuResponse):
    """菜单树形响应模型"""
    children: Optional[List["SysMenuTreeResponse"]] = Field([], description="子菜单列表")


class MenuQueryRequest(BaseModel):
    """菜单查询请求模型"""
    menu_name: Optional[str] = Field(None, description="菜单名称（模糊搜索）")
    menu_type: Optional[str] = Field(None, description="菜单类型")
    status: Optional[str] = Field(None, description="菜单状态")
    visible: Optional[str] = Field(None, description="显示状态")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class MenuQueryResponse(BaseModel):
    """菜单查询响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[SysMenuResponse] = Field(..., description="菜单列表")


class MenuPermissionCheck(BaseModel):
    """菜单权限检查请求模型"""
    menu_id: int = Field(..., description="菜单ID")
    required_perms: Optional[str] = Field(None, description="需要的权限标识")


class MenuPermissionResponse(BaseModel):
    """菜单权限检查响应模型"""
    has_access: bool = Field(..., description="是否有权限访问")
    menu_id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    missing_perms: List[str] = Field([], description="缺失的权限标识")


# 更新前向引用
SysMenuTreeResponse.model_rebuild()