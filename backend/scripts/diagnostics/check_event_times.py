import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

times = [e.time for e in result.events]
times_sorted = sorted(times)
print(f"Total events: {len(times)}")
print(f"Min time: {times_sorted[0]}")
print(f"Max time: {times_sorted[-1]}")
print(f"Median time: {times_sorted[len(times)//2]}")

# 检查异常大的时间值
threshold = 1_000_000_000_000  # 1 trillion
large_times = [(i, t) for i, t in enumerate(times) if t > threshold]
print(f"\nEvents with time > {threshold}: {len(large_times)}")
if large_times:
    print(f"First 5 large time events:")
    for idx, t in large_times[:5]:
        ev = result.events[idx]
        print(
            f"  event[{idx}] time={t}, statechange={ev.is_statechange}, src_agent={ev.src_agent}"
        )

# 检查 time == 0 的事件
zero_times = [(i, t) for i, t in enumerate(times) if t == 0]
print(f"\nEvents with time == 0: {len(zero_times)}")

# 正常范围的事件（在 median 附近 +- 1小时）
median = times_sorted[len(times) // 2]
normal_range = [t for t in times if median - 3600000 < t < median + 3600000]
print(f"\nEvents within 1 hour of median: {len(normal_range)}")
