# -*- coding: utf-8 -*-
# 模块功能：评分系统API 响应 Schema
# 作者：System
# 创建日期：2026-05-05
# 依赖说明：Pydantic v2
# 说明：为 /api/v1/scoring/* 接口提供结构化响应模型，确保 Swagger Docs 清晰展示

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """玩家评分维度明细"""

    damage: float = Field(0.0, ge=0, le=100, description="伤害维度评分")
    power_damage: float = Field(0.0, ge=0, le=100, description="直伤维度评分")
    condition_damage: float = Field(0.0, ge=0, le=100, description="症状维度评分")
    healing: float = Field(0.0, ge=0, le=100, description="治疗维度评分")
    boons: float = Field(0.0, ge=0, le=100, description="增益维度评分")
    alacrity: float = Field(0.0, ge=0, le=100, description="敏捷维度评分")
    quickness: float = Field(0.0, ge=0, le=100, description="急速维度评分")
    survival: float = Field(0.0, ge=0, le=100, description="生存维度评分")
    strips: float = Field(0.0, ge=0, le=100, description="增益移除维度评分")
    cleanses: float = Field(0.0, ge=0, le=100, description="症状清除维度评分")
    kills: float = Field(0.0, ge=0, le=100, description="击杀维度评分")
    breakbar: float = Field(0.0, ge=0, le=100, description="破蔑视维度评分")


class PlayerScoreItem(BaseModel):
    """单个玩家评分结果"""

    member_id: int = Field(..., description="成员 ID（关系members 表）")
    account: str = Field(..., description="玩家账号")
    character_name: Optional[str] = Field(None, description="角色名称")
    profession: Optional[str] = Field(None, description="职业")
    total_score: float = Field(..., ge=0, le=100, description="综合评分总分（0-100）")
    grade: str = Field(..., description="评分等级（S/A/B/C/D/F）")
    grade_label: str = Field(..., description="评分等级中文标签（如 S级、A级）")
    breakdown: ScoreBreakdown = Field(..., description="各维度评分明细")


class FightScoreResult(BaseModel):
    """一场战斗的评分计算结果"""

    fight_id: int = Field(..., description="战斗记录 ID（关系fights 表）")
    total_players: int = Field(..., ge=0, description="参与评分的玩家总数")
    scores: List[PlayerScoreItem] = Field(default_factory=list, description="玩家评分列表")
    scoring_rules: Dict[str, float] = Field(
        default_factory=dict, description="本次评分使用的规则权重配置"
    )


class ScoringRulesResult(BaseModel):
    """评分规则配置结果"""

    rules: Dict[str, float] = Field(..., description="评分规则键值对（如 damage_weight: 0.35）")
    role_type: str = Field("dps", description="当前规则对应的角色类型（dps/support/tank）")
    is_default: bool = Field(False, description="是否为系统默认规则（数据库无配置时回退）")
