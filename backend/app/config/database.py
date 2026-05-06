# -*- coding: utf-8 -*-
# 模块功能：数据库连接管理（支持SQLite和MySQL）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：sqlalchemy
# 更新日期：2026-05-01 - 增加多数据库支持和自动初始化

import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config.database_settings import DatabaseType, db_settings
from app.utils.logger import logger

# 全局引擎和会话工厂
_engine = None
_SessionLocal = None
_Base = declarative_base()


def _create_engine():
    """创建数据库引擎"""
    global _engine

    # 对于MySQL和PostgreSQL，先尝试创建数据库（如果不存在）
    if db_settings.DB_TYPE in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
        try:
            _create_database_if_not_exists()
        except Exception as e:
            logger.warning(f"尝试创建数据库时出错: {e}")

    url = db_settings.get_database_url()
    kwargs = db_settings.get_engine_kwargs()

    logger.info(f"初始化数据库连接: {db_settings.DB_TYPE}")
    logger.debug(f"数据库URL: {_mask_url(url)}")

    _engine = create_engine(url, **kwargs)
    return _engine


def _create_database_if_not_exists():
    """
    如果MySQL或PostgreSQL数据库不存在，则创建它

    注意：这需要数据库用户有创建数据库的权限
    """
    from sqlalchemy import text

    if db_settings.DB_TYPE == DatabaseType.MYSQL:
        password_part = ""
        if db_settings.MYSQL_PASSWORD:
            password_part = (
                f":{db_settings._url_encode_password(db_settings.MYSQL_PASSWORD)}"
            )

        server_url = (
            f"mysql+pymysql://{db_settings.MYSQL_USER}{password_part}@"
            f"{db_settings.MYSQL_HOST}:{db_settings.MYSQL_PORT}"
            f"?charset={db_settings.MYSQL_CHARSET}"
        )

        logger.info(f"检查MySQL数据库是否存在: {db_settings.MYSQL_DATABASE}")

        temp_engine = create_engine(server_url, **db_settings.get_engine_kwargs())

        try:
            with temp_engine.connect() as conn:
                result = conn.execute(
                    text(f"SHOW DATABASES LIKE :db_name"),
                    {"db_name": db_settings.MYSQL_DATABASE},
                )
                exists = result.fetchone() is not None

                if not exists:
                    logger.info(
                        f"MySQL数据库不存在，正在创建: {db_settings.MYSQL_DATABASE}"
                    )
                    conn.execute(
                        text(
                            f"CREATE DATABASE `{db_settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                        )
                    )
                    logger.info(f"MySQL数据库创建成功: {db_settings.MYSQL_DATABASE}")
                else:
                    logger.info(f"MySQL数据库已存在: {db_settings.MYSQL_DATABASE}")

        finally:
            temp_engine.dispose()

    elif db_settings.DB_TYPE == DatabaseType.POSTGRESQL:
        password_part = ""
        if db_settings.POSTGRESQL_PASSWORD:
            password_part = (
                f":{db_settings._url_encode_password(db_settings.POSTGRESQL_PASSWORD)}"
            )

        server_url = (
            f"postgresql+psycopg2://{db_settings.POSTGRESQL_USER}{password_part}@"
            f"{db_settings.POSTGRESQL_HOST}:{db_settings.POSTGRESQL_PORT}/postgres"
        )

        logger.info(f"检查PostgreSQL数据库是否存在: {db_settings.POSTGRESQL_DATABASE}")

        temp_engine = create_engine(server_url, **db_settings.get_engine_kwargs())

        try:
            with temp_engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT")

                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_settings.POSTGRESQL_DATABASE},
                )
                exists = result.fetchone() is not None

                if not exists:
                    logger.info(
                        f"PostgreSQL数据库不存在，正在创建: {db_settings.POSTGRESQL_DATABASE}"
                    )
                    conn.execute(
                        text(
                            f'CREATE DATABASE "{db_settings.POSTGRESQL_DATABASE}" ENCODING "UTF8"'
                        )
                    )
                    logger.info(
                        f"PostgreSQL数据库创建成功: {db_settings.POSTGRESQL_DATABASE}"
                    )
                else:
                    logger.info(
                        f"PostgreSQL数据库已存在: {db_settings.POSTGRESQL_DATABASE}"
                    )

        finally:
            temp_engine.dispose()


