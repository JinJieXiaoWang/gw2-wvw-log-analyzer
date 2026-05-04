# -*- coding: utf-8 -*-
"""
ZEVTC 解析器数据模型

定义了 Header、Agent、Skill、Event 的纯数据类，以及解析结果与导入结果。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True, slots=True)
class EvtcHeader:
    """EVTC 文件头 (24 bytes)"""

    magic: str  # "EVTC"
    build_date: str  # "YYYYMMDD"
    revision: int  # uint8
    auto_flag: int  # uint8, 1=本地录制
    boss_id: int  # uint16
    agent_count: int  # uint32
    skill_count: int  # uint32 (部分实现在 header 中读取)

    @property
    def record_date(self) -> Optional[str]:
        """将 build_date 转为 ISO 日期格式"""
        if len(self.build_date) == 8 and self.build_date.isdigit():
            return (
                f"{self.build_date[:4]}-{self.build_date[4:6]}-{self.build_date[6:8]}"
            )
        return None

    @property
    def evtc_version(self) -> str:
        return f"EVTC{self.build_date}-r{self.revision}"


@dataclass(frozen=True, slots=True)
class EvtcAgent:
    """EVTC Agent 记录 (96 bytes)"""

    agent_index: int  # 在 Agent 表中的索引
    address: int  # uint64
    prof: int  # uint32
    is_elite: int  # uint32
    toughness: int  # int16 → 存 int
    concentration: int  # int16 → 存 int
    healing: int  # int16 → 存 int
    hitbox_width: int  # int16 → 存 int
    condition: int  # int16 → 存 int
    hitbox_height: int  # int16 → 存 int
    name_raw: bytes  # 原始 UTF-8 字节
    member_name: str  # 玩家角色名 (name_raw 第一个空终止段)
    account_name: Optional[str]  # 账号名 (name_raw 第二个空终止段, ZEVTC中可能为空)

    @property
    def agent_type(self) -> str:
        from .constants import PROFESSION_MAP, UINT32_MAX

        if self.prof == UINT32_MAX:
            return "npc"
        if self.prof in PROFESSION_MAP:
            return "player"
        return "unknown"

    @property
    def is_player(self) -> bool:
        return self.agent_type == "player"

    @property
    def is_npc(self) -> bool:
        return self.agent_type == "npc"


@dataclass(frozen=True, slots=True)
class EvtcSkill:
    """EVTC Skill 记录 (68 bytes)"""

    skill_index: int  # 在 Skill 表中的索引
    gw2_skill_id: int  # int32 (可能为负)
    name_raw: bytes  # 原始 UTF-8 字节
    name: str  # 解析后名称


@dataclass(frozen=True, slots=True)
class EvtcEvent:
    """EVTC Combat Event 记录 (60/64 bytes)"""

    event_index: int  # 在 Event 流中的索引
    time: int  # uint64, 毫秒时间戳
    src_agent: int  # uint64
    dst_agent: int  # uint64
    value: int  # int32
    buff_dmg: int  # int32
    overstack_value: int  # uint32 (经实测验证，支持大于 65535 的值)
    skill_id: int  # uint32 (经实测验证，GW2 技能 ID 可 > 65535)
    src_instid: int  # uint16
    dst_instid: int  # uint16
    src_master_instid: int  # uint16
    dst_master_instid: int  # uint16
    iff: int  # uint8
    buff: int  # uint8
    result: int  # uint8
    is_activation: int  # uint8
    is_buffremove: int  # uint8
    is_ninety: int  # uint8
    is_fifty: int  # uint8
    is_moving: int  # uint8
    is_statechange: int  # uint8
    is_flanking: int  # uint8
    is_shields: int  # uint8
    is_offcycle: int  # uint8
    # Revision 0 无 pad；Revision 1 有 4 字节填充
    pad: bytes = field(default=b"\x00" * 4)

    @property
    def time_sec(self) -> float:
        return self.time / 1000.0

    def to_tuple(self) -> Tuple:
        """转换为可用于 executemany 的元组（不含 event_index）"""
        return (
            self.time,
            self.src_agent,
            self.dst_agent,
            self.value,
            self.buff_dmg,
            self.overstack_value,
            self.skill_id,
            self.src_instid,
            self.dst_instid,
            self.src_master_instid,
            self.dst_master_instid,
            self.iff,
            self.buff,
            self.result,
            self.is_activation,
            self.is_buffremove,
            self.is_ninety,
            self.is_fifty,
            self.is_moving,
            self.is_statechange,
            self.is_flanking,
            self.is_shields,
            self.is_offcycle,
        )


@dataclass
class ParseResult:
    """单次解析的完整结果"""

    header: EvtcHeader
    agents: List[EvtcAgent]
    skills: List[EvtcSkill]
    events: List[EvtcEvent]
    raw_data_size: int  # EVTC 解压后大小
    compressed_size: int  # ZEVTC 压缩后大小
    event_size: int  # 60 或 64
    filename: str  # 原始文件名
    file_sha256: str  # SHA-256 指纹

    # 派生统计
    @property
    def agent_count(self) -> int:
        return len(self.agents)

    @property
    def skill_count(self) -> int:
        return len(self.skills)

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def first_event_time(self) -> Optional[int]:
        if self.events:
            return min(e.time for e in self.events)
        return None

    @property
    def last_event_time(self) -> Optional[int]:
        if self.events:
            return max(e.time for e in self.events)
        return None

    @property
    def duration_ms(self) -> int:
        if self.first_event_time is not None and self.last_event_time is not None:
            return max(0, self.last_event_time - self.first_event_time)
        return 0

    def get_statechange_events(self) -> List[EvtcEvent]:
        return [e for e in self.events if e.is_statechange > 0]

    def get_combat_meta_stats(self) -> Dict[str, int]:
        """计算 evtc_combat_meta 所需的聚合统计"""
        stats = {
            "enter_combat_count": 0,
            "change_down_count": 0,
            "change_dead_count": 0,
            "weapon_swap_count": 0,
            "health_update_count": 0,
            "position_update_count": 0,
            "team_change_count": 0,
        }
        from .constants import StateChange

        sc_map = {
            StateChange.ENTER_COMBAT: "enter_combat_count",
            StateChange.CHANGE_DOWN: "change_down_count",
            StateChange.CHANGE_DEAD: "change_dead_count",
            StateChange.WEAPON_SWAP: "weapon_swap_count",
            StateChange.HEALTH_UPDATE: "health_update_count",
            StateChange.POSITION: "position_update_count",
            StateChange.TEAM_CHANGE: "team_change_count",
        }
        for e in self.events:
            if e.is_statechange in sc_map:
                stats[sc_map[e.is_statechange]] += 1
        return stats

    def get_events_per_second(self) -> List[Dict[str, Any]]:
        """计算 evtc_event_per_second 秒级聚合"""
        from collections import defaultdict

        if not self.events or self.duration_ms == 0:
            return []

        first_time = self.first_event_time or 0
        buckets: Dict[Tuple[int, int], Dict[str, Any]] = defaultdict(
            lambda: {
                "event_count": 0,
                "total_value": 0,
                "total_buff_dmg": 0,
                "damage_events": 0,
                "buff_apply_events": 0,
                "buff_remove_events": 0,
                "crit_count": 0,
                "hit_count": 0,
                "missed_count": 0,
            }
        )

        from .constants import Result

        for e in self.events:
            # 跳过 StateChange 事件（它们的 time 字段可能被重用于其他目的）
            if e.is_statechange != 0:
                continue
            sec = int((e.time - first_time) / 1000)
            key = (e.src_agent, sec)
            b = buckets[key]
            b["event_count"] += 1
            b["total_value"] += e.value
            b["total_buff_dmg"] += e.buff_dmg

            if e.buff == 0 and (e.value > 0 or e.buff_dmg > 0):
                b["damage_events"] += 1
            elif e.buff > 0 and e.is_buffremove == 0 and e.value > 0:
                b["buff_apply_events"] += 1
            elif e.buff > 0 and e.is_buffremove > 0:
                b["buff_remove_events"] += 1

            if e.result == Result.CRIT:
                b["crit_count"] += 1
            if e.result in (
                Result.NORMAL,
                Result.CRIT,
                Result.INTERRUPT,
                Result.KILLING_BLOW,
                Result.DOWNED,
            ):
                b["hit_count"] += 1
            if e.result in (Result.BLOCK, Result.EVADE, Result.ABSORB, Result.BLIND):
                b["missed_count"] += 1

        result = []
        for (src_agent, sec), data in sorted(buckets.items()):
            result.append(
                {
                    "src_agent": src_agent,
                    "second_offset": sec,
                    **data,
                }
            )
        return result


@dataclass
class ImportResult:
    """数据库导入结果"""

    log_id: int
    log_uuid: str
    filename: str
    file_sha256: str
    status: str  # "completed", "updated", "failed"
    is_duplicate: bool  # 是否为重复导入（更新模式）
    agent_count: int
    skill_count: int
    event_count: int
    duration_ms: int
    parse_time_ms: int
    parsed_at: datetime
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "log_uuid": self.log_uuid,
            "filename": self.filename,
            "file_sha256": self.file_sha256,
            "status": self.status,
            "is_duplicate": self.is_duplicate,
            "agent_count": self.agent_count,
            "skill_count": self.skill_count,
            "event_count": self.event_count,
            "duration_ms": self.duration_ms,
            "parse_time_ms": self.parse_time_ms,
            "parsed_at": self.parsed_at.isoformat() if self.parsed_at else None,
            "error_message": self.error_message,
        }
