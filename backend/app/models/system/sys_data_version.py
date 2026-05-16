# -*- coding: utf-8 -*-
# 模块功能：数据版本管理模型
# 说明：记录已应用的种子数据版本，支持增量迁移

from datetime import datetime

from app.config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, text


class SysDataVersion(Base):
    """数据版本管理模型"""

    __tablename__ = "sys_data_version"
    __table_args__ = {"comment": "数据版本管理"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    version = Column(String(20), nullable=False, unique=True, comment="数据版本号")
    applied_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="应用时间",
    )
    files = Column(String(2000), default="", comment="已应用的文件列表(JSON数组)")
    description = Column(String(500), nullable=True, comment="版本描述")
