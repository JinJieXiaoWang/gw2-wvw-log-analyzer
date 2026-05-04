#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境标准化流程脚本
功能：
  1. 保留系统表（admins, sys_dict_type, sys_dict_data），删除其他所有数据表
  2. 使用 SQLAlchemy 重建所有表
  3. 运行 ZEVTC 导入并验证数据完整性
  4. 输出测试报告

用法：
  python scripts/test_standardization.py [--keep-old] [--file tests/20260426-220412.zevtc]
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.config.database import Base, _get_engine, init_db
from app.config.database_settings import db_settings
from app.core.zevtc.db_writer import EvtcDatabaseWriter
from app.core.zevtc.exceptions import DuplicateFileError
from app.core.zevtc.parser_core import EvtcParser

# 系统基础设施表（保留）
SYSTEM_TABLES = {"admins", "sys_dict_type", "sys_dict_data"}

# ZEVTC 核心表（必须创建并通过测试验证）
ZEVTC_CORE_TABLES = {
    "evtc_log",
    "evtc_header",
    "evtc_agent",
    "evtc_skill",
    "evtc_event",
    "evtc_combat_meta",
    "evtc_event_per_second",
    "evtc_player_instance",
}

# EI 派生表
EI_TABLES = {"ei_player", "ei_target", "ei_skill_map", "ei_phase"}

# 旧运营表（按需保留）
OLD_OPERATIONAL = {
    "fights",
    "fight_stats",
    "fight_details",
    "members",
    "skills",
    "skill_events",
}

# 辅助功能表（测试时可删除）
AUXILIARY_TABLES = {
    "batch_parse_tasks",
    "batch_parse_task_items",
    "builds",
    "ai_reports",
    "profession_roles",
    "role_templates",
    "role_condition_expressions",
    "storage_cleanup_records",
    "storage_monitor_records",
}


def get_all_tables():
    """获取数据库中所有表名"""
    engine = _get_engine()
    inspector = inspect(engine)
    return set(inspector.get_table_names())


def drop_non_system_tables(dry_run=False):
    """删除所有非系统表"""
    engine = _get_engine()
    existing = get_all_tables()
    to_drop = existing - SYSTEM_TABLES

    print("=" * 70)
    print("[步骤 1/5] 清理非系统表")
    print("=" * 70)
    print(f"  现有表: {len(existing)} 个")
    print(f"  系统表（保留）: {', '.join(sorted(SYSTEM_TABLES & existing))}")
    print(f"  待删除表: {len(to_drop)} 个")
    for t in sorted(to_drop):
        print(f"    - {t}")

    if dry_run:
        print("  [DRY RUN] 未实际执行删除")
        return

    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in sorted(to_drop):
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS `{t}`"))
                print(f"    ✓ 已删除: {t}")
            except Exception as e:
                print(f"    ✗ 删除失败 {t}: {e}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

    print()


def recreate_tables():
    """使用 SQLAlchemy ORM 重建所有模型表"""
    print("=" * 70)
    print("[步骤 2/5] 重建表结构")
    print("=" * 70)

    engine = _get_engine()
    inspector = inspect(engine)
    before = set(inspector.get_table_names())

    # 加载所有模型（通过 import）
    from app.models import (
        Admin,
        AIReport,
        BatchParseTask,
        BatchParseTaskItem,
        Build,
        EiPhase,
        EiPlayer,
        EiSkillMap,
        EiTarget,
        EvtcAgentModel,
        EvtcCombatMeta,
        EvtcEventModel,
        EvtcEventPerSecond,
        EvtcHeaderModel,
        EvtcPlayerInstance,
        EvtcSkillModel,
        Fight,
        FightDetails,
        FightStats,
        Log,
        Member,
        ProfessionRole,
        RoleConditionExpression,
        RoleTemplate,
        Skill,
        SkillEvent,
        StorageCleanupRecord,
        StorageMonitorRecord,
        SysDictData,
        SysDictType,
    )

    # 创建所有缺失的表
    Base.metadata.create_all(bind=engine)

    after = set(inspector.get_table_names())
    created = after - before
    print(f"  重建前表数: {len(before)}")
    print(f"  重建后表数: {len(after)}")
    if created:
        print(f"  新建表: {len(created)} 个")
        for t in sorted(created):
            print(f"    ✓ {t}")
    print()


def verify_table_structure():
    """验证核心表结构是否符合预期"""
    print("=" * 70)
    print("[步骤 3/5] 验证表结构")
    print("=" * 70)

    engine = _get_engine()
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())

    required = ZEVTC_CORE_TABLES | EI_TABLES | OLD_OPERATIONAL | SYSTEM_TABLES
    missing = required - existing
    extra = existing - required - AUXILIARY_TABLES

    ok = True
    for t in sorted(required):
        if t in existing:
            print(f"  ✓ {t}")
        else:
            print(f"  ✗ {t} (缺失)")
            ok = False

    if missing:
        print(f"\n  警告: {len(missing)} 个必需表缺失")
    if extra:
        print(f"\n  信息: {len(extra)} 个额外表存在")
    print()
    return ok


