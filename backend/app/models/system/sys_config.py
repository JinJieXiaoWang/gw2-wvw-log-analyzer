# -*- coding: utf-8 -*-
# 模块功能：系统参数配置模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12
# 依赖说明：SQLAlchemy
# 说明：存储全局系统配置，如主题、水印、解析参数等

from datetime import datetime

from app.config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, text


class SysConfig(Base):
    """系统参数配置模型"""

    __tablename__ = "sys_config"
    __table_args__ = {"comment": "系统参数配置"}

    config_id = Column(
        Integer, primary_key=True, autoincrement=True, comment="参数主键"
    )
    config_name = Column(String(100), default="", comment="参数名称")
    config_key = Column(String(100), default="", nullable=False, comment="参数键名")
    config_value = Column(String(500), default="", comment="参数键值")
    config_type = Column(String(1), default="N", comment="系统内置（Y是，N否）")
    create_by = Column(String(64), default="", comment="创建人")
    create_time = Column(
        DateTime(timezone=True),
        default=datetime.now,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    update_by = Column(String(64), default="", comment="更新人")
    update_time = Column(
        DateTime(timezone=True),
        onupdate=datetime.now,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
    remark = Column(String(500), nullable=True, comment="备注")
