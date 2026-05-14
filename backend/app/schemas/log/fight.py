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

    damage: int = 0
    dps: int = 0
    healing: int = 0
    killed: int = 0
    dead_count: int = 0
    damage_taken: int = 0
    down_count: int = 0
    resurrects: int = 0


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
    has_commander_tag: bool = False


class FightListResponse(BaseModel):
    # 功能：战斗列表响应模型    model_config = ConfigDict(from_attributes=True)

    items: List[FightResponse]
    total: int
    page: int
    page_size: int