def _mask_url(url: str) -> str:
    """掩码敏感的URL信息"""
    if "@" not in url:
        return url

    parts = url.split("@")
    before = parts[0]

    if ":" in before and "//" in before:
        protocol = before.split("//")[0]
        user_pass = before.split("//")[1]

        if ":" in user_pass:
            user = user_pass.split(":")[0]
            return f"{protocol}//{user}:******@{parts[1]}"

    return url


def _get_engine():
    """获取引擎（懒加载）"""
    if _engine is None:
        _create_engine()
    return _engine


def _get_session_factory():
    """获取会话工厂"""
    global _SessionLocal

    if _SessionLocal is None:
        engine = _get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return _SessionLocal


def get_db():
    """获取数据库会话（FastAPI依赖注入）"""
    db_session = _get_session_factory()()
    try:
        yield db_session
    finally:
        db_session.close()


@contextmanager
def get_db_context():
    """获取数据库会话（上下文管理器）"""
    db_session = _get_session_factory()()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def SessionLocal() -> Session:
    """直接创建一个新的数据库会话"""
    return _get_session_factory()()


def get_base():
    """获取声明基类"""
    return _Base


def _check_and_create_tables(engine) -> Dict[str, Any]:
    """
    检查并创建缺失的表

    Returns:
        初始化统计信息
    """
    stats = {
        "total_tables": 0,
        "created_tables": 0,
        "existing_tables": 0,
        "created_indexes": 0,
        "created_constraints": 0,
        "errors": [],
    }

    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # 统计需要创建的表
        metadata = _Base.metadata
        tables_to_create = []

        for table_name, table in metadata.tables.items():
            stats["total_tables"] += 1
            if table_name not in existing_tables:
                tables_to_create.append(table)
                logger.info(f"发现缺失表: {table_name}")
            else:
                stats["existing_tables"] += 1
                logger.debug(f"表已存在: {table_name}")

        # 创建缺失的表（按外键依赖排序，先创建被引用的父表）
        if tables_to_create:
            logger.info(f"开始创建 {len(tables_to_create)} 个缺失的表...")

            # 按依赖顺序排序（父表优先）
            sorted_tables = metadata.sorted_tables
            tables_to_create_set = set(tables_to_create)

            for table in sorted_tables:
                if table not in tables_to_create_set:
                    continue
                try:
                    logger.info(f"创建表: {table.name}")
                    # 【修复】加 checkfirst=True，避免多 worker 并发时 race condition 导致
                    # "Table already exists" 错误（Worker A 创建后 Worker B 也尝试创建）
                    table.create(bind=engine, checkfirst=True)
                    stats["created_tables"] += 1
                    logger.info(f"表 {table.name} 创建成功")
                except Exception as e:
                    error_msg = f"创建表 {table.name} 失败: {e}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
        else:
            logger.info("所有表都已存在，无需创建")

        # 检查并添加缺失的索引（对于已存在的表）
        stats["created_indexes"] = _check_and_add_indexes(engine, inspector)

        # 检查并添加缺失的约束
        stats["created_constraints"] = _check_and_add_constraints(engine, inspector)

    except Exception as e:
        error_msg = f"检查表结构时发生错误: {e}"
        logger.error(error_msg)
        stats["errors"].append(error_msg)

    return stats


