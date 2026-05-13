# 模块功能：后台任务调度器
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：apscheduler

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config.database import SessionLocal
from app.config.settings import settings
from app.services.system.storage_service import (
    FileCleanupService,
    StorageMonitorService,
)
from app.utils.logger import logger


async def scheduled_sync_skill_icons():
    """定时同步技能图标（每周日凌晨 3:00）。"""
    logger.info("执行定时技能图标同步...")
    try:
        import subprocess
        import sys
        from pathlib import Path
        script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "sync_skill_icons.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode == 0:
            logger.info(f"技能图标同步成功:\n{result.stdout}")
        else:
            logger.error(f"技能图标同步失败:\n{result.stderr}")
    except Exception as e:
        logger.error(f"技能图标同步异常: {e}", exc_info=True)

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


async def scheduled_verify_permalinks():
    """定时抽样验证 dps.report permalink 有效性（每天执行）"""
    import random

    logger.info("执行 dps.report permalink 有效性巡检...")
    try:
        db = SessionLocal()
        try:
            from app.models.log.log import Log

            # 获取所有有 permalink 且标记为有效的记录
            logs = (
                db.query(Log)
                .filter(
                    Log.dps_report_permalink.isnot(None),
                    Log.dps_report_permalink_valid == 1,
                )
                .all()
            )

            if not logs:
                logger.info("没有需要验证的 permalink")
                return

            # 抽样验证（默认 10%）
            sample_rate = 0.1
            sample_size = max(1, int(len(logs) * sample_rate))
            sampled = random.sample(logs, min(sample_size, len(logs)))

            import requests

            invalid_count = 0
            for log in sampled:
                try:
                    resp = requests.head(
                        log.dps_report_permalink,
                        timeout=10,
                        allow_redirects=True,
                    )
                    if resp.status_code != 200:
                        log.dps_report_permalink_valid = 0
                        invalid_count += 1
                        logger.warning(
                            f"[permalink] 失效: log_id={log.id}, "
                            f"HTTP {resp.status_code}, {log.dps_report_permalink}"
                        )
                except Exception as e:
                    # 网络异常不直接标记为失效，避免误判
                    logger.warning(
                        f"[permalink] 验证异常: log_id={log.id}, 错误: {e}"
                    )

            db.commit()
            logger.info(
                f"[permalink] 巡检完成: 总计 {len(logs)} 个, "
                f"抽样 {len(sampled)} 个, 失效 {invalid_count} 个"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"permalink 巡检失败: {e}", exc_info=True)


async def scheduled_reset_stuck_parsing_logs():
    """定时扫描并重置卡住的解析中日志（每10分钟执行一次）"""
    logger.info("执行卡住解析日志扫描...")
    try:
        db = SessionLocal()
        try:
            from app.models.log.log import Log
            from app.services.zevtc import log_service

            # 超过30分钟仍处于 parsing 状态的视为卡住
            stuck_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)

            stuck_logs = (
                db.query(Log)
                .filter(
                    Log.parse_status == "parsing",
                    Log.parse_started_at.isnot(None),
                    Log.parse_started_at <= stuck_threshold,
                )
                .all()
            )

            reset_count = 0
            for log in stuck_logs:
                logger.warning(
                    f"发现卡住日志 log_id={log.id}, "
                    f"started_at={log.parse_started_at}, 自动重置为 failed"
                )
                log_service.update_parse_status(
                    db,
                    log.id,
                    "failed",
                    "解析任务超时或中断（超过30分钟），已由定时器自动重置",
                )
                reset_count += 1

            if reset_count > 0:
                logger.info(f"已重置 {reset_count} 个卡住日志为 failed 状态")
            else:
                logger.info("未发现卡住日志")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"扫描卡住日志失败: {e}", exc_info=True)


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

    # 添加技能图标同步任务（每周日凌晨 3:00）
    scheduler.add_job(
        scheduled_sync_skill_icons,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="sync_skill_icons",
        name="技能图标同步",
        replace_existing=True,
    )
    logger.info("已添加技能图标同步任务（每周日凌晨 3:00）")

    # 添加卡住解析日志扫描任务（每10分钟执行一次）
    scheduler.add_job(
        scheduled_reset_stuck_parsing_logs,
        trigger=IntervalTrigger(minutes=10),
        id="reset_stuck_parsing_logs",
        name="重置卡住解析日志",
        replace_existing=True,
    )
    logger.info("已添加卡住解析日志扫描任务（每10分钟执行）")

    # 添加 dps.report permalink 有效性巡检（每天凌晨 3:00）
    scheduler.add_job(
        scheduled_verify_permalinks,
        trigger=CronTrigger(hour=3, minute=0),
        id="verify_permalinks",
        name="验证 dps.report permalink 有效性",
        replace_existing=True,
    )
    logger.info("已添加 permalink 有效性巡检任务（每天凌晨 3:00）")

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
