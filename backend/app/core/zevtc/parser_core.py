# -*- coding: utf-8 -*-
"""
EVTC 二进制解析器核心

功能:
    - 读取 ZEVTC (ZIP) 或 EVTC (裸二进制) 文件
    - 解析 Header / Agent / Skill / Event 四段结构
    - 输出结构化数据 (ParseResult)，供数据库写入层消费

性能考虑:
    - 大文件 (>10MB) 使用 mmap 减少内存拷贝
    - Event 解析使用直接切片+struct.unpack_from，避免逐字节 read
    - 支持生成器模式 yield_event() 以极低的内存占用遍历事件
"""

import hashlib
import logging
import mmap
import os
import struct
import zipfile
from io import BytesIO
from typing import BinaryIO, Iterator, List, Optional, Union

from .constants import (
    AGENT_NAME_RAW_SIZE,
    AGENT_OFFSET_ADDRESS,
    AGENT_OFFSET_CONCENTRATION,
    AGENT_OFFSET_CONDITION,
    AGENT_OFFSET_HEALING,
    AGENT_OFFSET_HITBOX_HEIGHT,
    AGENT_OFFSET_HITBOX_WIDTH,
    AGENT_OFFSET_IS_ELITE,
    AGENT_OFFSET_NAME_RAW,
    AGENT_OFFSET_PROF,
    AGENT_OFFSET_TOUGHNESS,
    AGENT_SIZE,
    EVENT_OFFSET_BUFF,
    EVENT_OFFSET_BUFF_DMG,
    EVENT_OFFSET_DST_AGENT,
    EVENT_OFFSET_DST_INSTID,
    EVENT_OFFSET_DST_MASTER_INSTID,
    EVENT_OFFSET_IFF,
    EVENT_OFFSET_IS_ACTIVATION,
    EVENT_OFFSET_IS_BUFFREMOVE,
    EVENT_OFFSET_IS_FIFTY,
    EVENT_OFFSET_IS_FLANKING,
    EVENT_OFFSET_IS_MOVING,
    EVENT_OFFSET_IS_NINETY,
    EVENT_OFFSET_IS_OFFCYCLE,
    EVENT_OFFSET_IS_SHIELDS,
    EVENT_OFFSET_IS_STATECHANGE,
    EVENT_OFFSET_OVERSTACK,
    EVENT_OFFSET_PAD,
    EVENT_OFFSET_RESULT,
    EVENT_OFFSET_SKILL_ID,
    EVENT_OFFSET_SRC_AGENT,
    EVENT_OFFSET_SRC_INSTID,
    EVENT_OFFSET_SRC_MASTER_INSTID,
    EVENT_OFFSET_TIME,
    EVENT_OFFSET_VALUE,
    EVENT_SIZE_REV0,
    EVENT_SIZE_REV1,
    EVTC_MAGIC,
    HEADER_OFFSET_AGENT_COUNT,
    HEADER_OFFSET_AUTO_FLAG,
    HEADER_OFFSET_BOSS_ID,
    HEADER_OFFSET_BUILD_DATE,
    HEADER_OFFSET_MAGIC,
    HEADER_OFFSET_REVISION,
    HEADER_OFFSET_SKILL_COUNT,
    HEADER_SIZE,
    SKILL_NAME_RAW_SIZE,
    SKILL_OFFSET_GW2_SKILL_ID,
    SKILL_OFFSET_NAME_RAW,
    SKILL_SIZE,
)
from .exceptions import (
    FileCorruptedError,
    InvalidFileFormatError,
    UnsupportedVersionError,
)
from .models import EvtcAgent, EvtcEvent, EvtcHeader, EvtcSkill, ParseResult

logger = logging.getLogger(__name__)

# struct 格式预编译（小端序）
_U8 = struct.Struct("<B")
_U16 = struct.Struct("<H")
_I16 = struct.Struct("<h")
_U32 = struct.Struct("<I")
_I32 = struct.Struct("<i")
_U64 = struct.Struct("<Q")


