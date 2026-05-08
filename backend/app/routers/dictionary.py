# -*- coding: utf-8 -*-
# 模块功能：字典管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-29
# 依赖说明：FastAPI, JWT认证

import json
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.schemas.dictionary import (
    DictDataCreate,
    DictDataResponse,
    DictDataUpdate,
    DictOption,
    DictTypeCreate,
    DictTypeResponse,
    DictTypeUpdate,
)
from app.services.auth_service import get_current_admin, require_super_admin
from app.services.system.dictionary_service import DictionaryService
from app.utils.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/dictionary", tags=["字典管理"])


# ============ 字典类型管理 ============


@router.get(
    "/types",
    response_model=ApiResponse,
    summary="获取字典类型列表",
    description="获取所有字典类型，支持分页和状态筛选",
)
async def get_dict_types(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选：0-启用，1-禁用"),
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
    "/types/all",
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
    "/types/{dict_id}",
    response_model=ApiResponse,
    summary="获取单个字典类型",
    description="获取指定的字典类型详情",
)
async def get_dict_type(
    dict_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    service = DictionaryService(db)
    dict_type = service.get_dict_type_by_id(dict_id)
    if not dict_type:
        raise NotFoundException(f"字典类型不存在")
    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.post(
    "/types",
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

    # 检查是否已存在
    existing = service.get_dict_type_by_code(dict_type_data.dict_type)
    if existing:
        raise BadRequestException(f"字典类型编码已存在")

    dict_type = service.create_dict_type(
        dict_type_data.dict_type,
        dict_type_data.dict_name,
        dict_type_data.remark,
        dict_type_data.sort_order,
        dict_type_data.status,
    )

    logger.info(f"管理员 {current_admin.username} 创建了字典类型 {dict_type.dict_name}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="创建字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.put(
    "/types/{dict_id}",
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

    # 检查字典类型是否存在
    existing = service.get_dict_type_by_id(dict_id)
    if not existing:
        raise NotFoundException(f"字典类型不存在")

    dict_type = service.update_dict_type(
        dict_id,
        dict_type_data.dict_name,
        dict_type_data.remark,
        dict_type_data.sort_order,
        dict_type_data.status,
    )

    if not dict_type:
        raise NotFoundException(f"字典类型不存在")

    logger.info(f"管理员 {current_admin.username} 更新了字典类型 ID={dict_id}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="更新字典类型成功",
        data=DictTypeResponse.model_validate(dict_type),
    )


@router.delete(
    "/types/{dict_id}",
    response_model=ApiResponse,
    summary="删除字典类型",
    description="删除字典类型及关联的字典项",
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
            raise NotFoundException(f"字典类型不存在")

        logger.info(f"管理员 {current_admin.username} 删除了字典类型 ID={dict_id}")

        return ApiResponse.success_response(
            code=HTTP_200_OK, message="删除字典类型成功", data=None
        )
    except ValueError as e:
        # 预置字典类型不允许删除
        raise ForbiddenException(str(e))


# ============ 字典数据管理 ============


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
    summary="获取单个字典项",
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

    # 检查字典类型是否存在
    dict_type_obj = service.get_dict_type_by_code(dict_data_data.dict_type)
    if not dict_type_obj:
        raise NotFoundException(f"字典类型 {dict_data_data.dict_type} 不存在")

    # 检查值是否已存在
    existing = service.get_dict_data_by_type(dict_data_data.dict_type)
    for item in existing.get("items", []):
        if item.get("dict_value") == dict_data_data.dict_value:
            raise BadRequestException(f"字典项值 {dict_data_data.dict_value} 已存在")

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

    logger.info(f"管理员 {current_admin.username} 创建了字典项 {dict_data.dict_label}")

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="创建字典项成功",
        data=DictDataResponse.model_validate(dict_data),
    )


@router.put(
    "/data/{dict_code}",
    response_model=ApiResponse,
    summary="更新字典项",
    description="更新字典项信息",
)
async def update_dict_data(
    dict_code: int,
    dict_data_data: DictDataUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_super_admin),
):
    service = DictionaryService(db)

    # 检查字典项是否存在
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

    logger.info(f"管理员 {current_admin.username} 更新了字典项 ID={dict_code}")

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

    # 检查字典项是否存在
    existing = service.get_dict_data_by_id(dict_code)
    if not existing:
        raise NotFoundException(f"字典项不存在")

    success = service.delete_dict_data(dict_code)
    if not success:
        raise NotFoundException(f"字典项不存在")

    logger.info(f"管理员 {current_admin.username} 删除了字典项 ID={dict_code}")

    return ApiResponse.success_response(
        code=HTTP_200_OK, message="删除字典项成功", data=None
    )


@router.get(
    "/cascade/profession-specs",
    response_model=ApiResponse,
    summary="获取职业-精英特长级联数据",
    description="返回职业与精英特长的级联结构，数据来源于字典表和 professions.json",
)
async def get_profession_specs_cascade(db: Session = Depends(get_db)):
    """获取职业-精英特长级联数据（公开接口）

    返回结构包含每个职业及其下属的精英特长列表，
    数据合并自 sys_dict_data 字典表和 professions.json。
    """
    service = DictionaryService(db)

    # 从字典表获取职业和精英特长数据
    profession_options = service.get_dict_options("profession")
    spec_options = service.get_dict_options("specialization")

    # 构建字典值到标签/颜色的映射
    prof_map = {p["value"]: p for p in profession_options}
    spec_map = {s["value"]: s for s in spec_options}

    # 从 professions.json 读取结构关系
    professions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "professions.json"
    )

    result = []
    if os.path.exists(professions_file):
        with open(professions_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        base_professions = data.get("base_professions", {})
        elite_specs = data.get("elite_specs", {})

        for prof_key, prof_info in base_professions.items():
            prof_dict = prof_map.get(prof_key, {})
            spec_list = []

            for spec_name in prof_info.get("elite_specs", []):
                spec_dict = spec_map.get(spec_name, {})
                spec_info = elite_specs.get(spec_name, {})
                spec_list.append({
                    "value": spec_name,
                    "label": spec_dict.get("label") or spec_info.get("name_cn", spec_name),
                    "color": spec_dict.get("css_class", "#6b7280"),
                    "default_role": spec_info.get("default_role", "dps"),
                })

            result.append({
                "value": prof_key,
                "label": prof_dict.get("label") or prof_info.get("name_cn", prof_key),
                "color": prof_dict.get("css_class", "#6b7280"),
                "default_role": prof_info.get("default_role", "dps"),
                "elite_specs": spec_list,
            })

    return ApiResponse.success_response(
        code=HTTP_200_OK,
        message="获取职业级联数据成功",
        data={"professions": result, "count": len(result)},
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
    from app.utils.dict_utils import load_all_dictionaries

    load_all_dictionaries(db)
    logger.info(f"管理员 {current_admin.username} 刷新了字典缓存")
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
    from app.database.dict_init import DictionaryDataInitializer

    initializer = DictionaryDataInitializer(db)
    result = initializer.init_all_dictionaries()
    logger.info(f"管理员 {current_admin.username} 初始化了字典数据")
    return ApiResponse.success_response(
        code=HTTP_200_OK, message="初始化字典数据成功", data=result
    )