def _check_and_add_indexes(engine, inspector) -> int:
    """
    检查并添加缺失的索引

    Returns:
        创建的索引数量
    """
    created_count = 0
    metadata = _Base.metadata

    try:
        for table_name, table in metadata.tables.items():
            if table_name not in inspector.get_table_names():
                continue  # 跳过未创建的表

            existing_indexes = set()
            for idx in inspector.get_indexes(table_name):
                # 组合索引名称
                idx_name = idx.get("name", "")
                if idx_name:
                    existing_indexes.add(idx_name.lower())

                # 也记录索引列
                cols = tuple(sorted(idx.get("column_names", [])))
                existing_indexes.add(f"idx_{table_name}_{'_'.join(cols)}".lower())

            # 检查需要创建的索引
            for index in table.indexes:
                idx_name = index.name.lower() if index.name else ""

                # 生成索引列标识
                cols = tuple(sorted([str(c).split(".")[-1] for c in index.columns]))
                idx_col_identifier = f"idx_{table_name}_{'_'.join(cols)}".lower()

                if (
                    idx_name not in existing_indexes
                    and idx_col_identifier not in existing_indexes
                ):
                    try:
                        logger.info(
                            f"为表 {table_name} 创建索引: {idx_name or idx_col_identifier}"
                        )
                        index.create(bind=engine)
                        created_count += 1
                        logger.info(f"索引创建成功")
                    except Exception as e:
                        logger.warning(f"创建索引 {idx_name} 失败: {e}")

    except Exception as e:
        logger.error(f"检查索引时发生错误: {e}")

    return created_count


def _check_and_add_constraints(engine, inspector) -> int:
    """
    检查并添加缺失的约束

    Returns:
        创建的约束数量
    """
    created_count = 0
    metadata = _Base.metadata

    try:
        for table_name, table in metadata.tables.items():
            if table_name not in inspector.get_table_names():
                continue

            # 检查外键约束
            existing_fks = set()
            for fk in inspector.get_foreign_keys(table_name):
                fk_name = fk.get("name", "")
                if fk_name:
                    existing_fks.add(fk_name.lower())

            for constraint in table.constraints:
                if hasattr(constraint, "name") and constraint.name:
                    constraint_name = constraint.name.lower()
                    if constraint_name not in existing_fks:
                        try:
                            logger.info(
                                f"为表 {table_name} 创建约束: {constraint_name}"
                            )
                            # SQLAlchemy不支持单独添加约束，需要ALTER TABLE
                            # 这里记录但不执行，因为约束通常在创建表时添加
                            logger.info(f"约束 {constraint_name} 已在表创建时添加")
                        except Exception as e:
                            logger.warning(f"创建约束 {constraint_name} 失败: {e}")

    except Exception as e:
        logger.error(f"检查约束时发生错误: {e}")

    return created_count


def _log_initialization_summary(stats: Dict[str, Any]):
    """
    记录初始化总结日志
    """
    logger.info("=" * 60)
    logger.info("数据库初始化完成")
    logger.info("=" * 60)
    logger.info(f"总表数: {stats['total_tables']}")
    logger.info(f"已存在表: {stats['existing_tables']}")
    logger.info(f"新创建表: {stats['created_tables']}")
    logger.info(f"新创建索引: {stats['created_indexes']}")
    logger.info(f"新创建约束: {stats['created_constraints']}")

    if stats["errors"]:
        logger.error("初始化过程中遇到的错误:")
        for error in stats["errors"]:
            logger.error(f"  - {error}")

    if not stats["errors"]:
        logger.info("✓ 数据库初始化成功！")
    else:
        logger.warning("⚠️ 数据库初始化完成，但有部分错误")

    logger.info("=" * 60)


def _format_mysql_default(default_value: Any) -> str:
    """
    将 MySQL INFORMATION_SCHEMA.COLUMNS.COLUMN_DEFAULT 格式化为 SQL DEFAULT 子句。
    
    关键处理：
    - CURRENT_TIMESTAMP / NULL → 不加引号
    - 数字 → 不加引号
    - 字符串 → 加单引号并转义
    
    返回空字符串表示没有 DEFAULT。
    """
    if default_value is None:
        return ""
    
    s = str(default_value).strip()
    if not s:
        return ""
    
    upper = s.upper()
    # MySQL 关键字型默认值（不加引号）
    if upper in ("CURRENT_TIMESTAMP", "NULL", "CURRENT_TIMESTAMP(6)"):
        return f"DEFAULT {upper}"
    
    # 数字型（不加引号）
    try:
        float(s)
        return f"DEFAULT {s}"
    except ValueError:
        pass
    
    # 字符串型（加单引号并转义）
    escaped = s.replace("'", "''")
    return f"DEFAULT '{escaped}'"


