# 模块功能：菜单管理API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-05-11
# 依赖说明：FastAPI, Depends

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.schemas.system.sys_menu import (
    MenuQueryRequest,
    MenuQueryResponse,
    SysMenuCreate,
    SysMenuResponse,
    SysMenuTreeResponse,
    SysMenuUpdate,
)
from app.services.auth.auth_service import get_current_admin, get_current_user_optional, require_super_admin
from app.services.system.menu_service import MenuService
from app.utils.error.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.get(
    "/tree",
    response_model=ApiResponse,
    summary="获取菜单树形结构",
    description="获取所有菜单的树形结构，支持按父菜单ID筛?,
)
async def get_menu_tree(
    parent_id: int = Query(0, description="父菜单ID，默认为0（顶级菜单）"),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    tree = service.get_menu_tree(parent_id)
    return ApiResponse.success_response(data=tree, message="获取菜单树形结构成功")


@router.get(
    "/public",
    response_model=ApiResponse,
    summary="获取公开菜单",
    description="获取游客可以访问的公开菜单，不需要登?,
)
async def get_public_menus(
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    menus = service.get_public_menus()
    return ApiResponse.success_response(data=menus, message="获取公开菜单成功")


@router.get(
    "/user",
    response_model=ApiResponse,
    summary="获取用户可用菜单",
    description="根据当前登录用户的角色和权限，返回用户有权限访问的菜单树形结构。支持游客模式，游客只能访问公开菜单?,
)
async def get_user_menus(
    current_admin=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    from app.services.auth.auth_service import get_user_permissions
    if not current_admin:
        service = MenuService(db)
        menus = service.get_public_menus()
        return ApiResponse.success_response(data=menus, message="获取公开菜单成功")
    permissions = get_user_permissions(current_admin.role)
    service = MenuService(db)
    menus = service.get_user_menus(current_admin.role, permissions)
    return ApiResponse.success_response(data=menus, message="获取用户菜单成功")


@router.get(
    "/",
    response_model=ApiResponse,
    summary="分页查询菜单列表",
    description="分页查询菜单列表，支持多种筛选条?,
)
async def list_menus(
    query: MenuQueryRequest = Depends(),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    total, items = service.list_menus(
        menu_name=query.menu_name,
        menu_type=query.menu_type,
        status=query.status,
        visible=query.visible,
        parent_id=query.parent_id,
        page=query.page,
        size=query.size,
    )
    menu_list = [SysMenuResponse.from_orm(item) for item in items]
    response = MenuQueryResponse(total=total, items=menu_list)
    return ApiResponse.success_response(data=response.model_dump(), message="查询菜单列表成功")


@router.get(
    "/{menu_id}",
    response_model=ApiResponse,
    summary="获取菜单详情",
    description="根据菜单ID获取菜单详细信息",
)
async def get_menu_detail(
    menu_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    menu = service.get_menu_by_id(menu_id)
    if not menu:
        raise NotFoundException(detail=f"菜单不存在，ID: {menu_id}")
    return ApiResponse.success_response(data=SysMenuResponse.from_orm(menu).model_dump(), message="获取菜单详情成功")


@router.post(
    "/",
    response_model=ApiResponse,
    summary="创建菜单",
    description="创建新的菜单",
)
async def create_menu(
    menu_data: SysMenuCreate,
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    menu_dict = menu_data.model_dump()
    menu_dict["create_by"] = current_admin.username
    try:
        menu = service.create_menu(menu_dict)
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    return ApiResponse.success_response(data=SysMenuResponse.from_orm(menu).model_dump(), message="创建菜单成功")


@router.put(
    "/{menu_id}",
    response_model=ApiResponse,
    summary="更新菜单",
    description="更新指定菜单的信?,
)
async def update_menu(
    menu_id: int,
    menu_data: SysMenuUpdate,
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    menu = service.get_menu_by_id(menu_id)
    if not menu:
        raise NotFoundException(detail=f"菜单不存在，ID: {menu_id}")
    menu_dict = menu_data.model_dump(exclude_unset=True)
    menu_dict["update_by"] = current_admin.username
    try:
        updated_menu = service.update_menu(menu_id, menu_dict)
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    return ApiResponse.success_response(data=SysMenuResponse.from_orm(updated_menu).model_dump(), message="更新菜单成功")


@router.delete(
    "/{menu_id}",
    response_model=ApiResponse,
    summary="删除菜单",
    description="根据菜单ID删除菜单，需要超级管理员权限",
)
async def delete_menu(
    menu_id: int,
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    menu = service.get_menu_by_id(menu_id)
    if not menu:
        raise NotFoundException(detail="菜单不存?)
    success = service.delete_menu(menu_id)
    if not success:
        raise BadRequestException(detail="删除失败：菜单存在子菜单，不允许删除")
    return ApiResponse.success_response(message="删除菜单成功")


@router.post(
    "/batch",
    response_model=ApiResponse,
    summary="批量更新菜单",
    description="批量更新多个菜单的状态、显示、排序等属?,
)
async def batch_update_menus(
    menus_data: List[dict],
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    updated_count = service.batch_update_menus(menus_data, update_by=current_admin.username)
    return ApiResponse.success_response(data={"updated_count": updated_count}, message=f"批量更新成功，共更新 {updated_count} 条记?)


@router.get(
    "/permissions/all",
    response_model=ApiResponse,
    summary="获取所有权限标?,
    description="从菜单表中提取所有权限标?,
)
async def get_all_permissions(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    permissions = service.get_all_permissions()
    return ApiResponse.success_response(data=permissions, message="获取权限列表成功")


@router.post(
    "/init",
    response_model=ApiResponse,
    summary="初始化默认菜?,
    description="初始化系统默认菜单数据（仅在菜单为空时执行）",
)
async def init_default_menus(
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    created_count = service.init_default_menus(init_by=current_admin.username)
    return ApiResponse.success_response(data={"created_count": created_count}, message=f"初始化完成，共创?{created_count} 个菜?)


@router.post(
    "/refresh-cache",
    response_model=ApiResponse,
    summary="刷新菜单缓存",
    description="清除所有菜单相关的缓存，下次访问时重新加载",
)
async def refresh_menu_cache(
    current_admin=Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    service = MenuService(db)
    service._clear_cache()
    return ApiResponse.success_response(message="菜单缓存已刷?)
