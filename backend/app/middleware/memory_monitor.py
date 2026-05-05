# -*- coding: utf-8 -*-
# 模块功能：内存监控中间件
# 作者：系统
# 创建日期：2026-05-05
# 说明：
#   - 在请求处理前后记录进程 RSS 内存变化
#   - 识别异常内存增长的接口（如单次请求 +100MB）
#   - 不介入业务逻辑，仅记录日志

import gc
import os
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
    logger.warning("psutil 未安装，内存监控中间件将仅记录警告日志")

# 单次请求内存增长阈值（MB），超过则记录 warning
MEMORY_DELTA_THRESHOLD_MB = 100

# 进程 RSS 硬上限（MB），超过则记录 error
MEMORY_RSS_THRESHOLD_MB = int(os.environ.get("MAX_RSS_MB", "2048"))

_process: Optional[object] = None


def _get_process():
    global _process
    if _process is None and _PSUTIL_AVAILABLE:
        _process = psutil.Process()
    return _process


def get_memory_mb() -> float:
    """获取当前进程的 RSS 内存（MB）"""
    proc = _get_process()
    if proc is None:
        return 0.0
    return proc.memory_info().rss / (1024 * 1024)


def check_memory_limit(action: str = "") -> bool:
    """检查内存是否超过硬上限，返回是否超限"""
    rss_mb = get_memory_mb()
    if rss_mb > MEMORY_RSS_THRESHOLD_MB:
        logger.error(
            f"[memory] 内存超限警告 action={action} "
            f"rss_mb={rss_mb:.1f} threshold_mb={MEMORY_RSS_THRESHOLD_MB}"
        )
        return True
    return False


def trigger_gc(action: str = "") -> float:
    """显式触发 GC 并返回回收前后的内存变化（MB）"""
    before = get_memory_mb()
    gc.collect()
    after = get_memory_mb()
    delta = before - after
    if delta > 10:
        logger.info(
            f"[memory] GC回收 action={action} "
            f"before_mb={before:.1f} after_mb={after:.1f} freed_mb={delta:.1f}"
        )
    return delta


class MemoryMonitorMiddleware(BaseHTTPMiddleware):
    """内存监控中间件

    记录每个请求的内存增量，帮助识别异常增长的接口。
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        start_time = time.time()
        rss_before = get_memory_mb()

        try:
            response = await call_next(request)
        finally:
            rss_after = get_memory_mb()
            delta_mb = rss_after - rss_before
            duration_ms = (time.time() - start_time) * 1000

            # 只记录有明显内存变化或耗时较长的请求
            if delta_mb > MEMORY_DELTA_THRESHOLD_MB or duration_ms > 5000:
                level = "warning" if delta_mb > MEMORY_DELTA_THRESHOLD_MB else "info"
                log_msg = (
                    f"[memory] method={method} path={path} "
                    f"rss_before={rss_before:.1f}MB rss_after={rss_after:.1f}MB "
                    f"delta={delta_mb:+.1f}MB duration={duration_ms:.0f}ms"
                )
                if level == "warning":
                    logger.warning(log_msg)
                else:
                    logger.info(log_msg)

        return response
