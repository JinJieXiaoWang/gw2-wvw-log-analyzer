# 模块功能：战斗记录数据验证模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：pydantic v2

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FightBase(BaseModel):
    # 功能：战斗基础模型
    map_name: Optional[str] = None
    server_name: Optional[str] = None


class FightCreate(FightBase):
    # 功能：战斗创建模型    log_id: int
    start_time: datetime


class FightUpdate(BaseModel):
    # 功能：战斗更新模型    end_time: Optional[datetime] = None
    duration_sec: Optional[int] = None
    total_damage: Optional[int] = None
    total_healing: Optional[int] = None
    kill_count: Optional[int] = None
    death_count: Optional[int] = None
    is_ai_analyzed: Optional[bool] = None


class FightResponse(FightBase):
    # 功能：战斗响应模型
    model_config = ConfigDict(from_attributes=True)

    id: int
    log_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_sec: int
    total_damage: int
    total_healing: int
    kill_count: int
    death_count: int
    player_count: int = 0
    friendly_player_count: int = 0
    enemy_player_count: int = 0
    enemy_composition: Optional[str] = None
    is_ai_analyzed: bool


class FightDetailResponse(FightResponse):
    # 功能：战斗详情响应模型
    fight_stats: List["FightStatsResponse"] = []


class FightStatsBase(BaseModel):
    # 功能：战斗统计基础模型
    model_config = ConfigDict(from_attributes=True)

    # === DPS / 伤害 / 治疗 ===
    damage: int = 0
    dps: int = 0
    power_damage: int = 0
    condi_damage: int = 0
    breakbar_damage: int = 0
    healing: int = 0

    # === 命中质量 ===
    critical_rate: int = 0
    flanking_rate: int = 0
    glance_rate: int = 0
    missed: int = 0
    interrupts: int = 0
    swap_count: int = 0

    # === 击杀 / 控制 ===
    killed: int = 0
    downed: int = 0

    # === 防御 / 生存 ===
    damage_taken: int = 0
    blocked_count: int = 0
    evaded_count: int = 0
    dodge_count: int = 0
    down_count: int = 0
    dead_count: int = 0
    boon_strips: int = 0
    condition_cleanses: int = 0
    downed_damage_taken: int = 0
    interrupted_count: int = 0

    # === 支援 ===
    resurrects: int = 0
    condi_cleanse_ally: int = 0
    boon_strips_ally: int = 0
    stun_break: int = 0
    removed_stun_duration: float = 0.0

    # === 关键 Buff 覆盖率 ===
    might_uptime: float = 0.0
    fury_uptime: float = 0.0
    quickness_uptime: float = 0.0
    alacrity_uptime: float = 0.0
    protection_uptime: float = 0.0
    stability_uptime: float = 0.0
    regeneration_uptime: float = 0.0
    swiftness_uptime: float = 0.0
    vigor_uptime: float = 0.0
    aegis_uptime: float = 0.0
    resistance_uptime: float = 0.0
    resolution_uptime: float = 0.0

    # === 高级战斗指标 ===
    down_contribution: int = 0
    against_downed_damage: int = 0
    applied_cc_duration: int = 0
    applied_cc_count: int = 0
    barrier_damage_absorbed: int = 0
    condition_damage_taken: int = 0
    power_damage_taken: int = 0
    received_cc_duration: int = 0
    might_uptime_active: float = 0.0
    quickness_uptime_active: float = 0.0
    alacrity_uptime_active: float = 0.0
    avg_boons: float = 0.0
    avg_conditions: float = 0.0

    # === 技能效率与位置 ===
    wasted: int = 0
    saved: int = 0
    skill_cast_uptime: float = 0.0
    stack_dist: float = 0.0
    dist_to_com: float = 0.0

    # === 倒地/死亡详情 ===
    down_duration: int = 0
    dead_duration: int = 0
    dc_count: int = 0
    dc_duration: int = 0

    # === AI 评分 ===
    ai_score: float = 0.0
    score_grade: str = ""
    role_type: Optional[str] = None
    rule_version: int = 0
    scoring_profession_rule: Optional[str] = None


class FightStatsCreate(FightStatsBase):
    # 功能：战斗统计创建模型    fight_id: int
    member_id: int


class FightStatsResponse(FightStatsBase):
    # 功能：战斗统计响应模型    model_config = ConfigDict(from_attributes=True)

    id: int
    fight_id: int
    member_id: int
    account: Optional[str] = None
    character_name: Optional[str] = None
    profession: Optional[str] = None
    group_id: int = 0
    team_id: int = 0
    has_commander_tag: bool = False
    score_breakdown: Optional[dict] = None


class FightListResponse(BaseModel):
    # 功能：战斗列表响应模型    model_config = ConfigDict(from_attributes=True)

    items: List[FightResponse]
    total: int
    page: int
    page_size: int
