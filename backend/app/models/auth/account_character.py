# -*- coding: utf-8 -*-
# 模块功能：账号角色映射模型
# 作者：系统
# 创建日期?2026-05-03
# 依赖说明：SQLAlchemy
# 说明：支持同一account对应多个角色的映射关系

from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class AccountCharacter(Base):
    """账号角色映射??存储同一account下的所有角色信?""

    __tablename__ = "account_characters"
    __table_args__ = (
        Index("uk_account_character", "account_name", "character_name", unique=True),
        Index("idx_account_name", "account_name"),
        Index("idx_character_name", "character_name"),
        {"comment": "账号角色映射?},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="映射ID")
    account_name = Column(String(100), nullable=False, index=True, comment="账号名称")
    character_name = Column(String(100), nullable=False, index=True, comment="角色名称")
    profession = Column(String(50), nullable=True, comment="职业")
    first_seen_date = Column(Date, nullable=False, comment="首次出现日期")
    last_seen_date = Column(Date, nullable=False, comment="最后出现日期)
    seen_count = Column(Integer, default=1, comment="出现次数")

    def __repr__(self):
        return f"<AccountCharacter(account={self.account_name}, character={self.character_name})>"
