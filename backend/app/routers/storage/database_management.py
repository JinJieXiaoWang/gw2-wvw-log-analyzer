# -*- coding: utf-8 -*-
# 模块功能：数据库管理API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-05-01

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.database import (
    get_current_db_info,
    get_db,
    switch_database,
    test_connection,
)
from app.config.database.database_settings import DatabaseType
from app.schemas.auth.common import ApiResponse
from app.services.auth.auth_service import require_super_admin
from app.services.system.database_manager import DatabaseManager
from app.utils.logger import logger

router = APIRouter(prefix="/database", tags=["数据库管理"])


@router.get("/info", response_model=ApiResponse, summary="获取数据库信息息")
async def get_database_info():
    try:
        info = get_current_db_info()
        return ApiResponse.success_response(data=info, message="获取数据库信息成功")
    except Exception as e:
        logger.error(f"获取数据库信息失败 {e}")
        raise Exception(f"获取数据库信息失败 {e}")


@router.get("/check", response_model=ApiResponse, summary="检查表结构")
async def check_tables(db: Session = Depends(get_db)):
    try:
        manager = DatabaseManager()
        results = manager.check_tables()
        return ApiResponse.success_response(data=results, message="表结构检查完成")
    except Exception as e:
        logger.error(f"表结构检查失败 {e}")
        raise Exception(f"表结构检查失败 {e}")


@router.post("/init", response_model=ApiResponse, summary="初始化数据库")
async def init_database(
    force_recreate: bool = Query(False, description="是否强制重建"),
    init_data: bool = Query(True, description="是否初始化数据"),
    admin = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    try:
        manager = DatabaseManager()
        success = manager.init_database(force_recreate=force_recreate)
        if not success:
            raise Exception("数据库初始化失败")
        
        result = {"force_recreate": force_recreate}
        
        # 如果需要初始化数据
        if init_data:
            from app.data.init_all import initialize_all
            init_result = initialize_all(db)
            result["data_initialization"] = init_result
        
        return ApiResponse.success_response(
            data=result, 
            message="数据库初始化成功"
        )
    except Exception as e:
        logger.error(f"数据库初始化异常: {e}")
        raise Exception(f"数据库初始化失败: {str(e)}")


@router.post("/test-mysql", response_model=ApiResponse, summary="测试MySQL连接")
async def test_mysql(
    host: str = Query("localhost", description="MySQL主机"),
    port: int = Query(3306, description="MySQL端口"),
    user: str = Query("root", description="MySQL用户"),
    password: str = Query("", description="MySQL密码"),
    database: str = Query("gw2_log_system", description="MySQL数据库名"),
):
    try:
        manager = DatabaseManager()
        result = manager.test_mysql_connection(host, port, user, password, database)
        if result["success"]:
            return ApiResponse.success_response(data=result, message=result["message"])
        else:
            return ApiResponse.error_response(message=result["message"], code=400)
    except Exception as e:
        logger.error(f"MySQL连接测试失败: {e}")
        raise Exception(f"连接测试失败: {str(e)}")


@router.post("/switch", response_model=ApiResponse, summary="切换数据库")
async def switch_db(
    db_type: str = Query(..., description="数据库类 sqlite/mysql"),
    sqlite_path: Optional[str] = Query(None, description="SQLite路径"),
    mysql_host: Optional[str] = Query(None, description="MySQL主机"),
    mysql_port: Optional[int] = Query(None, description="MySQL端口"),
    mysql_user: Optional[str] = Query(None, description="MySQL用户"),
    mysql_password: Optional[str] = Query(None, description="MySQL密码"),
    mysql_database: Optional[str] = Query(None, description="MySQL数据库名"),
    admin = Depends(require_super_admin),
):
    try:
        try:
            db_type_enum = DatabaseType(db_type.lower())
        except ValueError:
            raise Exception(f"不支持的数据库类 {db_type}")

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

        switch_database(db_type_enum, **kwargs)
        connected = test_connection()

        return ApiResponse.success_response(
            data={
                "new_type": db_type_enum.value,
                "connected": connected,
                "info": get_current_db_info(),
            },
            message=f"已切换到 {db_type_enum.value} 数据库",
        )
    except Exception as e:
        logger.error(f"数据库切换失败 {e}")
        raise Exception(f"数据库切换失败 {str(e)}")

