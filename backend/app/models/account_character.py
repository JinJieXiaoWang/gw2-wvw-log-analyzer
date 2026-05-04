# -*- coding: utf-8 -*-
# 模块功能：账号角色映射模型
# 作者：系统
# 创建日期：2026-05-03
# 依赖说明：SQLAlchemy
# 说明：支持同一account对应多个角色的映射关系

from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class AccountCharacter(Base):
    """账号角色映射表 — 存储同一account下的所有角色信息"""

    __tablename__ = "account_characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String(100), nullable=False, index=True)
    character_name = Column(String(100), nullable=False, index=True)
    profession = Column(String(50), nullable=True)
    first_seen_date = Column(Date, nullable=False)
    last_seen_date = Column(Date, nullable=False)
    seen_count = Column(Integer, default=1)

    __table_args__ = (
        Index("uk_account_character", "account_name", "character_name", unique=True),
        Index("idx_account_name", "account_name"),
        Index("idx_character_name", "character_name"),
    )

    def __repr__(self):
        return f"<AccountCharacter(account={self.account_name}, character={self.character_name})>"
