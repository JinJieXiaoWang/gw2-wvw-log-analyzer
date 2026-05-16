# -*- coding: utf-8 -*-
"""数据库列结构同步"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.config.database import _Base

logger = logging.getLogger(__name__)

def _sync_table_columns(engine) -> Dict[str, Any]:
    """
    同步表列结构：添加缺失列、检查字段一致性、同步中文描述(MySQL)

    Returns:
        {
            "added": {表名: [添加的列? ...]},
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

            # === 1. 新增?===
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
                        # SQLAlchemy 表达式（?func.now()?
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
                    logger.info(f"为表 {table_name} 添加列 {col_name}")
                except Exception as e:
                    logger.warning(f"为表 {table_name} 添加列 {col_name} 失败: {e}")
                continue

            # === 2. 字段一致性检?===
            existing = existing_cols[col_name]
            expected_type_str = str(column.type)
            actual_type_str = str(existing.get("type", ""))

            # 清理类型字符串中?COLLATE 等噪声（MySQL 会返?"TEXT COLLATE 'utf8mb4_unicode_ci'"?
            import re
            def _clean_type_str(t: str) -> str:
                t = t.lower().strip()
                # 去除 COLLATE "..." ?COLLATE '...'
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
                    f"字段类型不一? {table_name}.{col_name} "
                    f"期望={expected_type_str}, 实际={actual_type_str}"
                )
                # 【新增】自动修改列类型（MySQL?
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
                                f"修改列类 {table_name}.{col_name} "
                                f"{actual_type_str} -> {expected_type_str}"
                            )
                    except Exception as e:
                        logger.warning(f"修改列类{table_name}.{col_name} 失败: {e}")

            # === 3. nullable 一致性检?===
            expected_nullable = column.nullable
            actual_nullable = existing.get("nullable", True)
            if expected_nullable != actual_nullable:
                result["nullable_mismatch"].append(
                    (table_name, col_name, expected_nullable, actual_nullable)
                )
                logger.warning(
                    f"nullable不一? {table_name}.{col_name} "
                    f"期望={expected_nullable}, 实际={actual_nullable}"
                )

            # === 4. 中文描述同步 (MySQL) ===
            # 策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义?
            # 重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失 DEFAULT/EXTRA/UNSIGNED 等属?
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
                        # COMMENT 中的单引号转?
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

