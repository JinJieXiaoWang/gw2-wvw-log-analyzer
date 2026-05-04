#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 功能：重置管理员密码
# 作者：系统自动生成
# 创建日期：2026-05-04

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.services.auth_service import get_admin_by_username, get_password_hash
from app.utils.logger import logger


def reset_admin_password(username="admin", new_password="admin123456"):
    """重置管理员密码"""
    db = SessionLocal()
    try:
        admin = get_admin_by_username(db, username)
        if not admin:
            logger.error(f"管理员用户不存在: {username}")
            return False

        admin.password_hash = get_password_hash(new_password)
        db.commit()
        logger.info(f"={80}")
        logger.info(f"管理员密码已重置成功！")
        logger.info(f"  用户名: {username}")
        logger.info(f"  新密码: {new_password}")
        logger.info(f"={80}")
        return True
    except Exception as e:
        logger.error(f"重置密码失败: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="重置管理员密码")
    parser.add_argument("--username", default="admin", help="管理员用户名")
    parser.add_argument("--password", default="admin123456", help="新密码")

    args = parser.parse_args()
    success = reset_admin_password(args.username, args.password)
    sys.exit(0 if success else 1)
