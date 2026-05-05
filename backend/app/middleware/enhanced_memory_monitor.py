
# -*- coding: utf-8 -*-
# Module: Enhanced Memory Monitor Middleware
# Author: System
# Date: 2026-05-06
# Description: Auto GC, memory alerts, OOM prevention

import gc
import os
import time
from collections import deque

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed, memory monitor limited")

# Config
MEMORY_DELTA_THRESHOLD_MB = int(os.environ.get("MEMORY_DELTA_THRESHOLD_MB", 100))
MEMORY_RSS_SOFT_LIMIT_MB = int(os.environ.get("MEMORY_RSS_SOFT_LIMIT_MB", 1536))
MEMORY_RSS_HARD_LIMIT_MB = int(os.environ.get("MEMORY_RSS_HARD_LIMIT_MB", 2048))
MEMORY_RSS_CRITICAL_LIMIT_MB = int(os.environ.get("MEMORY_RSS_CRITICAL_LIMIT_MB", 2560))
AUTO_GC_THRESHOLD_MB = int(os.environ.get("AUTO_GC_THRESHOLD_MB", 800))
MAX_MEMORY_HISTORY = 100

# Global state
_process = None
_memory_history = deque(maxlen=MAX_MEMORY_HISTORY)
_last_gc_time = 0.0
_gc_cooldown_seconds = 10.0
_consecutive_high_memory_count = 0


def _get_process():
    global _process
    if _process is None and _PSUTIL_AVAILABLE:
        _process = psutil.Process()
    return _process


def get_memory_mb():
    """Get current process RSS memory in MB"""
    proc = _get_process()
    if proc is None:
        return 0.0
    try:
        return proc.memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0


def check_memory_limit(action=""):
    """Check if memory limit exceeded, return bool"""
    rss_mb = get_memory_mb()
    
    if rss_mb > MEMORY_RSS_HARD_LIMIT_MB:
        logger.error(
            "[memory] Memory limit HARD! action=%s rss_mb=%.1f limit=%d",
            action, rss_mb, MEMORY_RSS_HARD_LIMIT_MB
        )
        return True
    elif rss_mb > MEMORY_RSS_SOFT_LIMIT_MB:
        logger.warning(
            "[memory] Memory limit SOFT! action=%s rss_mb=%.1f limit=%d",
            action, rss_mb, MEMORY_RSS_SOFT_LIMIT_MB
        )
        return True
    return False


def trigger_gc(action="", force=False):
    """Trigger GC and return freed memory in MB"""
    global _last_gc_time, _consecutive_high_memory_count
    
    now = time.time()
    if not force and (now - _last_gc_time) < _gc_cooldown_seconds:
        return 0.0
    
    before = get_memory_mb()
    gc.collect()
    gc.collect()
    after = get_memory_mb()
    delta = before - after
    
    _last_gc_time = now
    
    if delta > 10:
        logger.info(
            "[memory] GC freed action=%s before_mb=%.1f after_mb=%.1f freed_mb=%.1f",
            action, before, after, delta
        )
        _consecutive_high_memory_count = 0
    elif delta < -10:
        logger.warning(
            "[memory] GC increased memory! action=%s before_mb=%.1f after_mb=%.1f",
            action, before, after
        )
    
    return delta


def record_memory_snapshot(phase="unknown"):
    """Record memory snapshot to history"""
    rss_mb = get_memory_mb()
    snapshot = {
        "timestamp": time.time(),
        "phase": phase,
        "rss_mb": rss_mb,
    }
    _memory_history.append(snapshot)


def get_memory_stats():
    """Get memory statistics"""
    current_rss = get_memory_mb()
    if _memory_history:
        rss_values = [s["rss_mb"] for s in _memory_history]
        stats = {
            "current_mb": current_rss,
            "min_mb": min(rss_values) if rss_values else 0,
            "max_mb": max(rss_values) if rss_values else 0,
            "avg_mb": sum(rss_values) / len(rss_values) if rss_values else 0,
            "history_count": len(_memory_history),
            "soft_limit_mb": MEMORY_RSS_SOFT_LIMIT_MB,
            "hard_limit_mb": MEMORY_RSS_HARD_LIMIT_MB,
            "critical_limit_mb": MEMORY_RSS_CRITICAL_LIMIT_MB,
        }
    else:
        stats = {"current_mb": current_rss}
    return stats


class EnhancedMemoryMonitorMiddleware(BaseHTTPMiddleware):
    """Enhanced memory monitor middleware"""

    async def dispatch(self, request, call_next):
        global _consecutive_high_memory_count
        
        path = request.url.path
        method = request.method
        start_time = time.time()
        rss_before = get_memory_mb()
        
        # Skip system paths
        if path in ["/health", "/ready", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Check critical memory pressure
        current_rss = get_memory_mb()
        if current_rss > MEMORY_RSS_CRITICAL_LIMIT_MB:
            logger.critical(
                "[memory] Critical memory pressure! Rejecting request rss_mb=%.1f limit=%d path=%s",
                current_rss, MEMORY_RSS_CRITICAL_LIMIT_MB, path
            )
            trigger_gc(action="critical_memory_pressure", force=True)
            raise HTTPException(
                status_code=503,
                detail="Service unavailable due to high memory pressure. Please try again later."
            )
        
        # Auto GC on high memory
        if current_rss > AUTO_GC_THRESHOLD_MB:
            _consecutive_high_memory_count += 1
            if _consecutive_high_memory_count >= 3:
                trigger_gc(action="auto_threshold_reached", force=True)
                _consecutive_high_memory_count = 0
            else:
                trigger_gc(action="auto_threshold_reached")
        else:
            _consecutive_high_memory_count = 0
        
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            rss_after = get_memory_mb()
            delta_mb = rss_after - rss_before
            duration_ms = (time.time() - start_time) * 1000
            
            # Record snapshot
            record_memory_snapshot(phase="request_end:%s:%s" % (method, path))
            
            # Log significant changes
            if delta_mb > MEMORY_DELTA_THRESHOLD_MB:
                logger.warning(
                    "[memory] Significant memory growth method=%s path=%s rss_before=%.1fMB rss_after=%.1fMB delta=%+.1fMB duration=%.0fms",
                    method, path, rss_before, rss_after, delta_mb, duration_ms
                )
                if delta_mb > 200:
                    trigger_gc(action="large_memory_request", force=True)
            elif duration_ms > 5000:
                logger.info(
                    "[memory] Slow request method=%s path=%s rss_before=%.1fMB rss_after=%.1fMB delta=%+.1fMB duration=%.0fms",
                    method, path, rss_before, rss_after, delta_mb, duration_ms
                )
            
            check_memory_limit(action="request_end:%s:%s" % (method, path))

