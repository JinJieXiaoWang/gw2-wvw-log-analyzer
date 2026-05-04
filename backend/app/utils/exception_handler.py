# 模块功能：全局异常处理器
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI

from datetime import datetime

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.schemas.common import ApiResponse
from app.utils.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.logger import logger


async def app_exception_handler(request: Request, exc: AppException):
    """
    功能：处理应用自定义异常
    参数：
        request: 请求对象
        exc: 异常对象
    返回：JSON响应
    """
    logger.error(f"应用异常: {exc.detail}")
    content = {
        "success": False,
        "message": exc.detail,
        "error_code": "UNAUTHORIZED" if exc.status_code == 401 else "BAD_REQUEST",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }
    return JSONResponse(status_code=exc.status_code, content=content)


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """
    功能：处理资源未找到异常
    参数：
        request: 请求对象
        exc: 异常对象
    返回：JSON响应
    """
    logger.error(f"资源未找到: {exc.detail}")
    content = {
        "success": False,
        "message": exc.detail,
        "error_code": "NOT_FOUND",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=content)


async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    """
    功能：处理请求参数错误异常
    参数：
        request: 请求对象
        exc: 异常对象
    返回：JSON响应
    """
    logger.error(f"请求参数错误: {exc.detail}")
    content = {
        "success": False,
        "message": exc.detail,
        "error_code": "INVALID_CREDENTIALS",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    功能：处理数据库异常
    参数：
        request: 请求对象
        exc: 异常对象
    返回：JSON响应
    """
    logger.error(f"数据库异常: {str(exc)}")
    content = {
        "success": False,
        "message": "数据库操作失败",
        "error_code": "DATABASE_ERROR",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    功能：处理通用异常
    参数：
        request: 请求对象
        exc: 异常对象
    返回：JSON响应
    """
    logger.error(f"通用异常: {str(exc)}")
    content = {
        "success": False,
        "message": "服务器内部错误",
        "error_code": "INTERNAL_ERROR",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


def register_exception_handlers(app):
    """
    功能：注册所有异常处理器
    参数：app - FastAPI应用实例
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(BadRequestException, bad_request_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
