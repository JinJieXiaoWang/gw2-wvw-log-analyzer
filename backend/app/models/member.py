# -*- coding: utf-8 -*-
# 模块功能：成员数据模型
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy
# 说明：
#   members 表仅保存账号维度（account_name）。
#   角色名、职业等详细信息请去 account_characters 表查询。

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class Member(Base):
    """成员表 — 仅保存账号（account_name），角色信息去 account_characters 查"""

    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="成员ID")
    account_name = Column(String(100), nullable=False, unique=True, index=True, comment="账号名称")
    guild_tag = Column(String(20), nullable=True, comment="公会标签")
    join_date = Column(Date, nullable=True, comment="加入日期")

    fight_stats = relationship("FightStats", back_populates="member")

    def __repr__(self):
        return f"<Member({self.account_name})>"