def _decode_utf8_null_term(raw: bytes) -> str:
    """将空字节截断后的 UTF-8 字节解码为字符串，替换不可解码字符"""
    idx = raw.find(b"\x00")
    if idx >= 0:
        raw = raw[:idx]
    return raw.decode("utf-8", errors="replace")


def _decode_agent_name_raw(name_raw: bytes) -> tuple[str, Optional[str]]:
    """
    解析 Agent 的 name_raw (68 bytes) 为 member_name 和 account_name。
    格式: b"member_name\x00account_name\x00..."

    - member_name: 第一个空终止段，必须非空
    - account_name: 第二个空终止段，ZEVTC 中可能为空/缺失
    """
    # 找到第一个空字节
    first_null = name_raw.find(b"\x00")
    if first_null < 0:
        # 没有空字节，整个内容作为 member_name
        member = name_raw.decode("utf-8", errors="replace").strip()
        return member, None

    member_bytes = name_raw[:first_null]
    member = member_bytes.decode("utf-8", errors="replace").strip()

    # 找到第二个空字节（从第一个之后开始）
    second_null = name_raw.find(b"\x00", first_null + 1)
    if second_null < 0:
        account_bytes = name_raw[first_null + 1 :]
    else:
        account_bytes = name_raw[first_null + 1 : second_null]

    account = account_bytes.decode("utf-8", errors="replace").strip()
    if not account:
        account = None

    return member, account


