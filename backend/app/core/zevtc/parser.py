# -*- coding: utf-8 -*-
# 模块功能：evtc/zevtc二进制文件解析器
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：struct, zipfile, mmap, json

import datetime
import json
import logging
import mmap
import os
import struct
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.zevtc import (
    EvtcAgent,
    EvtcByteReader,
    EvtcEvent,
    EvtcHeader,
)
from app.core.zevtc import EvtcParser as CoreEvtcParser
from app.core.zevtc import (
    EvtcSkill,
)
from app.core.zevtc import ParseResult as CoreParseResult
from app.core.zevtc.constants import (
    ELITE_SPEC_MAP,
    IFF,
    PROFESSION_MAP,
    UINT32_MAX,
    Activation,
    BuffRemove,
    Result,
    StateChange,
)
from app.core.zevtc.exceptions import FileCorruptedError as _FileCorruptedError
from app.core.zevtc.exceptions import InvalidFileFormatError as _InvalidFileFormatError
from app.core.zevtc.exceptions import (
    UnsupportedVersionError as _UnsupportedVersionError,
)
from app.core.zevtc.exceptions import ZevtcError as _ZevtcError

logger = logging.getLogger(__name__)

# 精英特长映射表已从 app.core.zevtc.constants.ELITE_SPEC_MAP 导入
# 包含全部 36 个精英特长（9 职业 × 4 资料片）

COMMON_BUFFS = {
    1122: "Stability",
    26980: "Resistance",
    717: "Protection",
    719: "Swiftness",
    725: "Fury",
    740: "Might",
    718: "Regeneration",
    726: "Vigor",
    743: "Aegis",
    1187: "Quickness",
    30328: "Alacrity",
    742: "Vigor",
    738: "Quickness",
}

INT32_MAX = 2147483647
AGENT_SIZE = 96
SKILL_SIZE = 68

# 单次伤害最大值限制（100万，合理的单次攻击伤害上限）
MAX_DAMAGE_PER_HIT = 1000000
# 战斗总伤害最大值限制（WvW场景，约10分钟战斗的合理上限）
MAX_TOTAL_DAMAGE = 50000000
EVENT_REV0 = 60
EVENT_REV1 = 64

SC_NONE = StateChange.NONE
SC_ENTER_COMBAT = StateChange.ENTER_COMBAT
SC_EXIT_COMBAT = StateChange.EXIT_COMBAT
SC_CHANGE_UP = StateChange.CHANGE_UP
SC_CHANGE_DEAD = StateChange.CHANGE_DEAD
SC_CHANGE_DOWN = StateChange.CHANGE_DOWN
SC_SPAWN = StateChange.SPAWN
SC_DESPAWN = StateChange.DESPAWN
SC_HEALTH = StateChange.HEALTH_UPDATE
SC_LOG_START = StateChange.LOG_START
SC_LOG_END = StateChange.LOG_END
SC_WEAPON_SWAP = StateChange.WEAPON_SWAP
SC_MAX_HEALTH = StateChange.MAX_HEALTH_UPDATE
SC_POV = StateChange.POINT_OF_VIEW
SC_LANGUAGE = StateChange.LANGUAGE
SC_GW2_BUILD = StateChange.GW2_BUILD
SC_SHARD_ID = StateChange.SHARD_ID
SC_REWARD = StateChange.REWARD
SC_BUFF_INITIAL = StateChange.BUFF_INITIAL
SC_POSITION = StateChange.POSITION
SC_VELOCITY = StateChange.VELOCITY
SC_FACING = StateChange.ROTATION
SC_TEAM_CHANGE = StateChange.TEAM_CHANGE
SC_BREAK_BAR = StateChange.BREAKBAR_STATE
SC_TAG = StateChange.TAG

RESULT_KILLING_BLOW = Result.KILLING_BLOW
RESULT_DOWNING_BLOW = Result.DOWNED

IFF_FRIEND = IFF.FRIEND
IFF_FOE = IFF.FOE
IFF_UNKNOWN = IFF.UNKNOWN

BUFF_IDS = {
    717: "Protection",
    718: "Regeneration",
    719: "Swiftness",
    725: "Fury",
    726: "Vigor",
    740: "Might",
    743: "Aegis",
    1122: "Stability",
    1187: "Quickness",
    30328: "Alacrity",
    26980: "Resistance",
}

