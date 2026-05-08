# -*- coding: utf-8 -*-
# 模块功能：评分规则版本管理模型
# 说明：记录评分规则的每次变更版本，支持历史追溯和重算任务跟踪

from sqlalchemy import Column, Integer, String, DateTime, func

from app.config.database import Base


class ScoringRuleVersion(Base):
    """评分规则版本管理表
    
    每次批量更新评分规则时自动创建一条版本记录，
    用于追溯历史评分数据使用的规则版本，以及跟踪重算任务进度。
    """
    __tablename__ = "scoring_rule_version"
    __table_args__ = {"comment": "评分规则版本管理表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="版本记录ID")
    version = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="版本号，自增",
    )
    description = Column(
        String(500),
        nullable=True,
        comment="变更描述",
    )
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="状态: pending-待处理, processing-执行中, completed-已完成, failed-失败",
    )
    total_records = Column(
        Integer,
        default=0,
        comment="需更新的总记录数",
    )
    updated_records = Column(
        Integer,
        default=0,
        comment="已更新记录数",
    )
    failed_records = Column(
        Integer,
        default=0,
        comment="失败记录数",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间",
    )
