# -*- coding: utf-8 -*-
# 模块功能：战斗分析响应Schema定义（兼容ZEVTC分析服务?# 作者：系统
# 创建日期?2026-05-01
# 依赖说明：Pydantic

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    code: int = 200


class FightDetailsResponse(BaseModel):
    fight_id: int
    log_id: int
    basic_info: Dict[str, Any]
    meta_info: Dict[str, Any]
    summary: Dict[str, Any]


class PlayerStatsResponse(BaseModel):
    identifier: Dict[str, Any]
    stats: Dict[str, Any]


class PlayersListResponse(BaseModel):
    players: List[Dict[str, Any]]
    total: int = 0


class PlayerDetailResponse(BaseModel):
    identifier: Dict[str, Any]
    stats: Dict[str, Any]
    details: Optional[Dict[str, Any]] = None


class PlayerSkillDamageResponse(BaseModel):
    player_info: Dict[str, Any]
    skill_breakdown: Dict[str, Any]
    total_damage: int = 0


class PlayerDpsSeriesResponse(BaseModel):
    player_info: Dict[str, Any]
    dps_series: List[Dict[str, Any]]
    duration_ms: int = 0


class LeaderboardResponse(BaseModel):
    total_damage: int = 0
    ranking: List[Dict[str, Any]]
    top_damage_dealer: Optional[Dict[str, Any]] = None


FightDetailsApiResponse = ApiResponse
PlayersListApiResponse = ApiResponse
PlayerDetailApiResponse = ApiResponse
PlayerSkillDamageApiResponse = ApiResponse
PlayerDpsSeriesApiResponse = ApiResponse
LeaderboardApiResponse = ApiResponse