_BUFF_ID_SET = frozenset(BUFF_IDS.keys())


# 保留旧版异常类以兼容现有调用方
class ZevtcParseError(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidFileFormatError(ZevtcParseError):
    pass


class FileCorruptedError(ZevtcParseError):
    pass


class UnsupportedVersionError(ZevtcParseError):
    pass


class DataExtractionError(ZevtcParseError):
    pass


def _map_exception(e: _ZevtcError) -> ZevtcParseError:
    """将核心解析器异常映射为旧版异常"""
    if isinstance(e, _InvalidFileFormatError):
        return InvalidFileFormatError(e.message, e.details)
    if isinstance(e, _FileCorruptedError):
        return FileCorruptedError(e.message, e.details)
    if isinstance(e, _UnsupportedVersionError):
        return UnsupportedVersionError(e.message, e.details)
    return ZevtcParseError(e.message, e.details)


@dataclass
class AgentInfo:
    addr: int
    prof: int
    elite: int
    toughness: int
    concentration: int
    healing: int
    condition: int
    hitbox_w: int
    hitbox_h: int
    name: str
    account: str
    is_player: bool
    is_gadget: bool
    team: Optional[int] = None
    instid: Optional[int] = None

    @property
    def profession(self) -> str:
        if not self.is_player:
            return "Unknown"
        if self.elite in ELITE_SPEC_MAP:
            return ELITE_SPEC_MAP[self.elite]
        if self.prof in PROFESSION_MAP:
            return PROFESSION_MAP[self.prof]
        return "Unknown"

    @property
    def account_clean(self) -> str:
        return self.account.lstrip(":")


@dataclass
class CombatMeta:
    build_date: str = ""
    revision: int = 0
    boss_id: int = 0
    gw2_build: int = 0
    map_id: int = 0
    language: int = 0
    shard_id: int = 0
    log_start: Optional[int] = None
    log_end: Optional[int] = None
    pov_addr: Optional[int] = None

    @property
    def duration_s(self) -> float:
        if self.log_start is not None and self.log_end is not None:
            return float(self.log_end - self.log_start) / 1000.0
        return 0.0

    @property
    def duration_ms(self) -> int:
        if self.log_start is not None and self.log_end is not None:
            return max(0, int(self.log_end - self.log_start))
        return 0

    @property
    def start_datetime(self) -> Optional[str]:
        if self.log_start is not None:
            dt = datetime.datetime.fromtimestamp(
                self.log_start / 1000.0, datetime.timezone.utc
            )
            return dt.strftime("%Y-%m-%d %H:%M:%S +00:00")
        return None

    @property
    def end_datetime(self) -> Optional[str]:
        if self.log_end is not None:
            dt = datetime.datetime.fromtimestamp(
                self.log_end / 1000.0, datetime.timezone.utc
            )
            return dt.strftime("%Y-%m-%d %H:%M:%S +00:00")
        return None

    @property
    def map_name(self) -> str:
        MAP_NAMES = {
            38: "Eternal Battlegrounds",
            1099: "Eternal Battlegrounds",
            1143: "Red Desert Borderlands",
            1210: "Alpine Borderlands (Blue)",
            1052: "Alpine Borderlands (Green)",
            1062: "Red Desert Borderlands",
            968: "Edge of the Mists",
        }
        return MAP_NAMES.get(self.map_id, f"Map:{self.map_id}")

    @property
    def is_wvw(self) -> bool:
        WVW_MAPS = {38, 1099, 1143, 1210, 1052, 1062, 968, 1009}
        return self.map_id in WVW_MAPS

    @property
    def duration_str(self) -> str:
        ms = self.duration_ms
        seconds = ms // 1000
        ms_remain = ms % 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}m {seconds:02d}s {ms_remain:03d}ms"