def _sha256_file(path: str) -> str:
    """计算文件的 SHA-256 指纹（流式，适合大文件）"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    """计算字节串的 SHA-256 指纹"""
    return hashlib.sha256(data).hexdigest()


class EvtcByteReader:
    """基于 bytes/memoryview 的随机访问读取器，避免逐字节 copy"""

    def __init__(self, data: Union[bytes, mmap.mmap, memoryview]):
        self._data = data
        self._pos = 0
        self._len = len(data)

    @property
    def position(self) -> int:
        return self._pos

    @property
    def remaining(self) -> int:
        return self._len - self._pos

    def seek(self, pos: int) -> None:
        if pos < 0 or pos > self._len:
            raise FileCorruptedError(
                f"Seek 越界: pos={pos}, len={self._len}",
                {"position": pos, "length": self._len},
            )
        self._pos = pos

    def read(self, n: int) -> bytes:
        if self._pos + n > self._len:
            raise FileCorruptedError(
                f"读取越界: 需要{n}字节, 剩余{self._len - self._pos}字节",
                {
                    "position": self._pos,
                    "requested": n,
                    "remaining": self._len - self._pos,
                },
            )
        b = self._data[self._pos : self._pos + n]
        self._pos += n
        return bytes(b)  # 确保返回 bytes，memoryview slice 也是 bytes-like

    def u8(self) -> int:
        return _U8.unpack(self.read(1))[0]

    def u16(self) -> int:
        return _U16.unpack(self.read(2))[0]

    def i16(self) -> int:
        return _I16.unpack(self.read(2))[0]

    def u32(self) -> int:
        return _U32.unpack(self.read(4))[0]

    def i32(self) -> int:
        return _I32.unpack(self.read(4))[0]

    def u64(self) -> int:
        return _U64.unpack(self.read(8))[0]

    def slice(self, start: int, end: int) -> bytes:
        """返回 [start, end) 切片，不移动 pos"""
        if start < 0 or end > self._len or start > end:
            raise FileCorruptedError(
                f"切片越界: [{start}, {end}), len={self._len}",
                {"start": start, "end": end, "length": self._len},
            )
        return bytes(self._data[start:end])


class EvtcParser:
    """
    EVTC 二进制文件解析器

    支持两种模式:
        1. 全量解析 (parse_file): 返回包含所有 Agent/Skill/Event 的 ParseResult
        2. 流式解析 (iter_events): 仅遍历事件，内存占用极低
    """

    def __init__(
        self,
        path: Optional[str] = None,
        data: Optional[bytes] = None,
        filename: Optional[str] = None,
        compressed_size: int = 0,
    ):
        """
        参数:
            path: 文件路径（ZEVTC 或 EVTC）
            data: 直接传入已解压的 EVTC 二进制数据（跳过文件读取）
            filename: 原始文件名（用于元数据）
            compressed_size: 压缩后大小（ZEVTC）
        """
        self.path = path
        self._provided_data = data
        self._filename = filename or (os.path.basename(path) if path else "unknown")
        self._compressed_size = compressed_size
        self._reader: Optional[EvtcByteReader] = None
        self._mmap_obj: Optional[mmap.mmap] = None
        self._header: Optional[EvtcHeader] = None
        self._event_size: int = EVENT_SIZE_REV1

    # -----------------------------------------------------------------------
    # 文件加载
    # -----------------------------------------------------------------------
    def _load_file(self) -> bytes:
        """加载文件并解压（如为 ZIP），返回 EVTC 裸二进制"""
        if self._provided_data is not None:
            return self._provided_data

        if not self.path:
            raise InvalidFileFormatError("未提供文件路径或数据")

        if not os.path.exists(self.path):
            raise FileCorruptedError(f"文件不存在: {self.path}", {"path": self.path})

        file_size = os.path.getsize(self.path)
        if file_size == 0:
            raise FileCorruptedError("文件为空", {"path": self.path, "size": 0})

        # 尝试作为 ZIP 读取
        if zipfile.is_zipfile(self.path):
            try:
                with zipfile.ZipFile(self.path, "r") as zf:
                    namelist = zf.namelist()
                    if not namelist:
                        raise FileCorruptedError("ZIP 压缩包为空", {"path": self.path})
                    # 取第一个非目录条目
                    entries = [n for n in namelist if not n.endswith("/")]
                    if not entries:
                        raise FileCorruptedError(
                            "ZIP 压缩包无有效文件", {"path": self.path}
                        )
                    entry = entries[0]
                    data = zf.read(entry)
                    logger.info(f"ZIP 解压: {entry} → {len(data)} bytes")
                    return data
            except zipfile.BadZipFile:
                logger.warning("不是有效 ZIP，尝试直接读取")
            except Exception as e:
                raise FileCorruptedError(
                    f"ZIP 解压失败: {e}", {"path": self.path}
                ) from e

        # 直接读取文件（裸 EVTC）
        try:
            if file_size > 10 * 1024 * 1024:
                # 大文件使用 mmap，返回 memoryview 避免数据复制
                f = open(self.path, "rb")
                self._mmap_obj = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                logger.info(f"mmap 加载大文件: {file_size / (1024*1024):.2f} MB")
                return memoryview(self._mmap_obj)
            else:
                with open(self.path, "rb") as f:
                    data = f.read()
                return data
        except Exception as e:
            raise FileCorruptedError(f"文件读取失败: {e}", {"path": self.path}) from e

    def _cleanup(self) -> None:
        if self._mmap_obj:
            try:
                self._mmap_obj.close()
            except Exception as e:
                logger.warning(f"关闭 mmap 失败: {e}")
            self._mmap_obj = None

    # -----------------------------------------------------------------------
    # 公共接口
    # -----------------------------------------------------------------------
    def parse_file(self, compute_sha256: bool = True) -> ParseResult:
        """
        全量解析文件，返回 ParseResult

        参数:
            compute_sha256: 是否计算文件指纹
        """
        try:
            raw = self._load_file()
            self._reader = EvtcByteReader(raw)

            # 文件指纹
            file_sha256 = ""
            if compute_sha256:
                if self._provided_data is not None:
                    file_sha256 = _sha256_bytes(self._provided_data)
                elif self.path:
                    file_sha256 = _sha256_file(self.path)

            # 解析头部
            header = self._parse_header()
            self._header = header
            self._event_size = (
                EVENT_SIZE_REV1 if header.revision >= 1 else EVENT_SIZE_REV0
            )

            if header.revision > 1:
                raise UnsupportedVersionError(
                    f"不支持的 EVTC 版本: revision={header.revision}",
                    {"revision": header.revision, "max_supported": 1},
                )

            # 解析 Agent
            agents = self._parse_agents(header.agent_count)

            # 解析 Skill
            skills = self._parse_skills()

            # 解析 Event
            events = self._parse_events()

            compressed_size = self._compressed_size
            if compressed_size == 0 and self.path:
                compressed_size = os.path.getsize(self.path)

            return ParseResult(
                header=header,
                agents=agents,
                skills=skills,
                events=events,
                raw_data_size=len(raw),
                compressed_size=compressed_size,
                event_size=self._event_size,
                filename=self._filename,
                file_sha256=file_sha256,
            )

        finally:
            self._cleanup()

    def iter_events(self) -> Iterator[EvtcEvent]:
        """
        流式解析：仅遍历所有 Event，内存占用极低

        前置条件: 必须先调用 parse_file() 或 _parse_header() + _parse_agents() + _parse_skills()
        以定位到 Event 区域。

        注意: 此方法必须在 parse_file 之后调用，且复用内部 _reader 状态。
        """
        if self._reader is None:
            raise RuntimeError("必须先调用 parse_file() 初始化 reader")
        if self._header is None:
            raise RuntimeError("必须先解析 Header")

        events_start = self._reader.position
        data_len = self._reader._len
        ev_size = self._event_size
        n_events = (data_len - events_start) // ev_size

        for i in range(n_events):
            off = events_start + i * ev_size
            yield self._unpack_event_at(i, off, ev_size)

    # -----------------------------------------------------------------------
    # 内部解析方法
    # -----------------------------------------------------------------------
    def _parse_header(self) -> EvtcHeader:
        reader = self._reader
        magic_bytes = reader.read(4)
        if magic_bytes != EVTC_MAGIC:
            magic_str = magic_bytes.decode("ascii", errors="replace")
            raise InvalidFileFormatError(
                f"无效 EVTC Magic: 期望 'EVTC', 实际 '{magic_str}' (hex={magic_bytes.hex()})",
                {"expected": "EVTC", "actual_hex": magic_bytes.hex()},
            )

        build_date = reader.read(8).decode("ascii", errors="replace")
        revision = reader.u8()
        boss_id = reader.u16()
        auto_flag = reader.u8()
        agent_count = reader.u32()

        logger.info(
            f"Header: build={build_date}, revision={revision}, "
            f"boss_id={boss_id}, agents={agent_count}"
        )

        return EvtcHeader(
            magic="EVTC",
            build_date=build_date,
            revision=revision,
            auto_flag=auto_flag,
            boss_id=boss_id,
            agent_count=agent_count,
            skill_count=0,
        )

    def _parse_agents(self, agent_count: int) -> List[EvtcAgent]:
        reader = self._reader
        agents: List[EvtcAgent] = []

        for i in range(agent_count):
            try:
                raw = reader.read(AGENT_SIZE)
                # 使用 struct.unpack_from 避免切片拷贝
                addr = struct.unpack_from("<Q", raw, AGENT_OFFSET_ADDRESS)[0]
                prof = struct.unpack_from("<I", raw, AGENT_OFFSET_PROF)[0]
                is_elite = struct.unpack_from("<I", raw, AGENT_OFFSET_IS_ELITE)[0]
                toughness = struct.unpack_from("<h", raw, AGENT_OFFSET_TOUGHNESS)[0]
                concentration = struct.unpack_from(
                    "<h", raw, AGENT_OFFSET_CONCENTRATION
                )[0]
                healing = struct.unpack_from("<h", raw, AGENT_OFFSET_HEALING)[0]
                hitbox_width = struct.unpack_from("<h", raw, AGENT_OFFSET_HITBOX_WIDTH)[
                    0
                ]
                condition = struct.unpack_from("<h", raw, AGENT_OFFSET_CONDITION)[0]
                hitbox_height = struct.unpack_from(
                    "<h", raw, AGENT_OFFSET_HITBOX_HEIGHT
                )[0]
                name_raw = raw[
                    AGENT_OFFSET_NAME_RAW : AGENT_OFFSET_NAME_RAW + AGENT_NAME_RAW_SIZE
                ]
                member_name, account_name = _decode_agent_name_raw(name_raw)

                # member_name 必须非空
                if not member_name:
                    logger.error(f"Agent {i} member_name 为空，原始字节: {name_raw!r}")
                    # 跳过此 agent，不加入列表
                    continue

                agents.append(
                    EvtcAgent(
                        agent_index=i,
                        address=addr,
                        prof=prof,
                        is_elite=is_elite,
                        toughness=toughness,
                        concentration=concentration,
                        healing=healing,
                        hitbox_width=hitbox_width,
                        condition=condition,
                        hitbox_height=hitbox_height,
                        name_raw=name_raw,
                        member_name=member_name,
                        account_name=account_name,
                    )
                )
            except FileCorruptedError:
                raise
            except Exception as e:
                logger.warning(f"解析 Agent {i} 失败: {e}")
                # 继续解析下一个

        logger.info(f"解析到 {len(agents)}/{agent_count} 个 Agent")
        return agents

    def _parse_skills(self) -> List[EvtcSkill]:
        reader = self._reader
        try:
            skill_count = reader.u32()
        except FileCorruptedError as e:
            logger.error(f"读取 Skill 数量失败: {e}")
            skill_count = 0

        skills: List[EvtcSkill] = []
        for i in range(skill_count):
            try:
                raw = reader.read(SKILL_SIZE)
                gw2_skill_id = struct.unpack_from("<i", raw, SKILL_OFFSET_GW2_SKILL_ID)[
                    0
                ]
                name_raw = raw[
                    SKILL_OFFSET_NAME_RAW : SKILL_OFFSET_NAME_RAW + SKILL_NAME_RAW_SIZE
                ]
                name = _decode_utf8_null_term(name_raw)

                skills.append(
                    EvtcSkill(
                        skill_index=i,
                        gw2_skill_id=gw2_skill_id,
                        name_raw=name_raw,
                        name=name,
                    )
                )
            except FileCorruptedError:
                raise
            except Exception as e:
                logger.warning(f"解析 Skill {i} 失败: {e}")

        logger.info(f"解析到 {len(skills)}/{skill_count} 个 Skill")
        return skills

    def _parse_events(self) -> List[EvtcEvent]:
        reader = self._reader
        events_start = reader.position
        data_len = reader._len
        ev_size = self._event_size
        n_events = (data_len - events_start) // ev_size

        if n_events <= 0:
            logger.warning("未找到 Event 数据")
            return []

        # 内存安全保护：超大文件的事件数上限，防止 OOM
        # 30 分钟 WvW 日志约 2-5M 事件，5M 是一个安全的上限
        MAX_SAFE_EVENTS = 5_000_000
        if n_events > MAX_SAFE_EVENTS:
            raise FileCorruptedError(
                f"事件数超过安全上限: {n_events} > {MAX_SAFE_EVENTS}。"
                f"该文件可能损坏或战斗时间过长，建议手动检查。"
            )

        logger.info(f"发现 {n_events} 个 Event (size={ev_size})")

        events: List[EvtcEvent] = []
        # 预分配容量以减少列表扩容开销
        events_append = events.append

        for i in range(n_events):
            off = events_start + i * ev_size
            try:
                events_append(self._unpack_event_at(i, off, ev_size))
            except Exception as e:
                if i % 10000 == 0:
                    logger.warning(f"解析 Event {i} 失败: {e}")
                # 继续解析

        logger.info(f"成功解析 {len(events)}/{n_events} 个 Event")
        return events

    def _unpack_event_at(self, index: int, offset: int, ev_size: int) -> EvtcEvent:
        """在指定偏移处解包单个 Event（直接操作底层 bytes，避免 reader 方法调用开销）"""
        d = self._reader._data

        time = struct.unpack_from("<Q", d, offset + EVENT_OFFSET_TIME)[0]
        src_agent = struct.unpack_from("<Q", d, offset + EVENT_OFFSET_SRC_AGENT)[0]
        dst_agent = struct.unpack_from("<Q", d, offset + EVENT_OFFSET_DST_AGENT)[0]
        value = struct.unpack_from("<i", d, offset + EVENT_OFFSET_VALUE)[0]
        buff_dmg = struct.unpack_from("<i", d, offset + EVENT_OFFSET_BUFF_DMG)[0]
        overstack_value = struct.unpack_from("<I", d, offset + EVENT_OFFSET_OVERSTACK)[
            0
        ]
        skill_id = struct.unpack_from("<I", d, offset + EVENT_OFFSET_SKILL_ID)[0]
        src_instid = struct.unpack_from("<H", d, offset + EVENT_OFFSET_SRC_INSTID)[0]
        dst_instid = struct.unpack_from("<H", d, offset + EVENT_OFFSET_DST_INSTID)[0]
        src_master_instid = struct.unpack_from(
            "<H", d, offset + EVENT_OFFSET_SRC_MASTER_INSTID
        )[0]
        dst_master_instid = struct.unpack_from(
            "<H", d, offset + EVENT_OFFSET_DST_MASTER_INSTID
        )[0]

        # 字节字段直接索引
        iff = d[offset + EVENT_OFFSET_IFF]
        buff = d[offset + EVENT_OFFSET_BUFF]
        result = d[offset + EVENT_OFFSET_RESULT]
        is_activation = d[offset + EVENT_OFFSET_IS_ACTIVATION]
        is_buffremove = d[offset + EVENT_OFFSET_IS_BUFFREMOVE]
        is_ninety = d[offset + EVENT_OFFSET_IS_NINETY]
        is_fifty = d[offset + EVENT_OFFSET_IS_FIFTY]
        is_moving = d[offset + EVENT_OFFSET_IS_MOVING]
        is_statechange = d[offset + EVENT_OFFSET_IS_STATECHANGE]
        is_flanking = d[offset + EVENT_OFFSET_IS_FLANKING]
        is_shields = d[offset + EVENT_OFFSET_IS_SHIELDS]
        is_offcycle = d[offset + EVENT_OFFSET_IS_OFFCYCLE]

        pad = b"\x00" * 4
        if ev_size == EVENT_SIZE_REV1 and offset + 64 <= len(d):
            pad = bytes(d[offset + EVENT_OFFSET_PAD : offset + EVENT_OFFSET_PAD + 4])

        return EvtcEvent(
            event_index=index,
            time=time,
            src_agent=src_agent,
            dst_agent=dst_agent,
            value=value,
            buff_dmg=buff_dmg,
            overstack_value=overstack_value,
            skill_id=skill_id,
            src_instid=src_instid,
            dst_instid=dst_instid,
            src_master_instid=src_master_instid,
            dst_master_instid=dst_master_instid,
            iff=iff,
            buff=buff,
            result=result,
            is_activation=is_activation,
            is_buffremove=is_buffremove,
            is_ninety=is_ninety,
            is_fifty=is_fifty,
            is_moving=is_moving,
            is_statechange=is_statechange,
            is_flanking=is_flanking,
            is_shields=is_shields,
            is_offcycle=is_offcycle,
            pad=pad,
        )

    @staticmethod
    def parse_memory(
        data: bytes,
        filename: str = "memory",
        compressed_size: int = 0,
        compute_sha256: bool = True,
    ) -> ParseResult:
        """从内存中的 EVTC 数据直接解析（用于测试或已解压数据）"""
        parser = EvtcParser(
            data=data, filename=filename, compressed_size=compressed_size
        )
        return parser.parse_file(compute_sha256=compute_sha256)
