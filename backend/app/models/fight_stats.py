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
    critical_rate = Column(Integer, default=0, comment="暴击次数")
    flanking_rate = Column(Integer, default=0, comment="背击次数")
    glance_rate = Column(Integer, default=0, comment="偏斜次数")
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

    # === 高级战斗指标（dps.report API 专有）===
    down_contribution = Column(Integer, default=0, comment="倒地贡献")
    against_downed_damage = Column(BigInteger, default=0, comment="对倒地敌人伤害")
    applied_cc_duration = Column(Integer, default=0, comment="施加CC时长(ms)")
    applied_cc_count = Column(Integer, default=0, comment="施加CC次数")
    barrier_damage_absorbed = Column(BigInteger, default=0, comment="屏障吸收伤害")
    condition_damage_taken = Column(BigInteger, default=0, comment="症状承受伤害")
    power_damage_taken = Column(BigInteger, default=0, comment="直伤承受伤害")
    received_cc_duration = Column(Integer, default=0, comment="受到CC时长(ms)")
    might_uptime_active = Column(Numeric(5, 2), default=0, comment="战斗活跃期力量覆盖(%)")
    quickness_uptime_active = Column(Numeric(5, 2), default=0, comment="战斗活跃期急速覆盖(%)")
    alacrity_uptime_active = Column(Numeric(5, 2), default=0, comment="战斗活跃期敏捷覆盖(%)")
    avg_boons = Column(Numeric(5, 2), default=0, comment="平均增益层数")
    avg_conditions = Column(Numeric(5, 2), default=0, comment="平均症状层数")

    # === 技能效率与位置（EI 扩展字段）===
    wasted = Column(Integer, default=0, comment="技能浪费值")
    saved = Column(Integer, default=0, comment="技能节省值")
    skill_cast_uptime = Column(Numeric(5, 2), default=0, comment="技能施法占比(%)")
    stack_dist = Column(Numeric(10, 2), default=0, comment="堆叠距离")
    dist_to_com = Column(Numeric(10, 2), default=0, comment="与指挥官距离")

    # === 倒地/死亡详情（EI 扩展字段）===
    downed_damage_taken = Column(BigInteger, default=0, comment="倒地时承受伤害")
    interrupted_count = Column(Integer, default=0, comment="被打断次数")
    down_duration = Column(Integer, default=0, comment="倒地时长(ms)")
    dead_duration = Column(Integer, default=0, comment="死亡时长(ms)")
    dc_count = Column(Integer, default=0, comment="掉线次数")
    dc_duration = Column(Integer, default=0, comment="掉线时长(ms)")

    # === 支援详情（EI 扩展字段）===
    stun_break = Column(Integer, default=0, comment="解控次数")
    removed_stun_duration = Column(Numeric(8, 3), default=0, comment="解除眩晕时长(s)")

    # === AI 评分（后续计算或解析时生成）===
    ai_score = Column(Numeric(5, 2), default=0, comment="AI评分")
    score_grade = Column(String(10), default="", comment="评分等级（S/A/B/C/D）")
    score_breakdown = Column(JSON, nullable=True, comment="评分维度明细JSON")

    # === 评分规则元数据（用于追溯和重算）===
    role_type = Column(String(50), nullable=True, comment="评分时使用的职能类型")
    rule_version = Column(Integer, default=0, comment="评分规则版本号")
    scoring_profession_rule = Column(String(50), nullable=True, comment="使用的职业特定规则名")

    # === 关联关系 ===
    fight = relationship("Fight", back_populates="fight_stats")
    member = relationship("Member", back_populates="fight_stats")

    __table_args__ = (
        Index("idx_fight_stats_fight_member", "fight_id", "member_id"),
        Index("idx_fight_stats_profession", "profession"),
        Index("idx_fight_stats_dps", "dps"),
        Index("idx_fight_stats_damage", "damage"),
    )