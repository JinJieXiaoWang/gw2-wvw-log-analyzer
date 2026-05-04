import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect

from app.config.database import _get_engine

engine = _get_engine()
inspector = inspect(engine)

print("=== evtc_event columns (instid related) ===")
for c in inspector.get_columns("evtc_event"):
    if "instid" in c["name"]:
        print(f"  {c['name']}: {c['type']}")

# 检查 event 432 的 instid 值
from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)
if len(result.events) >= 432:
    ev = result.events[431]
    print(f"\nEvent 432:")
    print(f"  src_instid: {ev.src_instid}")
    print(f"  dst_instid: {ev.dst_instid}")
    print(f"  src_master_instid: {ev.src_master_instid}")
    print(f"  dst_master_instid: {ev.dst_master_instid}")
    print(f"  Max signed SMALLINT: {2**15-1}")
