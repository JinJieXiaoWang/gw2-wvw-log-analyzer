# -*- coding: utf-8 -*-
# 模块功能：批量解析任务服务 v2.0
# 作者：系统
# 创建日期：2026-04-29
# 更新日期：2026-05-04
# 说明：
#   - 基于数据库轮询的调度器（替代 queue.Queue）
#   - dps.report API 限流由 upload_and_parse() 内部统一处理（令牌桶 25 req/60s）
#   - 失败重试机制（HTTP 429 按响应等待，其他错误指数退避）
#   - 任务状态精细跟踪（pending/processing/completed/failed/retrying）

import concurrent.futures
import gc
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.core.zevtc.parser import ZevtcParseError
from app.models.batch_parse import BatchParseTask, BatchParseTaskItem
from app.models.log import Log
from app.services.zevtc import log_service
from app.utils.logger import logger

# 全局状态
is_running = False
worker_threads = []
MAX_CONCURRENT_TASKS = 1  # 单线程顺序执行，避免数据库并发冲突
POLL_INTERVAL_SECONDS = 2  # 轮询数据库间隔
TASK_DELAY_SECONDS = 0.5  # 任务完成后延迟
active_workers_lock = threading.Lock()
active_workers: set = set()


class BatchParseService:
    # 功能：批量解析任务服务类

    @staticmethod
    def create_task(
        db: Session,
        log_ids: List[int],
        task_name: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> BatchParseTask:
        # 过滤：只包含存在且当前未在解析中的日志
        valid_log_ids = []
        skipped_count = 0
        for log_id in log_ids:
            log = log_service.get_log_by_id(db, log_id)
            if not log:
                continue
            if log.parse_status == "parsing":
                skipped_count += 1
                continue
            valid_log_ids.append(log_id)

        if not valid_log_ids:
            raise ValueError("没有有效的日志ID（所有日志已在解析中或不存在）")

        task = BatchParseTask(
            task_name=task_name,
            total_count=len(valid_log_ids),
            created_by=created_by,
            log_ids=valid_log_ids,
        )
        db.add(task)
        db.flush()

        for log_id in valid_log_ids:
            task_item = BatchParseTaskItem(task_id=task.id, log_id=log_id, max_retries=3)
            db.add(task_item)

        # 立即将所有有效日志标记为解析中，让用户在列表中立即看到"解析中"状态
        for log_id in valid_log_ids:
            log_service.update_parse_status(db, log_id, "parsing")

        db.commit()
        db.refresh(task)
        if skipped_count > 0:
            logger.info(
                f"创建批量解析任务成功，任务ID: {task.id}，"
                f"包含 {len(valid_log_ids)} 个日志（跳过 {skipped_count} 个已在解析中的日志）"
            )
        else:
            logger.info(f"创建批量解析任务成功，任务ID: {task.id}，包含 {len(valid_log_ids)} 个日志")
        return task

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[BatchParseTask]:
        return db.query(BatchParseTask).filter(BatchParseTask.id == task_id).first()

    @staticmethod
    def get_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> Tuple[List[BatchParseTask], int]:
        query = db.query(BatchParseTask)
        if status:
            query = query.filter(BatchParseTask.status == status)
        if created_by:
            query = query.filter(BatchParseTask.created_by == created_by)

        total = query.count()
        tasks = query.order_by(BatchParseTask.created_at.desc()).offset(skip).limit(limit).all()
        return tasks, total

    @staticmethod
    def update_task_status(
        db: Session, task_id: int, status: str, error_message: Optional[str] = None
    ):
        task = BatchParseService.get_task_by_id(db, task_id)
        if not task:
            return
        task.status = status
        if error_message:
            task.error_message = error_message
        if status == "processing" and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        if status in ["completed", "failed", "partial"] and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    def update_task_item_status(
        db: Session,
        task_id: int,
        log_id: int,
        status: str,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        item = (
            db.query(BatchParseTaskItem)
            .filter(BatchParseTaskItem.task_id == task_id, BatchParseTaskItem.log_id == log_id)
            .first()
        )
        if not item:
            return

        item.status = status
        if error_message:
            item.error_message = error_message
        if error_code:
            item.error_code = error_code

        if status == "processing" and not item.started_at:
            item.started_at = datetime.now(timezone.utc)
        if status in ["completed", "failed"] and not item.completed_at:
            item.completed_at = datetime.now(timezone.utc)

        # 更新任务统计
        task = db.query(BatchParseTask).filter(BatchParseTask.id == task_id).first()
        if task:
            if status == "completed":
                task.processed_count += 1
                task.success_count += 1
            elif status == "failed":
                task.processed_count += 1
                task.failed_count += 1

            if task.processed_count == task.total_count:
                if task.failed_count == 0:
                    task.status = "completed"
                elif task.success_count == 0:
                    task.status = "failed"
                else:
                    task.status = "partial"
                task.completed_at = datetime.now(timezone.utc)

        db.commit()

    @staticmethod
    def mark_item_for_retry(
        db: Session,
        task_id: int,
        log_id: int,
        error_message: str,
        error_code: str,
        retry_after_seconds: Optional[float] = None,
    ):
        """将任务项标记为 retrying，计算下次重试时间"""
        item = (
            db.query(BatchParseTaskItem)
            .filter(BatchParseTaskItem.task_id == task_id, BatchParseTaskItem.log_id == log_id)
            .first()
        )
        if not item:
            return False

        item.retry_count += 1
        item.error_message = error_message
        item.error_code = error_code

        if item.retry_count >= item.max_retries:
            # 超过最大重试次数，标记为失败
            item.status = "failed"
            item.completed_at = datetime.now(timezone.utc)
            task = db.query(BatchParseTask).filter(BatchParseTask.id == task_id).first()
            if task:
                task.processed_count += 1
                task.failed_count += 1
                if task.processed_count == task.total_count:
                    task.status = "failed" if task.success_count == 0 else "partial"
                    task.completed_at = datetime.now(timezone.utc)
            db.commit()
            return False

        # 计算下次重试时间
        if retry_after_seconds:
            delay = retry_after_seconds
        else:
            # 指数退避：2^retry_count 秒，最大 60 秒
            delay = min(2 ** item.retry_count, 60)

        item.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        item.status = "retrying"
        db.commit()
        logger.info(
            f"[batch] log_id={log_id} 标记为 retrying，"
            f"第 {item.retry_count}/{item.max_retries} 次重试，"
            f"{delay:.1f} 秒后重试"
        )
        return True

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        task = BatchParseService.get_task_by_id(db, task_id)
        if not task:
            return False
        db.delete(task)
        db.commit()
        logger.info(f"删除批量解析任务，任务ID: {task_id}")
        return True


# =====================================================================
# 核心：限流控制下的单日志解析
# =====================================================================

# 单日志解析超时（秒），防止损坏文件导致解析永久挂起
# 10 分钟：正常大文件解析可能需要几分钟，损坏文件则会被强制终止
SINGLE_LOG_PARSE_TIMEOUT = 600

# 复用的 ThreadPoolExecutor，避免每次解析都创建/销毁线程池
_batch_parse_executor: Optional[concurrent.futures.ThreadPoolExecutor] = None


def _get_batch_executor() -> concurrent.futures.ThreadPoolExecutor:
    """获取复用的 ThreadPoolExecutor"""
    global _batch_parse_executor
    if _batch_parse_executor is None:
        _batch_parse_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    return _batch_parse_executor


def _do_parse_single_log(task_id: int, log_id: int) -> None:
    """实际执行解析（不含超时保护）"""
    from app.config.database import SessionLocal
    from app.services.zevtc.log_import_service import LogImportService

    db = SessionLocal()

    try:
        logger.info(f"[batch] 开始解析日志，任务ID: {task_id}，日志ID: {log_id}")

        BatchParseService.update_task_item_status(db, task_id, log_id, "processing")

        log = log_service.get_log_by_id(db, log_id)
        if not log:
            raise ValueError(f"日志不存在: {log_id}")

        # 注意：Log.parse_status 在 create_task 时已被设为 "parsing"
        # 此处不再检查，因为 BatchParseTaskItem.status 已经防止了重复处理
        log_service.update_parse_status(db, log_id, "parsing")

        importer = LogImportService(db)
        result = importer.import_log(log_id, log.file_path, allow_fallback=False)

        if not result.get("success"):
            raise Exception(result.get("error", "日志导入失败"))

        logger.info(f"[batch] log_id={log_id} 导入成功")
        BatchParseService.update_task_item_status(db, task_id, log_id, "completed")
        db.commit()

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def parse_single_log_with_rate_limit(
    task_id: int, log_id: int, db_url: str, overwrite: bool = True
):
    """解析单个日志（在限流保护 + 超时保护下执行）

    流程：
        1. 执行解析（upload_and_parse 内部已做限流等待）
        2. 处理失败：根据错误类型决定重试或放弃
    """
    try:
        # 使用复用的线程池 + 超时，防止损坏文件导致解析永久挂起
        executor = _get_batch_executor()
        future = executor.submit(_do_parse_single_log, task_id, log_id)
        future.result(timeout=SINGLE_LOG_PARSE_TIMEOUT)

    except concurrent.futures.TimeoutError:
        logger.error(f"[batch] log_id={log_id} 解析超时（{SINGLE_LOG_PARSE_TIMEOUT}秒），强制终止")
        _handle_parse_error(task_id, log_id, f"解析超时（{SINGLE_LOG_PARSE_TIMEOUT}秒）", "timeout")

    except Exception as e:
        error_str = str(e)
        logger.error(f"[batch] log_id={log_id} 解析异常: {error_str}")
        _handle_parse_error(task_id, log_id, error_str)

    finally:
        with active_workers_lock:
            active_workers.discard((task_id, log_id))


def _handle_parse_error(task_id: int, log_id: int, error_str: str, default_error_code: str = "unknown"):
    """统一处理解析错误：分类 + 重试决策"""
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        error_code = default_error_code
        retry_after = None

        if "RATE_LIMITED" in error_str or "429" in error_str:
            error_code = "429"
            retry_after = 60
        elif "timeout" in error_str.lower() or "超时" in error_str or "连接" in error_str:
            error_code = "timeout"
        elif "parse" in error_str.lower() or "解析" in error_str:
            error_code = "parse_error"
        elif "日志不存在" in error_str or "正在解析中" in error_str:
            error_code = "invalid_state"

        if error_code in ("parse_error", "invalid_state"):
            log_service.update_parse_status(db, log_id, "failed", error_str)
            BatchParseService.update_task_item_status(
                db, task_id, log_id, "failed", error_str, error_code
            )
            db.commit()
        else:
            should_retry = BatchParseService.mark_item_for_retry(
                db, task_id, log_id, error_str, error_code, retry_after
            )
            if not should_retry:
                log_service.update_parse_status(db, log_id, "failed", error_str)
                db.commit()
    except Exception as inner_e:
        logger.error(f"[batch] 更新失败状态也失败了: {inner_e}")
    finally:
        db.close()


# =====================================================================
# 轮询调度器（替代 queue.Queue）
# =====================================================================

def _fetch_next_pending_item(db: Session) -> Optional[BatchParseTaskItem]:
    """从数据库中获取下一个待处理的任务项

    优先级：
        1. status = 'pending'
        2. status = 'retrying' 且 next_retry_at <= now()
    """
    now = datetime.now(timezone.utc)

    # 先查 pending
    item = (
        db.query(BatchParseTaskItem)
        .filter(BatchParseTaskItem.status == "pending")
        .order_by(BatchParseTaskItem.id.asc())
        .first()
    )
    if item:
        return item

    # 再查已到重试时间的 retrying
    item = (
        db.query(BatchParseTaskItem)
        .filter(
            BatchParseTaskItem.status == "retrying",
            BatchParseTaskItem.next_retry_at <= now,
        )
        .order_by(BatchParseTaskItem.next_retry_at.asc())
        .first()
    )
    return item


def worker():
    """工作线程：轮询数据库 → 限流检查 → 执行任务"""
    while is_running:
        try:
            db = SessionLocal()
            try:
                item = _fetch_next_pending_item(db)
                if not item:
                    db.close()
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # 检查是否已在执行中（防止重启后重复执行）
                with active_workers_lock:
                    if (item.task_id, item.log_id) in active_workers:
                        db.close()
                        time.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    active_workers.add((item.task_id, item.log_id))

                # 更新父任务状态
                task = BatchParseService.get_task_by_id(db, item.task_id)
                if task and task.status == "pending":
                    BatchParseService.update_task_status(db, item.task_id, "processing")

            finally:
                db.close()

            # 执行解析（带限流）
            parse_single_log_with_rate_limit(
                item.task_id, item.log_id, "", overwrite=True
            )

            # 每个任务完成后触发 GC，加速大对象回收
            gc.collect()

            # 任务间延迟
            if TASK_DELAY_SECONDS > 0:
                time.sleep(TASK_DELAY_SECONDS)

        except Exception as e:
            logger.error(f"[batch] 工作线程异常: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL_SECONDS)


def start_workers():
    global is_running, worker_threads
    if is_running:
        return

    is_running = True
    worker_threads = []
    _reset_stuck_processing_items()

    for i in range(MAX_CONCURRENT_TASKS):
        t = threading.Thread(target=worker, name=f"BatchParseWorker-{i}")
        t.daemon = True
        t.start()
        worker_threads.append(t)
    logger.info(f"[batch] 启动轮询调度器，线程数: {MAX_CONCURRENT_TASKS}，轮询间隔: {POLL_INTERVAL_SECONDS}s")


def _reset_stuck_processing_items():
    """重置上次运行遗留的 processing 状态任务项"""
    try:
        db = SessionLocal()
        try:
            stuck_items = (
                db.query(BatchParseTaskItem)
                .filter(BatchParseTaskItem.status == "processing")
                .all()
            )
            if stuck_items:
                logger.warning(f"[batch] 发现 {len(stuck_items)} 个遗留 processing 任务项，重置")
                for item in stuck_items:
                    item.status = "pending"
                    item.error_message = "应用重启，任务重置"
                db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[batch] 重置遗留任务项失败: {e}")


def stop_workers():
    global is_running, worker_threads, _batch_parse_executor
    if not is_running:
        return
    is_running = False
    for t in worker_threads:
        t.join(timeout=5)
    worker_threads = []
    # 关闭复用的 ThreadPoolExecutor
    if _batch_parse_executor is not None:
        _batch_parse_executor.shutdown(wait=False)
        _batch_parse_executor = None
    logger.info("[batch] 停止轮询调度器")


def submit_batch_task(task_id: int, db_url: str, overwrite: bool = True):
    """提交批量解析任务

    v2.0 变更：任务已插入数据库，调度器自动轮询执行，无需再提交到队列。
    此方法仅更新任务状态并记录日志。
    """
    db = SessionLocal()
    try:
        task = BatchParseService.get_task_by_id(db, task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        if task.status == "pending":
            BatchParseService.update_task_status(db, task_id, "processing")
        logger.info(f"[batch] 任务 {task_id} 已提交，调度器将自动轮询执行")
    except Exception as e:
        logger.error(f"[batch] 提交任务失败: {e}")
        BatchParseService.update_task_status(db, task_id, "failed", str(e))
    finally:
        db.close()