@dataclass
class PlayerStats:
    addr: int
    name: str
    account: str
    profession: str
    team: Optional[int] = None
    instance_id: Optional[int] = None

    total_damage: int = 0
    power_damage: int = 0
    condi_damage: int = 0
    breakbar_damage: float = 0.0
    damage_taken: int = 0
    own_downs: int = 0
    own_deaths: int = 0
    combat_time_ms: int = 0
    downs_inflicted: int = 0
    kills_inflicted: int = 0
    boon_strips: int = 0
    condi_cleanses: int = 0

    buff_uptime: Dict[str, float] = field(default_factory=dict)

    group: int = 1
    has_commander_tag: bool = False
    friendly_npc: bool = False
    not_in_squad: bool = False
    is_fake: bool = False
    guild_id: str = ""
    total_health: int = -1
    toughness: int = 0
    condition: int = 0
    concentration: int = 0
    healing: int = 0
    hitbox_height: int = 0
    hitbox_width: int = 0

    dps_all: List[Dict] = field(default_factory=list)
    stats_all: List[Dict] = field(default_factory=list)
    defenses: List[Dict] = field(default_factory=list)
    support: List[Dict] = field(default_factory=list)
    total_damage_dist: List[List] = field(default_factory=list)
    total_damage_taken: List[List] = field(default_factory=list)
    damage1s: List[List] = field(default_factory=list)
    power_damage1s: List[List] = field(default_factory=list)
    condition_damage1s: List[List] = field(default_factory=list)
    dps_targets: List[List] = field(default_factory=list)
    target_damage1s: List[List] = field(default_factory=list)
    target_power_damage1s: List[List] = field(default_factory=list)
    target_condition_damage1s: List[List] = field(default_factory=list)
    target_damage_dist: List[List] = field(default_factory=list)
    stats_targets: List[List] = field(default_factory=list)
    buff_uptimes: List[Dict] = field(default_factory=list)
    buff_uptimes_active: List[Dict] = field(default_factory=list)
    self_buffs: List[Dict] = field(default_factory=list)
    self_buffs_active: List[Dict] = field(default_factory=list)
    weapons: List = field(default_factory=list)
    rotation: List[List] = field(default_factory=list)
    damage_modifiers: List[List] = field(default_factory=list)
    damage_modifiers_target: List[List] = field(default_factory=list)
    active_times: List[int] = field(default_factory=list)
    health_percents: List[int] = field(default_factory=list)
    barrier_percents: List[int] = field(default_factory=list)

    role: str = "dps"
    total_score: float = 0.0
    score_details: Dict = field(default_factory=dict)


def _calc_buff_uptime(events: List, duration_ms: int) -> int:
    if not events:
        return 0
    sorted_events = sorted(events, key=lambda x: x[0])
    active = False
    start_time = 0
    total = 0
    for t, typ in sorted_events:
        if typ == "apply" and not active:
            active = True
            start_time = t
        elif typ == "remove" and active:
            total += t - start_time
            active = False
    if active:
        total += duration_ms - start_time
    return max(0, min(total, duration_ms))


@dataclass
class ParseProgress:
    def __init__(self):
        self.stage = "初始化"
        self.progress = 0
        self.current_file = ""
        self.players_found = 0
        self.events_processed = 0
        self.errors = []
        self.warnings = []
        self.start_time = datetime.datetime.now()
        self.end_time: Optional[datetime.datetime] = None

    def update(self, stage: str, progress: int, **kwargs):
        self.stage = stage
        self.progress = progress
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        logger.debug(f"解析进度: {stage} - {progress}%")

    def add_error(self, error: str):
        self.errors.append(error)
        logger.error(f"解析错误: {error}")

    def add_warning(self, warning: str):
        self.warnings.append(warning)
        logger.warning(f"解析警告: {warning}")

    def finish(self):
        self.end_time = datetime.datetime.now()
        self.progress = 100

    def to_dict(self) -> Dict:
        return {
            "stage": self.stage,
            "progress": self.progress,
            "current_file": self.current_file,
            "players_found": self.players_found,
            "events_processed": self.events_processed,
            "errors": self.errors,
            "warnings": self.warnings,
            "elapsed_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time
                else None
            ),
        }


class DataValidator:
    @staticmethod
    def validate_parsed_data(data: Dict, reference: Optional[Dict] = None) -> Dict:
        errors = []
        warnings = []
        details = {}

        if not data:
            errors.append("解析数据为空")
            return {
                "passed": False,
                "errors": errors,
                "warnings": warnings,
                "details": details,
            }

        if "players" not in data:
            errors.append("缺少玩家数据")
        else:
            details["player_count"] = len(data["players"])

        if "durationMS" not in data:
            warnings.append("缺少战斗时长数据")

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details,
        }


