# -*- coding: utf-8 -*-
# 模块功能：评分规则配置模型
# 说明：基于角色类型的灵活评分规则配置

from app.config.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)


class ScoringRule(Base):
    """评分规则配置模型

    支持按角色类型（输出/辅助/承伤）和职业配置不同的评分权重和阈值?
    profession ?null 时表示该 role_type 的通用规则；有值时表示该职业的特定规则?
    """

    __tablename__ = "scoring_rule"
    __table_args__ = (
        UniqueConstraint(
            "role_type", "profession", "dimension", name="uk_role_profession_dimension"
        ),
        {"comment": "评分规则配置"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="规则ID")
    role_type = Column(
        String(50),
        nullable=False,
        comment="角色类型: dps-输出, support-辅助, tank-承伤",
    )
    profession = Column(
        String(50),
        nullable=True,
        comment="精英特长/职业名称，null表示通用规则",
    )
    dimension = Column(
        String(50),
        nullable=False,
        comment="评分维度: damage/power_damage/condition_damage/healing/boons/survival/strips/cleanses/kills/breakbar",
    )
    weight = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="权重系数(0~1)",
    )
    min_value = Column(
        Float,
        nullable=True,
        comment="最小值阈值，低于此值计为0",
    )
    max_value = Column(
        Float,
        nullable=True,
        comment="最大值上限，用于归一化评分",
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用: 1-启用, 0-禁用",
    )
    description = Column(
        String(500),
        nullable=True,
        comment="规则描述说明",
    )
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="显示排序",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="更新时间",
    )


class ScoringRulePreset(Base):
    """评分规则预设?

    存储不同角色类型的完整预设方案，便于一键切换和恢复默认预设规则。
    """

    __tablename__ = "scoring_rule_preset"
    __table_args__ = {"comment": "评分规则预设方案"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="预设ID")
    role_type = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="角色类型: dps/support/tank",
    )
    preset_name = Column(
        String(200),
        nullable=False,
        comment="预设名称",
    )
    preset_data = Column(
        Text,
        nullable=False,
        comment="预设JSON数据",
    )
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为系统默认预设",
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="更新时间",
    )
