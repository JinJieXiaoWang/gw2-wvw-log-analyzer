# -*- coding: utf-8 -*-
# 模块功能：EI 同步数据模型
# 作者：系统
# 创建日期：2026-05-01
# 更新日期：2026-05-04
# 依赖说明：SQLAlchemy
# 说明：
#   原 evtc_header/agent/skill/event/player_instance/combat_meta/event_per_second
#   等 7 个原始数据模型已随 ZEVTC 原始数据体系废弃而删除。
#   当前仅保留 EI 同步相关模型（ei_player, ei_target, ei_skill_map, ei_phase）。

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
)

from app.config.database import Base


class EiPlayer(Base):
    """EI玩家数据表 (ei_player) — 对应EI JSON players[]"""

    __tablename__ = "ei_player"

    player_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(
        BigInteger, ForeignKey("evtc_log.log_id", ondelete="CASCADE"), nullable=False,
        comment="关联日志ID"
    )
    agent_index = Column(Integer, comment="关联evtc_agent索引")
    account = Column(String(100), comment="玩家账户名")
    character_name = Column(String(100), nullable=False, comment="角色名称")
    profession = Column(String(50), nullable=False, comment="职业")
    group_id = Column(SmallInteger, comment="小队编号（1-5）")
    has_commander_tag = Column(SmallInteger, default=0, comment="是否有指挥官标记（1=是，0=否）")
    is_fake = Column(SmallInteger, default=0, comment="是否为假玩家（宠物、召唤物等）")
    weapons_json = Column(JSON, comment="武器配置JSON")
    consumables_json = Column(JSON, comment="食物与扳手配置JSON")
    dps_all_json = Column(JSON, comment="dpsAll数组JSON")
    stats_all_json = Column(JSON, comment="statsAll数组JSON")
    defenses_json = Column(JSON, comment="defenses数组JSON")
    support_json = Column(JSON, comment="support数组JSON")
    buff_uptimes_json = Column(JSON, comment="buffUptimes数组JSON")
    rotation_json = Column(JSON, comment="rotation数组JSON")
    death_recap_json = Column(JSON, comment="deathRecap数组JSON")

    __table_args__ = (
        Index("uk_log_agent_ei", "log_id", "agent_index", unique=True),
        Index("idx_profession", "profession"),
    )


class EiTarget(Base):
    """EI目标数据表 (ei_target) — 对应JSON targets[]"""

    __tablename__ = "ei_target"

    target_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(
        BigInteger, ForeignKey("evtc_log.log_id", ondelete="CASCADE"), nullable=False,
        comment="关联日志ID"
    )
    agent_index = Column(Integer, comment="关联evtc_agent索引")
    name = Column(String(100), nullable=False, comment="目标名称")
    enemy_player = Column(SmallInteger, default=0, comment="是否为敌方玩家（1=是，0=否）")
    total_health = Column(BigInteger, comment="总生命值")
    final_health = Column(BigInteger, comment="最终生命值")
    health_percent_burned = Column(Integer, comment="生命燃烧百分比")
    dps_all_json = Column(JSON, comment="dpsAll数组JSON")
    defenses_json = Column(JSON, comment="defenses数组JSON")

    __table_args__ = (
        Index("uk_log_target_agent", "log_id", "agent_index", unique=True),
    )


class EiSkillMap(Base):
    """EI技能映射表 (ei_skill_map) — 对应JSON skillMap"""

    __tablename__ = "ei_skill_map"

    map_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(
        BigInteger, ForeignKey("evtc_log.log_id", ondelete="CASCADE"), nullable=False,
        comment="关联日志ID"
    )
    skill_key = Column(String(20), nullable=False, comment="JSON中的技能键(s12345)")
    gw2_skill_id = Column(Integer, nullable=False, comment="GW2官方技能ID")
    name = Column(String(100), comment="技能名称")
    auto_attack = Column(SmallInteger, default=0, comment="是否为自动攻击（1=是，0=否）")
    can_crit = Column(SmallInteger, default=0, comment="是否可暴击（1=是，0=否）")
    is_swap = Column(SmallInteger, default=0, comment="是否为武器切换（1=是，0=否）")
    is_instant_cast = Column(SmallInteger, default=0, comment="是否为瞬发（1=是，0=否）")
    is_trait_proc = Column(SmallInteger, default=0, comment="是否为特性触发（1=是，0=否）")
    icon = Column(String(500), comment="技能图标URL")

    __table_args__ = (Index("uk_log_skill_key", "log_id", "skill_key", unique=True),)


class EiPhase(Base):
    """EI战斗阶段表 (ei_phase) — 对应JSON phases[]"""

    __tablename__ = "ei_phase"

    phase_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(
        BigInteger, ForeignKey("evtc_log.log_id", ondelete="CASCADE"), nullable=False,
        comment="关联日志ID"
    )
    phase_index = Column(Integer, nullable=False, comment="阶段索引")
    name = Column(String(100), nullable=False, comment="阶段名称")
    start_ms = Column(Integer, nullable=False, comment="阶段开始时间（毫秒）")
    end_ms = Column(Integer, nullable=False, comment="阶段结束时间（毫秒）")
    breakbar_phase = Column(SmallInteger, default=0, comment="是否为破蔑视阶段（1=是，0=否）")
    targets_json = Column(JSON, comment="目标信息JSON")

    __table_args__ = (Index("uk_log_phase", "log_id", "phase_index", unique=True),)