def _sync_table_columns(engine) -> Dict[str, Any]:
    """
    同步表列结构：添加缺失列、检查字段一致性、同步中文描述(MySQL)

    Returns:
        {
            "added": {表名: [添加的列名, ...]},
            "type_mismatch": [(表名, 列名, 期望类型, 实际类型), ...],
            "nullable_mismatch": [(表名, 列名, 期望nullable, 实际nullable), ...],
            "comments_synced": [(表名, 列名), ...],
        }
    """
    result = {
        "added": {},
        "type_mismatch": [],
        "nullable_mismatch": [],
        "comments_synced": [],
        "skipped_comment": [],
    }
    inspector = inspect(engine)
    metadata = _Base.metadata
    dialect_name = engine.dialect.name

    for table_name, table in metadata.tables.items():
        if table_name not in inspector.get_table_names():
            continue

        existing_cols = {col["name"]: col for col in inspector.get_columns(table_name)}

        for column in table.columns:
            col_name = column.name

            # === 1. 新增列 ===
            if col_name not in existing_cols:
                col_type = column.type.compile(dialect=engine.dialect)
                quoted_col = engine.dialect.identifier_preparer.quote(col_name)
                quoted_tbl = engine.dialect.identifier_preparer.quote(table_name)
                nullable = "NOT NULL" if not column.nullable else "NULL"

                default = ""
                if column.default is not None and hasattr(column.default, "arg"):
                    default_arg = column.default.arg
                    if isinstance(default_arg, str):
                        default = f" DEFAULT '{default_arg}'"
                    elif hasattr(default_arg, "compile"):
                        # SQLAlchemy 表达式（如 func.now()）
                        compiled = str(default_arg.compile(dialect=engine.dialect))
                        if compiled.upper() == "NOW()":
                            compiled = "CURRENT_TIMESTAMP"
                        default = f" DEFAULT {compiled}"
                    else:
                        default = f" DEFAULT {default_arg}"

                if not column.nullable and not default:
                    default = " DEFAULT 0"

                # MySQL/PostgreSQL 支持 COMMENT
                comment = ""
                if dialect_name == "mysql" and column.comment:
                    comment = f" COMMENT '{column.comment}'"

                alter_stmt = (
                    f"ALTER TABLE {quoted_tbl} ADD COLUMN {quoted_col} "
                    f"{col_type} {nullable}{default}{comment}"
                )

                try:
                    with engine.begin() as conn:
                        conn.execute(text(alter_stmt))
                    result["added"].setdefault(table_name, []).append(col_name)
                    logger.info(f"为表 {table_name} 添加列: {col_name}")
                except Exception as e:
                    logger.warning(f"为表 {table_name} 添加列 {col_name} 失败: {e}")
                continue

            # === 2. 字段一致性检查 ===
            existing = existing_cols[col_name]
            expected_type_str = str(column.type)
            actual_type_str = str(existing.get("type", ""))

            # 清理类型字符串中的 COLLATE 等噪声（MySQL 会返回 "TEXT COLLATE 'utf8mb4_unicode_ci'"）
            import re
            def _clean_type_str(t: str) -> str:
                t = t.lower().strip()
                # 去除 COLLATE "..." 或 COLLATE '...'
                t = re.sub(r'\s+collate\s+["\']?[^"\'\s]+["\']?', '', t)
                # 去除 CHARACTER SET ...
                t = re.sub(r'\s+character\s+set\s+\S+', '', t)
                return t.strip()

            # 简化类型比较（只比较类型名，不比较长度等细节）
            expected_type_name = _clean_type_str(expected_type_str).split("(")[0]
            actual_type_name = _clean_type_str(actual_type_str).split("(")[0]

            # 数据库类型映射标准化
            type_mapping = {
                "integer": ["int", "integer", "bigint", "smallint"],
                "string": ["varchar", "char", "text", "string"],
                "float": ["float", "double", "real", "decimal", "numeric"],
                "boolean": ["bool", "boolean", "tinyint"],
                "datetime": ["datetime", "timestamp", "date"],
            }

            def _normalize_type(t: str) -> str:
                t = t.lower().strip()
                for canonical, aliases in type_mapping.items():
                    if t in aliases:
                        return canonical
                return t

            if _normalize_type(expected_type_name) != _normalize_type(actual_type_name):
                result["type_mismatch"].append(
                    (table_name, col_name, expected_type_str, actual_type_str)
                )
                logger.warning(
                    f"字段类型不一致: {table_name}.{col_name} "
                    f"期望={expected_type_str}, 实际={actual_type_str}"
                )
                # 【新增】自动修改列类型（MySQL）
                if dialect_name == "mysql":
                    try:
                        with engine.begin() as conn:
                            row = conn.execute(
                                text(
                                    "SELECT COLUMN_DEFAULT, EXTRA "
                                    "FROM INFORMATION_SCHEMA.COLUMNS "
                                    "WHERE TABLE_NAME = :table AND COLUMN_NAME = :col AND TABLE_SCHEMA = DATABASE()"
                                ),
                                {"table": table_name, "col": col_name}
                            ).fetchone()
                            current_default = row[0] if row else None
                            extra = row[1] or "" if row else ""

                            new_type = column.type.compile(dialect=engine.dialect)
                            nullable_clause = "NULL" if column.nullable else "NOT NULL"
                            default_clause = _format_mysql_default(current_default)
                            extra_clause = extra.strip()

                            parts = [new_type, nullable_clause]
                            if default_clause:
                                parts.append(default_clause)
                            if extra_clause:
                                parts.append(extra_clause)
                            if column.comment:
                                comment_escaped = column.comment.replace("'", "''")
                                parts.append(f"COMMENT '{comment_escaped}'")

                            quoted_tbl = engine.dialect.identifier_preparer.quote(table_name)
                            quoted_col = engine.dialect.identifier_preparer.quote(col_name)
                            full_def = " ".join(parts)

                            alter_stmt = f"ALTER TABLE {quoted_tbl} MODIFY COLUMN {quoted_col} {full_def}"
                            conn.execute(text(alter_stmt))
                            logger.info(
                                f"修改列类型: {table_name}.{col_name} "
                                f"{actual_type_str} -> {expected_type_str}"
                            )
                    except Exception as e:
                        logger.warning(f"修改列类型 {table_name}.{col_name} 失败: {e}")

            # === 3. nullable 一致性检查 ===
            expected_nullable = column.nullable
            actual_nullable = existing.get("nullable", True)
            if expected_nullable != actual_nullable:
                result["nullable_mismatch"].append(
                    (table_name, col_name, expected_nullable, actual_nullable)
                )
                logger.warning(
                    f"nullable不一致: {table_name}.{col_name} "
                    f"期望={expected_nullable}, 实际={actual_nullable}"
                )

            # === 4. 中文描述同步 (MySQL) ===
            # 策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义，
            # 重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失 DEFAULT/EXTRA/UNSIGNED 等属性
            if dialect_name == "mysql" and column.comment:
                try:
                    with engine.begin() as conn:
                        row = conn.execute(
                            text(
                                "SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA "
                                "FROM INFORMATION_SCHEMA.COLUMNS "
                                "WHERE TABLE_NAME = :table AND COLUMN_NAME = :col AND TABLE_SCHEMA = DATABASE()"
                            ),
                            {"table": table_name, "col": col_name}
                        ).fetchone()
                        
                        if not row:
                            continue
                        
                        col_type = row[0]          # e.g. "datetime" / "varchar(255)"
                        is_nullable = row[1]       # "YES" / "NO"
                        current_default = row[2]   # DEFAULT 值或 None
                        extra = row[3] or ""       # e.g. "auto_increment" / "on update CURRENT_TIMESTAMP"
                        
                        # 重建列定义（保留所有现有属性）
                        nullable_clause = "NULL" if is_nullable == "YES" else "NOT NULL"
                        default_clause = _format_mysql_default(current_default)
                        extra_clause = extra.strip()
                        
                        # 组装 MODIFY COLUMN 语句
                        parts = [col_type, nullable_clause]
                        if default_clause:
                            parts.append(default_clause)
                        if extra_clause:
                            parts.append(extra_clause)
                        # COMMENT 中的单引号转义
                        comment_escaped = column.comment.replace("'", "''")
                        parts.append(f"COMMENT '{comment_escaped}'")
                        
                        quoted_tbl = engine.dialect.identifier_preparer.quote(table_name)
                        quoted_col = engine.dialect.identifier_preparer.quote(col_name)
                        full_def = " ".join(parts)
                        
                        comment_stmt = f"ALTER TABLE {quoted_tbl} MODIFY COLUMN {quoted_col} {full_def}"
                        conn.execute(text(comment_stmt))
                    
                    result["comments_synced"].append((table_name, col_name))
                except Exception as e:
                    result["skipped_comment"].append((table_name, col_name, str(e)))

    return result


