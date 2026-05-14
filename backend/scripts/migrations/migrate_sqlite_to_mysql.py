# -*- coding: utf-8 -*-
"""
SQLite → MySQL 数据迁移脚本
用法: cd backend && python scripts/migrations/migrate_sqlite_to_mysql.py
"""

import sys
import os

# 将backend加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, get_base

# 导入所有模型，确保Base.metadata包含所有表
from app.models import *

# 配置
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app", "database", "app.db")
MYSQL_URL = "mysql+pymysql://root:123456@192.168.1.26:3306/gw2_log_system?charset=utf8mb4"


def get_sqlite_engine():
    return create_engine(f"sqlite:///{SQLITE_PATH}")


def create_mysql_database():
    """先创建数据库（如果不存在）"""
    server_url = "mysql+pymysql://root:123456@192.168.1.26:3306?charset=utf8mb4"
    engine = create_engine(server_url)
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        print("  ✓ 数据库 gw2_log_system 已创建或已存在")
    engine.dispose()


def get_mysql_engine():
    return create_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
    )


def serialize_value(value):
    """序列化值，处理特殊类型"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def get_table_row_count(sqlite_engine, table_name):
    with sqlite_engine.connect() as conn:
        result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
        return result.scalar()


def migrate_table(sqlite_engine, mysql_engine, table, batch_size=500):
    """迁移单张表的数据"""
    table_name = table.name
    row_count = get_table_row_count(sqlite_engine, table_name)
    
    if row_count == 0:
        print(f"  [{table_name}] 空表，跳过")
        return 0
    
    print(f"  [{table_name}] 迁移 {row_count} 行...")
    
    columns = [c.name for c in table.columns]
    placeholders = ", ".join([f":{c}" for c in columns])
    quoted_cols = ", ".join([f"`{c}`" for c in columns])
    
    insert_sql = f"INSERT INTO `{table_name}` ({quoted_cols}) VALUES ({placeholders})"
    
    SessionMySQL = sessionmaker(bind=mysql_engine)
    session = SessionMySQL()
    
    total_inserted = 0
    offset = 0
    
    try:
        with sqlite_engine.connect() as sqlite_conn:
            while offset < row_count:
                # SQLite分页读取
                rows = sqlite_conn.execute(
                    text(f'SELECT * FROM "{table_name}" LIMIT {batch_size} OFFSET {offset}')
                ).mappings().all()
                
                if not rows:
                    break
                
                batch_data = []
                for row in rows:
                    item = {}
                    for col in columns:
                        val = row.get(col)
                        item[col] = serialize_value(val)
                    batch_data.append(item)
                
                # MySQL批量插入
                if batch_data:
                    session.execute(text(insert_sql), batch_data)
                    session.commit()
                    total_inserted += len(batch_data)
                
                offset += batch_size
                if offset % 5000 == 0 or offset >= row_count:
                    print(f"    ... {total_inserted}/{row_count}")
    except Exception as e:
        session.rollback()
        print(f"  [{table_name}] 迁移失败: {e}")
        raise
    finally:
        session.close()
    
    print(f"  [{table_name}] 完成: {total_inserted} 行")
    return total_inserted


def reset_mysql_database():
    """彻底重置MySQL数据库（DROP + CREATE）"""
    server_url = "mysql+pymysql://root:123456@192.168.1.26:3306?charset=utf8mb4"
    engine = create_engine(server_url)
    with engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS gw2_log_system"))
        conn.execute(text("CREATE DATABASE gw2_log_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
    engine.dispose()
    print("  ✓ 数据库已重置")
    # MySQL 8.0 需要等待DDL同步完成
    import time
    time.sleep(1)


def create_mysql_tables(mysql_engine):
    """在MySQL中创建表结构（使用项目自带的init_db）"""
    print("=" * 60)
    print("步骤1: 创建MySQL表结构")
    print("=" * 60)
    
    # 使用项目自带的init_db，它已处理所有MySQL边界情况
    from app.config.database import init_db
    init_db()
    
    # init_db()会自动初始化sys_config等默认数据，需要清空以便从SQLite迁移
    print("清空自动初始化的数据...")
    inspector = inspect(mysql_engine)
    tables = inspector.get_table_names()
    with mysql_engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE `{t}`"))
            print(f"  ✓ 清空 {t}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    
    inspector = inspect(mysql_engine)
    created = inspector.get_table_names()
    print(f"成功创建 {len(created)} 张表")
    for t in created:
        print(f"  ✓ {t}")
    return created


def verify_migration(sqlite_engine, mysql_engine):
    """验证迁移结果"""
    print("\n" + "=" * 60)
    print("步骤3: 验证迁移结果")
    print("=" * 60)
    
    inspector_sqlite = inspect(sqlite_engine)
    inspector_mysql = inspect(mysql_engine)
    
    sqlite_tables = inspector_sqlite.get_table_names()
    mysql_tables = inspector_mysql.get_table_names()
    
    all_ok = True
    total_sqlite_rows = 0
    total_mysql_rows = 0
    
    for table_name in sorted(set(sqlite_tables) & set(mysql_tables)):
        # SQLite行数
        with sqlite_engine.connect() as conn:
            sqlite_count = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
        
        # MySQL行数
        with mysql_engine.connect() as conn:
            mysql_count = conn.execute(text(f'SELECT COUNT(*) FROM `{table_name}`')).scalar()
        
        total_sqlite_rows += sqlite_count
        total_mysql_rows += mysql_count
        
        status = "✓" if sqlite_count == mysql_count else "✗"
        if sqlite_count != mysql_count:
            all_ok = False
        print(f"  {status} {table_name}: SQLite={sqlite_count}, MySQL={mysql_count}")
    
    print(f"\n总计: SQLite={total_sqlite_rows}, MySQL={total_mysql_rows}")
    return all_ok


def fix_auto_increment(mysql_engine):
    """为MySQL主键列添加AUTO_INCREMENT"""
    print("\n" + "=" * 60)
    print("步骤4: 修复主键AUTO_INCREMENT")
    print("=" * 60)
    
    inspector = inspect(mysql_engine)
    fixed = 0
    
    for table_name in inspector.get_table_names():
        pk = inspector.get_pk_constraint(table_name)
        pk_cols = pk.get("constrained_columns", []) if pk else []
        
        if not pk_cols or len(pk_cols) != 1:
            continue
        
        pk_col = pk_cols[0]
        
        with mysql_engine.begin() as conn:
            # 检查是否已有AUTO_INCREMENT
            result = conn.execute(text(
                "SELECT EXTRA FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
            ), {"t": table_name, "c": pk_col}).fetchone()
            
            if result and "auto_increment" not in (result[0] or "").lower():
                # 获取列类型
                col_info = inspector.get_columns(table_name)
                col_type = next((c["type"] for c in col_info if c["name"] == pk_col), None)
                
                if col_type and "int" in str(col_type).lower():
                    conn.execute(text(
                        f"ALTER TABLE `{table_name}` MODIFY COLUMN `{pk_col}` {col_type} NOT NULL AUTO_INCREMENT"
                    ))
                    fixed += 1
                    print(f"  ✓ {table_name}.{pk_col} -> AUTO_INCREMENT")
    
    print(f"共修复 {fixed} 个表的主键AUTO_INCREMENT")


def main():
    print("=" * 60)
    print("SQLite → MySQL 数据迁移")
    print("=" * 60)
    print(f"SQLite源: {SQLITE_PATH}")
    print(f"MySQL目标: mysql://192.168.1.26:3306/gw2_log_system")
    print("")
    
    # 创建引擎
    sqlite_engine = get_sqlite_engine()
    mysql_engine = get_mysql_engine()
    
    # 重置数据库
    print("重置MySQL数据库...")
    reset_mysql_database()
    
    # 【关键】重置后必须重新创建MySQL引擎，否则连接池仍指向旧数据库状态
    mysql_engine.dispose()
    mysql_engine = get_mysql_engine()
    
    # 测试连接
    print("测试连接...")
    with sqlite_engine.connect() as conn:
        print("  ✓ SQLite连接成功")
    with mysql_engine.connect() as conn:
        print("  ✓ MySQL连接成功")
    
    # 创建表
    create_mysql_tables(mysql_engine)
    
    # 迁移数据
    print("\n" + "=" * 60)
    print("步骤2: 迁移数据")
    print("=" * 60)
    
    # 临时禁用MySQL外键检查（解决自引用外键等问题）
    with mysql_engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    print("  已禁用外键检查（迁移期间）")
    
    # 按依赖顺序获取表（父表优先）
    sorted_tables = Base.metadata.sorted_tables
    
    total_migrated = 0
    for table in sorted_tables:
        total_migrated += migrate_table(sqlite_engine, mysql_engine, table)
    
    # 重新启用外键检查
    with mysql_engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("  已重新启用外键检查")
    
    # 修复AUTO_INCREMENT
    fix_auto_increment(mysql_engine)
    
    # 验证
    all_ok = verify_migration(sqlite_engine, mysql_engine)
    
    # 关闭连接
    sqlite_engine.dispose()
    mysql_engine.dispose()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 迁移完成，所有数据验证通过！")
    else:
        print("⚠ 迁移完成，但部分表数据不一致，请检查")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
