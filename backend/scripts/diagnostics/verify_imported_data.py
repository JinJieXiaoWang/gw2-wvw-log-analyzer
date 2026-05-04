import os

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证已导入的 ZEVTC 测试文件数据
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config.database import _get_engine

engine = _get_engine()

file_sha256 = "7e8d31e59ef7189e4289054323db889f2c5ad67eb5cbdfc0ec49385c63535aec"

with engine.connect() as conn:
    # 获取 log_id
    row = conn.execute(
        text(
            "SELECT log_id, log_uuid, filename, parse_status, upload_time FROM evtc_log WHERE file_sha256 = :sha"
        ),
        {"sha": file_sha256},
    ).fetchone()

    if not row:
        print("[ERROR] 未找到导入的记录")
        sys.exit(1)

    log_id = row[0]
    print("=" * 70)
    print("导入验证报告")
    print("=" * 70)
    print(f"  log_id      : {row[0]}")
    print(f"  log_uuid    : {row[1]}")
    print(f"  filename    : {row[2]}")
    print(f"  parse_status: {row[3]}")
    print(f"  upload_time : {row[4]}")
    print()

    tables = [
        ("evtc_header", "log_id"),
        ("evtc_agent", "log_id"),
        ("evtc_skill", "log_id"),
        ("evtc_event", "log_id"),
        ("evtc_combat_meta", "log_id"),
        ("evtc_event_per_second", "log_id"),
    ]

    print("各表记录数量:")
    total_records = 0
    for table, pk_col in tables:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table} WHERE {pk_col} = :log_id"),
            {"log_id": log_id},
        ).scalar()
        total_records += count
        print(f"  {table:30s}: {count:>10,} 条")

    print()
    print(f"  总记录数（不含主表）: {total_records:,} 条")
    print("=" * 70)

    # 检查 evtc_header 详情
    header = conn.execute(
        text(
            "SELECT magic, evtc_date, revision, agent_count, skill_count FROM evtc_header WHERE log_id = :log_id"
        ),
        {"log_id": log_id},
    ).fetchone()
    if header:
        print()
        print("EVTC Header 详情:")
        print(f"  magic      : {header[0]}")
        print(f"  evtc_date  : {header[1]}")
        print(f"  revision   : {header[2]}")
        print(f"  agent_count: {header[3]}")
        print(f"  skill_count: {header[4]}")

    # 检查 combat_meta 详情
    meta = conn.execute(
        text(
            "SELECT first_event_time, last_event_time, duration_ms, enter_combat_count, change_down_count, change_dead_count FROM evtc_combat_meta WHERE log_id = :log_id"
        ),
        {"log_id": log_id},
    ).fetchone()
    if meta:
        print()
        print("Combat Meta 详情:")
        print(f"  first_event_time : {meta[0]}")
        print(f"  last_event_time  : {meta[1]}")
        print(f"  duration_ms      : {meta[2]}")
        print(f"  enter_combat_count: {meta[3]}")
        print(f"  change_down_count : {meta[4]}")
        print(f"  change_dead_count : {meta[5]}")

    print()
    print("=" * 70)
    print("验证完成。数据已就绪，可供审查。")
    print("=" * 70)
