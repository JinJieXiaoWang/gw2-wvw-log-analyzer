# -*- coding: utf-8 -*-
# 模块功能：数据库管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.database import (
    get_current_db_info,
    get_db,
    switch_database,
    test_connection,
)
from app.config.database_settings import DatabaseType
from app.models.sys_user import SysUser
from app.schemas.common import ApiResponse
from app.services.auth_service import get_current_admin, require_super_admin
from app.services.system.database_manager import DatabaseManager
from app.utils.logger import logger

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/info", response_model=ApiResponse, summary="获取数据库信息")
async def get_database_info():
    """获取当前数据库配置和连接状态"""
    try:
        info = get_current_db_info()

        return ApiResponse.success_response(data=info, message="获取数据库信息成功")

    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据库信息失败")


@router.get("/check", response_model=ApiResponse, summary="检查表结构")
async def check_tables():
    """检查数据库表结构"""
    try:
        manager = DatabaseManager()
        results = manager.check_tables()

        return ApiResponse.success_response(data=results, message="表结构检查完成")

    except Exception as e:
        logger.error(f"表结构检查失败: {e}")
        raise HTTPException(status_code=500, detail="表结构检查失败")


@router.post("/init", response_model=ApiResponse, summary="初始化数据库")
async def init_database(
    force_recreate: bool = Query(False, description="是否强制重建表"),
    admin: SysUser = Depends(require_super_admin),
):
    """初始化数据库，创建表结构"""
    try:
        manager = DatabaseManager()
        success = manager.init_database(force_recreate=force_recreate)

        if success:
            return ApiResponse.success_response(
                data={"force_recreate": force_recreate}, message="数据库初始化成功"
            )
        else:
            raise HTTPException(status_code=500, detail="数据库初始化失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据库初始化异常: {e}")
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")


@router.post("/test-mysql", response_model=ApiResponse, summary="测试MySQL连接")
async def test_mysql(
    host: str = Query("localhost", description="MySQL主机"),
    port: int = Query(3306, description="MySQL端口"),
    user: str = Query("root", description="MySQL用户名"),
    password: str = Query("", description="MySQL密码"),
    database: str = Query("gw2_log_system", description="MySQL数据库名"),
):
    """测试MySQL连接（不保存配置）"""
    try:
        manager = DatabaseManager()
        result = manager.test_mysql_connection(host, port, user, password, database)

        if result["success"]:
            return ApiResponse.success_response(data=result, message=result["message"])
        else:
            return ApiResponse.error_response(message=result["message"], code=400)

    except Exception as e:
        logger.error(f"MySQL连接测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


@router.post("/switch", response_model=ApiResponse, summary="切换数据库")
async def switch_db(
    db_type: str = Query(..., description="数据库类型: sqlite/mysql"),
    sqlite_path: Optional[str] = Query(None, description="SQLite路径"),
    mysql_host: Optional[str] = Query(None, description="MySQL主机"),
    mysql_port: Optional[int] = Query(None, description="MySQL端口"),
    mysql_user: Optional[str] = Query(None, description="MySQL用户"),
    mysql_password: Optional[str] = Query(None, description="MySQL密码"),
    mysql_database: Optional[str] = Query(None, description="MySQL数据库"),
    admin: SysUser = Depends(require_super_admin),
):
    """切换数据库类型（运行时切换）"""
    try:
        # 验证类型
        try:
            db_type_enum = DatabaseType(db_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"不支持的数据库类型: {db_type}"
            )

        # 准备参数
        kwargs = {}
        if sqlite_path:
            kwargs["sqlite_path"] = sqlite_path
        if mysql_host:
            kwargs["mysql_host"] = mysql_host
        if mysql_port:
            kwargs["mysql_port"] = mysql_port
        if mysql_user:
            kwargs["mysql_user"] = mysql_user
        if mysql_password:
            kwargs["mysql_password"] = mysql_password
        if mysql_database:
            kwargs["mysql_database"] = mysql_database

        # 切换
        switch_database(db_type_enum, **kwargs)

        # 测试连接
        connected = test_connection()

        return ApiResponse.success_response(
            data={
                "new_type": db_type_enum.value,
                "connected": connected,
                "info": get_current_db_info(),
            },
            message=f"已切换到 {db_type_enum.value} 数据库",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据库切换失败: {e}")
        raise HTTPException(status_code=500, detail=f"数据库切换失败: {str(e)}")
