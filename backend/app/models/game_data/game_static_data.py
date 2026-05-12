# -*- coding: utf-8 -*-
"""
游戏静态数据模型

功能：存?GW2 API 原始游戏数据（技能、特性线、特性、调色板映射、增益效果）?
这些数据在应用启动时从数据库加载到内存缓存，运行时不再读?JSON 文件?

对应被替代的 JSON?
- bdcode_skills.json      ?gw_skill
- bdcode_specializations.json ?gw_specialization
- bdcode_traits.json      ?gw_trait
- skill_palettes.json     ?gw_skill_palette
- buffs.json              ?gw_buff
"""

from sqlalchemy import JSON, Boolean, Column, Integer, String, Text

from app.config.database import Base


class GwSkill(Base):
    """游戏技能表 ?替代 bdcode_skills.json"""

    __tablename__ = "gw_skill"
    __table_args__ = {"comment": "GW2 API 技能原始数据}

    id = Column(Integer, primary_key=True, comment="游戏技能ID")
    name = Column(String(100), nullable=True, comment="英文?)
    name_cn = Column(String(100), nullable=True, comment="中文?)
    description = Column(Text, nullable=True, comment="技能描?)
    icon = Column(String(500), nullable=True, comment="图标URL")
    slot = Column(String(50), nullable=True, comment="技能槽?)
    type = Column(String(50), nullable=True, comment="技能类)
    weapon_type = Column(String(50), nullable=True, comment="武器类型")
    professions = Column(JSON, default=list, comment="适用职业列表")
    facts = Column(JSON, default=list, comment="技能效果数据)
    chat_link = Column(String(50), nullable=True, comment="聊天链接")
    flags = Column(JSON, default=list, comment="标志列表")


class GwSpecialization(Base):
    """游戏特性线??替代 bdcode_specializations.json

    注意：此表存?GW2 API 原始特性线数据（含普?精英），
    与业务层?gw_elite_specialization 表不同?
    """

    __tablename__ = "gw_specialization"
    __table_args__ = {"comment": "GW2 API 特性线原始数据"}

    id = Column(Integer, primary_key=True, comment="游戏特性线ID")
    name = Column(String(100), nullable=True, comment="特性线名称")
    profession = Column(String(50), nullable=True, index=True, comment="所属职?)
    elite = Column(Boolean, default=False, comment="是否为精英特长线")
    minor_traits = Column(JSON, default=list, comment="小特性ID列表")
    major_traits = Column(JSON, default=list, comment="大特性ID列表")
    icon = Column(String(500), nullable=True, comment="图标URL")
    background = Column(String(500), nullable=True, comment="背景图URL")


class GwTrait(Base):
    """游戏特性表 ?替代 bdcode_traits.json"""

    __tablename__ = "gw_trait"
    __table_args__ = {"comment": "GW2 API 特性原始数据}

    id = Column(Integer, primary_key=True, comment="游戏特性ID")
    name = Column(String(100), nullable=True, comment="特性名?)
    description = Column(Text, nullable=True, comment="特性描?)
    icon = Column(String(500), nullable=True, comment="图标URL")
    slot = Column(String(50), nullable=True, comment="槽位 Major/Minor")
    tier = Column(Integer, nullable=True, comment="层级")
    order = Column(Integer, nullable=True, comment="顺序")
    specialization = Column(
        Integer, nullable=True, index=True, comment="所属特性线ID"
    )
    facts = Column(JSON, default=list, comment="效果数据")


class GwSkillPalette(Base):
    """技能调色板映射??替代 skill_palettes.json

    BD码中?palette_id 需要通过此表映射到实?skill_id?
    按职业分组，避免不同职业?palette_id 冲突?
    """

    __tablename__ = "gw_skill_palette"
    __table_args__ = {"comment": "BD码调色板ID到技能ID的映?}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    palette_id = Column(
        Integer, nullable=False, index=True, comment="调色板ID（BD码中使用?
    )
    skill_id = Column(
        Integer, nullable=False, index=True, comment="实际技能ID"
    )
    profession = Column(
        String(50), nullable=False, index=True, comment="所属职?
    )


class GwBuff(Base):
    """增益效果??替代 buffs.json

    存储游戏中所?Buff/Condition 的定义，用于战斗日志解析和增益统计?
    替代?sys_dict_data ?dict_type='buff_id' 的字典项?
    """

    __tablename__ = "gw_buff"
    __table_args__ = {"comment": "GW2 增益/症状效果定义"}

    id = Column(Integer, primary_key=True, comment="游戏Buff ID")
    name = Column(String(100), nullable=True, comment="英文?)
    name_cn = Column(String(100), nullable=True, comment="中文?)
    category = Column(
        String(50), nullable=True, index=True, comment="分类: offensive/defensive/healing/utility/debuff"
    )
    stacking = Column(String(50), nullable=True, comment="堆叠方式: duration/intensity")
    max_stacks = Column(Integer, nullable=True, comment="最大堆叠数")
    is_key_buff = Column(
        Boolean, default=False, comment="是否为关键增?
    )
    icon = Column(String(500), nullable=True, comment="图标URL")
    description = Column(Text, nullable=True, comment="效果描述")
