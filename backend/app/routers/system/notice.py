# -*- coding: utf-8 -*-
"""通知路由

提供通知列表查询、未读数、标记已读等接口
支持游客访问（返回空数据）
"""

from typing import Optional

from app.config.database import get_db
from app.models.auth.sys_user import SysUser
from app.schemas.auth.common import ApiResponse
from app.services.auth.auth_service import get_current_admin, get_current_user_optional
from app.services.system.notice_service import NoticeService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/notices", tags=["通知"])


@router.get("/unread-count", response_model=ApiResponse, summary="获取未读通知")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: Optional[SysUser] = Depends(get_current_user_optional),
):
    if not current_user:
        return ApiResponse(success=True, message="游客无未读通知", data={"count": 0})
    count = NoticeService.get_unread_count(db, current_user.id)
    return ApiResponse(success=True, message="获取未读通知数成功", data={"count": count})


@router.get("", response_model=ApiResponse, summary="获取通知列表")
async def get_notice_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Optional[SysUser] = Depends(get_current_user_optional),
):
    if not current_user:
        return ApiResponse(success=True, message="游客通知列表为空", data={
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
        })
    data = NoticeService.get_notice_list(
        db, current_user.id, page=page, page_size=page_size, unread_only=unread_only
    )
    return ApiResponse(success=True, message="获取通知列表成功", data=data)


@router.post("/{notice_id}/read", response_model=ApiResponse, summary="标记通知已读")
async def mark_notice_read(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_admin),
):
    NoticeService.mark_as_read(db, current_user.id, notice_id)
    return ApiResponse(success=True, message="标记已读成功")


@router.post("/read-all", response_model=ApiResponse, summary="标记所有通知已读")
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_admin),
):
    count = NoticeService.mark_all_as_read(db, current_user.id)
    return ApiResponse(success=True, message=f"已标记 {count} 条通知为已读", data={"count": count})
