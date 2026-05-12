# -*- coding: utf-8 -*-
# 模块功能：字典类型管理API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-29
# 依赖说明：FastAPI, JWT认证

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.schemas.auth.common import ApiResponse
from app.schemas.game_data.dictionary import (
    DictTypeCreate,
    DictTypeResponse,
    DictTypeUpdate,
)
from app.services.auth.auth_service import get_current_admin, require_super_admin
from app.services.system.dictionary_service import DictionaryService
from app.utils.error.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/dictionary/types", tags=["字典类型管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="获取字典类型列表",
    description="获取所有字典类型，支持分页和状态筛?,
)
async def get_dict_types(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选：0-启用?-禁用"),
    keyword: Optional[str] = Query(None, description="关键词筛选：按名称或编码搜索"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    service = DictionaryService(db)
    result = service.get_dict_types(
        status=status, keyword=keyword, page=page, page_size=page_size
    )
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取字典类型成功", data=result
    )


@router.get(
    "/all",
    response_model=ApiResponse,
    summary="获取所有启用的字典类型",
    description="获取所有启用的字典类型，不分页",
)
async def get_all_dict_types(
    db: Session = Depends(get_db), current_admin=Depends(get_current_admin)
):
    service = DictionaryService(db)
    types = service.get_all_dict_types()
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取字典类型成功", data=types
    )


@router.get(
    "/{dict_id}",
    response_model=ApiResponse,
    summary="获取单个字典类型",
    description="获取指定的字典类型详?,
)
async def get_dict_type(
    dict_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    service = DictionaryService(db)
    dict_type = service.get_dict_type_by_id(dict_id)
    if not dict_type:
        raise NotFoundException(f"字典类型不存?)
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.post(
    "",
    response_model=ApiResponse,
    summary="创建字典类型",
    description="创建新的字典类型",
)
async def create_dict_type(
    dict_type_data: DictTypeCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)
    existing = service.get_dict_type_by_code(dict_type_data.dict_type)
    if existing:
        raise BadRequestException(f"字典类型编码已存?)

    dict_type = service.create_dict_type(
        dict_type_data.dict_type,
        dict_type_data.dict_name,
        dict_type_data.remark,
        dict_type_data.sort_order,
        dict_type_data.status,
    )

    logger.info(f"管理?{current_admin.username} 创建了字典类{dict_type.dict_name}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="创建字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.put(
    "/{dict_id}",
    response_model=ApiResponse,
    summary="更新字典类型",
    description="更新字典类型信息",
)
async def update_dict_type(
    dict_id: int,
    dict_type_data: DictTypeUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)
    existing = service.get_dict_type_by_id(dict_id)
    if not existing:
        raise NotFoundException(f"字典类型不存?)

    dict_type = service.update_dict_type(
        dict_id,
        dict_type_data.dict_name,
        dict_type_data.remark,
        dict_type_data.sort_order,
        dict_type_data.status,
    )

    if not dict_type:
        raise NotFoundException(f"字典类型不存?)

    logger.info(f"管理?{current_admin.username} 更新了字典类ID={dict_id}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="更新字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.delete(
    "/{dict_id}",
    response_model=ApiResponse,
    summary="删除字典类型",
    description="删除字典类型及关联的字典?,
)
async def delete_dict_type(
    dict_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)

    try:
        success = service.delete_dict_type(dict_id)
        if not success:
            raise NotFoundException(f"字典类型不存?)

        logger.info(f"管理?{current_admin.username} 删除了字典类ID={dict_id}")

        return ApiResponse.success_response(
            code=HTTP_200_OK, message="删除字典类型成功", data=None
        )
    except ValueError as e:
        raise ForbiddenException(str(e))

