import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect

from app.config.database import _get_engine

engine = _get_engine()
inspector = inspect(engine)

for c in inspector.get_columns("evtc_event_per_second"):
    print(f"  {c['name']}: {c['type']}")

# 检查 second_offset 最大值
from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

if result.events:
    first_time = result.events[0].time
    last_time = result.events[-1].time
    duration_sec = (last_time - first_time) // 1000
    print(f"\nFirst event time: {first_time}")
    print(f"Last event time: {last_time}")
    print(f"Duration sec: {duration_sec}")
    print(f"Max signed INT: {2**31-1}")