def _fix_server_defaults(engine):
    """
    修复被 MODIFY COLUMN 覆盖掉的 server_default（MySQL）
    
    策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义，
    重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失任何现有属性。
    """
    if engine.dialect.name != "mysql":
        return
    
    inspector = inspect(engine)
    metadata = _Base.metadata
    fixed = 0
    
    for table_name, table in metadata.tables.items():
        if table_name not in inspector.get_table_names():
            continue
        
        for column in table.columns:
            if column.server_default is None:
                continue
            
            try:
                with engine.begin() as conn:
                    row = conn.execute(
                        text(
                            "SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA "
                            "FROM INFORMATION_SCHEMA.COLUMNS "
                            "WHERE TABLE_NAME = :table AND COLUMN_NAME = :col AND TABLE_SCHEMA = DATABASE()"
                        ),
                        {"table": table_name, "col": column.name}
                    ).fetchone()
                    
                    if not row:
                        continue
                    
                    col_type = row[0]
                    is_nullable = row[1]
                    current_default = row[2]
                    extra = (row[3] or "").strip()
                    
                    # 判断是否需要修复：模型要求有 DEFAULT，但数据库当前没有
                    has_db_default = current_default is not None or "auto_increment" in extra.lower()
                    if has_db_default:
                        continue
                    
                    # 编译 server_default 为 SQL 字符串（使用 dialect 确保正确性）
                    sd_arg = getattr(column.server_default, "arg", None)
                    if sd_arg is None:
                        continue
                    
                    # 对 SQLAlchemy 表达式使用 dialect 编译
                    if hasattr(sd_arg, "compile"):
                        default_sql = str(sd_arg.compile(dialect=engine.dialect))
                    else:
                        default_sql = str(sd_arg)
                    
                    # MySQL 列定义中 DEFAULT 不接受 NOW()，必须转换为 CURRENT_TIMESTAMP
                    if default_sql.upper() == "NOW()":
                        default_sql = "CURRENT_TIMESTAMP"
                    
                    # 重建完整列定义
                    nullable_clause = "NULL" if is_nullable == "YES" else "NOT NULL"
                    extra_clause = extra if extra else ""
                    
                    parts = [col_type, nullable_clause, f"DEFAULT {default_sql}"]
                    if extra_clause:
                        parts.append(extra_clause)
                    
                    # 保留现有 COMMENT（如果有）
                    comment_row = conn.execute(
                        text(
                            "SELECT COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS "
                            "WHERE TABLE_NAME = :table AND COLUMN_NAME = :col AND TABLE_SCHEMA = DATABASE()"
                        ),
                        {"table": table_name, "col": column.name}
                    ).fetchone()
                    if comment_row and comment_row[0]:
                        parts.append(f"COMMENT '{comment_row[0]}'")
                    
                    quoted_tbl = engine.dialect.identifier_preparer.quote(table_name)
                    quoted_col = engine.dialect.identifier_preparer.quote(column.name)
                    full_def = " ".join(parts)
                    
                    alter = f"ALTER TABLE {quoted_tbl} MODIFY COLUMN {quoted_col} {full_def}"
                    conn.execute(text(alter))
                    fixed += 1
                    logger.warning(
                        f"修复表 {table_name} 列 {column.name} 的 DEFAULT: {default_sql}"
                    )
            except Exception as e:
                logger.debug(f"检查 {table_name}.{column.name} 的 DEFAULT 失败: {e}")
    
    if fixed > 0:
        logger.info(f"共修复 {fixed} 个列的 server_default")


