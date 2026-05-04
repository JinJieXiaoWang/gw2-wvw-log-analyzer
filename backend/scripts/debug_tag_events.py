#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：分析 ZEVTC 文件中的 SC_TAG 事件
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List, Optional, Set, Tuple
from app.core.zevtc import EvtcEvent
from app.core.zevtc.parser import EnhancedZevtcParser

def debug_tag_events(file_path):
    """调试 SC_TAG 事件"""
    print(f"分析文件: {file_path}")
    print("=" * 80)

    parser = EnhancedZevtcParser(file_path)

    # 临时保存原始处理逻辑
    original_process_single_event = parser._process_single_event

    tag_events = []

    def debug_process_single_event(ev: EvtcEvent, buff_states: Dict):
        """调试用的事件处理"""
        if ev.is_statechange == 37:  # SC_TAG
            tag_events.append({
                'time': ev.time,
                'src_addr': ev.src_agent,
                'value': ev.value,
                'group_id': ev.value >> 8,
                'tag_type': ev.value & 0xFF,
            })
            print(f"[SC_TAG] time={ev.time:.3f}, src_addr={ev.src_agent}, value={ev.value}, group_id={ev.value >> 8}, tag_type={ev.value & 0xFF}")

        # 调用原始处理逻辑
        return original_process_single_event(ev, buff_states)

    # 替换为调试版本
    parser._process_single_event = debug_process_single_event

    # 解析文件
    result = parser.parse()

    print("\n" + "=" * 80)
    print(f"共发现 {len(tag_events)} 个 SC_TAG 事件")
    print("\n按 src_addr 分组:")
    addr_groups = {}
    for event in tag_events:
        addr = event['src_addr']
        if addr not in addr_groups:
            addr_groups[addr] = []
        addr_groups[addr].append(event)

    for addr, events in addr_groups.items():
        player = parser.player_stats.get(addr)
        player_name = player.name if player else "Unknown"
        player_account = player.account if player else "Unknown"

        # 只显示有指挥官标记的事件（value != 0）
        commander_events = [e for e in events if e['value'] != 0]
        if commander_events:
            print(f"\n地址 {addr} ({player_name}, {player_account}):")
            print(f"  事件数量: {len(events)} (其中指挥官标记事件: {len(commander_events)})")
            for event in events:
                marker = " <-- 指挥官" if event['value'] != 0 else ""
                print(f"    time={event['time']:.3f}, value={event['value']}, group_id={event['group_id']}, tag_type={event['tag_type']}{marker}")

if __name__ == "__main__":
    test_file = r"d:\Code\backend\tests\fixtures\20260426-220412.zevtc"
    debug_tag_events(test_file)
