#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据初始化 CLI 工具

用法：
    python scripts/init_data.py              # 检查状态
    python scripts/init_data.py --run        # 执行初始化
    python scripts/init_data.py --run --force # 强制重新初始化
    python scripts/init_data.py --validate   # 仅校验种子数据

作者：帅妹妹丶.8297
创建日期：2026-05-15
"""

import argparse
import json
import sys
import traceback

# 将 backend 加入路径
sys.path.insert(0, "backend")

from app.config.database import SessionLocal, init_db
from app.core.initialization import (
    DataVersionManager,
    InitializationError,
    RetryConfig,
    SeedDataLoader,
    SeedDataValidator,
)
from app.services.system.initialization_service import InitializationService
from app.utils.logger import logger


def print_json(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_status():
    """查询初始化状态"""
    print("=" * 60)
    print("数据初始化状态查询")
    print("=" * 60)

    init_db()
    db = SessionLocal()
    try:
        vm = DataVersionManager(db)
        applied = vm.get_applied_version()
        should_apply, reason = vm.check_version(force=False)

        print(f"\n当前数据版本: {DataVersionManager.CURRENT_VERSION}")
        print(f"已应用版本:   {applied['version'] if applied else '无'}")
        print(f"需要初始化:   {'是' if should_apply else '否'}")
        print(f"原因:         {reason}")

        if applied:
            print(f"\n应用时间:     {applied['applied_at']}")
            print(f"文件列表:     {len(applied.get('files', []))} 个")
    finally:
        db.close()


def cmd_validate():
    """仅校验种子数据"""
    print("=" * 60)
    print("种子数据强制校验")
    print("=" * 60)

    seeds = {}
    seed_names = [
        "sys_menu",
        "sys_dict_type",
        "sys_dict_data",
        "gw_role_type",
        "gw_profession",
        "gw_elite_specialization",
    ]

    print("\n正在加载种子数据...")
    for name in seed_names:
        try:
            seeds[name] = SeedDataLoader.load(name)
            print(f"  ✓ {name}: {len(seeds[name]) if isinstance(seeds[name], list) else 'N/A'} 条")
        except InitializationError as e:
            print(f"  ✗ {name}: 加载失败 - {e}")
            return 1

    print("\n正在执行校验...")
    errors, warnings = SeedDataValidator.validate_all(seeds)

    for w in warnings:
        print(f"  ⚠ {w}")

    if errors:
        print(f"\n✗ 校验失败，共 {len(errors)} 个错误:")
        for e in errors:
            print(f"    - {e}")
        return 1
    else:
        print(f"\n✓ 校验通过，共 {len(seeds)} 个种子数据")
        return 0


def cmd_run(force: bool = False, max_attempts: int = 5):
    """执行初始化"""
    print("=" * 60)
    print("数据初始化")
    print("=" * 60)
    print(f"强制模式:     {force}")
    print(f"最大重试:     {max_attempts}")
    print()

    init_db()
    db = SessionLocal()
    try:
        retry_config = RetryConfig(max_attempts=max_attempts)
        service = InitializationService(db, retry_config=retry_config, force=force)
        summary = service.run()

        print("\n" + "=" * 60)
        print("初始化完成")
        print("=" * 60)
        print_json(summary)
        return 0
    except InitializationError as e:
        print("\n" + "=" * 60)
        print("初始化失败")
        print("=" * 60)
        print(f"步骤:        {e.step}")
        print(f"错误类型:    {e.error_type}")
        print(f"时间戳:      {e.timestamp}")
        print(f"建议:        {e.suggestion}")
        if e.data_snippet:
            print(f"数据片段:    {json.dumps(e.data_snippet, ensure_ascii=False, default=str)[:500]}")
        print()
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ 未预料错误: {e}")
        traceback.print_exc()
        return 1
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="GW2 日志系统数据初始化工具")
    parser.add_argument("--run", action="store_true", help="执行初始化")
    parser.add_argument("--force", action="store_true", help="强制重新初始化")
    parser.add_argument("--validate", action="store_true", help="仅校验种子数据")
    parser.add_argument("--status", action="store_true", help="查询状态")
    parser.add_argument("--max-attempts", type=int, default=5, help="最大重试次数")

    args = parser.parse_args()

    if args.validate:
        sys.exit(cmd_validate())
    elif args.status:
        sys.exit(cmd_status())
    elif args.run:
        sys.exit(cmd_run(force=args.force, max_attempts=args.max_attempts))
    else:
        # 默认查询状态
        cmd_status()
        print("\n提示: 使用 --run 执行初始化, --validate 校验数据, --help 查看帮助")


if __name__ == "__main__":
    main()
