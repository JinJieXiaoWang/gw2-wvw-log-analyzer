#!/usr/bin/env python3
"""
数据库迁移脚本：为 evtc_agent 表添加 has_commander_tag 字段
"""

import sys

sys.path.insert(0, "D:/Code/backend")

from sqlalchemy import text

from app.config.database import engine


def migrate():
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'evtc_agent'
            AND COLUMN_NAME = 'has_commander_tag'
            AND TABLE_SCHEMA = DATABASE()
        """)).scalar()

        if result and result > 0:
            print("字段 has_commander_tag 已存在，跳过迁移")
            return

        # 添加字段
        conn.execute(text("""
            ALTER TABLE evtc_agent
            ADD COLUMN has_commander_tag SMALLINT NOT NULL DEFAULT 0
            COMMENT '是否携带指挥官标签: 0否/1是'
        """))
        conn.commit()
        print("成功添加字段 has_commander_tag 到 evtc_agent 表")


if __name__ == "__main__":
    migrate()
