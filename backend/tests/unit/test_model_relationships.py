#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：测试模型关系定义
# 作者：系统
# 创建日期：2026-05-01
# 依赖说明：SQLAlchemy

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models import *  # 强制加载所有模型


def test_model_relationships():
    """测试所有模型关系是否正确定义"""
    print()
    print("=" * 60)
    print("测试模型关系定义")
    print("=" * 60)
    print()

    errors = []
    warnings = []

    # 使用 SQLite 内存数据库进行测试（隔离且快速）
    test_engine = create_engine("sqlite:///:memory:", echo=False)

    # 尝试创建所有表
    print("1. 验证所有模型表结构:")
    try:
        Base.metadata.create_all(bind=test_engine)
        inspector = inspect(test_engine)
        table_names = inspector.get_table_names()

        expected_tables = [
            "evtc_log",
            "ei_player",
            "ei_target",
            "ei_skill_map",
            "ei_phase",
            "fights",
            "fight_stats",
            "members",
            "batch_parse_tasks",
            "batch_parse_task_items",
            "sys_dict_type",
            "sys_dict_data",
            "storage_cleanup_records",
            "storage_monitor_records",
        ]

        for table in expected_tables:
            if table in table_names:
                print(f"   [OK] 表 {table} 创建成功")
            else:
                errors.append(f"表 {table} 未创建")
                print(f"   [FAIL] 表 {table} 未创建")

    except Exception as e:
        errors.append(f"创建表失败: {e}")
        print(f"   [FAIL] 创建表失败: {e}")
        import traceback

        traceback.print_exc()

    # 验证外键关系
    print("\n2. 验证外键关系:")
    try:
        inspector = inspect(test_engine)
        tables_with_relations = {
            "evtc_log": [],
            "ei_player": ["evtc_log"],
            "ei_target": ["evtc_log"],
            "ei_skill_map": ["evtc_log"],
            "ei_phase": ["evtc_log"],
            "fights": ["evtc_log"],
            "fight_stats": ["fights", "members"],
            "batch_parse_tasks": ["sys_user"],
            "batch_parse_task_items": ["batch_parse_tasks", "evtc_log"],
        }

        for table_name, expected_references in tables_with_relations.items():
            if table_name not in inspector.get_table_names():
                continue

            fks = inspector.get_foreign_keys(table_name)
            referenced_tables = set()

            for fk in fks:
                ref_table = fk.get("referred_table")
                if ref_table:
                    referenced_tables.add(ref_table)

            missing_refs = [
                ref for ref in expected_references if ref not in referenced_tables
            ]
            if missing_refs:
                errors.append(f"表 {table_name} 缺少外键引用: {missing_refs}")
                print(f"   [FAIL] 表 {table_name} 缺少外键引用: {missing_refs}")
            else:
                print(f"   [OK] 表 {table_name} 外键关系正确")

    except Exception as e:
        errors.append(f"外键验证失败: {e}")
        print(f"   [FAIL] 外键验证失败: {e}")

    # 输出结果
    print("\n" + "=" * 60)
    if errors:
        print("[FAIL] 发现问题:")
        for error in errors:
            print(f"   - {error}")
        print("\n请修复上述问题后重新运行测试")
        return False
    else:
        print("[OK] 所有模型关系定义正确！")
        return True


if __name__ == "__main__":
    success = test_model_relationships()
    sys.exit(0 if success else 1)
