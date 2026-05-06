# -*- coding: utf-8 -*-
# 模块功能：FastAPI应用主入口
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI, uvicorn, contextlib

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config.settings import settings
from app.config.database import init_db, get_db_context
from app.services.auth_service import init_predefined_admin
import app.models  # 确保所有模型类注册到 Base.metadata
from app.services.build_data_initializer import BuildDataInitializer
from app.services.zevtc.batch_parse_service import start_workers, stop_workers
from app.core.task_scheduler import start_scheduler, stop_scheduler
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.monitor import router as monitor_router
from app.routers.logs import router as logs_router
from app.routers.fights import router as fights_router
from app.routers.ei_analysis import router as ei_analysis_router
from app.routers.attendance import router as attendance_router
from app.routers.ai import router as ai_router
from app.routers.dashboard import router as dashboard_router

from app.routers.scoring import router as scoring_router
from app.routers.scoring_rules import router as scoring_rules_router
from app.routers.game_data import router as game_data_router
from app.routers.bdcode import router as bdcode_router
from app.routers.dictionary import router as dictionary_router
from app.routers.settings import router as settings_router
from app.routers.monitoring import router as monitoring_router
from app.routers.storage import router as storage_router
from app.routers.builds import router as builds_router
from app.routers.test_dps_report import router as test_dps_report_router
from app.routers.memory_monitor import router as memory_monitor_router
from app.utils.logger import logger
from app.utils.exceptions import AppException
from app.utils.exception_handler import register_exception_handlers


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
            lock_acquired = False
            try:
                result = db.execute(text("SELECT GET_LOCK('gw2_init_lock', 30)")).scalar()
                lock_acquired = (result == 1)
            except Exception as e:
                logger.warning(f"获取初始化锁失败: {e}")

            if lock_acquired:
                logger.info("获取初始化锁成功，开始执行数据初始化")
                try:
                    init_predefined_admin(db)
                    logger.info("预置管理员账号初始化完成")

                    # 初始化字典数据
                    from app.database.dict_init import DictionaryDataInitializer

                    dict_init = DictionaryDataInitializer(db)
                    dict_result = dict_init.init_all_dictionaries()
                    logger.info(f"字典数据初始化完成: {dict_result}")

                    # 加载字典缓存
                    from app.utils.dict_utils import load_all_dictionaries

                    load_all_dictionaries(db)
                    logger.info("字典缓存加载完成")

                    # 初始化评分规则（如果表为空）
                    from app.services.scoring_rule_service import ScoringRuleService

                    scoring_service = ScoringRuleService(db)
                    scoring_init = scoring_service.init_default_rules_if_empty()
                    if scoring_init["initialized"]:
                        logger.info(f"评分规则初始化完成: {scoring_init}")
                    else:
                        logger.info(f"评分规则已存在，跳过初始化: {scoring_init}")

                    # 初始化 Build 图书馆数据（表为空时自动导入 GW2.txt）
                    build_init = BuildDataInitializer(db)
                    build_result = build_init.init_builds()
                    if build_result["initialized"]:
                        logger.info(f"Build 图书馆数据初始化完成: 导入 {build_result['count']} 条配置")
                    elif build_result["errors"]:
                        logger.warning(f"Build 图书馆数据初始化有警告: {build_result['errors']}")
                finally:
                    try:
                        db.execute(text("SELECT RELEASE_LOCK('gw2_init_lock')"))
                        logger.info("释放初始化锁")
                    except Exception:
                        pass
            else:
                logger.info("其他 worker 正在执行初始化，本 worker 跳过数据初始化")

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
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册增强版内存监控中间件（自动GC、内存超限告警、OOM预防）
from app.middleware.enhanced_memory_monitor import EnhancedMemoryMonitorMiddleware
app.add_middleware(EnhancedMemoryMonitorMiddleware)

register_exception_handlers(app)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(logs_router, prefix=settings.API_PREFIX)
app.include_router(ai_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(game_data_router, prefix=settings.API_PREFIX)

app.include_router(bdcode_router)
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
app.include_router(test_dps_report_router, prefix=settings.API_PREFIX)
app.include_router(memory_monitor_router)


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
