#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入测试 ZEVTC 文件到数据库
使用最新版本的解析器 (app/core/zevtc/) 和数据库写入器 (tests/zevtc/)
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database_settings import db_settings
from app.core.zevtc.db_writer import EvtcDatabaseWriter
from app.core.zevtc.exceptions import DuplicateFileError
from app.core.zevtc.parser_core import EvtcParser


def main():
    file_path = "tests/20260426-220412.zevtc"
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        sys.exit(1)

    print("=" * 70)
    print("ZEVTC 文件导入任务")
    print("=" * 70)
    print(f"文件路径: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path):,} bytes")
    print(
        f"目标数据库: {db_settings.DB_TYPE.value} @ {db_settings.MYSQL_HOST}:{db_settings.MYSQL_PORT}/{db_settings.MYSQL_DATABASE}"
    )
    print("=" * 70)
    print()

    # 阶段 1: 解析
    print("[1/3] 开始解析文件...")
    parse_start = time.time()
    parser = EvtcParser(path=file_path)
    parse_result = parser.parse_file(compute_sha256=True)
    parse_elapsed = (time.time() - parse_start) * 1000

    print(f"      解析耗时: {parse_elapsed:.1f} ms")
    print(f"      文件 SHA256: {parse_result.file_sha256}")
    print(f"      压缩大小: {parse_result.compressed_size:,} bytes")
    print(f"      解压大小: {parse_result.raw_data_size:,} bytes")
    print(f"      EVTC 版本: {parse_result.header.evtc_version}")
    print(f"      记录日期: {parse_result.header.record_date}")
    print(f"      Agent 数量: {parse_result.agent_count:,}")
    print(f"      Skill 数量: {parse_result.skill_count:,}")
    print(f"      Event 数量: {parse_result.event_count:,}")
    print()

    # 阶段 2: 数据库导入 (不执行删除操作)
    print("[2/3] 开始数据库导入...")
    print("      策略: update_on_duplicate=False (重复文件将跳过，不删除任何数据)")
    print()

    writer = EvtcDatabaseWriter(
        host=db_settings.MYSQL_HOST,
        port=db_settings.MYSQL_PORT,
        user=db_settings.MYSQL_USER,
        password=db_settings.MYSQL_PASSWORD,
        database=db_settings.MYSQL_DATABASE,
        charset=db_settings.MYSQL_CHARSET,
    )

    import_start = time.time()
    try:
        import_result = writer.import_parse_result(
            parse_result, update_on_duplicate=False  # 关键：不删除任何已有数据
        )
        import_elapsed = (time.time() - import_start) * 1000

        print("=" * 70)
        print("导入成功")
        print("=" * 70)
        print(f"  log_id      : {import_result.log_id}")
        print(f"  log_uuid    : {import_result.log_uuid}")
        print(f"  filename    : {import_result.filename}")
        print(f"  status      : {import_result.status}")
        print(f"  is_duplicate: {import_result.is_duplicate}")
        print(f"  agent_count : {import_result.agent_count:,}")
        print(f"  skill_count : {import_result.skill_count:,}")
        print(f"  event_count : {import_result.event_count:,}")
        print(f"  parse_time  : {parse_elapsed:.1f} ms")
        print(f"  import_time : {import_elapsed:.1f} ms")
        print(f"  total_time  : {parse_elapsed + import_elapsed:.1f} ms")
        print("=" * 70)
        print()
        print("[3/3] 数据已写入以下表（无删除操作）:")
        print("      - evtc_log")
        print("      - evtc_header")
        print("      - evtc_agent")
        print("      - evtc_skill")
        print("      - evtc_event")
        print("      - evtc_combat_meta (派生)")
        print("      - evtc_event_per_second (派生)")
        print()
        print("请审查数据库中的数据以验证准确性和完整性。")

    except DuplicateFileError as e:
        print("=" * 70)
        print("文件已存在 — 跳过导入（未执行任何删除操作）")
        print("=" * 70)
        print(f"  原因: {e}")
        print(f"  该文件的 SHA256 指纹已在 evtc_log 表中存在。")
        print(f"  根据要求，未删除任何数据，也未更新现有记录。")
        print("=" * 70)
        sys.exit(0)

    except Exception as e:
        print("=" * 70)
        print("导入失败")
        print("=" * 70)
        print(f"  错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        writer.close()


if __name__ == "__main__":
    main()