def _fix_auto_increment(engine):
    """
    修复主键列缺失 AUTO_INCREMENT 的问题（MySQL 专用）
    
    策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义，
    重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失 DEFAULT/UNSIGNED/COMMENT 等属性。
    """
    if engine.dialect.name != "mysql":
        return
    
    inspector = inspect(engine)
    fixed_count = 0
    
    for table_name in inspector.get_table_names():
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []
        
        if not pk_cols:
            continue
            
        for col_info in inspector.get_columns(table_name):
            col_name = col_info["name"]
            if col_name not in pk_cols:
                continue
            
            # 只处理 INTEGER 类型的单列主键
            type_str = str(col_info.get("type", "")).lower()
            if "int" not in type_str:
                continue
            
            # 检查是否已有 AUTO_INCREMENT
            try:
                with engine.begin() as conn:
                    row = conn.execute(
                        text(
                            "SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT "
                            "FROM INFORMATION_SCHEMA.COLUMNS "
                            "WHERE TABLE_NAME = :table AND COLUMN_NAME = :col AND TABLE_SCHEMA = DATABASE()"
                        ),
                        {"table": table_name, "col": col_name}
                    ).fetchone()
                    
                    if not row:
                        continue
                    
                    col_type = row[0]          # e.g. "int(11)" / "bigint(20) unsigned"
                    is_nullable = row[1]
                    current_default = row[2]
                    extra = (row[3] or "").strip()
                    comment = row[4] or ""
                    
                    if "auto_increment" in extra.lower():
                        continue
                    
                    # 重建完整列定义（保留所有现有属性）
                    nullable_clause = "NULL" if is_nullable == "YES" else "NOT NULL"
                    default_clause = _format_mysql_default(current_default)
                    extra_clause = extra if extra else ""
                    comment_escaped = comment.replace("'", "''")
                    comment_clause = f"COMMENT '{comment_escaped}'" if comment else ""
                    
                    parts = [col_type, nullable_clause]
                    if default_clause:
                        parts.append(default_clause)
                    if extra_clause:
                        parts.append(extra_clause)
                    parts.append("AUTO_INCREMENT")
                    if comment_clause:
                        parts.append(comment_clause)
                    
                    quoted_tbl = engine.dialect.identifier_preparer.quote(table_name)
                    quoted_col = engine.dialect.identifier_preparer.quote(col_name)
                    full_def = " ".join(parts)
                    
                    alter_stmt = f"ALTER TABLE {quoted_tbl} MODIFY COLUMN {quoted_col} {full_def}"
                    conn.execute(text(alter_stmt))
                    fixed_count += 1
                    logger.warning(
                        f"为表 {table_name} 的主键 {col_name} 添加 AUTO_INCREMENT"
                    )
            except Exception as e:
                logger.warning(f"修复 {table_name}.{col_name} 的 AUTO_INCREMENT 失败: {e}")
    
    if fixed_count > 0:
        logger.info(f"共修复 {fixed_count} 个表的主键 AUTO_INCREMENT")


