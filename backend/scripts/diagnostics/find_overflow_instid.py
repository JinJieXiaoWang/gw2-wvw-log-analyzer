import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser_core import EvtcParser

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

max_signed_smallint = 32767

for i, ev in enumerate(result.events):
    for field in ["src_instid", "dst_instid", "src_master_instid", "dst_master_instid"]:
        val = getattr(ev, field)
        if val > max_signed_smallint:
            print(f"Event {i+1} (0-index {i}): {field} = {val}")
            if i > 0:
                prev = result.events[i - 1]
                print(
                    f"  Prev event: src_instid={prev.src_instid}, dst_instid={prev.dst_instid}, src_master={prev.src_master_instid}, dst_master={prev.dst_master_instid}"
                )
            break
    else:
        continue
    break
else:
    print("No overflow found in direct check")

# 也检查所有值的最大值
max_src = max(ev.src_instid for ev in result.events)
max_dst = max(ev.dst_instid for ev in result.events)
max_src_master = max(ev.src_master_instid for ev in result.events)
max_dst_master = max(ev.dst_master_instid for ev in result.events)
print(f"\nMax values:")
print(f"  src_instid: {max_src}")
print(f"  dst_instid: {max_dst}")
print(f"  src_master_instid: {max_src_master}")
print(f"  dst_master_instid: {max_dst_master}")
