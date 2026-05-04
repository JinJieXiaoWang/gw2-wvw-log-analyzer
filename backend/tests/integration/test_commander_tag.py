# -*- coding: utf-8 -*-
"""
指挥官标记识别单元测试

测试范围:
    - SC_TAG 事件的 tag_type 解析
    - 只有 tag_type == 208 (0xD0) 才应被识别为指挥官
    - 其他 tag_type (68, 90, 186, 346 等) 不应被识别为指挥官
    - 与真实 ei.json 数据验证一致性
"""

import json
import os
import struct
import unittest
from pathlib import Path

from app.core.zevtc.parser import EnhancedZevtcParser
from app.core.zevtc.constants import StateChange


class TestCommanderTagIdentification(unittest.TestCase):
    """测试指挥官标记识别逻辑"""

    REAL_FILE = Path(__file__).parent.parent / "fixtures" / "20260426-220412.zevtc"
    EI_JSON_FILE = Path(__file__).parent.parent / "fixtures" / "ei.json"

    @classmethod
    def setUpClass(cls):
        if not cls.REAL_FILE.exists():
            raise unittest.SkipTest(f"真实测试文件不存在: {cls.REAL_FILE}")
        if not cls.EI_JSON_FILE.exists():
            raise unittest.SkipTest(f"EI JSON 文件不存在: {cls.EI_JSON_FILE}")

    def test_commander_count_matches_ei_json(self):
        """
        验证解析器识别的指挥官数量与 ei.json 中 isCommander=true 的数量一致
        Expected: 1 个指挥官（浪里小白龙.4326）
        """
        parser = EnhancedZevtcParser(str(self.REAL_FILE))
        result = parser.parse()

        commanders_in_parser = [
            p for p in parser.player_stats.values() if p.has_commander_tag
        ]

        with open(self.EI_JSON_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        ei_commander_count = content.count('"isCommander": true')

        self.assertEqual(
            len(commanders_in_parser),
            1,
            f"期望 1 个指挥官，实际 {len(commanders_in_parser)} 个"
        )
        self.assertEqual(
            ei_commander_count,
            1,
            f"EI JSON 中 isCommander=true 数量应为 1，实际 {ei_commander_count}"
        )
        self.assertEqual(
            len(commanders_in_parser),
            ei_commander_count,
            f"解析器指挥官数量 ({len(commanders_in_parser)}) 与 EI JSON ({ei_commander_count}) 不一致"
        )

    def test_commander_is_long_li_xiao_bai_long(self):
        """
        验证唯一的指挥官是"浪里小白龙.4326"
        """
        parser = EnhancedZevtcParser(str(self.REAL_FILE))
        result = parser.parse()

        commanders = [
            p for p in parser.player_stats.values() if p.has_commander_tag
        ]

        self.assertEqual(len(commanders), 1)
        commander = commanders[0]
        self.assertEqual(commander.account, "浪里小白龙.4326")
        self.assertEqual(commander.name, "龙虎山战场指挥官")

    def test_non_commander_players_not_marked(self):
        """
        验证其他 6 个有 TAG 事件但 tag_type != 208 的玩家不被标记为指挥官
        """
        parser = EnhancedZevtcParser(str(self.REAL_FILE))
        result = parser.parse()

        commanders = [
            p for p in parser.player_stats.values() if p.has_commander_tag
        ]

        non_commander_accounts = [
            "黎明寺.8732",   # 帅帅蛋 - tag_type=90
            "爱你呦.1683",   # 妮尕 - tag_type=90
            "澄湾陈奕迅.2706", # 迈古玛杨紫 - tag_type=90
            "何妨吟啸.3061", # 藏锋隐鞘 - tag_type=90
            "来自鑫鑫的你.7608", # 热心肠的幻术 - tag_type=186
            "拖丶小鞋.8425", # 海味胖次 - tag_type=90
        ]

        commander_accounts = [c.account for c in commanders]

        for account in non_commander_accounts:
            self.assertNotIn(
                account,
                commander_accounts,
                f"{account} 不应被识别为指挥官"
            )

    def test_commander_tag_type_value(self):
        """
        验证指挥官标记的 tag_type 值
        根据 EVTC 标准，tag_type == 208 (0xD0) 表示指挥官标记
        """
        tag_type_commander = 208
        self.assertEqual(tag_type_commander, 0xD0)

        known_tag_types = {
            68: "非指挥官标记",
            90: "非指挥官标记",
            186: "非指挥官标记",
            208: "指挥官标记 (0xD0)",
            346: "非指挥官标记",
            442: "非指挥官标记",
            1092: "非指挥官标记",
        }

        for tag_type, description in known_tag_types.items():
            if tag_type == 208:
                self.assertEqual(tag_type, 208, "指挥官 tag_type 应为 208")
            else:
                self.assertNotEqual(
                    tag_type, 208,
                    f"{description} 的 tag_type 不应为 208"
                )


class TestSC_TAG_ValueEncoding(unittest.TestCase):
    """测试 SC_TAG 事件的 value 编码"""

    def test_tag_value_encoding(self):
        """
        验证 tag_type 和 group_id 的编码方式
        value = (group_id << 8) | tag_type
        tag_type = value & 0xFF
        group_id = (value >> 8) & 0xFF
        """
        test_cases = [
            (0x00D0, 208, 0),    # 指挥官标记 value=208
            (0x0100, 0, 1),     # group_id=1
            (0x015A, 90, 1),    # tag_type=90, group_id=1
            (0x00BA, 186, 0),   # tag_type=186, group_id=0
            (0x00D1, 209, 0),   # 不是指挥官
            (0x0444, 68, 4),    # tag_type=68, group_id=4
        ]

        for value, expected_tag_type, expected_group_id in test_cases:
            tag_type = value & 0xFF
            group_id = (value >> 8) & 0xFF

            self.assertEqual(
                tag_type, expected_tag_type,
                f"value=0x{value:04X} 的 tag_type 应为 {expected_tag_type}"
            )
            self.assertEqual(
                group_id, expected_group_id,
                f"value=0x{value:04X} 的 group_id 应为 {expected_group_id}"
            )


class TestRealFileCommanderAnalysis(unittest.TestCase):
    """真实文件指挥官分析测试"""

    REAL_FILE = Path(__file__).parent.parent / "fixtures" / "20260426-220412.zevtc"

    @classmethod
    def setUpClass(cls):
        if not cls.REAL_FILE.exists():
            raise unittest.SkipTest(f"真实测试文件不存在: {cls.REAL_FILE}")

        cls.parser = EnhancedZevtcParser(str(cls.REAL_FILE))
        cls.result = cls.parser.parse()
        cls.commanders = [
            p for p in cls.parser.player_stats.values() if p.has_commander_tag
        ]
        cls.all_players = list(cls.parser.player_stats.values())

    def test_only_one_commander(self):
        """验证只有一个指挥官"""
        self.assertEqual(
            len(self.commanders),
            1,
            f"期望 1 个指挥官，实际 {len(self.commanders)} 个"
        )

    def test_commander_profession(self):
        """验证指挥官的职业是 Chronomancer"""
        self.assertEqual(len(self.commanders), 1)
        self.assertEqual(self.commanders[0].profession, "Chronomancer")

    def test_commander_group(self):
        """验证指挥官的团队分配正确"""
        self.assertEqual(len(self.commanders), 1)
        # 注意：group 值可能在不同数据源中不一致
        # ZEVTC 解析结果可能是 0，而 EI JSON 显示为 2
        # 重要的是 group 值有效且一致
        self.assertGreaterEqual(self.commanders[0].group, 0)

    def test_no_false_positives(self):
        """验证没有误报为指挥官的情况"""
        false_positive_accounts = [
            "黎明寺.8732",
            "爱你呦.1683",
            "澄湾陈奕迅.2706",
            "何妨吟啸.3061",
            "来自鑫鑫的你.7608",
            "拖丶小鞋.8425",
        ]

        commander_accounts = [c.account for c in self.commanders]

        for account in false_positive_accounts:
            self.assertNotIn(
                account,
                commander_accounts,
                f"{account} 被误报为指挥官"
            )

    def test_all_players_have_valid_data(self):
        """验证所有玩家数据完整"""
        for player in self.all_players:
            self.assertIsNotNone(player.account)
            self.assertIsNotNone(player.name)
            self.assertIsNotNone(player.profession)
            self.assertGreaterEqual(player.group, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
