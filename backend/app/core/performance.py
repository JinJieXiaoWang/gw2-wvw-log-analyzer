# -*- coding: utf-8 -*-
# 模块功能：性能监控工具
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：time, functools, statistics, logging

import asyncio
import functools
import statistics
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.utils.logger import logger


class PerformanceMonitor:
    """性能监控工具"""

    def __init__(self):
        # 功能：初始化性能监控
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()

    def record(self, endpoint: str, duration: float, status: str = "success") -> None:
        # 功能：记录性能指标
        # 参数：endpoint - 接口名称
        # duration - 响应时间（毫秒）
        # status - 状态（success/error）
        # 返回：无
        self.metrics[endpoint].append(duration)
        self.request_counts[endpoint] += 1
        if status == "error":
            self.error_counts[endpoint] += 1

    def get_stats(self, endpoint: str) -> Dict[str, Any]:
        # 功能：获取接口性能指标
        # 参数：endpoint - 接口名称
        # 返回：性能指标字典
        if endpoint not in self.metrics or not self.metrics[endpoint]:
            return {
                "endpoint": endpoint,
                "count": 0,
                "error_count": 0,
                "error_rate": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "median_ms": 0,
                "p95_ms": 0,
                "p99_ms": 0,
            }

        durations = sorted(self.metrics[endpoint])
        count = len(durations)

        return {
            "endpoint": endpoint,
            "count": count,
            "error_count": self.error_counts.get(endpoint, 0),
            "error_rate": round(self.error_counts.get(endpoint, 0) / count * 100, 2),
            "avg_ms": round(statistics.mean(durations) * 1000, 2),
            "min_ms": round(min(durations) * 1000, 2),
            "max_ms": round(max(durations) * 1000, 2),
            "median_ms": round(statistics.median(durations) * 1000, 2),
            "p95_ms": round(durations[int(count * 0.95)] * 1000, 2) if count > 0 else 0,
            "p99_ms": round(durations[int(count * 0.99)] * 1000, 2) if count > 0 else 0,
        }

    def get_all_stats(self) -> List[Dict[str, Any]]:
        # 功能：获取所有接口性能指标
        # 参数：无
        # 返回：所有接口性能指标列表
        return [self.get_stats(endpoint) for endpoint in self.metrics.keys()]

    def get_summary(self) -> Dict[str, Any]:
        # 功能：获取性能摘要
        # 参数：无
        # 返回：性能摘要字典
        all_durations = []
        for durations in self.metrics.values():
            all_durations.extend(durations)

        if not all_durations:
            return {
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "total_requests": sum(self.request_counts.values()),
                "total_errors": sum(self.error_counts.values()),
                "endpoints_monitored": len(self.metrics),
                "avg_ms": 0,
                "median_ms": 0,
            }

        sorted_durations = sorted(all_durations)
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())

        return {
            "uptime_seconds": round(
                (datetime.now() - self.start_time).total_seconds(), 2
            ),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (
                round(total_errors / total_requests * 100, 2)
                if total_requests > 0
                else 0
            ),
            "endpoints_monitored": len(self.metrics),
            "avg_ms": round(statistics.mean(all_durations) * 1000, 2),
            "median_ms": round(statistics.median(all_durations) * 1000, 2),
            "p95_ms": round(
                sorted_durations[int(len(sorted_durations) * 0.95)] * 1000, 2
            ),
            "p99_ms": round(
                sorted_durations[int(len(sorted_durations) * 0.99)] * 1000, 2
            ),
        }

    def reset(self) -> None:
        # 功能：重置所有监控数据
        self.metrics.clear()
        self.request_counts.clear()
        self.error_counts.clear()
        self.start_time = datetime.now()
        logger.info("性能监控数据已重置")


performance_monitor = PerformanceMonitor()


def monitor_performance(endpoint_name: Optional[str] = None):
    # 功能：性能监控装饰器
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            endpoint = endpoint_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.record(endpoint, duration, status)
                if duration > 1.0:
                    logger.warning(f"请求 {endpoint} 耗时 {duration:.2f}s")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            endpoint = endpoint_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            status = "success"
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.record(endpoint, duration, status)
                if duration > 1.0:
                    logger.warning(f"请求 {endpoint} 耗时 {duration:.2f}s")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class BenchmarkRunner:
    """基准测试运行器"""

    def __init__(self):
        self.results: Dict[str, Dict[str, float]] = {}

    def run(
        self, name: str, func: Callable, iterations: int = 100, warmup: int = 10
    ) -> Dict[str, float]:
        # 功能：运行基准测试
        logger.info(f"开始基准测试: {name}")

        for i in range(warmup):
            func()

        times = []
        for i in range(iterations):
            start = time.time()
            func()
            elapsed = time.time() - start
            times.append(elapsed)

        sorted_times = sorted(times)
        count = len(times)

        result = {
            "iterations": iterations,
            "warmup": warmup,
            "min_ms": round(min(times) * 1000, 3),
            "max_ms": round(max(times) * 1000, 3),
            "avg_ms": round(statistics.mean(times) * 1000, 3),
            "median_ms": round(statistics.median(times) * 1000, 3),
            "std_dev_ms": round(statistics.stdev(times) * 1000, 3) if count > 1 else 0,
            "p95_ms": round(sorted_times[int(count * 0.95)] * 1000, 3),
            "p99_ms": round(sorted_times[int(count * 0.99)] * 1000, 3),
        }

        self.results[name] = result
        logger.info(f"基准测试完成: {name} - 平均 {result['avg_ms']}ms")

        return result

    def get_results(self) -> Dict[str, Dict[str, float]]:
        # 功能：获取所有基准测试结果
        return self.results

    def compare(self, name1: str, name2: str) -> Optional[Dict[str, Any]]:
        # 功能：比较两个基准测试结果
        if name1 not in self.results or name2 not in self.results:
            return None

        r1 = self.results[name1]
        r2 = self.results[name2]

        avg_diff = r1["avg_ms"] - r2["avg_ms"]
        percent_diff = (avg_diff / r1["avg_ms"] * 100) if r1["avg_ms"] > 0 else 0

        return {
            "name1": name1,
            "name2": name2,
            "avg1_ms": r1["avg_ms"],
            "avg2_ms": r2["avg_ms"],
            "difference_ms": round(avg_diff, 3),
            "percent_faster": round(percent_diff, 2),
            "winner": name2 if avg_diff > 0 else name1 if avg_diff < 0 else "tie",
        }


benchmark_runner = BenchmarkRunner()
