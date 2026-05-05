# 模块功能：AI分析报告数据模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.config.database import Base


class AIReport(Base):
    # 功能：AI分析报告数据结构类型定义。
    # #参数：无。
    # 返回值：无

    __tablename__ = "ai_reports"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    report_type = Column(String(50), nullable=False, comment="报告类型")
    target_type = Column(String(50), nullable=False, comment="目标类型")
    target_id = Column(Integer, nullable=False, comment="目标ID")
    content = Column(Text, nullable=False, comment="报告内容")
    summary = Column(Text, nullable=True, comment="报告摘要")
    ai_score = Column(Float, nullable=True, comment="AI评分")
    created_by = Column(
        Integer, ForeignKey("sys_user.id"), nullable=True, comment="创建者ID"
    )
    created_at = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="创建时间"
    )
    is_public = Column(Integer, default=1, comment="是否公开")
    is_deleted = Column(Integer, default=0, comment="是否删除")