class EnhancedZevtcParser:
    """基于核心解析器的增强版解析器，保留EI JSON生成功能"""

    def __init__(self, path: str, progress: Optional[ParseProgress] = None):
        self.path = path
        self.progress = progress or ParseProgress()

        self.meta = None
        self.agents = []
        self.agents_by_addr = {}
        self.skills = {}
        self.player_stats = {}

        self.all_events = []
        self.buff_trackers = {}
        self.instid_to_addr = {}
        self.combat_enter = {}
        self.combat_exit = {}

        self._fight_duration_ms = 0
        self._core_result: Optional[CoreParseResult] = None

    def parse(self) -> Dict[str, Any]:
        try:
            logger.info(f"开始解析文件: {self.path}")
            self.progress.update(
                "加载文件", 5, current_file=os.path.basename(self.path)
            )

            # 使用核心解析器进行底层解析
            core_parser = CoreEvtcParser(path=self.path)
            self._core_result = core_parser.parse_file(compute_sha256=False)

            self.progress.update("解析文件头", 10)
            self._build_meta_from_core()

            self.progress.update("解析代理信息", 20)
            self._build_agents_from_core()

            self.progress.update("解析技能信息", 30)
            self._build_skills_from_core()
            
            # 清理不需要的skill数据
            if hasattr(self._core_result, 'skills'):
                del self._core_result.skills

            self.progress.update("第一轮事件扫描", 40)
            self._first_pass_events()

            self.progress.update("第二轮事件扫描", 60)
            self._second_pass_events()
            
            # 清理事件数据（占用最大的部分）
            if hasattr(self._core_result, 'events'):
                del self._core_result.events

            self.progress.update("计算BUFF覆盖率", 75)
            self._calculate_buff_uptimes()

            self.progress.update("构建输出数据", 90)
            self._build_ei_players()
            result = self._generate_ei_json()

            self.progress.update("完成", 100, players_found=len(self.player_stats))
            self.progress.finish()

            logger.info(f"解析完成，找到{len(self.player_stats)}个玩家")
            
            # 主动清理大对象以降低内存峰值
            self._cleanup()
            
            return result

        except _ZevtcError as e:
            self._cleanup()
            raise _map_exception(e)
        except Exception as e:
            self._cleanup()
            logger.exception(f"解析异常: {e}")
            self.progress.add_error(str(e))
            raise ZevtcParseError(f"解析过程出错: {e}", {"path": self.path}) from e
    
    def _cleanup(self):
        """清理大对象以释放内存"""
        import gc
        
        # 清理核心结果
        self._core_result = None
        
        # 清空不需要的大列表
        self.all_events = []
        self.buff_trackers = {}
        
        # 清理agents（player_stats已包含需要的信息）
        self.agents = []
        self.agents_by_addr = {}
        self.skills = {}
        
        gc.collect()
        logger.debug(f"解析器清理完成")

    def _build_meta_from_core(self):
        h = self._core_result.header
        self.meta = CombatMeta(
            build_date=h.build_date,
            revision=h.revision,
            boss_id=h.boss_id,
        )

    def _build_agents_from_core(self):
        agents_list = []
        agents_by_addr = {}

        for ag in self._core_result.agents:
            is_player = ag.prof != UINT32_MAX
            is_gadget = ag.prof == UINT32_MAX and ag.is_elite == UINT32_MAX

            info = AgentInfo(
                addr=ag.address,
                prof=ag.prof,
                elite=ag.is_elite,
                toughness=ag.toughness,
                concentration=ag.concentration,
                healing=ag.healing,
                condition=ag.condition,
                hitbox_w=ag.hitbox_width,
                hitbox_h=ag.hitbox_height,
                name=ag.member_name,
                account=ag.account_name or "",
                is_player=is_player,
                is_gadget=is_gadget,
            )
            agents_list.append(info)
            agents_by_addr[ag.address] = info

        self.agents = agents_list
        self.agents_by_addr = agents_by_addr
        logger.debug(f"解析到{len(agents_list)}个代理")

    def _build_skills_from_core(self):
        skills = {}
        for sk in self._core_result.skills:
            skills[sk.gw2_skill_id] = sk.name
        self.skills = skills
        logger.debug(f"解析到{len(skills)}个技能")

    def _first_pass_events(self):
        events = self._core_result.events
        if not events:
            self.progress.add_warning("没有找到事件数据")
            return

        instid_to_addr = {}
        addr_team = {}
        addr_combat_enter = {}
        addr_combat_exit = {}

        log_start_event_time = None
        log_end_event_time = None

        for ev in events:
            sc = ev.is_statechange
            src_agent = ev.src_agent
            src_instid = ev.src_instid
            time = ev.time
            value = ev.value

            if sc in (
                SC_ENTER_COMBAT,
                SC_CHANGE_UP,
                SC_SPAWN,
                SC_EXIT_COMBAT,
                SC_CHANGE_DEAD,
                SC_CHANGE_DOWN,
                SC_DESPAWN,
            ):
                if src_instid and src_agent and src_agent in self.agents_by_addr:
                    instid_to_addr[src_instid] = src_agent

            if sc == SC_LOG_START:
                self.meta.log_start = time
                log_start_event_time = time
            elif sc == SC_LOG_END:
                self.meta.log_end = time
                log_end_event_time = time
            elif sc == SC_GW2_BUILD:
                self.meta.gw2_build = src_agent
            elif sc == SC_LANGUAGE:
                self.meta.language = src_agent
            elif sc == SC_SHARD_ID:
                self.meta.shard_id = src_agent
            elif sc == SC_POV:
                self.meta.pov_addr = src_agent
            elif sc == SC_TEAM_CHANGE:
                addr = instid_to_addr.get(src_instid, src_agent)
                addr_team[addr] = value
            elif sc == SC_ENTER_COMBAT:
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr not in addr_combat_enter:
                    addr_combat_enter[addr] = time
            elif sc in (SC_EXIT_COMBAT, SC_CHANGE_DEAD):
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr in addr_combat_enter:
                    addr_combat_exit[addr] = time
            elif sc == StateChange.MAP_ID:
                self.meta.map_id = src_agent

        if log_start_event_time is not None and log_end_event_time is not None:
            self._fight_duration_ms = max(1, log_end_event_time - log_start_event_time)
        else:
            self._fight_duration_ms = max(1, int(self.meta.duration_ms))

        for ag in self.agents:
            ag.team = addr_team.get(ag.addr)
        for iid, addr in instid_to_addr.items():
            if addr in self.agents_by_addr:
                self.agents_by_addr[addr].instid = iid

        self.instid_to_addr = instid_to_addr
        self.combat_enter = addr_combat_enter
        self.combat_exit = addr_combat_exit

    def _second_pass_events(self):
        ps: Dict[int, PlayerStats] = {}
        seen_addrs = set()
        seen_names = set()

        for ag in self.agents:
            # 排除宠物代理（account 为空）和无效代理
            if ag.is_player and 0 <= ag.prof <= 9 and ag.account:
                if ag.addr in seen_addrs:
                    continue
                seen_addrs.add(ag.addr)
                if ag.name in seen_names:
                    continue
                seen_names.add(ag.name)

                player = PlayerStats(
                    addr=ag.addr,
                    name=ag.name,
                    account=ag.account_clean,
                    profession=ag.profession,
                    team=ag.team,
                    instance_id=ag.instid,
                )
                ps[ag.addr] = player

        self.player_stats = ps
        self.progress.update("第二轮事件扫描", 50, players_found=len(ps))

        buff_states: Dict[int, Dict[int, List]] = defaultdict(lambda: defaultdict(list))
        events = self._core_result.events

        events_processed = 0
        n_events = len(events)
        for i, ev in enumerate(events):
            try:
                self._process_single_event(ev, buff_states)
                events_processed += 1
                if events_processed % 10000 == 0:
                    self.progress.update(
                        "第二轮事件扫描",
                        50 + int(events_processed / n_events * 25),
                        events_processed=events_processed,
                    )
            except Exception as e:
                if i % 10000 == 0:
                    self.progress.add_warning(f"处理事件{i}时出错: {e}")

        self.progress.events_processed = events_processed
        self.buff_trackers = buff_states

    def _process_single_event(self, ev: EvtcEvent, buff_states: Dict):
        time = ev.time
        src_agent = ev.src_agent
        dst_agent = ev.dst_agent
        value = ev.value
        buff_dmg = ev.buff_dmg
        skill_id = ev.skill_id
        src_instid = ev.src_instid
        dst_instid = ev.dst_instid
        iff = ev.iff
        is_buff = ev.buff
        result = ev.result
        is_buff_remove = ev.is_buffremove
        sc = ev.is_statechange

        src_addr = self.instid_to_addr.get(src_instid, src_agent)
        dst_addr = self.instid_to_addr.get(dst_instid, dst_agent)

        src_is_player = src_addr in self.player_stats
        dst_is_player = dst_addr in self.player_stats

        # 玩家造成的伤害
        if src_is_player and iff == IFF_FOE and sc == SC_NONE:
            p = self.player_stats[src_addr]
            if is_buff == 0 and 0 < value < MAX_DAMAGE_PER_HIT:
                p.total_damage += value
                p.power_damage += value
            elif is_buff == 1 and 0 < buff_dmg < MAX_DAMAGE_PER_HIT:
                p.total_damage += buff_dmg
                p.condi_damage += buff_dmg

            # 限制总伤害不超过合理上限
            if p.total_damage > MAX_TOTAL_DAMAGE:
                p.total_damage = MAX_TOTAL_DAMAGE
            if p.power_damage > MAX_TOTAL_DAMAGE:
                p.power_damage = MAX_TOTAL_DAMAGE
            if p.condi_damage > MAX_TOTAL_DAMAGE:
                p.condi_damage = MAX_TOTAL_DAMAGE

        # 玩家受到的承伤
        if dst_is_player and sc == SC_NONE and src_addr != dst_addr:
            p = self.player_stats[dst_addr]
            if is_buff == 0 and 0 < value < MAX_DAMAGE_PER_HIT:
                p.damage_taken += value
            elif is_buff == 1 and 0 < buff_dmg < MAX_DAMAGE_PER_HIT:
                p.damage_taken += buff_dmg
            if p.damage_taken > MAX_TOTAL_DAMAGE:
                p.damage_taken = MAX_TOTAL_DAMAGE
            if p.condi_damage > MAX_TOTAL_DAMAGE:
                p.condi_damage = MAX_TOTAL_DAMAGE

            if result == 6:
                p.breakbar_damage += float(abs(value or buff_dmg))
            if result == RESULT_DOWNING_BLOW:
                p.downs_inflicted += 1
            elif result == RESULT_KILLING_BLOW:
                p.kills_inflicted += 1

        if is_buff_remove in (1, 2) and src_is_player:
            p = self.player_stats[src_addr]
            if iff == IFF_FOE:
                p.boon_strips += 1
            if iff == IFF_FRIEND:
                p.condi_cleanses += 1

        if sc == SC_CHANGE_DOWN and src_is_player:
            self.player_stats[src_addr].own_downs += 1
        elif sc == SC_CHANGE_DEAD and src_is_player:
            self.player_stats[src_addr].own_deaths += 1
        elif sc == SC_TAG and src_is_player:
            if value != 0:
                # SC_TAG value 编码: value = (group_id << 8) | tag_type
                # tag_type 在低 8 位，group_id 在高 8 位
                tag_type = value & 0xFF
                group_id = (value >> 8) & 0xFF
                if group_id > 0:
                    self.player_stats[src_addr].group = group_id
                # 只有 tag_type == 208 (0xD0) 才是真正的指挥官标记
                # 其他 tag_type (68, 90, 186, 346 等) 是其他标记类型
                if tag_type == 208:
                    self.player_stats[src_addr].has_commander_tag = True

        # 只追踪关心的 buff（BUFF_IDS 中定义的），大幅减少内存占用
        if is_buff == 1 and dst_is_player and sc == SC_NONE and skill_id in _BUFF_ID_SET:
            if dst_addr not in buff_states:
                buff_states[dst_addr] = {}
            if skill_id not in buff_states[dst_addr]:
                buff_states[dst_addr][skill_id] = []

            if is_buff_remove == 0 and value > 0:
                buff_states[dst_addr][skill_id].append((time, "apply"))
            elif is_buff_remove > 0:
                buff_states[dst_addr][skill_id].append((time, "remove"))

    def _calculate_buff_uptimes(self):
        fight_duration_ms = self._fight_duration_ms
        for addr, player in self.player_stats.items():
            for bid, bname in BUFF_IDS.items():
                events_b = self.buff_trackers.get(addr, {}).get(bid, [])
                uptime_ms = _calc_buff_uptime(events_b, fight_duration_ms)
                player.buff_uptime[bname] = round(
                    uptime_ms / fight_duration_ms * 100, 2
                )

                if uptime_ms > 0:
                    buff_uptime_entry = {
                        "id": bid,
                        "buffData": [
                            {
                                "uptime": 0,
                                "buffApplied": 0,
                                "wasted": 0,
                                "extended": 0,
                                "unknownExtended": 0,
                                "stackRemoval": 0,
                                "stackDist": [0.0, 0.0],
                            }
                        ],
                        "uptime": uptime_ms,
                    }
                    player.buff_uptimes.append(buff_uptime_entry)

        for addr, player in self.player_stats.items():
            enter = self.combat_enter.get(addr, 0)
            exit_t = self.combat_exit.get(addr, 0)
            if enter and exit_t > enter:
                player.combat_time_ms = max(0, exit_t - enter)
            else:
                player.combat_time_ms = fight_duration_ms

    def _build_ei_players(self):
        duration_sec = max(1, self.meta.duration_s)
        duration_ms = max(1, self.meta.duration_ms)

        for addr, player in self.player_stats.items():
            player.dps_all = [
                {
                    "dps": (
                        int(player.total_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "damage": player.total_damage,
                    "condiDps": (
                        int(player.condi_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "condiDamage": player.condi_damage,
                    "powerDps": (
                        int(player.power_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "powerDamage": player.power_damage,
                    "breakbarDamage": float(player.breakbar_damage),
                    "actorDps": (
                        int(player.total_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "actorDamage": player.total_damage,
                    "actorCondiDps": (
                        int(player.condi_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "actorCondiDamage": player.condi_damage,
                    "actorPowerDps": (
                        int(player.power_damage / duration_sec)
                        if duration_sec > 0
                        else 0
                    ),
                    "actorPowerDamage": player.power_damage,
                    "actorBreakbarDamage": float(player.breakbar_damage),
                }
            ]

            player.stats_all = [
                {
                    "wasted": 0,
                    "timeWasted": 0.0,
                    "saved": 0,
                    "timeSaved": 0.0,
                    "stackDist": 0.0,
                    "distToCom": 0.0,
                    "avgBoons": 0.0,
                    "avgActiveBoons": 0.0,
                    "avgConditions": 0.0,
                    "avgActiveConditions": 0.0,
                    "swapCount": 0,
                    "skillCastUptime": 0.0,
                    "skillCastUptimeNoAA": 0.0,
                    "totalDamageCount": 0,
                    "totalDmg": player.total_damage,
                    "directDamageCount": 0,
                    "directDmg": player.power_damage,
                    "connectedDirectDamageCount": 0,
                    "connectedDirectDmg": player.power_damage,
                    "connectedDamageCount": 0,
                    "connectedDmg": player.total_damage,
                    "critableDirectDamageCount": 0,
                    "criticalRate": 0.0,
                    "criticalDmg": 0,
                    "flankingRate": 0.0,
                    "againstMovingRate": 0.0,
                    "glanceRate": 0.0,
                    "missed": 0,
                    "evaded": 0,
                    "blocked": 0,
                    "interrupts": 0,
                    "invulned": 0,
                    "killed": player.kills_inflicted,
                    "downed": player.downs_inflicted,
                    "downContribution": 0,
                    "connectedPowerCount": 0,
                    "connectedPowerAbove90HPCount": 0,
                    "connectedConditionCount": 0,
                    "connectedConditionAbove90HPCount": 0,
                    "againstDownedCount": 0,
                    "againstDownedDamage": 0,
                }
            ]

            player.defenses = [
                {
                    "damageTaken": player.damage_taken,
                    "downedDamageTaken": 0,
                    "breakbarDamageTaken": 0.0,
                    "blockedCount": 0,
                    "evadedCount": 0,
                    "missedCount": 0,
                    "dodgeCount": 0,
                    "invulnedCount": 0,
                    "damageBarrier": 0,
                    "interruptedCount": 0,
                    "downCount": player.own_downs,
                    "downDuration": 0,
                    "deadCount": player.own_deaths,
                    "deadDuration": 0,
                    "dcCount": 0,
                    "dcDuration": 0,
                    "boonStrips": player.boon_strips,
                    "boonStripsTime": 0.0,
                    "conditionCleanses": player.condi_cleanses,
                    "conditionCleansesTime": 0.0,
                }
            ]

            player.support = [
                {
                    "condiCleanse": player.condi_cleanses,
                    "boonStrips": player.boon_strips,
                }
            ]

            duration_sec_int = int(duration_ms / 1000)
            player.damage1s = [[0] * duration_sec_int] if duration_sec_int > 0 else []
            player.power_damage1s = (
                [[0] * duration_sec_int] if duration_sec_int > 0 else []
            )
            player.condition_damage1s = (
                [[0] * duration_sec_int] if duration_sec_int > 0 else []
            )
            player.total_damage_dist = [[]]
            player.total_damage_taken = [[]]

    def _generate_ei_json(self) -> Dict[str, Any]:
        duration_ms = self.meta.duration_ms
        duration_sec = max(1, self.meta.duration_s)

        # 查找POV玩家
        pov_player = None
        for ag in self.agents:
            if ag.addr == self.meta.pov_addr:
                pov_player = ag
                break

        recorded_by = pov_player.name if pov_player else "Unknown"
        recorded_account_by = pov_player.account_clean if pov_player else "Unknown"

        players = []
        for addr, p in self.player_stats.items():
            players.append(
                {
                    "account": p.account,
                    "name": p.name,
                    "profession": p.profession,
                    "group": p.group,
                    "hasCommanderTag": p.has_commander_tag,
                    "friendlyNPC": p.friendly_npc,
                    "notInSquad": p.not_in_squad,
                    "isFake": p.is_fake,
                    "guildID": p.guild_id,
                    "totalHealth": p.total_health,
                    "toughness": p.toughness,
                    "condition": p.condition,
                    "concentration": p.concentration,
                    "healing": p.healing,
                    "hitboxHeight": p.hitbox_height,
                    "hitboxWidth": p.hitbox_width,
                    "instanceID": p.instance_id,
                    "teamID": p.team if p.team is not None else 0,
                    "dpsAll": p.dps_all,
                    "statsAll": p.stats_all,
                    "defenses": p.defenses,
                    "support": p.support,
                    "buffUptimes": p.buff_uptimes,
                    "buffUptimesActive": p.buff_uptimes_active,
                    "selfBuffs": p.self_buffs,
                    "selfBuffsActive": p.self_buffs_active,
                    "weapons": p.weapons,
                    "rotation": p.rotation,
                    "damageModifiers": p.damage_modifiers,
                    "damageModifiersTarget": p.damage_modifiers_target,
                    "activeTimes": p.active_times,
                    "healthPercents": p.health_percents,
                    "barrierPercents": p.barrier_percents,
                    "totalDamageDist": p.total_damage_dist,
                    "totalDamageTaken": p.total_damage_taken,
                    "damage1S": p.damage1s,
                    "powerDamage1S": p.power_damage1s,
                    "conditionDamage1S": p.condition_damage1s,
                    "dpsTargets": p.dps_targets,
                    "targetDamage1S": p.target_damage1s,
                    "targetPowerDamage1S": p.target_power_damage1s,
                    "targetConditionDamage1S": p.target_condition_damage1s,
                    "targetDamageDist": p.target_damage_dist,
                    "statsTargets": p.stats_targets,
                }
            )

        total_damage = sum(p.total_damage for p in self.player_stats.values())
        total_kills = sum(p.kills_inflicted for p in self.player_stats.values())
        total_deaths = sum(p.own_deaths for p in self.player_stats.values())

        return {
            "triggerID": self.meta.boss_id,
            "eiEncounterID": self.meta.boss_id,
            "fightName": self.meta.map_name,
            "arcVersion": f"EVTC{self.meta.build_date}",
            "gW2Build": self.meta.gw2_build,
            "recordedBy": recorded_by,
            "recordedAccountBy": recorded_account_by,
            "timeStart": self.meta.start_datetime or "",
            "timeEnd": self.meta.end_datetime or "",
            "duration": self.meta.duration_str,
            "durationMS": duration_ms,
            "success": True,
            "isCM": False,
            "isLegendaryCM": False,
            "isRayMode": False,
            "detailedWvW": self.meta.is_wvw,
            "players": players,
            "targets": [],
            "phases": [],
            "logErrors": [],
            "combatReplayMap": None,
            "version": "2.0.0",
            "parser": "EnhancedZevtcParser",
            "uploadLinks": [],
            "total_damage": total_damage,
            "total_kills": total_kills,
            "total_deaths": total_deaths,
        }


def parse_zevtc_file(
    path: str, progress: Optional[ParseProgress] = None
) -> Dict[str, Any]:
    """便捷函数：解析ZEVTC文件并返回EI格式JSON"""
    parser = EnhancedZevtcParser(path, progress)
    return parser.parse()
