# -*- coding: utf-8 -*-
# 模块功能：BDCode解析API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.schemas.bdcode import (
    BDCodeBatchItem,
    BDCodeBatchRequest,
    BDCodeBatchResponse,
    BDCodeParseRequest,
    BDCodeParseResponse,
    BDCodeStatsResponse,
    BDCodeValidationRequest,
    BDCodeValidationResponse,
)
from app.services.game_data.bdcode_service import get_bdcode_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/bdcode", tags=["BDCode解析"])


# ==================== BDCode解析 ====================
@router.post(
    "/parse",
    summary="解析单个BDCode",
    response_model=BDCodeParseResponse,
    description="解析单个BDCode获取完整Build信息",
)
async def parse_bdcode(request: BDCodeParseRequest):
    """
    解析BDCode获取完整Build信息

    - **bd_code**: BDCode字符串，格式 [&...]
    - **include_icons**: 是否包含图标URL（可选，默认true）
    """
    logger.info(f"解析BDCode: {request.bd_code[:30]}...")

    try:
        service = get_bdcode_service()
        result = service.parse_bdcode(request.bd_code, request.include_icons)
        return BDCodeParseResponse(**result)

    except Exception as e:
        logger.error(f"BDCode解析失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get(
    "/parse/{bd_code:path}",
    summary="通过URL解析BDCode",
    response_model=BDCodeParseResponse,
)
async def parse_bdcode_url(bd_code: str, include_icons: bool = True):
    """
    通过URL参数解析BDCode
    """
    logger.info(f"URL解析BDCode: {bd_code[:30]}...")

    try:
        service = get_bdcode_service()
        result = service.parse_bdcode(bd_code, include_icons)
        return BDCodeParseResponse(**result)

    except Exception as e:
        logger.error(f"BDCode解析失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


# ==================== BDCode验证 ====================
@router.post(
    "/validate", summary="验证BDCode格式", response_model=BDCodeValidationResponse
)
async def validate_bdcode(request: BDCodeValidationRequest):
    """
    验证BDCode格式是否正确
    """
    logger.info(f"验证BDCode: {request.bd_code[:30]}...")

    try:
        service = get_bdcode_service()
        validation = service.validate_bdcode(request.bd_code)
        return BDCodeValidationResponse(**validation)

    except Exception as e:
        logger.error(f"BDCode验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


# ==================== 批量解析 ====================
@router.post("/batch", summary="批量解析BDCode", response_model=BDCodeBatchResponse)
async def parse_batch(request: BDCodeBatchRequest):
    """
    批量解析BDCode（最多50个）
    """
    logger.info(f"批量解析BDCode: {len(request.bd_codes)}个")

    if len(request.bd_codes) > 50:
        raise HTTPException(status_code=400, detail="单次最多解析50个BDCode")

    try:
        service = get_bdcode_service()
        results = []
        success_count = 0
        error_count = 0

        for bd_code in request.bd_codes:
            result = service.parse_bdcode(bd_code, request.include_icons)

            item = BDCodeBatchItem(
                bd_code=bd_code,
                success=result["success"],
                error=result.get("error"),
                data=result.get("data"),
            )
            results.append(item)

            if result["success"]:
                success_count += 1
            else:
                error_count += 1

        return BDCodeBatchResponse(
            total_count=len(request.bd_codes),
            success_count=success_count,
            error_count=error_count,
            results=results,
        )

    except Exception as e:
        logger.error(f"批量解析异常: {e}")
        raise HTTPException(status_code=500, detail=f"批量解析失败: {str(e)}")


# ==================== 统计信息 ====================
@router.get(
    "/stats", summary="获取BDCode解析服务统计信息", response_model=BDCodeStatsResponse
)
async def get_bdcode_stats():
    """
    获取BDCode解析服务的统计信息（用于监控和诊断）
    """
    try:
        service = get_bdcode_service()

        loader = service._loader
        loader._load_all_data()

        from app.services.game_data.game_data_service import get_game_data_service

        gds = get_game_data_service()
        cache_stats = gds.get_cache_stats()

        return BDCodeStatsResponse(
            skill_palettes_count=len(loader._palette_map) if loader._palette_map else 0,
            skills_count=len(loader._skill_idx) if loader._skill_idx else 0,
            specializations_count=len(loader._spec_idx) if loader._spec_idx else 0,
            traits_count=len(loader._trait_idx) if loader._trait_idx else 0,
            cache_stats=cache_stats,
        )

    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ==================== 健康检查 ====================
@router.get("/health", summary="BDCode解析服务健康检查")
async def bdcode_health():
    """
    检测BDCode解析服务是否正常工作
    """
    try:
        service = get_bdcode_service()
        test_bd = "[&DQg1KTIlIjbBEigPQAGBAIEAQAHxEnUBAxOVAAAAAAAAAAAAAAAAAAAAAAA=]"
        validation = service.validate_bdcode(test_bd)

        return {
            "status": "healthy",
            "service": "bdcode_parser",
            "test_passed": validation["is_valid"],
            "message": "BDCode解析服务运行正常",
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {"status": "unhealthy", "service": "bdcode_parser", "error": str(e)}
