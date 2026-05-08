# -*- coding: utf-8 -*-
"""系统通知公告表模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from app.config.database import Base


class SysNotice(Base):
    """通知公告表 — 所有人可见"""

    __tablename__ = "sys_notice"

    notice_id = Column(Integer, primary_key=True, autoincrement=True, comment="公告ID")
    notice_title = Column(String(100), nullable=False, default="", comment="标题")
    notice_type = Column(String(10), nullable=False, default="1", comment="类型：1通知 2公告")
    notice_content = Column(Text, nullable=True, comment="内容")
    status = Column(String(10), nullable=False, default="0", comment="状态：0正常 1关闭")
    source_type = Column(String(50), nullable=True, comment="来源类型：parse_complete/parse_failed")
    source_id = Column(String(100), nullable=True, comment="来源ID：日志ID等")
    create_by = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, nullable=True, default=datetime.utcnow, comment="创建时间")
    update_by = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    remark = Column(String(255), nullable=True, comment="备注")

    __table_args__ = (
        Index("idx_notice_status_type", "status", "notice_type"),
    )


class SysNoticeRead(Base):
    """通知公告已读记录表"""

    __tablename__ = "sys_notice_read"

    read_id = Column(Integer, primary_key=True, autoincrement=True, comment="已读主键")
    notice_id = Column(Integer, nullable=False, comment="公告ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    read_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="阅读时间")

    __table_args__ = (
        Index("uk_user_notice", "user_id", "notice_id", unique=True),
    )
