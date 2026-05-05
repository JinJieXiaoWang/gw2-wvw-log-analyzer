# -*- coding: utf-8 -*-
# 模块功能：战斗统计数据模型（精简版，每条记录对应一个玩家的一场战斗）
# 作者：系统
# 创建日期：2026-04-27
# 更新说明：v2.0 扩展字段，支持 DPS、Buff 覆盖率等 WvW 核心指标

from sqlalchemy import BigInteger, Column, ForeignKey, Index, Integer, JSON, Numeric, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class FightStats(Base):
    """战斗统计表 — 每个玩家每场战斗一条记录（~50行/日志）"""

    __tablename__ = "fight_stats"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    fight_id = Column(Integer, ForeignKey("fights.id"), nullable=False, comment="关联战斗记录ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="关联成员记录ID")

    # === 身份信息（冗余存储，避免 JOIN）===
    account = Column(String(100), nullable=False, comment="玩家账户名")
    character_name = Column(String(100), nullable=True, comment="角色名称")
    profession = Column(String(50), nullable=True, comment="职业")
    group_id = Column(Integer, default=1, comment="小队编号（1-5）")
    team_id = Column(Integer, default=0, comment="队伍ID（0=蓝队，1=红队，2=绿队）")
    has_commander_tag = Column(Integer, default=0, comment="是否有指挥官标记（1=是，0=否）")

    # === DPS / 伤害 / 治疗 ===
    damage = Column(BigInteger, default=0, comment="总伤害量")
    dps = Column(Integer, default=0, comment="每秒伤害")
    power_damage = Column(BigInteger, default=0, comment="直伤伤害")
    condi_damage = Column(BigInteger, default=0, comment="症状伤害")
    breakbar_damage = Column(BigInteger, default=0, comment="破蔑视伤害")
    healing = Column(BigInteger, default=0, comment="治疗量")

    # === 命中质量 ===
    critical_rate = Column(Numeric(5, 2), default=0, comment="暴击率（百分比）")
    flanking_rate = Column(Numeric(5, 2), default=0, comment="背击率（百分比）")
    glance_rate = Column(Numeric(5, 2), default=0, comment="偏斜率（百分比）")
    missed = Column(Integer, default=0, comment="未命中次数")

    # === 击杀 / 控制 ===
    killed = Column(Integer, default=0, comment="击杀敌人数量")
    downed = Column(Integer, default=0, comment="击倒敌人数量")
    interrupts = Column(Integer, default=0, comment="打断次数")
    swap_count = Column(Integer, default=0, comment="切换目标次数")

    # === 防御 / 生存 ===
    damage_taken = Column(BigInteger, default=0, comment="承受伤害量")
    blocked_count = Column(Integer, default=0, comment="格挡次数")
    evaded_count = Column(Integer, default=0, comment="闪避次数")
    dodge_count = Column(Integer, default=0, comment="翻滚次数")
    down_count = Column(Integer, default=0, comment="倒地次数")
    dead_count = Column(Integer, default=0, comment="死亡次数")
    boon_strips = Column(Integer, default=0, comment="移除增益次数")
    condition_cleanses = Column(Integer, default=0, comment="清除症状次数")

    # === 支援 ===
    resurrects = Column(Integer, default=0, comment="复活队友次数")
    condi_cleanse_ally = Column(Integer, default=0, comment="清除队友症状次数")
    boon_strips_ally = Column(Integer, default=0, comment="移除队友增益次数")

    # === 关键 Buff 覆盖率（标量，直接查询排序）===
    might_uptime = Column(Numeric(5, 2), default=0, comment="力量覆盖（百分比）")
    fury_uptime = Column(Numeric(5, 2), default=0, comment="狂怒覆盖（百分比）")
    quickness_uptime = Column(Numeric(5, 2), default=0, comment="急速覆盖（百分比）")
    alacrity_uptime = Column(Numeric(5, 2), default=0, comment="敏捷覆盖（百分比）")
    protection_uptime = Column(Numeric(5, 2), default=0, comment="保护覆盖（百分比）")
    stability_uptime = Column(Numeric(5, 2), default=0, comment="稳定覆盖（百分比）")

    # === AI 评分（后续计算或解析时生成）===
    ai_score = Column(Numeric(5, 2), default=0, comment="AI评分")
    score_grade = Column(String(10), default="", comment="评分等级（S/A/B/C/D）")
    score_breakdown = Column(JSON, nullable=True, comment="评分维度明细JSON")

    # === 关联关系 ===
    fight = relationship("Fight", back_populates="fight_stats")
    member = relationship("Member", back_populates="fight_stats")

    __table_args__ = (
        Index("idx_fight_stats_fight_member", "fight_id", "member_id"),
        Index("idx_fight_stats_profession", "profession"),
        Index("idx_fight_stats_dps", "dps"),
        Index("idx_fight_stats_damage", "damage"),
    )