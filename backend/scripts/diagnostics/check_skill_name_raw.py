import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)
if result.skills:
    sk = result.skills[0]
    print(
        f"First skill name_raw type: {type(sk.name_raw)}, len: {len(sk.name_raw) if sk.name_raw else 0}"
    )
    print(f"First skill name_raw repr: {repr(sk.name_raw[:30])}")
