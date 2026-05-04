# -*- coding: utf-8 -*-
"""
WvW 战斗报告 API Schema

设计原则：
  - 扁平化结构，前端易于消费
  - 不追求 EI 的完整字段，聚焦 WvW 核心需求
  - 使用显式字段而非 Dict[str, Any]，提高 API 文档可读性
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =====================================================================
# 基础响应
# =====================================================================
class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    code: int = 200


# =====================================================================
# 玩家摘要（用于排行榜）
# =====================================================================
class WvwPlayerSummary(BaseModel):
    player_id: int
    agent_index: Optional[int] = None
    account: Optional[str] = None
    character_name: str
    profession: str
    group_id: int = 1
    has_commander_tag: bool = False
    damage: int = 0
    dps: int = 0
    power_damage: int = 0
    condi_damage: int = 0
    critical_rate: float = 0.0
    flanking_rate: float = 0.0
    missed: int = 0
    glance_rate: float = 0.0
    swap_count: int = 0
    damage_taken: int = 0
    down_count: int = 0
    dead_count: int = 0
    condi_cleanse: int = 0
    healing: int = 0
    rotation_length: int = 0


# =====================================================================
# 玩家详情
# =====================================================================
class WvwPlayerDetailResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


# =====================================================================
# 目标摘要
# =====================================================================
class WvwTargetSummary(BaseModel):
    target_id: int
    agent_index: Optional[int] = None
    name: str
    enemy_player: bool = False
    total_health: Optional[int] = None
    final_health: Optional[int] = None
    dps_all: List[Dict[str, Any]] = []
    defenses: List[Dict[str, Any]] = []


# =====================================================================
# 阶段摘要
# =====================================================================
class WvwPhaseSummary(BaseModel):
    phase_id: int
    phase_index: int
    name: str
    start_ms: int
    end_ms: int
    duration_ms: int
    breakbar_phase: bool = False
    targets: List[Dict[str, Any]] = []


# =====================================================================
# 时间线事件
# =====================================================================
class WvwTimelineEvent(BaseModel):
    time_ms: int
    event_type: str
    agent_instid: int
    agent_name: str
    skill_id: int


# =====================================================================
# 技能条目
# =====================================================================
class WvwSkillEntry(BaseModel):
    gw2_skill_id: int
    name: Optional[str] = None
    auto_attack: bool = False
    can_crit: bool = False
    is_swap: bool = False
    icon: Optional[str] = None


# =====================================================================
# 报告列表项
# =====================================================================
class WvwReportListItem(BaseModel):
    log_id: int
    log_name: Optional[str] = None
    duration_ms: int = 0
    duration_sec: int = 0
    player_count: int = 0
    uploaded_at: Optional[str] = None


# =====================================================================
# 各端点响应
# =====================================================================
class WvwSummaryResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwPlayersResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwTargetsResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwPhasesResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwTimelineResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwSkillMapResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None


class WvwReportListResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None
