import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect

from app.config.database import _get_engine

engine = _get_engine()
inspector = inspect(engine)

print("=== evtc_event columns ===")
for c in inspector.get_columns("evtc_event"):
    print(f"  {c['name']}: {c['type']}")

# 检查第8个event的src_agent
from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)
if len(result.events) >= 8:
    ev = result.events[7]
    print(f"\nEvent 8 src_agent: {ev.src_agent}")
    print(f"Event 8 dst_agent: {ev.dst_agent}")
    print(f"Max signed BIGINT: {2**63-1}")
