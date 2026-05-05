# 模块功能：存储管理相关数据模型
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：SQLAlchemy

from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.config.database import Base


class StorageCleanupRecord(Base):
    # 功能：存储清理记录数据模型
    __tablename__ = "storage_cleanup_records"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    cleanup_type = Column(
        String(50), nullable=False, comment="清理类型：manual/auto/scheduled"
    )
    start_time = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="开始时间"
    )
    end_time = Column(DateTime(timezone=True), nullable=True, comment="结束时间")
    files_deleted = Column(Integer, default=0, comment="删除文件数")
    space_freed = Column(Float, default=0.0, comment="释放空间（字节）")
    status = Column(
        String(20), default="in_progress", comment="状态：in_progress/completed/failed"
    )
    error_message = Column(Text, nullable=True, comment="错误信息")
    triggered_by = Column(String(100), nullable=True, comment="触发者")

    __table_args__ = (
        Index("idx_cleanup_start_time", "start_time"),
        Index("idx_cleanup_status", "status"),
    )


class StorageMonitorRecord(Base):
    # 功能：存储监控记录数据模型
    __tablename__ = "storage_monitor_records"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    record_time = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="记录时间"
    )
    total_size = Column(Float, nullable=False, comment="总存储使用量（字节）")
    file_count = Column(Integer, nullable=False, comment="文件总数")
    log_file_count = Column(Integer, default=0, comment="日志文件数量")
    warning_triggered = Column(Boolean, default=False, comment="是否触发警告")

    __table_args__ = (Index("idx_monitor_record_time", "record_time"),)
