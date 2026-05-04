import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

eps_list = result.get_events_per_second()
print(f"EPS entries: {len(eps_list)}")

# 打印前5个和后5个
for i in range(min(5, len(eps_list))):
    eps = eps_list[i]
    print(f"  [{i}] src_agent={eps['src_agent']}, second_offset={eps['second_offset']}")

print("  ...")
for i in range(max(0, len(eps_list) - 5), len(eps_list)):
    eps = eps_list[i]
    print(f"  [{i}] src_agent={eps['src_agent']}, second_offset={eps['second_offset']}")

# 检查是否有超出INT范围的second_offset
overflows = [
    eps
    for eps in eps_list
    if eps["second_offset"] > 2147483647 or eps["second_offset"] < 0
]
print(f"\nOverflow count: {len(overflows)}")
if overflows:
    print(f"First overflow: {overflows[0]}")
