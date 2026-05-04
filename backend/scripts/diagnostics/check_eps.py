import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

eps_list = result.get_events_per_second()
print(f"EPS entries: {len(eps_list)}")

max_second_offset = max(eps["second_offset"] for eps in eps_list)
min_second_offset = min(eps["second_offset"] for eps in eps_list)
print(f"second_offset range: {min_second_offset} - {max_second_offset}")

# 查找异常值
for i, eps in enumerate(eps_list):
    if eps["second_offset"] > 2147483647 or eps["second_offset"] < 0:
        print(
            f"Overflow at index {i}: second_offset={eps['second_offset']}, src_agent={eps['src_agent']}"
        )
        break
else:
    print("No overflow in second_offset values")
