# -*- coding: utf-8 -*-
# 模块功能：数据库操作重试工具
# 作者：系统
# 创建日期?2026-05-02
# 依赖说明：SQLAlchemy, tenacity（如果可用）

import logging
import time
from functools import wraps

from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# MySQL锁等待超时错误码
MYSQL_LOCK_WAIT_TIMEOUT = 1205


def retry_on_lock_wait(
    max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0
):
    """
    装饰器：在发生数据库锁等待超时时自动重试

    Args:
        max_retries: 最大重试次?        initial_delay: 初始延迟（秒?        backoff_factor: 延迟倍增因子

    Usage:
        @retry_on_lock_wait(max_retries=3)
        def sync_ei_data(db, log_id):
            # 可能发生锁等待的数据库操?            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    # 检查是否为锁等待超时错?                    if hasattr(e, "args") and len(e.args) > 0:
                        orig_exc = e.args[0]
                        # 检查MySQL错误?                        if hasattr(orig_exc, "args") and len(orig_exc.args) >= 2:
                            if orig_exc.args[0] == MYSQL_LOCK_WAIT_TIMEOUT:
                                if retries < max_retries:
                                    logger.warning(
                                        f"数据库锁等待超时，正在重?({retries + 1}/{max_retries})，延?{delay:.2f}s"
                                    )
                                    time.sleep(delay)
                                    retries += 1
                                    delay *= backoff_factor
                                    continue
                                else:
                                    logger.error(
                                        f"数据库锁等待超时，已达到最大重试次?({max_retries})"
                                    )

                    # 非锁等待超时错误，直接抛?                    raise
                except Exception:
                    # 其他异常直接抛出
                    raise

            # 重试次数用尽
            raise OperationalError(
                f"数据库操作失败：锁等待超时，已重?{max_retries} ?,
                params=None,
                orig=None,
            )

        return wrapper

    return decorator


def execute_with_retry(db_session, query_func, *args, max_retries: int = 3):
    """
    执行数据库操作并在锁等待超时时重?
    Args:
        db_session: 数据库会?        query_func: 查询函数，接?db_session ?*args
        *args: 传递给 query_func 的参?        max_retries: 最大重试次?
    Returns:
        query_func 的返回?
    Usage:
        result = execute_with_retry(db, sync_players, log_id, players, stats, duration_ms)
    """
    retries = 0
    delay = 1.0

    while retries <= max_retries:
        try:
            return query_func(db_session, *args)
        except OperationalError as e:
            if hasattr(e, "args") and len(e.args) > 0:
                orig_exc = e.args[0]
                if hasattr(orig_exc, "args") and len(orig_exc.args) >= 2:
                    if orig_exc.args[0] == MYSQL_LOCK_WAIT_TIMEOUT:
                        if retries < max_retries:
                            logger.warning(
                                f"数据库锁等待超时，正在重?({retries + 1}/{max_retries})"
                            )
                            time.sleep(delay)
                            retries += 1
                            delay *= 2
                            continue
                raise
        except Exception:
            raise

    raise OperationalError(
        f"数据库操作失败：锁等待超时，已重?{max_retries} ?, params=None, orig=None
    )
