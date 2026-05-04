import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

times = [e.time for e in result.events]
min_time = min(times)
max_time = max(times)
first_time = result.events[0].time
last_time = result.events[-1].time

print(f"events count: {len(result.events)}")
print(f"first event time: {first_time}")
print(f"last event time: {last_time}")
print(f"min time: {min_time}")
print(f"max time: {max_time}")
print(f"sorted by time? {times == sorted(times)}")

# 找到时间小于 first_time 的事件
early_events = [e for e in result.events if e.time < first_time]
print(f"events before first_event_time: {len(early_events)}")
if early_events:
    print(f"earliest such event time: {min(e.time for e in early_events)}")
