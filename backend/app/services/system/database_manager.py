# -*- coding: utf-8 -*-
# 模块功能：数据库管理工具
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01
# 依赖说明：SQLAlchemy, pydantic

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import (
    Base,
    SessionLocal,
    get_current_db_info,
    init_db,
    switch_database,
    test_connection,
)
from app.config.database_settings import DatabaseType, db_settings
from app.utils.logger import logger


class DatabaseManager:
    """数据库管理器"""

    @staticmethod
    def init_database(force_recreate: bool = False) -> bool:
        """初始化数据库"""
        print("=" * 80)
        print("初始化数据库")
        print("=" * 80)

        try:
            # 验证配置
            if not db_settings.validate_config():
                print("✗ 数据库配置验证失败")
                return False

            # 显示配置
            info = get_current_db_info()
            print(f"数据库类型: {info['type']}")
            print(f"状态: {'连接正常' if test_connection() else '连接失败'}")

            # 初始化
            success = init_db(force_recreate=force_recreate)

            if success:
                print("\n✓ 数据库初始化成功")
            else:
                print("\n✗ 数据库初始化失败")
                return False

            # 检查并创建表
            if success:
                print("\n✓ 表结构创建完成")

            return True

        except Exception as e:
            logger.error(f"数据库初始化异常: {e}")
            return False

    @staticmethod
    def check_tables() -> Dict[str, Any]:
        """检查表结构"""
        print("\n" + "=" * 80)
        print("检查表结构")
        print("=" * 80)

        db = SessionLocal()

        try:
            # 获取所有表
            metadata = Base.metadata
            tables = metadata.tables.keys()

            print(f"已定义的模型: {len(tables)}")

            # 检查每个表
            from sqlalchemy import inspect

            inspector = inspect(db.bind)

            existing_tables = inspector.get_table_names()

            results = {
                "defined": list(tables),
                "existing": existing_tables,
                "missing": [],
                "extra": [],
            }

            for table_name in tables:
                if table_name not in existing_tables:
                    results["missing"].append(table_name)

            for table_name in existing_tables:
                if table_name not in tables:
                    results["extra"].append(table_name)

            # 显示结果
            print(f"表结构检查:")
            print(f"  已定义: {len(results['defined'])}")
            print(f"  已存在: {len(results['existing'])}")
            if results["missing"]:
                print(f"  ⚠️ 缺失: {results['missing']}")
            if results["extra"]:
                print(f"  ⚠️ 多余: {results['extra']}")

            # 统计数据
            if not results["missing"]:
                results["status"] = "complete"
                print(f"\n✓ 所有表结构完整")
            else:
                results["status"] = "incomplete"
                print(f"\n⚠️ 表结构不完整")

            return results

        finally:
            db.close()

    @staticmethod
    def test_mysql_connection(
        host: str, port: int, user: str, password: str, database: str
    ) -> Dict[str, Any]:
        """测试MySQL连接"""
        print("\n" + "=" * 80)
        print("测试MySQL连接")
        print("=" * 80)

        try:
            # 临时切换配置测试
            original_type = db_settings.DB_TYPE

            try:
                switch_database(
                    DatabaseType.MYSQL,
                    mysql_host=host,
                    mysql_port=port,
                    mysql_user=user,
                    mysql_password=password,
                    mysql_database=database,
                )

                success = test_connection()
                if success:
                    print("✓ MySQL连接测试成功")
                    return {"success": True, "message": "连接成功"}
                else:
                    print("✗ MySQL连接测试失败")
                    return {"success": False, "message": "连接失败"}

            finally:
                # 恢复原配置
                switch_database(original_type)

        except Exception as e:
            logger.error(f"MySQL连接测试异常: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def create_migration_script() -> str:
        """创建迁移脚本提示（将来扩展）"""
        content = """# 数据库迁移脚本
# 注意：这是一个模板，真实的迁移需要使用Alembic等工具

from app.config.database import SessionLocal
from app.config.database_settings import db_settings
from app.utils.logger import logger

def run_migration():
    \"\"\"运行迁移\"\"\"
    # 实际项目建议使用Alembic
    logger.info("数据库迁移功能")
    pass

if __name__ == "__main__":
    run_migration()
"""
        return content


def main():
    """主函数 - 命令行工具入口"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库管理工具")
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # 初始化命令
    init_parser = subparsers.add_parser("init", help="初始化数据库")
    init_parser.add_argument("--force", action="store_true", help="强制重建表")

    # 检查命令
    subparsers.add_parser("check", help="检查表结构")

    # 测试命令
    test_parser = subparsers.add_parser("test", help="测试连接")
    test_parser.add_argument("--mysql", action="store_true", help="测试MySQL")
    test_parser.add_argument("--host", default="localhost", help="MySQL主机")
    test_parser.add_argument("--port", type=int, default=3306, help="MySQL端口")
    test_parser.add_argument("--user", default="root", help="MySQL用户")
    test_parser.add_argument("--password", default="", help="MySQL密码")
    test_parser.add_argument("--database", default="gw2_log_system", help="MySQL数据库")

    args = parser.parse_args()

    manager = DatabaseManager()

    if args.command == "init":
        manager.init_database(force_recreate=args.force)

    elif args.command == "check":
        manager.check_tables()

    elif args.command == "test":
        if args.mysql:
            manager.test_mysql_connection(
                args.host, args.port, args.user, args.password, args.database
            )
        else:
            test_connection()


if __name__ == "__main__":
    main()
