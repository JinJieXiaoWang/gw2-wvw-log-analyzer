# -*- coding: utf-8 -*-
# 模块功能：AI分析API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-27
# 依赖说明：FastAPI

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.routers.auth.auth import get_current_admin
from app.schemas.system.ai_report import (
    AIReportDetailResponse,
    AIReportListResponse,
    AIReportResponse,
    AISuggestionResponse,
)
from app.schemas.auth.common import ApiResponse
from app.services import ai_service as ai_service
from app.utils.error.exceptions import NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/ai", tags=["AI分析"])


@router.get("/reports", response_model=ApiResponse, summary="获取AI报告列表")
async def get_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    report_type: Optional[str] = Query(None, description="报告类型"),
    target_type: Optional[str] = Query(None, description="目标类型"),
    db: Session = Depends(get_db),
):
    # 功能：获取AI报告列表
    skip = (page - 1) * page_size
    reports, total = ai_service.get_reports(
        db, skip=skip, limit=page_size, report_type=report_type, target_type=target_type
    )

    return ApiResponse(
        success=True,
        message="获取AI报告列表成功",
        data={
            "items": [AIReportResponse.model_validate(r) for r in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get(
    "/reports/{report_id}", response_model=ApiResponse, summary="获取AI报告详情"
)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    # 功能：获取AI报告详情
    report = ai_service.get_report_by_id(db, report_id)
    if not report:
        raise NotFoundException(f"报告ID {report_id} 不存?)

    try:
        parsed_content = json.loads(report.content)
    except json.JSONDecodeError as e:
        logger.warning(f"AI报告内容解析失败: {e}")
        parsed_content = {}
    except Exception as e:
        logger.error(f"获取AI报告详情异常: {e}")
        parsed_content = {}

    return ApiResponse(
        success=True,
        message="获取AI报告成功",
        data={
            **AIReportResponse.model_validate(report).model_dump(),
            "parsed_content": parsed_content,
        },
    )


@router.delete("/reports/{report_id}", response_model=ApiResponse, summary="删除AI报告")
async def delete_report(
    report_id: int, request: Request, db: Session = Depends(get_db)
):
    # 功能：删除AI报告
    get_current_admin(request, db)

    success = ai_service.delete_report(db, report_id)
    if not success:
        raise NotFoundException(f"报告ID {report_id} 不存?)

    return ApiResponse(success=True, message="删除AI报告成功")


@router.post(
    "/analyze/fight/{fight_id}", response_model=ApiResponse, summary="AI分析战斗"
)
async def analyze_fight(fight_id: int, request: Request, db: Session = Depends(get_db)):
    # 功能：AI分析战斗
    admin_id = get_current_admin(request, db)

    result = ai_service.analyze_fight(db, fight_id, created_by=admin_id)

    if "error" in result:
        raise NotFoundException(result["error"])

    return ApiResponse(success=True, message="战斗AI分析完成", data=result)


@router.post(
    "/analyze/build/{build_id}", response_model=ApiResponse, summary="AI分析Build"
)
async def analyze_build(build_id: int, request: Request, db: Session = Depends(get_db)):
    # 功能：AI分析Build
    admin_id = get_current_admin(request, db)

    result = ai_service.analyze_build(db, build_id, created_by=admin_id)

    if "error" in result:
        raise NotFoundException(result["error"])

    return ApiResponse(success=True, message="Build AI分析完成", data=result)


@router.get("/trend", response_model=ApiResponse, summary="获取AI趋势分析")
async def get_trend_analysis(db: Session = Depends(get_db)):
    # 功能：获取AI趋势分析
    result = ai_service.get_trend_analysis(db)

    if "error" in result:
        raise NotFoundException(result["error"])

    return ApiResponse(success=True, message="获取趋势分析成功", data=result)


@router.get("/suggestions", response_model=ApiResponse, summary="获取AI优化建议")
async def get_suggestions(db: Session = Depends(get_db)):
    # 功能：获取AI优化建议
    result = ai_service.get_suggestions(db)

    return ApiResponse(success=True, message="获取优化建议成功", data=result)
