# -*- coding: utf-8 -*-
# 模块功能：通用装饰?
# 作者：系统
# 创建日期?2026-05-12

import functools
import inspect
from typing import Callable

from app.schemas.auth.common import ApiResponse
from app.utils.logger import logger


def handle_api_errors(func: Callable) -> Callable:
    """统一处理 API 接口异常，消除路由层重复 try/except 代码?

    捕获所有未处理异常，记录错误日志并返回标准化的 ApiResponse(success=False, code=500)?
    通过保留原始函数签名，确保与 FastAPI 的参数解析和依赖注入兼容?
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} 执行失败: {e}", exc_info=True)
            return ApiResponse(
                success=False,
                message=f"{func.__name__} 执行失败: {str(e)}",
                code=500,
            )

    # 保留原始签名，供 FastAPI 提取路径参数、查询参数和依赖注入
    wrapper.__signature__ = inspect.signature(func)
    return wrapper
