# -*- coding: utf-8 -*-
"""通知服务 — 全局公告，所有人可见"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system.sys_notice import SysNotice, SysNoticeRead
from app.utils.logger import logger


class NoticeService:
    """通知服务"""

    @staticmethod
    def create_notice(
        db: Session,
        title: str,
        content: str,
        notice_type: str = "1",
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        create_by: str = "system",
    ) -> SysNotice:
        """创建通知"""
        notice = SysNotice(
            notice_title=title,
            notice_content=content,
            notice_type=notice_type,
            status="0",
            source_type=source_type,
            source_id=source_id,
            create_by=create_by,
            create_time=datetime.utcnow(),
        )
        db.add(notice)
        db.flush()
        return notice

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """获取用户未读通知数"""
        subquery = (
            select(SysNoticeRead.notice_id)
            .where(SysNoticeRead.user_id == user_id)
            .scalar_subquery()
        )
        count = (
            db.query(SysNotice)
            .filter(
                SysNotice.status == "0",
                SysNotice.notice_id.notin_(subquery),
            )
            .count()
        )
        return count

    @staticmethod
    def get_notice_list(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> Dict[str, Any]:
        """获取通知列表"""
        subquery = (
            select(SysNoticeRead.notice_id)
            .where(SysNoticeRead.user_id == user_id)
            .scalar_subquery()
        )

        query = db.query(SysNotice).filter(SysNotice.status == "0")

        if unread_only:
            query = query.filter(SysNotice.notice_id.notin_(subquery))

        total = query.count()
        items = (
            query.order_by(SysNotice.create_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        read_ids = {
            r.notice_id
            for r in db.query(SysNoticeRead)
            .filter(
                SysNoticeRead.user_id == user_id,
                SysNoticeRead.notice_id.in_([n.notice_id for n in items]),
            )
            .all()
        }

        return {
            "items": [
                {
                    "notice_id": n.notice_id,
                    "notice_title": n.notice_title,
                    "notice_content": n.notice_content,
                    "notice_type": n.notice_type,
                    "source_type": n.source_type,
                    "source_id": n.source_id,
                    "create_time": n.create_time.isoformat() if n.create_time else None,
                    "is_read": n.notice_id in read_ids,
                }
                for n in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    def mark_as_read(db: Session, user_id: int, notice_id: int) -> bool:
        """标记通知为已读（存在则忽略）"""
        exists = (
            db.query(SysNoticeRead)
            .filter(
                SysNoticeRead.user_id == user_id,
                SysNoticeRead.notice_id == notice_id,
            )
            .first()
        )
        if exists:
            return True
        read_record = SysNoticeRead(
            notice_id=notice_id,
            user_id=user_id,
            read_time=datetime.utcnow(),
        )
        db.add(read_record)
        db.flush()
        return True

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """标记用户所有未读通知为已读"""
        subquery = (
            select(SysNoticeRead.notice_id)
            .where(SysNoticeRead.user_id == user_id)
            .scalar_subquery()
        )
        unread_notices = (
            db.query(SysNotice)
            .filter(
                SysNotice.status == "0",
                SysNotice.notice_id.notin_(subquery),
            )
            .all()
        )

        count = 0
        for notice in unread_notices:
            db.add(
                SysNoticeRead(
                    notice_id=notice.notice_id,
                    user_id=user_id,
                    read_time=datetime.utcnow(),
                )
            )
            count += 1
        if count > 0:
            db.flush()
        return count
