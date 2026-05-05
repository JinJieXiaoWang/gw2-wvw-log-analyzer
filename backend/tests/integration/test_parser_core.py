# -*- coding: utf-8 -*-
"""
ZEVTC 解析器核心单元测试

测试范围:
    - 文件加载 (ZIP / 裸 EVTC / mmap)
    - Header 解析 (正常 / 异常)
    - Agent 解析 (正常 / 编码错误 / 截断)
    - Skill 解析
    - Event 解析 (rev0 / rev1)
    - 边界情况 (空文件、损坏文件、无效 Magic)
    - 与真实测试文件的对照验证
"""

import hashlib
import os
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.core.zevtc.constants import (
    AGENT_SIZE,
    EVENT_SIZE_REV0,
    EVENT_SIZE_REV1,
    EVTC_MAGIC,
    HEADER_SIZE,
    IFF,
    SKILL_SIZE,
    Activation,
    BuffRemove,
    Result,
    StateChange,
)
from app.core.zevtc.exceptions import (
    FileCorruptedError,
    InvalidFileFormatError,
    UnsupportedVersionError,
)
from app.core.zevtc.parser_core import (
    EvtcByteReader,
    EvtcParser,
    _decode_utf8_null_term,
    _sha256_bytes,
)


class TestByteReader(unittest.TestCase):
    """测试字节读取器"""

    def test_basic_read(self):
        data = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        reader = EvtcByteReader(data)
        self.assertEqual(reader.u8(), 1)
        self.assertEqual(reader.u16(), 0x0302)
        self.assertEqual(reader.u32(), 0x07060504)

    def test_u64(self):
        data = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        reader = EvtcByteReader(data)
        self.assertEqual(reader.u64(), 0x0807060504030201)

    def test_i16_i32(self):
        data = struct.pack("<hi", -1, -2)
        reader = EvtcByteReader(data)
        self.assertEqual(reader.i16(), -1)
        self.assertEqual(reader.i32(), -2)

    def test_read_past_end(self):
        reader = EvtcByteReader(b"\x01")
        with self.assertRaises(FileCorruptedError):
            reader.u16()

    def test_seek_and_slice(self):
        reader = EvtcByteReader(b"ABCDEFGH")
        reader.seek(2)
        self.assertEqual(reader.slice(2, 5), b"CDE")
        self.assertEqual(reader.position, 2)  # slice 不移动 pos

    def test_seek_out_of_bounds(self):
        reader = EvtcByteReader(b"ABC")
        with self.assertRaises(FileCorruptedError):
            reader.seek(10)


class TestNullStringDecode(unittest.TestCase):
    """测试 UTF-8 空字节截断解码"""

    def test_basic(self):
        self.assertEqual(_decode_utf8_null_term(b"hello\x00world"), "hello")

    def test_no_null(self):
        self.assertEqual(_decode_utf8_null_term(b"hello"), "hello")

    def test_utf8(self):
        self.assertEqual(_decode_utf8_null_term("测试\x00".encode("utf-8")), "测试")

    def test_invalid_utf8(self):
        # 非法 UTF-8 序列应被替换字符替代
        result = _decode_utf8_null_term(b"\xff\xfe")
        self.assertIn("\ufffd", result)


