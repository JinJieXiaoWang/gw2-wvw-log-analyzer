# -*- coding: utf-8 -*-
"""
API 限流器 — 令牌桶算法

针对 dps.report API 限流规则：
    - /uploadContent：25 请求 / 60 秒
    - 超出限制返回 HTTP 429 + retry_after

使用说明：
    from app.services.zevtc.rate_limiter import dps_report_limiter
    
    # 检查是否允许请求
    if dps_report_limiter.acquire():
        # 执行请求
    else:
        wait_seconds = dps_report_limiter.wait_time()
        # 等待或排队
"""

import threading
import time
from typing import Optional


class TokenBucketRateLimiter:
    """线程安全的令牌桶限流器"""

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: 时间窗口内允许的最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.rate = max_requests / window_seconds
        self.tokens = float(max_requests)
        self.last_update = time.monotonic()
        self.cooldown_until = 0.0  # 外部强制冷却截止时间（如收到 429）
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌，成功返回 True"""
        with self.lock:
            now = time.monotonic()
            if now < self.cooldown_until:
                return False

            elapsed = now - self.last_update
            self.tokens = min(
                self.max_requests,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_time(self, tokens: int = 1) -> float:
        """计算获取指定令牌需要等待的秒数"""
        with self.lock:
            now = time.monotonic()
            if now < self.cooldown_until:
                return self.cooldown_until - now

            elapsed = now - self.last_update
            self.tokens = min(
                self.max_requests,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= tokens:
                return 0.0

            # 需要补充的令牌数
            needed = tokens - self.tokens
            # 补充 needed 个令牌需要的时间
            return needed * (self.window_seconds / self.max_requests)

    def record_rejection(self, retry_after: Optional[float] = None):
        """记录一次被限流拒绝的事件，可选设置等待时间"""
        with self.lock:
            self.tokens = 0
            self.last_update = time.monotonic()
            if retry_after:
                self.cooldown_until = time.monotonic() + retry_after
            else:
                self.cooldown_until = 0.0


# dps.report 全局限流器实例
# 25 请求 / 60 秒 = 每 2.4 秒 1 个请求
dps_report_limiter = TokenBucketRateLimiter(max_requests=25, window_seconds=60)
