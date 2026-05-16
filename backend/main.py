# -*- coding: utf-8 -*-
# 模块功能：FastAPI应用主入口
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI, uvicorn, contextlib

from contextlib import asynccontextmanager

import app.models  # 确保所有模型类注册到 Base.metadata
from app.config.database import get_db_context, init_db
from app.config.settings import settings
from app.core.task_scheduler import start_scheduler, stop_scheduler

# 注册增强版内存监控中间件（自动GC、内存超限告警、OOM预防）
from app.middleware.enhanced_memory_monitor import EnhancedMemoryMonitorMiddleware
from app.routers.ai import router as ai_router
from app.routers.auth import router as auth_router
from app.routers.auth.users import router as users_router
from app.routers.dictionary import router as dictionary_router
from app.routers.game import router as game_data_router
from app.routers.game.bdcode import router as bdcode_router
from app.routers.game.builds import router as builds_router
from app.routers.game.professions import router as professions_router
from app.routers.game.ref_data import router as ref_data_router
from app.routers.logs import router as logs_router
from app.routers.logs.ei_analysis import router as ei_analysis_router
from app.routers.logs.fights import router as fights_router
from app.routers.scoring import router as scoring_router
from app.routers.scoring.attendance import router as attendance_router
from app.routers.scoring.scoring_rules import router as scoring_rules_router
from app.routers.skills.skill_rotation import router as skill_rotation_router
from app.routers.storage import router as storage_router
from app.routers.system.config import router as config_router
from app.routers.system.dashboard import router as dashboard_router
from app.routers.system.dps_report_monitor import router as dps_report_queue_router
from app.routers.system.memory_monitor import router as memory_monitor_router
from app.routers.system.monitor import router as monitor_router
from app.routers.system.monitoring import router as monitoring_router
from app.routers.system.notice import router as notice_router
from app.routers.system.settings import router as settings_router
from app.routers.system.initialization import router as initialization_router
from app.routers.system.menus import router as menus_router
from app.routers.test.test_dps_report import router as test_dps_report_router
from app.services.auth.auth_service import init_predefined_admin
from app.services.zevtc.batch_parse_service import start_workers, stop_workers
from app.utils.error.exception_handler import register_exception_handlers
from app.utils.error.exceptions import AppException
from app.utils.logger import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("GW2日志系统启动中...")
    init_db()
    # 启动批量解析工作线程池
    start_workers()
    # 启动任务调度器
    start_scheduler()
    try:
        with get_db_context() as db:
            # 【修复】使用 MySQL GET_LOCK 分布式锁，确保多 worker 并发启动时
            # 只有一个 worker 执行数据初始化，避免 Duplicate entry 错误。
            # GET_LOCK 是会话级锁，即使不同 worker 也能正确互斥。
            # SQLite 不支持 GET_LOCK，跳过锁直接执行初始化
            # MySQL 使用 GET_LOCK 确保多 worker 并发安全
            lock_acquired = False
            try:
                result = db.execute(
                    text("SELECT GET_LOCK('gw2_init_lock', 30)")
                ).scalar()
                lock_acquired = result == 1
            except Exception as e:
                # SQLite 会走到这里，直接放行
                logger.info(f"跳过分布式锁（SQLite 模式或无锁支持）: {e}")
                lock_acquired = True

            if lock_acquired:
                logger.info("获取初始化锁成功，开始执行数据初始化")
                try:
                    # 统一数据初始化入口（包含所有数据初始化）
                    from app.data.init_all import initialize_all
                    from app.core.initialization import InitializationError

                    init_result = initialize_all(db)
                    logger.info(f"统一数据初始化完成: {init_result}")
                except InitializationError as e:
                    # 【强化】初始化失败立即终止启动
                    logger.critical("=" * 60)
                    logger.critical("数据初始化失败，启动终止")
                    logger.critical("=" * 60)
                    logger.critical(f"错误: {e}")
                    logger.critical(f"步骤: {e.step}")
                    logger.critical(f"类型: {e.error_type}")
                    logger.critical(f"建议: {e.suggestion}")
                    logger.critical("=" * 60)
                    # 释放锁后抛出异常，阻止 FastAPI 继续启动
                    try:
                        db.execute(text("SELECT RELEASE_LOCK('gw2_init_lock')"))
                    except Exception:
                        pass
                    raise RuntimeError(
                        f"数据初始化失败 [{e.error_type}] {e.step}: {e}\n"
                        f"建议: {e.suggestion}"
                    ) from e
                finally:
                    try:
                        db.execute(text("SELECT RELEASE_LOCK('gw2_init_lock')"))
                        logger.info("释放初始化锁")
                    except Exception:
                        pass
            else:
                logger.info("其他 worker 正在执行初始化，本 worker 跳过数据初始化")

    except RuntimeError:
        # 重新抛出启动终止异常
        raise
    except Exception as e:
        logger.error(f"初始化失败: {e}")
    logger.info("GW2日志系统启动完成")
    yield
    logger.info("GW2日志系统关闭中...")
    # 停止批量解析工作线程池
    stop_workers()
    # 停止任务调度器
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    description="GW2 WvW日志解析与评分系统后端API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[*settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Silent-Request"],
)

app.add_middleware(EnhancedMemoryMonitorMiddleware)

register_exception_handlers(app)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(logs_router, prefix=settings.API_PREFIX)
app.include_router(ai_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(game_data_router, prefix=settings.API_PREFIX)
app.include_router(professions_router, prefix=settings.API_PREFIX)

app.include_router(bdcode_router, prefix="/api")
app.include_router(attendance_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(monitoring_router, prefix=settings.API_PREFIX)
app.include_router(ei_analysis_router, prefix=settings.API_PREFIX)
app.include_router(dictionary_router, prefix=settings.API_PREFIX)
app.include_router(monitor_router, prefix=settings.API_PREFIX)
app.include_router(scoring_router, prefix=settings.API_PREFIX)
app.include_router(scoring_rules_router, prefix=settings.API_PREFIX)

app.include_router(fights_router, prefix=settings.API_PREFIX)
app.include_router(storage_router, prefix=settings.API_PREFIX)
app.include_router(builds_router, prefix=settings.API_PREFIX)
app.include_router(ref_data_router, prefix=settings.API_PREFIX)
app.include_router(skill_rotation_router, prefix=settings.API_PREFIX)
app.include_router(test_dps_report_router, prefix=settings.API_PREFIX)
app.include_router(memory_monitor_router)
app.include_router(notice_router, prefix=settings.API_PREFIX)
app.include_router(menus_router, prefix=settings.API_PREFIX)
app.include_router(initialization_router, prefix=settings.API_PREFIX)
app.include_router(config_router, prefix=settings.API_PREFIX)
app.include_router(dps_report_queue_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
