import os

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排查 _raw 字段乱码问题
对比数据库中的 name_raw 与 parser 解析出的 name_raw / name
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config.database import _get_engine
from app.core.zevtc.parser_core import EvtcParser

engine = _get_engine()

# 1. 从数据库读取 name_raw 样本
print("=" * 70)
print("[1] 数据库中 name_raw 样本")
print("=" * 70)

with engine.connect() as conn:
    # 取前5个 agent 的 name_raw
    rows = conn.execute(
        text(
            "SELECT agent_index, name_raw, name FROM evtc_agent WHERE log_id = 8 ORDER BY agent_index LIMIT 5"
        )
    ).fetchall()
    for row in rows:
        idx, raw_db, name_db = row
        raw_hex = raw_db.hex() if raw_db else "NULL"
        raw_len = len(raw_db) if raw_db else 0
        print(f"  Agent[{idx}] name_raw(len={raw_len}): {raw_hex[:40]}...")
        print(f"           name(DB): {name_db}")
        if raw_db:
            # 尝试用 UTF-8 解码，忽略错误
            decoded = raw_db.split(b"\x00")[0].decode("utf-8", errors="replace")
            print(f"           decoded : {decoded}")
        print()

    # 取前5个 skill 的 name_raw
    rows = conn.execute(
        text(
            "SELECT skill_index, name_raw, name FROM evtc_skill WHERE log_id = 8 ORDER BY skill_index LIMIT 5"
        )
    ).fetchall()
    for row in rows:
        idx, raw_db, name_db = row
        raw_hex = raw_db.hex() if raw_db else "NULL"
        raw_len = len(raw_db) if raw_db else 0
        print(f"  Skill[{idx}] name_raw(len={raw_len}): {raw_hex[:40]}...")
        print(f"           name(DB): {name_db}")
        if raw_db:
            decoded = raw_db.split(b"\x00")[0].decode("utf-8", errors="replace")
            print(f"           decoded : {decoded}")
        print()

# 2. 从 parser 直接读取对比
print("=" * 70)
print("[2] Parser 直接解析出的 name_raw 样本")
print("=" * 70)

parser = EvtcParser(path="tests/20260426-220412.zevtc")
result = parser.parse_file(compute_sha256=False)

for i in range(min(5, len(result.agents))):
    ag = result.agents[i]
    raw_hex = ag.name_raw.hex() if ag.name_raw else "NULL"
    raw_len = len(ag.name_raw) if ag.name_raw else 0
    print(f"  Agent[{i}] name_raw(len={raw_len}): {raw_hex[:40]}...")
    print(f"           name(parser): {ag.name}")
    print()

for i in range(min(5, len(result.skills))):
    sk = result.skills[i]
    raw_hex = sk.name_raw.hex() if sk.name_raw else "NULL"
    raw_len = len(sk.name_raw) if sk.name_raw else 0
    print(f"  Skill[{i}] name_raw(len={raw_len}): {raw_hex[:40]}...")
    print(f"           name(parser): {sk.name}")
    print()

# 3. 检查数据库连接编码
print("=" * 70)
print("[3] 数据库连接字符集设置")
print("=" * 70)
with engine.connect() as conn:
    rs = conn.execute(text("SHOW VARIABLES LIKE 'character_set%'"))
    for row in rs:
        print(f"  {row[0]}: {row[1]}")
