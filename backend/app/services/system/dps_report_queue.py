# -*- coding: utf-8 -*-
# 模块功能：dps.report API 严格单并发请求队列
# 说明：
#   - 使用 queue.Queue + threading.Lock 实现线程安全的严格单并发
#   - 所有 dps.report API 调用（上传、获取 JSON）统一通过此队列提交
#   - 兼容同步代码（import_log、批量解析 worker）和异步代码（FastAPI 端点）
#   - 提供队列监控能力（长度、当前任务、统计）

import asyncio
import concurrent.futures
import queue
import threading
import time
import traceback
from typing import Any, Callable, Dict, Optional

from app.utils.logger import logger


class DpsReportRequestQueue:
    """dps.report API 严格单并发请求队列（线程安全）

    设计要点：
        1. queue.Queue 保证多线程/多协程安全入队
        2. threading.Lock 保证任意时刻只有 1 个请求在飞行中
        3. 独立 daemon worker 线程消费队列，避免阻塞调用方事件循环
        4. submit() 返回 Future.result()，调用方阻塞等待但队列全局串行
    """

    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._lock = threading.Lock()
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown = False
        self._stats = {
            "submitted": 0,
            "completed": 0,
            "failed": 0,
            "current_task": None,
            "current_started_at": 0.0,
        }
        self._stats_lock = threading.Lock()

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def submit(self, func: Callable, *args, **kwargs) -> Any:
        """提交同步任务到队列，阻塞等待结果。

        使用场景：LogImportService.import_log、批量解析 worker（同步线程）
        """
        if self._shutdown:
            raise RuntimeError("队列已关闭")

        future = concurrent.futures.Future()
        self._queue.put((func, args, kwargs, future))
        with self._stats_lock:
            self._stats["submitted"] += 1
        self._start_worker_if_needed()
        return future.result()

    async def submit_async(self, func: Callable, *args, **kwargs) -> Any:
        """提交同步任务到队列，async 调用方非阻塞等待。

        使用场景：FastAPI 端点、后台任务（async 上下文）
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.submit, func, *args, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """获取队列实时统计信息"""
        with self._stats_lock:
            stats = dict(self._stats)
        stats["queue_size"] = self._queue.qsize()
        stats["is_busy"] = self._lock.locked()
        current = stats.get("current_task")
        if current and stats.get("current_started_at"):
            stats["current_elapsed_sec"] = round(time.time() - stats["current_started_at"], 2)
        else:
            stats["current_elapsed_sec"] = 0.0
        return stats

    def shutdown(self, wait: bool = True):
        """优雅关闭队列，等待当前任务完成。"""
        self._shutdown = True
        if wait and self._worker_thread and self._worker_thread.is_alive():
            self._queue.join()

    # ------------------------------------------------------------------
    # 内部实现
    # ------------------------------------------------------------------

    def _start_worker_if_needed(self):
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
            logger.info("[dps_report_queue] worker 线程已启动")

    def _worker_loop(self):
        while not self._shutdown:
            try:
                func, args, kwargs, future = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            task_desc = f"{func.__name__}({args[:1] if args else ''})"
            with self._stats_lock:
                self._stats["current_task"] = task_desc
                self._stats["current_started_at"] = time.time()

            # 严格单并发：获取锁后才执行请求
            with self._lock:
                try:
                    logger.info(f"[dps_report_queue] 开始执行任务: {task_desc}")
                    result = func(*args, **kwargs)
                    future.set_result(result)
                    with self._stats_lock:
                        self._stats["completed"] += 1
                    logger.info(f"[dps_report_queue] 任务完成: {task_desc}")
                except Exception as e:
                    future.set_exception(e)
                    with self._stats_lock:
                        self._stats["failed"] += 1
                    logger.warning(f"[dps_report_queue] 任务失败: {task_desc}, 错误: {e}")
                finally:
                    with self._stats_lock:
                        self._stats["current_task"] = None
                        self._stats["current_started_at"] = 0.0

            self._queue.task_done()


# 全局单例（进程级）
dps_report_queue = DpsReportRequestQueue()
