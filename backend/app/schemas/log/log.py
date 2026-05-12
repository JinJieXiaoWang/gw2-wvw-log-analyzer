# 模块功能：日志文件数据验证模型# 作者：系统
# 创建日期?2026-04-27
# 依赖说明：pydantic v2
# 说明：Log 相关 schema 仅反映文件上传管理信息，不包含解析业务数据?#       服务器、地图等解析结果?Fight / evtc_header 等子表提供?
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LogBase(BaseModel):
    # 功能：日志基础模型
    filename: str


class LogCreate(LogBase):
    # 功能：日志创建模型（内部使用?
    file_path: str
    file_size_compressed: Optional[int] = None
    file_size_raw: Optional[int] = None


class LogUpdate(BaseModel):
    # 功能：日志更新模型
    parse_status: Optional[str] = None
    parse_time_ms: Optional[int] = None
    parsed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_path: Optional[str] = None


class LogResponse(LogBase):
    # 功能：日志响应模型
    model_config = ConfigDict(from_attributes=True)

    id: int
    log_uuid: Optional[str] = None
    file_sha256: Optional[str] = None
    file_size_compressed: Optional[int] = None
    file_size_raw: Optional[int] = None
    file_path: Optional[str] = None
    upload_time: Optional[datetime] = None
    parse_status: Optional[str] = None
    parse_time_ms: Optional[int] = None
    parsed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    dps_report_permalink: Optional[str] = None
    upload_ip: Optional[str] = None
    uploaded_by: Optional[int] = None


class LogDetailResponse(LogResponse):
    # 功能：日志详情响应模型
    fights: List["FightResponse"] = []


class LogListResponse(BaseModel):
    # 功能：日志列表响应模型
    model_config = ConfigDict(from_attributes=True)

    items: List[LogResponse]
    total: int
    page: int
    page_size: int


class ParseProgressResponse(BaseModel):
    # 功能：解析进度响应模型
    model_config = ConfigDict(from_attributes=True)

    stage: str
    progress: int
    current_file: str
    players_found: int
    events_processed: int
    errors: List[str]
    warnings: List[str]
    elapsed_seconds: Optional[float] = None


class ParseResultResponse(BaseModel):
    # 功能：解析结果响应模型
    model_config = ConfigDict(from_attributes=True)

    success: bool
    log_id: int
    fight_id: Optional[int] = None
    player_count: int
    duration_ms: int
    error_message: Optional[str] = None


class PlayerStatsResponse(BaseModel):
    # 功能：玩家统计响应模型
    model_config = ConfigDict(from_attributes=True)

    account_name: str
    name: str
    profession: str
    team_id: int
    group: int
    has_commander_tag: bool
    damage: int
    power_damage: int
    condi_damage: int
    dps: int
    kills: int
    deaths: int
    downs: int
    downs_inflicted: int
    time_in_combat: int
    damage_taken: int
    boon_strips: int
    condi_cleanses: int
    breakbar_damage: float


class FightInfoResponse(BaseModel):
    # 功能：战斗信息响应模型
    model_config = ConfigDict(from_attributes=True)

    map_name: str
    server_name: str
    total_damage: int
    total_healing: int
    kill_count: int
    death_count: int
    duration_sec: int
    duration_str: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_wvw: bool
    gw2_build: int


class BuffUptimeResponse(BaseModel):
    # 功能：BUFF覆盖率响应模型
    model_config = ConfigDict(from_attributes=True)

    buff_name: str
    uptime_ms: int
    uptime_percent: float


class SkillRotationResponse(BaseModel):
    # 功能：技能循环响应模型
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skill_name: str
    time: int
    duration: int


class ValidationReportResponse(BaseModel):
    # 功能：数据验证报告响应模型
    model_config = ConfigDict(from_attributes=True)

    passed: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
