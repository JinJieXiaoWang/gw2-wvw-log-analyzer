# -*- coding: utf-8 -*-
# 模块功能：字典数据管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：FastAPI, JWT认证

import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.schemas.auth.common import ApiResponse
from app.schemas.game.dictionary import (
    DictDataCreate,
    DictDataResponse,
    DictDataUpdate,
)
from app.services.auth.auth_service import get_current_admin, require_super_admin
from app.services.game.profession_service import ProfessionService
from app.services.system.dictionary_service import DictionaryService
from app.utils.error.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/dictionary", tags=["字典数据管理"])


@router.get(
    "/data",
    response_model=ApiResponse,
    summary="获取字典项列表",
    description="获取字典项列表，支持按字典类型筛选",
)
async def get_dict_data(
    dict_type: str = Query(..., description="字典类型编码"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    service = DictionaryService(db)
    result = service.get_dict_data_by_type(
        dict_type, status=status, page=page, page_size=page_size
    )
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取字典项成功", data=result
    )


@router.get(
    "/data/{dict_code}",
    response_model=ApiResponse,
    summary="获取单个字典项详情",
    description="获取指定的字典项详情",
)
async def get_dict_data_detail(
    dict_code: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    service = DictionaryService(db)
    dict_data = service.get_dict_data_by_id(dict_code)
    if not dict_data:
        raise NotFoundException(f"字典项不存在")
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取字典项成功",
        data=DictDataResponse.model_validate(dict_data),
    )


@router.get(
    "/options/{dict_type}",
    response_model=ApiResponse,
    summary="获取字典选项",
    description="获取指定字典类型的下拉选项（公开接口）",
)
async def get_dict_options(dict_type: str, db: Session = Depends(get_db)):
    service = DictionaryService(db)
    options = service.get_dict_options(dict_type)
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="获取字典选项成功", data=options
    )


@router.post(
    "/data",
    response_model=ApiResponse,
    summary="创建字典项",
    description="创建新的字典项",
)
async def create_dict_data(
    dict_data_data: DictDataCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)
    dict_type_obj = service.get_dict_type_by_code(dict_data_data.dict_type)
    if not dict_type_obj:
        raise NotFoundException(f"字典类型 {dict_data_data.dict_type} 不存在")

    if service.check_dict_value_exists(dict_data_data.dict_type, dict_data_data.dict_value):
        raise BadRequestException(f"字典项 {dict_data_data.dict_value} 已存在")

    dict_data = service.create_dict_data(
        dict_type=dict_data_data.dict_type,
        dict_label=dict_data_data.dict_label,
        dict_value=dict_data_data.dict_value,
        dict_sort=dict_data_data.dict_sort,
        data_type=dict_data_data.data_type,
        css_class=dict_data_data.css_class,
        list_class=dict_data_data.list_class,
        is_default=dict_data_data.is_default,
        status=dict_data_data.status,
        remark=dict_data_data.remark,
    )

    logger.info(f"管理?{current_admin.username} 创建了字典项 {dict_data.dict_label}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="创建字典项成功",
        data=DictDataResponse.model_validate(dict_data),
    )


@router.put(
    "/data/{dict_code}",
    response_model=ApiResponse,
    summary="更新字典项",
    description="更新指定的字典项",
)
async def update_dict_data(
    dict_code: int,
    dict_data_data: DictDataUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)
    existing = service.get_dict_data_by_id(dict_code)
    if not existing:
        raise NotFoundException(f"字典项不存在")

    dict_data = service.update_dict_data(
        dict_code=dict_code,
        dict_label=dict_data_data.dict_label,
        dict_value=dict_data_data.dict_value,
        dict_sort=dict_data_data.dict_sort,
        data_type=dict_data_data.data_type,
        css_class=dict_data_data.css_class,
        list_class=dict_data_data.list_class,
        is_default=dict_data_data.is_default,
        status=dict_data_data.status,
        remark=dict_data_data.remark,
    )

    if not dict_data:
        raise NotFoundException(f"字典项不存在")

    logger.info(f"管理?{current_admin.username} 更新了字典项 ID={dict_code}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="更新字典项成功",
        data=DictDataResponse.model_validate(dict_data),
    )


@router.delete(
    "/data/{dict_code}",
    response_model=ApiResponse,
    summary="删除字典项",
    description="删除指定的字典项",
)
async def delete_dict_data(
    dict_code: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)
    existing = service.get_dict_data_by_id(dict_code)
    if not existing:
        raise NotFoundException(f"字典项不存在")

    success = service.delete_dict_data(dict_code)
    if not success:
        raise NotFoundException(f"字典项不存在")

    logger.info(f"管理?{current_admin.username} 删除了字典项 ID={dict_code}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除字典项成功", data=None
    )


@router.get(
    "/cascade/profession-specs",
    response_model=ApiResponse,
    summary="获取职业-精英特长级联数据",
    description="返回职业与精英特长的级联结构（从 profession 专用表读取，不从字典表获取）",
)
async def get_profession_specs_cascade(db: Session = Depends(get_db)):
    service = ProfessionService(db)
    result = service.get_profession_spec_cascade()
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取职业级联数据成功",
        data=result,
    )


@router.post(
    "/reload-cache",
    response_model=ApiResponse,
    summary="刷新字典缓存",
    description="手动刷新所有字典数据到内存缓存",
)
async def reload_dict_cache(
    db: Session = Depends(get_db), current_admin=Depends(get_current_admin)
):
    from app.utils.db.dict_utils import load_all_dictionaries
    load_all_dictionaries(db)
    logger.info(f"管理?{current_admin.username} 刷新了字典缓存")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="刷新字典缓存成功", data=None
    )


@router.post(
    "/init",
    response_model=ApiResponse,
    summary="初始化字典数据",
    description="初始化系统预置字典数据",
)
async def init_dictionary_data(
    db: Session = Depends(get_db), current_admin=Depends(require_super_admin)
):
    from app.data.init_all import init_dictionary_data
    result = init_dictionary_data(db)
    logger.info(f"管理?{current_admin.username} 初始化了字典数据")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="初始化字典数据成功", data=result
    )
