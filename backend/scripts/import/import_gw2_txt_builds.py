# -*- coding: utf-8 -*-
"""
数据迁移脚本：从 builds_initial_data.json 导入配置数据到数据库

功能说明：
1. 清空现有 builds 表数据
2. 从 JSON 文件读取配置数据（已与数据库表结构完全兼容）
3. 直接写入数据库（无需调用 BD Code 解析 API）
4. 生成导入报告

使用方法：
    cd D:\Code\Gw2-wvw-log-analyzer\backend
    python scripts/import/import_gw2_txt_builds.py

作者: System
创建日期: 2026-05-06
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config.database import SessionLocal, init_db
from app.services.build_service import create_build
from app.models.build import Build
from app.utils.logger import logger

# JSON 数据文件路径
JSON_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app", "data", "builds_initial_data.json"
)


def load_json_data(path: str) -> List[Dict[str, Any]]:
    """从 JSON 文件加载配置数据"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"成功从 {path} 加载 {len(data)} 条配置数据")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON 文件解析失败: {e}")
        raise
    except Exception as e:
        logger.error(f"读取 JSON 文件失败: {e}")
        raise


def clear_existing_builds(db) -> int:
    """清空现有 builds 表数据"""
    count = db.query(Build).count()
    if count > 0:
        db.query(Build).delete()
        db.commit()
        logger.info(f"已清空 builds 表，删除 {count} 条旧数据")
    return count


def import_builds(db, builds_data: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """导入配置数据到数据库"""
    success_count = 0
    failure_count = 0
    errors: List[str] = []

    for idx, raw in enumerate(builds_data, 1):
        try:
            # JSON 数据已经与数据库表结构兼容，直接使用
            build = create_build(db, raw)
            logger.info(f"[{idx}/{len(builds_data)}] 导入成功: {build.title} (id={build.id})")
            success_count += 1
        except Exception as e:
            err_msg = f"[{idx}/{len(builds_data)}] 导入失败: {raw.get('title', 'Unknown')} - {e}"
            logger.error(err_msg)
            errors.append(err_msg)
            failure_count += 1

    return success_count, failure_count, errors


def print_report(cleared: int, success: int, failure: int, errors: List[str]) -> None:
    """打印导入结果报告"""
    total = success + failure
    print("\n" + "=" * 60)
    print("Build 数据导入报告")
    print("=" * 60)
    print(f"数据文件: {JSON_DATA_PATH}")
    print(f"导入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"清空旧数据: {cleared} 条")
    print(f"总记录数: {total}")
    print(f"  [OK] 成功: {success}")
    print(f"  [FAIL] 失败: {failure}")
    print(f"成功率:   {success / total * 100:.1f}%" if total > 0 else "N/A")

    if errors:
        print("\n失败明细:")
        print("-" * 60)
        for err in errors:
            print(f"  • {err}")

    print("=" * 60)

    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs", "build_import_report.txt"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Build 数据导入报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据文件: {JSON_DATA_PATH}\n")
        f.write(f"清空旧数据: {cleared} 条\n")
        f.write(f"总记录数: {total}\n")
        f.write(f"成功: {success}\n")
        f.write(f"失败: {failure}\n")
        if errors:
            f.write("\n失败明细:\n")
            for err in errors:
                f.write(f"  • {err}\n")
    print(f"\n报告已保存至: {report_path}")


def main():
    print("=" * 60)
    print("Build 数据导入工具 (JSON)")
    print("=" * 60)

    if not os.path.exists(JSON_DATA_PATH):
        print(f"错误: 找不到数据文件 {JSON_DATA_PATH}")
        sys.exit(1)

    print(f"\n数据文件路径: {JSON_DATA_PATH}")

    # 初始化数据库
    print("\n初始化数据库连接...")
    init_db()

    # 加载数据
    print("加载 JSON 数据...")
    builds_data = load_json_data(JSON_DATA_PATH)
    print(f"共加载到 {len(builds_data)} 个配置")

    # 确认导入
    print(f"\n即将执行以下操作:")
    print(f"  1. 清空现有 builds 表数据")
    print(f"  2. 导入 {len(builds_data)} 条来自 JSON 文件的配置")
    confirm = input("\n确认继续? [Y/n]: ").strip().lower()
    if confirm and confirm not in ("y", "yes"):
        print("操作已取消。")
        sys.exit(0)

    db = SessionLocal()
    try:
        # 清空旧数据
        cleared = clear_existing_builds(db)

        # 执行导入
        print("\n开始导入数据...")
        success, failure, errors = import_builds(db, builds_data)
        print_report(cleared, success, failure, errors)
    finally:
        db.close()

    if failure == 0:
        print("\n[OK] 所有数据导入成功!")
    else:
        print(f"\n[WARN] 导入完成，有 {failure} 条记录失败，请查看日志。")


if __name__ == "__main__":
    main()