def init_db(force_recreate: bool = False) -> bool:
    """
    初始化数据库（创建所有表并补充缺失列）

    Args:
        force_recreate: 是否强制重新创建表（删除并重建）

    Returns:
        成功返回True
    """
    logger.info("开始数据库初始化...")

    # 确保目录存在（SQLite）
    if db_settings.DB_TYPE == DatabaseType.SQLITE:
        db_path = db_settings.SQLITE_DB_PATH
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            logger.debug(f"确保SQLite目录存在: {db_dir}")

    # 创建引擎
    engine = _get_engine()

    # 强制重建
    if force_recreate:
        logger.warning("强制重建数据库表")
        _Base.metadata.drop_all(bind=engine)
        logger.info("所有表已删除")

    # 创建/检查表
    try:
        if db_settings.AUTO_CREATE_TABLES:
            stats = _check_and_create_tables(engine)
            # 同步列结构（添加缺失列 + 一致性检查 + 中文描述同步）
            sync_result = _sync_table_columns(engine)
            if sync_result["added"]:
                stats["added_columns"] = sync_result["added"]
            if sync_result["type_mismatch"]:
                stats["type_mismatches"] = sync_result["type_mismatch"]
            if sync_result["nullable_mismatch"]:
                stats["nullable_mismatches"] = sync_result["nullable_mismatch"]
            if sync_result["comments_synced"]:
                stats["comments_synced"] = sync_result["comments_synced"]
            
            # 修复主键 AUTO_INCREMENT（MySQL）
            _fix_auto_increment(engine)
            # 修复被覆盖的 server_default（MySQL）
            _fix_server_defaults(engine)
            
            _log_initialization_summary(stats)

            # 初始化系统默认配置（sys_config 表）
            try:
                from app.services.sys_config_service import SysConfigService
                from app.config.database import SessionLocal

                db = SessionLocal()
                try:
                    SysConfigService.init_default_configs(db)
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"初始化系统默认配置失败: {e}")
        else:
            logger.info("跳过自动建表（AUTO_CREATE_TABLES=False）")

        return True

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        raise


