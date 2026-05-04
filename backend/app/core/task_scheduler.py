# 模块功能：后台任务调度器
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：apscheduler

import asyncio
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config.database import SessionLocal
from app.config.settings import settings
from app.services.system.storage_service import (
    FileCleanupService,
    StorageMonitorService,
)
from app.utils.logger import logger

scheduler: Optional[AsyncIOScheduler] = None


async def scheduled_storage_monitor():
    # 功能：定时存储监控任务
    logger.info("执行定时存储监控...")
    try:
        db = SessionLocal()
        try:
            StorageMonitorService.record_monitor_data(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"定时存储监控失败: {e}", exc_info=True)


async def scheduled_cleanup():
    # 功能：定时清理任务
    if not settings.AUTO_CLEANUP_ENABLED:
        logger.info("自动清理已禁用，跳过")
        return

    logger.info("执行定时文件清理...")
    try:
        db = SessionLocal()
        try:
            # 先按天数清理
            age_result = FileCleanupService.cleanup_by_age(db, triggered_by="scheduled")
            logger.info(f"定时按天数清理结果: {age_result}")

            # 再检查是否需要按容量清理
            storage_result = FileCleanupService.cleanup_by_storage_limit(
                db, triggered_by="scheduled"
            )
            logger.info(f"定时按容量清理结果: {storage_result}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"定时清理失败: {e}", exc_info=True)


def init_scheduler():
    # 功能：初始化任务调度器
    global scheduler
    if scheduler is not None:
        logger.warning("调度器已初始化")
        return scheduler

    scheduler = AsyncIOScheduler()
    logger.info("初始化任务调度器")

    # 添加存储监控任务（每小时执行一次）
    scheduler.add_job(
        scheduled_storage_monitor,
        trigger=IntervalTrigger(hours=1),
        id="storage_monitor",
        name="存储监控",
        replace_existing=True,
    )
    logger.info("已添加存储监控任务（每小时执行）")

    # 添加自动清理任务
    cleanup_interval = settings.AUTO_CLEANUP_INTERVAL
    scheduler.add_job(
        scheduled_cleanup,
        trigger=IntervalTrigger(hours=cleanup_interval),
        id="auto_cleanup",
        name="自动文件清理",
        replace_existing=True,
    )
    logger.info(f"已添加自动清理任务（每 {cleanup_interval} 小时执行）")

    return scheduler


def start_scheduler():
    # 功能：启动调度器
    global scheduler
    if scheduler is None:
        scheduler = init_scheduler()

    if not scheduler.running:
        scheduler.start()
        logger.info("任务调度器已启动")


def stop_scheduler():
    # 功能：停止调度器
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("任务调度器已停止")
