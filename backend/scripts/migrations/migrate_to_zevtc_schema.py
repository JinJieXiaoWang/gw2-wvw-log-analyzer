#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：数据库迁移脚本 - 迁移到ZEVTC完整schema
# 作者：系统
# 创建日期：2026-05-01
# 依赖说明：SQLAlchemy

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.config.database import Base, SessionLocal, engine
from app.config.database_settings import db_settings
from app.models import *  # 导入所有模型
from app.utils.logger import logger


def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def backup_table_data(db, table_name: str):
    """备份表数据（仅记录数量）"""
    import re

    # 安全校验：表名只能包含字母、数字和下划线
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        logger.warning(f"非法表名，跳过备份: {table_name}")
        return 0
    try:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        logger.info(f"表 {table_name} 有 {count} 条记录")
        return count
    except Exception as e:
        logger.warning(f"无法备份表 {table_name}: {e}")
        return 0


def drop_old_zevtc_tables():
    """删除旧的ZEVTC相关表（如果存在）"""
    tables_to_drop = [
        "fight_buff_snapshots",
        "fight_dps_timeline",
        "fight_state_changes",
        "fight_position_timeline",
    ]

    with engine.connect() as conn:
        import re

        for table in tables_to_drop:
            if check_table_exists(table):
                # 安全校验：表名只能包含字母、数字和下划线
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
                    logger.warning(f"非法表名，跳过删除: {table}")
                    continue
                logger.info(f"删除表: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.commit()


def create_new_zevtc_tables():
    """创建新的ZEVTC数据表"""
    logger.info("开始创建新的ZEVTC数据表...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    logger.info("ZEVTC数据表创建完成")


def migrate_logs_table(db):
    """迁移logs表 - 删除冗余字段"""
    logger.info("开始迁移logs表...")

    # 检查是否需要迁移
    if not check_table_exists("logs"):
        logger.info("logs表不存在，将创建新表")
        return

    # 备份数据
    backup_count = backup_table_data(db, "logs")
    logger.info(f"logs表当前有 {backup_count} 条记录")

    # SQLite不支持DROP COLUMN，需要重建表
    if db_settings.DB_TYPE.value == "sqlite":
        logger.info("SQLite数据库，需要重建logs表")

        # 创建临时表
        db.execute(text("""
            CREATE TABLE logs_backup AS 
            SELECT id, filename, file_path, file_size, upload_time, parse_status, parse_time, error_message
            FROM logs
        """))

        # 删除原表
        db.execute(text("DROP TABLE logs"))

        # 重命名临时表
        db.execute(text("ALTER TABLE logs_backup RENAME TO logs"))

        db.commit()
        logger.info("logs表迁移完成（SQLite）")

    # MySQL支持DROP COLUMN
    elif db_settings.DB_TYPE.value == "mysql":
        logger.info("MySQL数据库，直接删除冗余字段")

        # 获取当前列
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("logs")]

        # 需要删除的字段
        fields_to_drop = [
            "server",
            "map_name",
            "guild_tag",
            "uploaded_by",
            "fight_count",
            "recorded_by",
            "recorded_account_by",
            "raw_json",
            "zevtc_path",
            "event_count",
        ]

        import re

        for field in fields_to_drop:
            if field in columns:
                # 安全校验：字段名只能包含字母、数字和下划线
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field):
                    logger.warning(f"非法字段名，跳过删除: {field}")
                    continue
                logger.info(f"删除字段: {field}")
                db.execute(text(f"ALTER TABLE logs DROP COLUMN {field}"))

        # 添加新字段（如果不存在）
        if "file_hash" not in columns:
            logger.info("添加字段: file_hash")
            db.execute(text("ALTER TABLE logs ADD COLUMN file_hash VARCHAR(64)"))
            db.execute(text("CREATE INDEX idx_log_file_hash ON logs(file_hash)"))

        if "upload_ip" not in columns:
            logger.info("添加字段: upload_ip")
            db.execute(text("ALTER TABLE logs ADD COLUMN upload_ip VARCHAR(50)"))

        db.commit()
        logger.info("logs表迁移完成（MySQL）")


def verify_migration():
    """验证迁移结果"""
    logger.info("验证迁移结果...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # 检查新表是否创建
    required_tables = [
        "logs",
        "fights",
        "fight_details",
        "members",
        "fight_stats",
        "zevtc_agents",
        "zevtc_skills",
        "zevtc_events",
        "zevtc_buff_applications",
        "zevtc_position_data",
        "zevtc_health_data",
    ]

    missing_tables = [t for t in required_tables if t not in tables]

    if missing_tables:
        logger.error(f"缺少表: {missing_tables}")
        return False

    logger.info("所有必需的表都已创建")

    # 检查logs表字段
    logs_columns = [col["name"] for col in inspector.get_columns("logs")]
    expected_columns = [
        "id",
        "filename",
        "file_path",
        "file_size",
        "file_hash",
        "upload_time",
        "upload_ip",
        "parse_status",
        "parse_time",
        "error_message",
    ]

    missing_columns = [c for c in expected_columns if c not in logs_columns]
    if missing_columns:
        logger.warning(f"logs表缺少字段: {missing_columns}")

    logger.info("迁移验证完成")
    return True


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("ZEVTC数据库迁移脚本")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        # 步骤1：删除旧的ZEVTC表
        logger.info("步骤1：删除旧的ZEVTC表...")
        drop_old_zevtc_tables()

        # 步骤2：迁移logs表
        logger.info("步骤2：迁移logs表...")
        migrate_logs_table(db)

        # 步骤3：创建新的ZEVTC表
        logger.info("步骤3：创建新的ZEVTC表...")
        create_new_zevtc_tables()

        # 步骤4：验证迁移
        logger.info("步骤4：验证迁移...")
        success = verify_migration()

        if success:
            print()
            print("=" * 60)
            print("✓ 迁移成功完成！")
            print("=" * 60)
            print()
        else:
            print()
            print("=" * 60)
            print("✗ 迁移验证失败，请检查日志")
            print("=" * 60)
            print()
            return 1

        return 0

    except Exception as e:
        logger.exception(f"迁移失败: {e}")
        print()
        print("=" * 60)
        print(f"✗ 迁移失败: {e}")
        print("=" * 60)
        print()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
