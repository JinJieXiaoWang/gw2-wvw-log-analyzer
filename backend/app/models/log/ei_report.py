
# -*- coding: utf-8 -*-
"""
EI 完整报告数据模型

功能：存储Elite Insights 生成的完整报告数据（_logData + _graphData）
由于原始 JSON 体积巨大（可达100MB+），采用"元数据存 DB + 大文件存磁盘"的混合策略：
  - summary_json: 存储摘要数据（players/targets/phases 基础信息 + 定义表），用于快速查询
  - log_data_path: 指向 gzip 压缩后的完整 _logData JSON 文件
  - graph_data_path: 指向 gzip 压缩后的完整 _graphData JSON 文件
"""

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
from sqlalchemy.sql import func

from app.config.database import Base


class EiReport(Base):
    """EI 完整报告存储表(ei_report)"""

    __tablename__ = "ei_report"

    report_id = Column(
        Integer, primary_key=True, autoincrement=True, comment="自增主键"
    )
    log_id = Column(
        Integer,
        ForeignKey("evtc_log.log_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="关联日志",
    )
    report_type = Column(
        String(50),
        nullable=False,
        default="detailed_wvw",
        comment="报告类型: detailed_wvw, raid, fractal",
    )
    ei_version = Column(String(50), nullable=True, comment="EI 解析器版本，如3.21.1.0")

    # 摘要 JSON：存储players/targets/phases 基础信息 + 元数据 + 定义表
    # 体积约1-5MB，可直接从数据库读取
    summary_json = Column(JSON, comment="EI 报告摘要数据(JSON)")

    # 大文件路径：指向 gzip 压缩的完成JSON 文件
    log_data_path = Column(String(500), comment="完整 _logData JSON 压缩文件路径")
    graph_data_path = Column(String(500), comment="完整 _graphData JSON 压缩文件路径")
    cr_data_path = Column(String(500), comment="Combat Replay 数据压缩文件路径")

    # 报告生成时的原始元数据（冗余存储，便于直接查询）
    log_name = Column(String(200), comment="战斗名称")
    duration_ms = Column(BigInteger, comment="战斗时长(毫秒)")
    player_count = Column(BigInteger, comment="玩家数量")
    target_count = Column(BigInteger, comment="目标数量")
    success = Column(String(10), comment="是否成功")
    recorded_by = Column(String(100), comment="录制者角色名")
    recorded_account_by = Column(String(100), comment="录制者账号")
    map_id = Column(BigInteger, comment="地图ID")
    region = Column(String(50), comment="服务器区域")
    wvw = Column(String(10), comment="是否为WvW")

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="记录创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="记录更新时间",
    )

    __table_args__ = (
        Index("idx_ei_report_type", "report_type"),
        Index("idx_ei_report_map", "map_id"),
    )