def import_zevtc_file(file_path: str):
    """导入 ZEVTC 文件并返回结果"""
    print("=" * 70)
    print("[步骤 4/5] 导入 ZEVTC 文件")
    print("=" * 70)
    print(f"  文件: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 解析
    parse_start = time.time()
    parser = EvtcParser(path=file_path)
    parse_result = parser.parse_file(compute_sha256=True)
    parse_elapsed = (time.time() - parse_start) * 1000

    print(f"  解析耗时: {parse_elapsed:.1f} ms")
    print(f"  Agents: {parse_result.agent_count}")
    print(f"  Skills: {parse_result.skill_count}")
    print(f"  Events: {parse_result.event_count}")

    # 写入数据库
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
        result = writer.import_parse_result(parse_result, update_on_duplicate=False)
        import_elapsed = (time.time() - import_start) * 1000
        print(f"  导入耗时: {import_elapsed:.1f} ms")
        print(f"  log_id: {result.log_id}")
        print(f"  status: {result.status}")
        writer.close()
        return result
    except DuplicateFileError as e:
        print(f"  文件已存在，跳过导入: {e}")
        writer.close()
        return None


def verify_imported_data(log_id: int, expected: dict):
    """验证导入数据的完整性和一致性"""
    print("=" * 70)
    print("[步骤 5/5] 验证数据完整性")
    print("=" * 70)

    engine = _get_engine()
    checks = []

    with engine.connect() as conn:
        # 检查 1: evtc_log 记录存在
        row = conn.execute(
            text("SELECT log_id, parse_status FROM evtc_log WHERE log_id = :id"),
            {"id": log_id},
        ).fetchone()
        if row and row[1] == "completed":
            checks.append(("evtc_log 记录存在且状态=completed", True))
        else:
            checks.append(("evtc_log 记录存在且状态=completed", False))

        # 检查 2: 各表记录数匹配
        tables_to_check = {
            "evtc_header": expected.get("header", 1),
            "evtc_agent": expected.get("agents", 0),
            "evtc_skill": expected.get("skills", 0),
            "evtc_event": expected.get("events", 0),
            "evtc_combat_meta": expected.get("combat_meta", 1),
            "evtc_event_per_second": expected.get("event_per_second", 0),
        }

        for table, expected_count in tables_to_check.items():
            actual = conn.execute(
                text(f"SELECT COUNT(*) FROM {table} WHERE log_id = :id"), {"id": log_id}
            ).scalar()
            ok = actual == expected_count
            checks.append((f"{table}: {actual} == {expected_count}", ok))

        # 检查 3: evtc_event 的 event_index 连续性
        event_indices = conn.execute(
            text(
                "SELECT COUNT(DISTINCT event_index), MIN(event_index), MAX(event_index) FROM evtc_event WHERE log_id = :id"
            ),
            {"id": log_id},
        ).fetchone()
        if event_indices:
            distinct, min_idx, max_idx = event_indices
            expected_events = expected.get("events", 0)
            # event_index 应从 0 开始到 events-1
            ok = (
                distinct == expected_events
                and min_idx == 0
                and max_idx == expected_events - 1
            )
            checks.append((f"evtc_event event_index 连续性: 0~{expected_events-1}", ok))

        # 检查 4: agent_index 范围
        agent_range = conn.execute(
            text(
                "SELECT MIN(agent_index), MAX(agent_index) FROM evtc_agent WHERE log_id = :id"
            ),
            {"id": log_id},
        ).fetchone()
        if agent_range:
            min_a, max_a = agent_range
            ok = min_a == 0 and max_a == expected.get("agents", 0) - 1
            checks.append(
                (f"evtc_agent agent_index 范围: 0~{expected.get('agents', 0)-1}", ok)
            )

        # 检查 5: SHA256 一致性
        sha_row = conn.execute(
            text("SELECT file_sha256 FROM evtc_log WHERE log_id = :id"), {"id": log_id}
        ).fetchone()
        if sha_row:
            checks.append((f"file_sha256 已存储: {sha_row[0][:16]}...", True))

    all_passed = all(ok for _, ok in checks)
    for desc, ok in checks:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {desc}")

    print()
    if all_passed:
        print("  [PASS] 所有完整性检查通过")
    else:
        print("  [FAIL] 部分检查未通过，请查看详情")
    print()
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="测试环境标准化流程")
    parser.add_argument(
        "--file", default="tests/20260426-220412.zevtc", help="要导入的 ZEVTC 文件路径"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印要删除的表，不实际执行"
    )
    parser.add_argument(
        "--skip-drop", action="store_true", help="跳过删除步骤（仅重建缺失表）"
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("ZEVTC 测试环境标准化流程")
    print("=" * 70)
    print(f"  数据库: {db_settings.DB_TYPE.value}")
    print(f"  目标文件: {args.file}")
    print()

    # 步骤 1: 清理
    if not args.skip_drop:
        drop_non_system_tables(dry_run=args.dry_run)
    else:
        print("[步骤 1/5] 跳过清理（--skip-drop）\n")

    if args.dry_run:
        print("干运行结束，未执行任何变更。")
        return

    # 步骤 2: 重建表
    recreate_tables()

    # 步骤 3: 验证结构
    if not verify_table_structure():
        print("[ABORT] 表结构验证失败，终止测试")
        sys.exit(1)

    # 步骤 4: 导入文件
    result = import_zevtc_file(args.file)
    if result is None:
        print("[ABORT] 导入失败或文件已存在")
        sys.exit(1)

    # 步骤 5: 验证数据
    expected = {
        "header": 1,
        "agents": result.agent_count,
        "skills": result.skill_count,
        "events": result.event_count,
        "combat_meta": 1,
        "event_per_second": result.event_count,  # approximate upper bound
    }
    passed = verify_imported_data(result.log_id, expected)

    # 最终报告
    print("=" * 70)
    print("测试报告摘要")
    print("=" * 70)
    print(f"  log_id       : {result.log_id}")
    print(f"  filename     : {result.filename}")
    print(f"  agent_count  : {result.agent_count}")
    print(f"  skill_count  : {result.skill_count}")
    print(f"  event_count  : {result.event_count}")
    print(f"  完整性检查   : {'通过' if passed else '未通过'}")
    print("=" * 70)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
