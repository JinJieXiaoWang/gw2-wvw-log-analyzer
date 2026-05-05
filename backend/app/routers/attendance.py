# -*- coding: utf-8 -*-
# 模块功能：出勤统计API路由 v2.0
# 作者：系统
# 创建日期：2026-05-04
# 说明：
#   - members 表仅保存 account_name，角色信息去 account_characters 查
#   - 所有统计基于 fight_stats + fights 表聚合
#   - 支持多维度筛选、排序、分页

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.services.zevtc import attendance_service
from app.utils.logger import logger

router = APIRouter(prefix="/attendance", tags=["出勤统计"])


# =====================================================================
# 账号维度出勤统计
# =====================================================================

@router.get("/accounts", response_model=ApiResponse, summary="获取账号出勤列表")
async def get_accounts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="搜索账号或角色名"),
    server_name: Optional[str] = Query(None, description="服务器筛选"),
    map_name: Optional[str] = Query(None, description="地图筛选"),
    profession: Optional[str] = Query(None, description="职业筛选"),
    sort_by: str = Query("attendance_count", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 (asc/desc)"),
    db: Session = Depends(get_db),
):
    """获取所有出勤账号的聚合统计列表

    返回每个账号的：角色数、出勤次数、总时长、总伤害、总治疗、
    击杀、死亡、K/D、平均评分、最后出勤时间
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            if end_date
            else None
        )

        items, total = attendance_service.get_account_attendance_list(
            db,
            page=page,
            page_size=page_size,
            start_date=start_dt,
            end_date=end_dt,
            search=search,
            server_name=server_name,
            map_name=map_name,
            profession=profession,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
        )

    except Exception as e:
        logger.error(f"获取账号出勤列表失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"查询失败: {str(e)}", code=500)


@router.get(
    "/accounts/{account_name}",
    response_model=ApiResponse,
    summary="获取账号出勤详情",
)
async def get_account_detail(
    account_name: str = Path(..., description="账号名"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """获取指定账号的出勤详情

    包含：
        - 账号汇总统计
        - 该账号下所有角色的出勤统计
        - 最近 20 条战斗记录（含 Buff 覆盖率）
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            if end_date
            else None
        )

        data = attendance_service.get_account_detail(
            db, account_name, start_date=start_dt, end_date=end_dt
        )

        if not data:
            return ApiResponse(
                success=False,
                message=f"账号 {account_name} 无出勤记录",
                code=404,
            )

        return ApiResponse(success=True, message="获取成功", data=data)

    except Exception as e:
        logger.error(f"获取账号详情失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"查询失败: {str(e)}", code=500)


@router.get(
    "/accounts/{account_name}/score-breakdown",
    response_model=ApiResponse,
    summary="获取账号评分维度明细",
)
async def get_account_score_breakdown(
    account_name: str = Path(..., description="账号名"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """获取指定账号的评分维度明细（点击评分分数时展示）

    返回该账号在统计周期内各评分维度的平均得分、权重及加权贡献值。
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            if end_date
            else None
        )

        data = attendance_service.get_account_score_breakdown(
            db, account_name, start_date=start_dt, end_date=end_dt
        )

        if not data:
            return ApiResponse(
                success=False,
                message=f"账号 {account_name} 无评分记录",
                code=404,
            )

        return ApiResponse(success=True, message="获取成功", data=data)

    except Exception as e:
        logger.error(f"获取评分维度明细失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"查询失败: {str(e)}", code=500)


@router.get(
    "/accounts/{account_name}/characters/{character_name}",
    response_model=ApiResponse,
    summary="获取角色战斗记录",
)
async def get_character_detail(
    account_name: str = Path(..., description="账号名"),
    character_name: str = Path(..., description="角色名"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """获取指定角色的详细战斗记录

    包含每次战斗的：伤害、DPS、治疗、击杀/死亡、Buff 覆盖率、AI 评分等
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            if end_date
            else None
        )

        items, total, summary = attendance_service.get_character_detail(
            db,
            account_name,
            character_name,
            page=page,
            page_size=page_size,
            start_date=start_dt,
            end_date=end_dt,
        )

        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "account": account_name,
                "character_name": character_name,
                "summary": summary,
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
        )

    except Exception as e:
        logger.error(f"获取角色详情失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"查询失败: {str(e)}", code=500)


# =====================================================================
# 筛选选项（用于前端下拉框）
# =====================================================================

@router.get("/filters", response_model=ApiResponse, summary="获取筛选选项")
async def get_filters(db: Session = Depends(get_db)):
    """获取出勤管理页面所需的筛选选项

    返回服务器列表、地图列表、职业列表
    """
    try:
        return ApiResponse(
            success=True,
            message="获取成功",
            data={
                "servers": attendance_service.get_distinct_servers(db),
                "maps": attendance_service.get_distinct_maps(db),
                "professions": attendance_service.get_distinct_professions(db),
            },
        )

    except Exception as e:
        logger.error(f"获取筛选选项失败: {e}", exc_info=True)
        return ApiResponse(success=False, message=f"查询失败: {str(e)}", code=500)


