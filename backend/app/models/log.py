# 模块功能：日志文件数据模型
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy
# 说明：evtc_log 表为纯粹的上传文件注册表（Upload Registry），负责文件上传及文件信息保存。
#       不直接存储任何解析后的业务数据（如服务器、地图、战斗统计等），
#       这些数据由 evtc_header / fights / ei_* 等子表独立维护。

from sqlalchemy import (
    CHAR,
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


class Log(Base):
    """上传日志文件注册表 — 纯粹的文件管理与解析生命周期跟踪"""

    __tablename__ = "evtc_log"

    # === 核心标识 ===
    id = Column(
        "log_id",
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="日志实例主键",
    )
    log_uuid = Column(CHAR(36), unique=True, nullable=False, comment="全局唯一UUID(v4)")
    filename = Column(String(255), nullable=False, comment="原始上传文件名")

    # === 文件完整性 ===
    file_sha256 = Column(
        CHAR(64), unique=True, nullable=False, comment="原始文件SHA-256指纹(去重用)"
    )
    file_size_compressed = Column(
        Integer, nullable=False, comment="zevtc压缩后大小(字节)"
    )
    file_size_raw = Column(Integer, nullable=False, comment="evtc解压后大小(字节)")

    # === 文件存储 ===
    file_path = Column(String(500), nullable=True, comment="文件存储路径")

    # === 解析生命周期（轻量级状态机） ===
    parse_status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="解析状态",
    )
    parse_time_ms = Column(Integer, comment="解析耗时(毫秒)")
    dps_report_permalink = Column(
        String(500), nullable=True, comment="dps.report 报告链接"
    )
    parsed_at = Column(DateTime(timezone=True), comment="解析完成时间")
    error_message = Column(Text, comment="解析失败时的错误信息")

    # === 上传审计 ===
    upload_time = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="上传时间，毫秒精度"
    )
    upload_ip = Column(String(50), nullable=True, comment="上传者IP地址")
    uploaded_by = Column(
        Integer, ForeignKey("sys_user.id"), nullable=True, comment="上传者ID"
    )

    # === 关联关系 ===
    uploader = relationship("SysUser")
    fights = relationship("Fight", back_populates="log", cascade="all, delete-orphan")

    # 索引：加速查询
    __table_args__ = (
        Index("idx_log_parse_status", "parse_status"),
        Index("idx_log_upload_time", "upload_time"),
        Index("idx_log_file_sha256", "file_sha256"),
        Index("idx_log_filename", "filename"),
        Index("idx_log_uploader_id", "uploaded_by"),
    )
