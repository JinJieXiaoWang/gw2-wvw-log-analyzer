# -*- coding: utf-8 -*-
# 模块功能：批量解析任务内容内存管理服务
# 作者：帅妹妹丶.8297
# 说明：内存管理辅助函数与配置常量
# 创建日期：2026-05-04

import gc
import time
from typing import Dict

from app.config.settings import settings
from app.utils.logger import logger

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

# =====================================================================
# 内存管理配置（针对低内存服务器优化）
# =====================================================================
# 系统可用内存低于此值（MB）时暂停解析，等 GC 后恢复
MIN_SYSTEM_FREE_MEMORY_MB = settings.MIN_SYSTEM_FREE_MEMORY_MB
# 进程 RSS 超过此值（MB）时强制 GC
PROCESS_RSS_THRESHOLD_MB = settings.PROCESS_RSS_THRESHOLD_MB
# 是否启用子进程隔离解析（默认开启，Windows 下自动关闭）
USE_SUBPROCESS_PARSE = settings.USE_SUBPROCESS_PARSE
# 子进程解析超时（秒）
SUBPROCESS_TIMEOUT = settings.SUBPROCESS_TIMEOUT


def _get_memory_info() -> Dict[str, float]:
    """获取内存信息（MB）"""
    result = {"rss_mb": 0.0, "system_free_mb": 0.0, "system_total_mb": 0.0}
    if not _PSUTIL_AVAILABLE:
        return result
    try:
        proc = psutil.Process()
        result["rss_mb"] = proc.memory_info().rss / (1024 * 1024)
        vm = psutil.virtual_memory()
        result["system_free_mb"] = vm.available / (1024 * 1024)
        result["system_total_mb"] = vm.total / (1024 * 1024)
    except Exception:
        pass
    return result


def _check_memory_and_wait(action: str = "") -> bool:
    """检查内存状态，如果不足则等待并 GC，直到恢复或超时

    Returns:
        True: 内存已恢复，可以继续
        False: 应该跳过本次任务
    """
    if not _PSUTIL_AVAILABLE:
        return True

    mem = _get_memory_info()
    rss_mb = mem["rss_mb"]
    free_mb = mem["system_free_mb"]

    # 进程内存过高，立即 GC
    if rss_mb > PROCESS_RSS_THRESHOLD_MB:
        logger.warning(
            f"[batch] 进程内存偏高 action={action} rss={rss_mb:.0f}MB "
            f"强制 GC (threshold={PROCESS_RSS_THRESHOLD_MB}MB)"
        )
        gc.collect()
        gc.collect()
        time.sleep(0.5)

    # 系统可用内存不足，等 GC 后恢复
    wait_rounds = 0
    max_wait_rounds = 30  # 最多等 30 * 2 = 60 秒
    while free_mb < MIN_SYSTEM_FREE_MEMORY_MB and wait_rounds < max_wait_rounds:
        logger.warning(
            f"[batch] 系统可用内存不足 action={action} free={free_mb:.0f}MB "
            f"(need {MIN_SYSTEM_FREE_MEMORY_MB}MB)，暂 {wait_rounds + 1}/{max_wait_rounds}"
        )
        gc.collect()
        gc.collect()
        time.sleep(2)
        wait_rounds += 1
        mem = _get_memory_info()
        free_mb = mem["system_free_mb"]

    if free_mb < MIN_SYSTEM_FREE_MEMORY_MB:
        logger.error(
            f"[batch] 系统可用内存持续不足 action={action} free={free_mb:.0f}MB "
            f"跳过本次任务以避免 OOM 问题"
        )
        return False

    return True


def _deep_gc(action: str = ""):
    """深度 GC：释放未引用对象并记录效果"""
    if not _PSUTIL_AVAILABLE:
        gc.collect()
        return
    try:
        before = _get_memory_info()["rss_mb"]
        gc.collect()
        gc.collect()
        gc.collect()
        after = _get_memory_info()["rss_mb"]
        freed = before - after
        if freed > 5:
            logger.info(
                f"[batch] 深度 GC action={action} freed={freed:.1f}MB "
                f"before={before:.1f}MB after={after:.1f}MB"
            )
    except Exception:
        gc.collect()