class TestHeaderParsing(unittest.TestCase):
    """测试 Header 解析"""

    def _make_minimal_evtc(self, revision=1, agent_count=1, skill_count=0, events=0):
        """构造最小 EVTC 数据"""
        # Header: 20 bytes
        header = EVTC_MAGIC
        header += b"20260101"  # build_date
        header += struct.pack("<B", revision)  # revision
        header += struct.pack("<H", 1)  # boss_id
        header += b"\x00"  # skip/auto_flag
        header += struct.pack("<I", agent_count)  # agent_count

        # Agents
        for i in range(agent_count):
            agent = struct.pack("<Q", 1000 + i)  # address
            agent += struct.pack("<I", 1)  # prof (Guardian)
            agent += struct.pack("<I", 0)  # is_elite
            agent += struct.pack("<hhhhhh", 1000, 500, 0, 0, 0, 0)  # stats + hitbox
            name_raw = b"Player\x00Account\x00"
            agent += name_raw.ljust(68, b"\x00")
            header += agent

        # Skill count + Skills
        header += struct.pack("<I", skill_count)
        # Skills
        for i in range(skill_count):
            skill = struct.pack("<i", 100 + i)
            skill += b"SkillName\x00".ljust(64, b"\x00")
            header += skill

        # Events
        ev_size = EVENT_SIZE_REV1 if revision >= 1 else EVENT_SIZE_REV0
        for i in range(events):
            ev = struct.pack("<Q", 1000000 + i * 100)  # time
            ev += struct.pack("<QQ", 1000, 2000)  # src, dst
            ev += struct.pack("<ii", 100, 0)  # value, buff_dmg
            ev += struct.pack("<II", 0, 0)  # overstack(u32), skill_id(u32)
            ev += struct.pack("<HHHH", 1, 2, 0, 0)  # instids
            ev += bytes([0, 0, Result.NORMAL, 0, 0, 0, 0, 0])  # flags
            ev += bytes(
                [StateChange.NONE, 0, 0, 0]
            )  # statechange + flanking + shields + offcycle
            if revision >= 1:
                ev += b"\x00" * 4  # pad
            header += ev

        return header

    def test_valid_header_rev1(self):
        data = self._make_minimal_evtc(
            revision=1, agent_count=2, skill_count=1, events=3
        )
        result = EvtcParser.parse_memory(data, filename="test.evtc")

        self.assertEqual(result.header.magic, "EVTC")
        self.assertEqual(result.header.build_date, "20260101")
        self.assertEqual(result.header.revision, 1)
        self.assertEqual(result.header.agent_count, 2)
        self.assertEqual(result.agent_count, 2)
        self.assertEqual(result.skill_count, 1)
        self.assertEqual(result.event_count, 3)
        self.assertEqual(result.event_size, EVENT_SIZE_REV1)

    def test_valid_header_rev0(self):
        data = self._make_minimal_evtc(revision=0, agent_count=1, events=2)
        result = EvtcParser.parse_memory(data, filename="test.evtc")
        self.assertEqual(result.header.revision, 0)
        self.assertEqual(result.event_size, EVENT_SIZE_REV0)
        self.assertEqual(result.event_count, 2)

    def test_invalid_magic(self):
        data = b"FAKE" + b"\x00" * 20
        with self.assertRaises(InvalidFileFormatError) as ctx:
            EvtcParser.parse_memory(data)
        self.assertIn("FAKE", str(ctx.exception))

    def test_truncated_header(self):
        data = EVTC_MAGIC + b"2026"
        with self.assertRaises(FileCorruptedError):
            EvtcParser.parse_memory(data)

    def test_unsupported_revision(self):
        data = self._make_minimal_evtc(revision=2)
        with self.assertRaises(UnsupportedVersionError):
            EvtcParser.parse_memory(data)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".evtc", delete=False) as f:
            f.write(b"")
            path = f.name
        try:
            parser = EvtcParser(path=path)
            with self.assertRaises(FileCorruptedError):
                parser.parse_file()
        finally:
            os.remove(path)

    def test_zip_loading(self):
        """测试 ZIP 文件加载"""
        data = self._make_minimal_evtc(
            revision=1, agent_count=1, skill_count=1, events=2
        )

        with tempfile.NamedTemporaryFile(suffix=".zevtc", delete=False) as f:
            with zipfile.ZipFile(f.name, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("test.evtc", data)
            path = f.name

        try:
            result = EvtcParser(path=path).parse_file()
            self.assertEqual(result.agent_count, 1)
            self.assertEqual(result.event_count, 2)
            self.assertTrue(result.compressed_size > 0)
        finally:
            os.remove(path)

    def test_sha256(self):
        data = self._make_minimal_evtc()
        result = EvtcParser.parse_memory(data, compute_sha256=True)
        expected = hashlib.sha256(data).hexdigest()
        self.assertEqual(result.file_sha256, expected)


class TestAgentParsing(unittest.TestCase):
    """测试 Agent 解析"""

    def _make_agent(self, addr, prof, elite, name, account):
        agent = struct.pack("<Q", addr)
        agent += struct.pack("<I", prof)
        agent += struct.pack("<I", elite)
        agent += struct.pack("<hhhhhh", 0, 0, 0, 0, 0, 0)
        name_bytes = f"{name}\x00{account}\x00".encode("utf-8")
        name_bytes += b"\x00" * (68 - len(name_bytes))
        agent += name_bytes[:68]
        return agent

    def test_player_agent(self):
        data = EVTC_MAGIC + b"20260101"
        data += struct.pack("<B", 1)  # revision
        data += struct.pack("<H", 1)  # boss_id
        data += b"\x00"  # skip
        data += struct.pack("<I", 1)  # agent_count

        data += self._make_agent(12345, 1, 0, "Hero", ":Account.1234")

        data += struct.pack("<I", 0)  # skill_count (必须添加)

        result = EvtcParser.parse_memory(data)
        ag = result.agents[0]
        self.assertEqual(ag.address, 12345)
        self.assertEqual(ag.prof, 1)
        self.assertEqual(ag.is_elite, 0)
        self.assertEqual(ag.member_name, "Hero")
        self.assertEqual(ag.account_name, ":Account.1234")
        self.assertTrue(ag.is_player)
        self.assertEqual(ag.agent_type, "player")

    def test_npc_agent(self):
        data = EVTC_MAGIC + b"20260101"
        data += struct.pack("<B", 1)
        data += struct.pack("<H", 1)
        data += b"\x00"
        data += struct.pack("<I", 1)

        agent = struct.pack("<Q", 99999)
        agent += struct.pack("<I", 0xFFFFFFFF)  # NPC prof
        agent += struct.pack("<I", 0xFFFFFFFF)  # NPC elite
        agent += struct.pack("<hhhhhh", 0, 0, 0, 0, 0, 0)
        name_raw = b"NPC Name\x00\x00"
        agent += name_raw.ljust(68, b"\x00")
        data += agent

        data += struct.pack("<I", 0)  # skill_count (必须添加)

        result = EvtcParser.parse_memory(data)
        ag = result.agents[0]
        self.assertTrue(ag.is_npc)
        self.assertEqual(ag.agent_type, "npc")

    def test_gbk_name_fallback(self):
        """测试非 UTF-8 名称被替换字符处理"""
        data = EVTC_MAGIC + b"20260101"
        data += struct.pack("<B", 1)
        data += struct.pack("<H", 1)
        data += b"\x00"
        data += struct.pack("<I", 1)

        agent = struct.pack("<Q", 1)
        agent += struct.pack("<II", 1, 0)
        agent += struct.pack("<hhhhhh", 0, 0, 0, 0, 0, 0)
        agent += b"\x80\x81\x82\x00".ljust(68, b"\x00")
        data += agent

        data += struct.pack("<I", 0)  # skill_count (必须添加)

        result = EvtcParser.parse_memory(data)
        # 应包含替换字符 \ufffd
        self.assertIn("\ufffd", result.agents[0].member_name)

    def test_agent_count_mismatch(self):
        """Header 声明更多 Agent 但数据不足 — 应触发 FileCorruptedError"""
        data = EVTC_MAGIC + b"20260101"
        data += struct.pack("<B", 1)
        data += struct.pack("<H", 1)
        data += struct.pack("<B", 1)
        data += struct.pack("<I", 10)  # 声明 10 个 agent
        data += self._make_agent(1, 1, 0, "A", "B")  # 但只提供 1 个

        with self.assertRaises(FileCorruptedError):
            EvtcParser.parse_memory(data)


class TestEventParsing(unittest.TestCase):
    """测试 Event 解析"""

    def _make_evtc_with_events(self, events_data, revision=1):
        data = EVTC_MAGIC + b"20260101"
        data += struct.pack("<B", revision)
        data += struct.pack("<H", 1)
        data += struct.pack("<B", 1)
        data += struct.pack("<I", 0)  # no agents
        data += struct.pack("<I", 0)  # no skills
        data += events_data
        return data

    def test_basic_event_rev1(self):
        ev = struct.pack("<Q", 1000)  # time
        ev += struct.pack("<QQ", 1, 2)  # src, dst
        ev += struct.pack("<ii", 100, 50)  # value, buff_dmg
        ev += struct.pack("<II", 0, 12345)  # overstack, skill_id
        ev += struct.pack("<HHHH", 1, 2, 3, 4)  # instids
        ev += bytes(
            [IFF.FOE, 0, Result.CRIT, Activation.NORMAL, BuffRemove.NONE, 1, 1, 1]
        )
        ev += bytes([StateChange.ENTER_COMBAT, 1, 1, 1])
        ev += b"\x00" * 4  # pad

        data = self._make_evtc_with_events(ev)
        result = EvtcParser.parse_memory(data)

        self.assertEqual(result.event_count, 1)
        ev = result.events[0]
        self.assertEqual(ev.time, 1000)
        self.assertEqual(ev.src_agent, 1)
        self.assertEqual(ev.dst_agent, 2)
        self.assertEqual(ev.value, 100)
        self.assertEqual(ev.buff_dmg, 50)
        self.assertEqual(ev.skill_id, 12345)
        self.assertEqual(ev.src_instid, 1)
        self.assertEqual(ev.dst_instid, 2)
        self.assertEqual(ev.src_master_instid, 3)
        self.assertEqual(ev.dst_master_instid, 4)
        self.assertEqual(ev.iff, IFF.FOE)
        self.assertEqual(ev.result, Result.CRIT)
        self.assertEqual(ev.is_activation, Activation.NORMAL)
        self.assertEqual(ev.is_statechange, StateChange.ENTER_COMBAT)
        self.assertEqual(ev.is_ninety, 1)
        self.assertEqual(ev.is_fifty, 1)
        self.assertEqual(ev.is_moving, 1)
        self.assertEqual(ev.is_flanking, 1)
        self.assertEqual(ev.is_shields, 1)
        self.assertEqual(ev.is_offcycle, 1)

    def test_event_skill_id_uint32(self):
        """验证 skill_id 作为 uint32 读取（可 > 65535）"""
        ev = struct.pack("<Q", 1000)
        ev += struct.pack("<QQ", 1, 2)
        ev += struct.pack("<ii", 0, 0)
        ev += struct.pack("<II", 0, 70000)  # skill_id > 65535
        ev += struct.pack("<HHHH", 0, 0, 0, 0)
        ev += bytes([0] * 8)
        ev += bytes([0, 0, 0, 0])
        ev += b"\x00" * 4

        data = self._make_evtc_with_events(ev)
        result = EvtcParser.parse_memory(data)
        self.assertEqual(result.events[0].skill_id, 70000)

    def test_log_start_end_detection(self):
        """验证 LogStart/LogEnd 事件检测"""
        ev_start = struct.pack("<Q", 1000)
        ev_start += struct.pack("<QQ", 1, 0)
        ev_start += struct.pack("<ii", 0, 0)
        ev_start += struct.pack("<II", 0, 0)
        ev_start += struct.pack("<HHHH", 0, 0, 0, 0)
        ev_start += bytes([0] * 8)
        ev_start += bytes([StateChange.LOG_START, 0, 0, 0])
        ev_start += b"\x00" * 4

        ev_end = struct.pack("<Q", 5000)
        ev_end += struct.pack("<QQ", 1, 0)
        ev_end += struct.pack("<ii", 0, 0)
        ev_end += struct.pack("<II", 0, 0)
        ev_end += struct.pack("<HHHH", 0, 0, 0, 0)
        ev_end += bytes([0] * 8)
        ev_end += bytes([StateChange.LOG_END, 0, 0, 0])
        ev_end += b"\x00" * 4

        data = self._make_evtc_with_events(ev_start + ev_end)
        result = EvtcParser.parse_memory(data)
        self.assertEqual(result.duration_ms, 4000)

    def test_zero_events(self):
        data = self._make_evtc_with_events(b"")
        result = EvtcParser.parse_memory(data)
        self.assertEqual(result.event_count, 0)
        self.assertEqual(result.duration_ms, 0)

    def test_truncated_event(self):
        """最后一个 Event 被截断 — 应被忽略"""
        ev = struct.pack("<Q", 1000)
        ev += b"\x00" * 30  # 不完整的事件数据
        data = self._make_evtc_with_events(ev)
        result = EvtcParser.parse_memory(data)
        # 由于事件不完整，不应被解析
        self.assertEqual(result.event_count, 0)


class TestRealFile(unittest.TestCase):
    """与真实测试文件对照验证"""

    REAL_FILE = Path(__file__).parent.parent / "20260426-220412.zevtc"

    @classmethod
    def setUpClass(cls):
        if not cls.REAL_FILE.exists():
            raise unittest.SkipTest(f"真实测试文件不存在: {cls.REAL_FILE}")

    def test_parse_real_file(self):
        result = EvtcParser(path=str(self.REAL_FILE)).parse_file()

        # 与已知值对照 (来自前期分析)
        self.assertEqual(result.header.magic, "EVTC")
        self.assertEqual(result.header.build_date, "20260416")
        self.assertEqual(result.header.revision, 1)
        self.assertEqual(result.header.agent_count, 655)
        self.assertEqual(result.agent_count, 655)
        self.assertEqual(result.skill_count, 1208)
        self.assertEqual(result.event_count, 672502)
        self.assertEqual(result.event_size, 64)
        self.assertEqual(result.duration_ms, 367295)
        self.assertEqual(result.compressed_size, 8795473)
        self.assertTrue(len(result.file_sha256) == 64)

    def test_log_start_end(self):
        result = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        log_start = [
            e for e in result.events if e.is_statechange == StateChange.LOG_START
        ]
        log_end = [e for e in result.events if e.is_statechange == StateChange.LOG_END]

        self.assertEqual(len(log_start), 1)
        self.assertEqual(len(log_end), 1)
        self.assertEqual(log_start[0].time, 30468211)
        self.assertEqual(log_end[0].time, 30835506)

    def test_statechange_distribution(self):
        result = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        sc_events = result.get_statechange_events()

        # 验证几个关键 StateChange 的数量级
        sc_counts = {}
        for e in sc_events:
            sc_counts[e.is_statechange] = sc_counts.get(e.is_statechange, 0) + 1

        self.assertEqual(sc_counts.get(StateChange.LOG_START), 1)
        self.assertEqual(sc_counts.get(StateChange.LOG_END), 1)
        self.assertGreater(sc_counts.get(StateChange.POSITION, 0), 60000)
        self.assertGreater(sc_counts.get(StateChange.VELOCITY, 0), 50000)

    def test_large_skill_ids(self):
        """验证大量技能 ID > 65535 被正确解析"""
        result = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        large_skill_events = [e for e in result.events if e.skill_id > 65535]
        self.assertGreater(len(large_skill_events), 50000)

    def test_sha256_consistency(self):
        """验证 SHA-256 计算稳定"""
        result1 = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        result2 = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        self.assertEqual(result1.file_sha256, result2.file_sha256)


class TestPerformance(unittest.TestCase):
    """性能基准测试"""

    REAL_FILE = Path(__file__).parent.parent / "20260426-220412.zevtc"

    @classmethod
    def setUpClass(cls):
        if not cls.REAL_FILE.exists():
            raise unittest.SkipTest(f"真实测试文件不存在: {cls.REAL_FILE}")

    def test_parse_speed(self):
        import time

        start = time.perf_counter()
        result = EvtcParser(path=str(self.REAL_FILE)).parse_file()
        elapsed = time.perf_counter() - start

        # 43MB 文件应在 5 秒内解析完成（宽松标准）
        self.assertLess(
            elapsed, 5.0, f"解析过慢: {elapsed:.2f}s for {result.event_count} events"
        )
        print(
            f"\n解析耗时: {elapsed:.3f}s ({result.event_count / elapsed / 1000:.1f}K events/sec)"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
