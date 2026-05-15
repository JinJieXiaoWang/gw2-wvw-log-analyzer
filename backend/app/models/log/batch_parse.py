
# -*- coding: utf-8 -*-
# 模块功能：批量解析任务数据模型
# 作者：系统
# 创建日期：2026-04-29
# 依赖说明：SQLAlchemy

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base
from app.constants.dict_values import BatchTaskStatus


class BatchParseTask(Base):
    """批量解析任务数据模型类"""

    __tablename__ = "batch_parse_tasks"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    task_name = Column(String(255), nullable=True, comment="任务名称")
    status = Column(
        String(20),
        default=BatchTaskStatus.PENDING.value,
        comment="状态：pending/processing/completed/failed/partial",
    )
    total_count = Column(Integer, default=0, comment="总数据量")
    processed_count = Column(Integer, default=0, comment="已处理数据量")
    success_count = Column(Integer, default=0, comment="成功数量")
    failed_count = Column(Integer, default=0, comment="失败数量")
    created_at = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="创建时间"
    )
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_by = Column(
        Integer, ForeignKey("sys_user.id"), nullable=True, comment="创建者ID"
    )
    error_message = Column(Text, nullable=True, comment="错误信息")
    log_ids = Column(JSON, nullable=True, comment="日志ID列表")

    creator = relationship("SysUser")
    items = relationship(
        "BatchParseTaskItem", back_populates="task", cascade="all, delete-orphan"
    )

    # 索引：加速查询
    __table_args__ = (
        Index("idx_batch_task_status", "status"),
        Index("idx_batch_task_created", "created_at"),
    )


class BatchParseTaskItem(Base):
    """批量解析任务单个日志项模型
    v2.0 增强：支持重试、限流、错误分类"""

    __tablename__ = "batch_parse_task_items"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    task_id = Column(
        Integer,
        ForeignKey("batch_parse_tasks.id"),
        nullable=False,
        comment="关联任务ID",
    )
    log_id = Column(
        Integer, ForeignKey("evtc_log.log_id"), nullable=False, comment="关联日志ID"
    )
    status = Column(
        String(20),
        default=BatchTaskStatus.PENDING.value,
        comment="状态：pending/processing/completed/failed/retrying",
    )
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # === v2.0 新增：重试与限流相关字段 ===
    retry_count = Column(
        Integer, default=0, comment="已重试次数"
    )
    max_retries = Column(
        Integer, default=3, comment="最大重试次数"
    )
    next_retry_at = Column(
        DateTime(timezone=True), nullable=True, comment="下次重试时间"
    )
    error_code = Column(
        String(50), nullable=True, comment="错误代码:429/timeout/parse_error/unknown"
    )

    task = relationship("BatchParseTask", back_populates="items")
    log = relationship("Log")

    # 索引：加速查询
    __table_args__ = (
        Index("idx_batch_item_task", "task_id"),
        Index("idx_batch_item_log", "log_id"),
        # v2.0 新增：加速轮询查询
        Index("idx_batch_item_status_retry", "status", "next_retry_at"),
    )

