# -*- coding: utf-8 -*-
# 模块功能：Build图书馆API路由
# 依赖说明：FastAPI

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.sys_user import SysUser
from app.schemas.build import BuildCreate, BuildListResponse, BuildResponse, BuildUpdate
from app.schemas.common import ApiResponse
from app.services.auth_service import get_current_admin, require_permission
from app.services.build_service import (
    create_build,
    delete_build,
    get_build_by_id,
    list_builds,
    update_build,
)
from app.utils.exceptions import NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/builds", tags=["Build图书馆"])


@router.get("", response_model=ApiResponse, summary="获取Build列表")
async def get_builds(
    profession: Optional[str] = Query(None, description="职业过滤"),
    role: Optional[str] = Query(None, description="角色过滤: dps/support"),
    sub_role: Optional[str] = Query(None, description="子角色过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("updated", description="排序: updated/updated_asc/profession/name"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """获取Build列表（支持分页、过滤、搜索）"""
    result = list_builds(
        db,
        profession=profession,
        role=role,
        sub_role=sub_role,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success_response(
        message="获取Build列表成功",
        data={
            "items": [BuildResponse.model_validate(b) for b in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
        },
    )


@router.get("/{build_id}", response_model=ApiResponse, summary="获取单个Build")
async def get_build(build_id: int, db: Session = Depends(get_db)):
    """根据ID获取Build详情"""
    build = get_build_by_id(db, build_id)
    if not build:
        raise NotFoundException(f"Build ID {build_id} 不存在")
    return ApiResponse.success_response(
        message="获取Build成功",
        data=BuildResponse.model_validate(build).model_dump(),
    )


@router.post(
    "",
    response_model=ApiResponse,
    summary="创建Build",
    dependencies=[Depends(require_permission("write"))],
)
async def create_build_endpoint(
    build_data: BuildCreate,
    db: Session = Depends(get_db),
):
    """创建新Build（需要write权限）"""
    build = create_build(db, build_data.model_dump())
    return ApiResponse.success_response(
        message="创建Build成功",
        data=BuildResponse.model_validate(build).model_dump(),
    )


@router.put(
    "/{build_id}",
    response_model=ApiResponse,
    summary="更新Build",
    dependencies=[Depends(require_permission("write"))],
)
async def update_build_endpoint(
    build_id: int,
    build_data: BuildUpdate,
    db: Session = Depends(get_db),
):
    """更新Build（需要write权限）"""
    build = get_build_by_id(db, build_id)
    if not build:
        raise NotFoundException(f"Build ID {build_id} 不存在")
    build = update_build(db, build, build_data.model_dump(exclude_unset=True))
    return ApiResponse.success_response(
        message="更新Build成功",
        data=BuildResponse.model_validate(build).model_dump(),
    )


@router.delete(
    "/{build_id}",
    response_model=ApiResponse,
    summary="删除Build",
    dependencies=[Depends(require_permission("delete"))],
)
async def delete_build_endpoint(
    build_id: int,
    db: Session = Depends(get_db),
):
    """删除Build（需要delete权限）"""
    build = get_build_by_id(db, build_id)
    if not build:
        raise NotFoundException(f"Build ID {build_id} 不存在")
    delete_build(db, build)
    return ApiResponse.success_response(message="删除Build成功", data=None)
