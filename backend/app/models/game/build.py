# -*- coding: utf-8 -*-
# 模块功能：Build图书馆数据模型
# 依赖说明：SQLAlchemy

from app.config.database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, func


class Build(Base):
    """Build图书馆表 (builds)"""

    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    slug = Column(
        String(100), unique=True, index=True, nullable=False, comment="URL标识"
    )
    title = Column(String(100), nullable=False, comment="Build标题")
    profession = Column(String(50), nullable=False, index=True, comment="职业名称")
    profession_color = Column(String(20), nullable=True, comment="职业颜色(HEX)")
    elite_spec = Column(String(50), nullable=True, comment="精英特长")
    role = Column(String(20), nullable=False, index=True, comment="主角? dps/support")
    sub_roles = Column(JSON, default=list, comment="子角色列? boon/heal/tank/cc")
    armor_type = Column(String(100), nullable=True, comment="护甲类型")
    weapons = Column(JSON, default=list, comment="武器配置(JSON)")
    relic = Column(String(100), nullable=True, comment=" relic")
    rune = Column(String(100), nullable=True, comment="符文")
    food = Column(String(100), nullable=True, comment="食物")
    wrench = Column(String(100), nullable=True, comment="扳手(通用技?")
    infusion = Column(String(100), nullable=True, comment="灌注")
    attr_requirements = Column(JSON, default=list, comment="属性要求列(JSON)")
    bd_code = Column(String(255), nullable=False, comment="GW2 Build Code")
    trait_lines = Column(JSON, default=list, comment="特性线配置(JSON)")
    rotation_commands = Column(JSON, default=list, comment="循环指令(JSON)")
    mechanics = Column(JSON, default=list, comment="机制说明(JSON)")
    videos = Column(JSON, default=list, comment="视频链接(JSON)")
    author = Column(String(50), nullable=False, comment="作者")
    word_count = Column(Integer, default=0, comment="字数统计")
    is_meta = Column(Boolean, default=False, comment="是否推荐配置")
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
