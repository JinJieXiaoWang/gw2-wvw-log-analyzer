# -*- coding: utf-8 -*-
# 模块功能：GW2职业层级数据2职业层级数据模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-11
# 依赖说明：SQLAlchemy
# 说明：统一管理职业、精英特长、角色定位的层级关系

from app.config.database import Base
from sqlalchemy import JSON, Column, Integer, String, UniqueConstraint


class GwRoleType(Base):
    """
    角色定位类型表
    存储角色类型信息：DPS、辅助、坦克等
    """

    __tablename__ = "gw_role_type"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    role_key = Column(String(20), nullable=False, unique=True, index=True, comment="角色?dps/support/tank)")
    role_name = Column(String(50), nullable=False, comment="角色名称(输出/辅助/坦克)")
    color = Column(String(20), nullable=True, comment="角色颜色(HEX)")
    icon = Column(String(100), nullable=True, comment="角色图标")
    sort_order = Column(Integer, default=0, comment="排序顺序")


class GwProfession(Base):
    """
    职业基础信息表
    存储GW2的所有基础职业信息
    """

    __tablename__ = "gw_profession"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    profession_key = Column(String(50), nullable=False, unique=True, index=True, comment="职业英文键")
    profession_name = Column(String(100), nullable=False, comment="职业中文名称")
    profession_name_en = Column(String(100), nullable=False, comment="职业英文名称")
    color = Column(String(20), nullable=False, comment="职业颜色(HEX)")
    icon = Column(String(200), nullable=True, comment="职业图标URL")
    default_role = Column(String(20), default="dps", comment="默认角色定位")
    possible_roles = Column(JSON, default=list, comment="可能的角色定位列(JSON)")
    is_active = Column(Integer, default=1, comment="是否启用: 1-启用, 0-禁用")
    sort_order = Column(Integer, default=0, comment="排序顺序")


class GwEliteSpecialization(Base):
    """
    精英特长特性线表
    存储各职业的精英特长（特性线）信息
    """

    __tablename__ = "gw_elite_specialization"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    spec_key = Column(String(50), nullable=False, unique=True, index=True, comment="特长英文键")
    spec_name = Column(String(100), nullable=False, comment="特长中文名称")
    spec_name_en = Column(String(100), nullable=False, comment="特长英文名称")
    profession_key = Column(String(50), nullable=False, index=True, comment="所属职业键")
    color = Column(String(20), nullable=True, comment="特长颜色(HEX)")
    icon = Column(String(200), nullable=True, comment="特长图标URL")
    default_role = Column(String(20), default="dps", comment="默认角色定位")
    dps_type = Column(String(20), nullable=True, comment="DPS类型(power/condi/hybrid)")
    scoring_config = Column(JSON, default=dict, comment="评分配置")
    is_key_support = Column(Integer, default=0, comment="是否关键辅助: 1-是, 0-否")
    is_active = Column(Integer, default=1, comment="是否启用: 1-启用, 0-禁用")
    sort_order = Column(Integer, default=0, comment="排序顺序")

    __table_args__ = (
        UniqueConstraint("profession_key", "spec_key", name="_uk_profession_spec"),
    )
