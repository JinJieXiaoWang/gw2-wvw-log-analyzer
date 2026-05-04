import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

print(f"first_event_time: {result.first_event_time}")
print(f"first event time: {result.events[0].time if result.events else None}")
print(f"last event time: {result.events[-1].time if result.events else None}")
print(f"duration_ms: {result.duration_ms}")
