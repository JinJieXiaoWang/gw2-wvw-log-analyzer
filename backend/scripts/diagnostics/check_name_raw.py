import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.config.database import _get_engine

engine = _get_engine()
inspector = inspect(engine)

cols = inspector.get_columns("evtc_agent")
for c in cols:
    if c["name"] == "name_raw":
        print(f"name_raw: {c['type']}, nullable={c['nullable']}")

# 也检查第一个 agent 的 name_raw 长度
from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)
if result.agents:
    ag = result.agents[0]
    print(
        f"First agent name_raw type: {type(ag.name_raw)}, len: {len(ag.name_raw) if ag.name_raw else 0}"
    )
    print(f"First agent name_raw repr: {repr(ag.name_raw[:20])}")
