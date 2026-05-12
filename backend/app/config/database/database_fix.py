# -*- coding: utf-8 -*-
"""数据库修复工?""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

def _fix_server_defaults(engine):
    """
    修复?MODIFY COLUMN 覆盖掉的 server_default（MySQL?
    
    策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义?
    重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失任何现有属性?
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
                    
                    # 判断是否需要修复：模型要求?DEFAULT，但数据库当前没?
                    has_db_default = current_default is not None or "auto_increment" in extra.lower()
                    if has_db_default:
                        continue
                    
                    # 编译 server_default ?SQL 字符串（使用 dialect 确保正确性）
                    sd_arg = getattr(column.server_default, "arg", None)
                    if sd_arg is None:
                        continue
                    
                    # ?SQLAlchemy 表达式使?dialect 编译
                    if hasattr(sd_arg, "compile"):
                        default_sql = str(sd_arg.compile(dialect=engine.dialect))
                    else:
                        default_sql = str(sd_arg)
                    
                    # MySQL 列定义中 DEFAULT 不接?NOW()，必须转换为 CURRENT_TIMESTAMP
                    if default_sql.upper() == "NOW()":
                        default_sql = "CURRENT_TIMESTAMP"
                    
                    # 重建完整列定义
                    nullable_clause = "NULL" if is_nullable == "YES" else "NOT NULL"
                    extra_clause = extra if extra else ""
                    
                    parts = [col_type, nullable_clause, f"DEFAULT {default_sql}"]
                    if extra_clause:
                        parts.append(extra_clause)
                    
                    # 保留现有 COMMENT（如果有?
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
                        f"修复?{table_name} ?{column.name} ?DEFAULT: {default_sql}"
                    )
            except Exception as e:
                logger.debug(f"检?{table_name}.{column.name} ?DEFAULT 失败: {e}")
    
    if fixed > 0:
        logger.info(f"共修?{fixed} 个列?server_default")


def _fix_auto_increment(engine):
    """
    修复主键列缺?AUTO_INCREMENT 的问题（MySQL 专用?
    
    策略：通过 INFORMATION_SCHEMA 读取当前列的完整定义?
    重建 ALTER TABLE ... MODIFY COLUMN ... 语句，确保不丢失 DEFAULT/UNSIGNED/COMMENT 等属性?
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
            
            # 只处?INTEGER 类型的单列主?
            type_str = str(col_info.get("type", "")).lower()
            if "int" not in type_str:
                continue
            
            # 检查是否已?AUTO_INCREMENT
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
                        f"为表 {table_name} 的主?{col_name} 添加 AUTO_INCREMENT"
                    )
            except Exception as e:
                logger.warning(f"修复 {table_name}.{col_name} ?AUTO_INCREMENT 失败: {e}")
    
    if fixed_count > 0:
        logger.info(f"共修?{fixed_count} 个表的主?AUTO_INCREMENT")


def _ensure_scoring_rule_constraint(engine):
    """确保 scoring_rule 表的唯一约束已升级为支持职业特定规则
    
    创建新的唯一索引 uk_role_profession_dimension（如果不存在）?
    对于已有数据（profession ?NULL），新旧索引都兼容?
    """
    try:
        with engine.begin() as conn:
            # 检查新索引是否已存?
            inspector = inspect(engine)
            existing_indexes = {
                idx["name"].lower()
                for idx in inspector.get_indexes("scoring_rule")
            }

            if "uk_role_profession_dimension" in existing_indexes:
                return

            # 创建新的唯一索引
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uk_role_profession_dimension "
                    "ON scoring_rule (role_type, profession, dimension)"
                )
            )
            logger.info("创建 scoring_rule 唯一索引: uk_role_profession_dimension")
    except Exception as e:
        logger.warning(f"升级 scoring_rule 约束失败: {e}")


# 导出
Base = get_base()


class _EngineProxy:
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def __call__(self):
        return _get_engine()


engine = _EngineProxy()

def _log_initialization_summary(stats: Dict[str, Any]):
    """
    记录初始化总结日志
    """
    logger.info("=" * 60)
    logger.info("数据库初始化完成")
    logger.info("=" * 60)
    logger.info(f"总表? {stats['total_tables']}")
    logger.info(f"已存在表: {stats['existing_tables']}")
    logger.info(f"新创建表: {stats['created_tables']}")
    logger.info(f"新创建索? {stats['created_indexes']}")
    logger.info(f"新创建约? {stats['created_constraints']}")

    if stats["errors"]:
        logger.error("初始化过程中遇到的错?")
        for error in stats["errors"]:
            logger.error(f"  - {error}")

    if not stats["errors"]:
        logger.info("?数据库初始化成功?)
    else:
        logger.warning("⚠️ 数据库初始化完成，但有部分错?)

    logger.info("=" * 60)


def _format_mysql_default(default_value: Any) -> str:
    """
    ?MySQL INFORMATION_SCHEMA.COLUMNS.COLUMN_DEFAULT 格式化为 SQL DEFAULT 子句?
    
    关键处理?
    - CURRENT_TIMESTAMP / NULL ?不加引号
    - 数字 ?不加引号
    - 字符??加单引号并转?
    
    返回空字符串表示没有 DEFAULT?
    """
    if default_value is None:
        return ""
    
    s = str(default_value).strip()
    if not s:
        return ""
    
    upper = s.upper()
    # MySQL 关键字型默认值（不加引号?
    if upper in ("CURRENT_TIMESTAMP", "NULL", "CURRENT_TIMESTAMP(6)"):
        return f"DEFAULT {upper}"
    
    # 数字型（不加引号?
    try:
        float(s)
        return f"DEFAULT {s}"
    except ValueError:
        pass
    
    # 字符串型（加单引号并转义?
    escaped = s.replace("'", "''")
    return f"DEFAULT '{escaped}'"

