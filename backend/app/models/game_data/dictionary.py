# -*- coding: utf-8 -*-
# 模块功能：字典数据模型
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-29
# 依赖说明：SQLAlchemy

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint

from app.config.database import Base


class SysDictType(Base):
    # 功能：字典类型表
    # 参数：无
    # 返回：无

    __tablename__ = "sys_dict_type"

    dict_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="字典类型ID"
    )
    dict_type = Column(
        String(100), nullable=False, unique=True, index=True, comment="字典类型编码"
    )
    dict_name = Column(String(200), nullable=False, comment="字典类型名称")
    status = Column(Integer, nullable=False, default=0, comment="状态：0-启用?-禁用")
    sort_order = Column(Integer, nullable=False, default=0, comment="排序顺序")
    remark = Column(Text, nullable=True, comment="备注说明")
    is_system = Column(
        Integer, nullable=False, default=0, comment="是否系统预置?-否，1-?
    )


class SysDictData(Base):
    # 功能：字典数据表
    # 参数：无
    # 返回：无

    __tablename__ = "sys_dict_data"

    dict_code = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="字典项编?
    )
    dict_sort = Column(Integer, nullable=False, default=0, comment="排序顺序")
    dict_label = Column(String(200), nullable=False, comment="字典标签")
    dict_value = Column(String(200), nullable=False, comment="字典?)
    dict_type = Column(String(100), nullable=False, index=True, comment="字典类型")
    data_type = Column(String(100), nullable=True, comment="数据类型")
    css_class = Column(String(200), nullable=True, comment="CSS样式?颜色?)
    list_class = Column(String(100), nullable=True, comment="列表样式?)
    is_default = Column(
        Integer, nullable=False, default=0, comment="是否默认值：0-否，1-?
    )
    status = Column(Integer, nullable=False, default=0, comment="状态：0-启用?-禁用")
    remark = Column(Text, nullable=True, comment="备注说明")

    __table_args__ = (
        UniqueConstraint("dict_type", "dict_value", name="_dict_type_value_uc"),
    )
