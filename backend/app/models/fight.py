# -*- coding: utf-8 -*-
# 模块功能：战斗记录数据模型
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Fight(Base):
    """战斗记录表 — 每场战斗一条记录"""

    __tablename__ = "fights"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="战斗记录ID")
    log_id = Column(Integer, ForeignKey("evtc_log.log_id"), nullable=False, comment="关联日志ID")
    start_time = Column(DateTime(timezone=True), nullable=False, comment="战斗开始时间")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="战斗结束时间")
    duration_sec = Column(Integer, default=0, comment="战斗时长(秒)")
    duration_ms = Column(BigInteger, default=0, comment="战斗时长(毫秒)")
    map_name = Column(String(100), nullable=True, comment="地图名称")
    server_name = Column(String(100), nullable=True, comment="服务器名称")
    recorded_by = Column(String(100), nullable=True, comment="录制者角色名")
    recorded_account = Column(String(100), nullable=True, comment="录制者账号")
    total_damage = Column(BigInteger, default=0, comment="总伤害量")
    total_healing = Column(BigInteger, default=0, comment="总治疗量")
    kill_count = Column(Integer, default=0, comment="击杀数")
    death_count = Column(Integer, default=0, comment="死亡数")
    player_count = Column(Integer, default=0, comment="玩家数量")
    is_ai_analyzed = Column(Boolean, default=False, comment="是否已完成AI分析")
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), comment="记录创建时间")

    # 关联关系
    log = relationship("Log", back_populates="fights")
    fight_stats = relationship(
        "FightStats", back_populates="fight", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_fight_log_id", "log_id"),
        Index("idx_fight_map_name", "map_name"),
        Index("idx_fight_start_time", "start_time"),
    )
