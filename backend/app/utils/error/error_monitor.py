# -*- coding: utf-8 -*-
"""
错误监控与日志系统提供详细的错误捕获、日志记录和监控功能
"""

import json
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from app.utils.logger import logger

# 错误统计存储
ERROR_STATS = {"total_errors": 0, "5xx_errors": 0, "4xx_errors": 0, "recent_errors": []}

# 错误统计配置
MAX_RECENT_ERRORS = 100


class ErrorMonitor:
    """错误监控"""

    @staticmethod
    def record_error(
        endpoint: str,
        status_code: int,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        user_info: Optional[Dict] = None,
        request_info: Optional[Dict] = None,
    ):
        """记录错误"""
        # 更新统计
        ERROR_STATS["total_errors"] += 1
        if status_code >= 500:
            ERROR_STATS["5xx_errors"] += 1
        elif status_code >= 400:
            ERROR_STATS["4xx_errors"] += 1

        # 构建错误记录
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "status_code": status_code,
            "error_type": error_type,
            "message": message,
            "stack_trace": stack_trace,
            "user_info": user_info,
            "request_info": request_info,
        }

        # 添加到最近错误列?        ERROR_STATS["recent_errors"].append(error_record)

        # 保持列表大小
        if len(ERROR_STATS["recent_errors"]) > MAX_RECENT_ERRORS:
            ERROR_STATS["recent_errors"].pop(0)

        # 记录到日期        log_msg = f"ERROR - {endpoint} - {status_code} - {error_type}: {message}"
        if stack_trace:
            logger.error(log_msg, exc_info=True)
        else:
            logger.error(log_msg)

        logger.debug(f"Error details: {json.dumps(error_record, ensure_ascii=False)}")

        return error_record

    @staticmethod
    def get_error_stats() -> Dict[str, Any]:
        """获取错误统计"""
        return {
            "total_errors": ERROR_STATS["total_errors"],
            "5xx_errors": ERROR_STATS["5xx_errors"],
            "4xx_errors": ERROR_STATS["4xx_errors"],
            "recent_errors": ERROR_STATS["recent_errors"][-20:],  # 返回最?0?            "stats_time": datetime.now().isoformat(),
        }

    @staticmethod
    def clear_stats():
        """清空统计"""
        ERROR_STATS["total_errors"] = 0
        ERROR_STATS["5xx_errors"] = 0
        ERROR_STATS["4xx_errors"] = 0
        ERROR_STATS["recent_errors"].clear()


def monitor_errors(endpoint_name: str = None):
    """
    错误监控装饰?    自动捕获并记录函数中的异?    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                endpoint = endpoint_name or func.__name__

                ErrorMonitor.record_error(
                    endpoint=endpoint,
                    status_code=500,
                    error_type=type(e).__name__,
                    message=str(e),
                    stack_trace=traceback.format_exc(),
                )
                raise

        return wrapper

    return decorator


def monitor_sync_errors(endpoint_name: str = None):
    """同步版本的错误监控装饰器"""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                endpoint = endpoint_name or func.__name__

                ErrorMonitor.record_error(
                    endpoint=endpoint,
                    status_code=500,
                    error_type=type(e).__name__,
                    message=str(e),
                    stack_trace=traceback.format_exc(),
                )
                raise

        return wrapper

    return decorator


def get_error_report() -> Dict[str, Any]:
    """生成错误报告"""
    stats = ErrorMonitor.get_error_stats()

    # 分析错误分布
    error_types = {}
    for error in ERROR_STATS["recent_errors"]:
        etype = error["error_type"]
        error_types[etype] = error_types.get(etype, 0) + 1

    return {
        "summary": stats,
        "error_type_distribution": error_types,
        "generated_at": datetime.now().isoformat(),
    }


def export_errors_to_file(file_path: str, limit: int = 100):
    """导出错误到JSON文件"""
    errors = ERROR_STATS["recent_errors"][-limit:]

    report = {
        "export_time": datetime.now().isoformat(),
        "total_errors_exported": len(errors),
        "errors": errors,
    }

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Errors exported to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export errors: {e}")
        return False


def setup_global_error_handlers(app):
    """设置全局错误处理器（用于FastAPI）"""
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        ErrorMonitor.record_error(
            endpoint=request.url.path,
            status_code=500,
            error_type=type(exc).__name__,
            message=str(exc),
            stack_trace=traceback.format_exc(),
            request_info={
                "method": request.method,
                "url": str(request.url),
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "服务器内部错误",
                "error_code": "INTERNAL_ERROR",
            },
        )

    logger.info("Global error monitor setup complete")
    return app