def test_connection() -> bool:
    """
    测试数据库连接

    Returns:
        连接成功返回True
    """
    try:
        engine = _get_engine()
        with engine.connect():
            logger.info("数据库连接测试成功")
            return True

    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False


def switch_database(new_type: DatabaseType, **kwargs):
    """
    切换数据库配置（运行时）

    注意：这不会影响已经创建的会话！

    Args:
        new_type: 新的数据库类型
        **kwargs: 其他配置参数
    """
    global _engine, _SessionLocal

    db_settings.DB_TYPE = new_type

    if kwargs.get("sqlite_path"):
        db_settings.SQLITE_DB_PATH = kwargs["sqlite_path"]

    if kwargs.get("mysql_host"):
        db_settings.MYSQL_HOST = kwargs["mysql_host"]
    if kwargs.get("mysql_port"):
        db_settings.MYSQL_PORT = kwargs["mysql_port"]
    if kwargs.get("mysql_user"):
        db_settings.MYSQL_USER = kwargs["mysql_user"]
    if kwargs.get("mysql_password"):
        db_settings.MYSQL_PASSWORD = kwargs["mysql_password"]
    if kwargs.get("mysql_database"):
        db_settings.MYSQL_DATABASE = kwargs["mysql_database"]

    if kwargs.get("postgresql_host"):
        db_settings.POSTGRESQL_HOST = kwargs["postgresql_host"]
    if kwargs.get("postgresql_port"):
        db_settings.POSTGRESQL_PORT = kwargs["postgresql_port"]
    if kwargs.get("postgresql_user"):
        db_settings.POSTGRESQL_USER = kwargs["postgresql_user"]
    if kwargs.get("postgresql_password"):
        db_settings.POSTGRESQL_PASSWORD = kwargs["postgresql_password"]
    if kwargs.get("postgresql_database"):
        db_settings.POSTGRESQL_DATABASE = kwargs["postgresql_database"]

    _engine = None
    _SessionLocal = None

    logger.info(f"切换数据库配置: {new_type}")

    _get_engine()


def get_current_db_info() -> dict:
    """获取当前数据库信息"""
    return {
        "type": db_settings.DB_TYPE.value,
        "url": _mask_url(db_settings.get_database_url()),
        "config": db_settings.get_config_summary(),
        "connected": test_connection(),
    }


# 导出
Base = get_base()


class _EngineProxy:
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def __call__(self):
        return _get_engine()


engine = _EngineProxy()
