# -*- coding: utf-8 -*-
# 模块功能：批量解析任务执行服务
# 说明：实际解析执行逻辑（子进程隔离、线程池、错误处理）

import concurrent.futures
import multiprocessing
import sys
import time
from typing import Any, Dict, Optional

from app.config.database import SessionLocal
from app.services.zevtc import log_service
from app.services.zevtc.batch_memory_service import (
    SUBPROCESS_TIMEOUT,
    USE_SUBPROCESS_PARSE,
    _check_memory_and_wait,
    _deep_gc,
)
from app.services.zevtc.batch_parse_service import (
    BatchParseService,
    active_workers,
    active_workers_lock,
)
from app.constants.dict_values import ParseStatus
from app.utils.logger import logger

# 单日志解析超时（秒），防止损坏文件导致解析永久挂?
# 10 分钟：正常大文件解析可能需要几分钟，损坏文件则会被强制终止
SINGLE_LOG_PARSE_TIMEOUT = 600

# 复用?ThreadPoolExecutor，避免每次解析都创建/销毁线程池
_batch_parse_executor: Optional[concurrent.futures.ThreadPoolExecutor] = None


def _get_batch_executor() -> concurrent.futures.ThreadPoolExecutor:
    """获取复用?ThreadPoolExecutor（用于非子进程模式）"""
    global _batch_parse_executor
    if _batch_parse_executor is None:
        _batch_parse_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    return _batch_parse_executor


def shutdown_batch_executor() -> None:
    """关闭复用?ThreadPoolExecutor"""
    global _batch_parse_executor
    if _batch_parse_executor is not None:
        _batch_parse_executor.shutdown(wait=False)
        _batch_parse_executor = None


def _import_log_subprocess(log_id: int, file_path: str) -> Dict[str, Any]:
    """在独立子进程中执行日志导入（隔离内存，防?OOM 拖垮主进程）

    注意：此函数在子进程中运行，必须自包含所有导入口
    """
    try:
        # 子进程中重新初始化数据库连接
        from app.config.database import SessionLocal
        from app.services.zevtc.log_import_service import LogImportService

        db = SessionLocal()
        try:
            importer = LogImportService(db)
            result = importer.import_log(log_id, file_path)
            return result
        finally:
            db.expunge_all()
            db.close()
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {str(e)}"}


def _do_parse_single_log(task_id: int, log_id: int) -> None:
    """实际执行解析（主进程直接执行，含内存检查）"""
    from app.config.database import SessionLocal
    from app.services.zevtc.log_import_service import LogImportService

    db = SessionLocal()

    try:
        logger.info(f"[batch] 开始解析日志，任务ID: {task_id}，日志ID: {log_id}")

        BatchParseService.update_task_item_status(db, task_id, log_id, "processing")

        log = log_service.get_log_by_id(db, log_id)
        if not log:
            raise ValueError(f"日志不存在 {log_id}")

        log_service.update_parse_status(db, log_id, ParseStatus.PARSING)

        importer = LogImportService(db)
        result = importer.import_log(log_id, log.file_path)

        if not result.get("success"):
            raise Exception(result.get("error", "日志导入失败"))

        logger.info(f"[batch] log_id={log_id} 导入成功")
        BatchParseService.update_task_item_status(db, task_id, log_id, "completed")
        db.commit()

    except Exception:
        db.rollback()
        raise
    finally:
        db.expunge_all()
        db.close()


def _parse_worker(queue, log_id: int, file_path: str) -> None:
    """子进程工作函数（必须在模块级别定义，否则无法被 pickle）"""
    result = _import_log_subprocess(log_id, file_path)
    queue.put(result)


def _do_parse_single_log_subprocess(task_id: int, log_id: int, file_path: str) -> None:
    """使用子进程隔离执行解析，主进程只负责状态更新

    流程?
        1. 子进程执?import_log（独立内存空间）
        2. 子进程退出后内存完全释放
        3. 主进程根据返回结果更新数据库状态
    """
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        logger.info(f"[batch] 子进程解析开始，任务ID: {task_id}，日志ID: {log_id}")
        BatchParseService.update_task_item_status(db, task_id, log_id, "processing")
        log_service.update_parse_status(db, log_id, ParseStatus.PARSING)
        db.commit()
    finally:
        db.close()

    # 启动子进程执行解?
    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()

    proc = ctx.Process(target=_parse_worker, args=(queue, log_id, file_path))
    proc.start()
    proc.join(timeout=SUBPROCESS_TIMEOUT)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join()
        raise TimeoutError(f"子进程解析超时（{SUBPROCESS_TIMEOUT}秒）")

    if proc.exitcode != 0:
        # 尝试获取子进程错误输?
        error_detail = ""
        try:
            error_detail = queue.get(timeout=1)
        except Exception:
            pass
        raise RuntimeError(
            f"子进程异常退出，exitcode={proc.exitcode}"
            f"{(', 错误: ' + str(error_detail)) if error_detail else ''}"
        )

    try:
        result = queue.get(timeout=5)
    except Exception:
        raise RuntimeError("子进程未返回结果")

    if not result.get("success"):
        raise Exception(result.get("error", "日志导入失败"))

    logger.info(f"[batch] log_id={log_id} 子进程导入成功")

    # 更新状态
    db = SessionLocal()
    try:
        BatchParseService.update_task_item_status(db, task_id, log_id, "completed")
        db.commit()
    finally:
        db.close()


def parse_single_log_with_rate_limit(
    task_id: int, log_id: int, db_url: str = "", overwrite: bool = True
):
    """解析单个日志（在限流保护 + 超时保护 + 内存保护下执行）

    根据系统平台和配置，选择子进程隔离或线程执行?
    """
    # 解析前内存检?
    if not _check_memory_and_wait(f"parse_start_log_{log_id}"):
        _handle_parse_error(task_id, log_id, "系统内存不足，跳过解析", "oom_risk")
        with active_workers_lock:
            active_workers.discard((task_id, log_id))
        return

    try:
        # 查询文件路径（主进程查一次，避免子进程重复查询）
        db = SessionLocal()
        try:
            log = log_service.get_log_by_id(db, log_id)
            file_path = log.file_path if log else None
        finally:
            db.close()

        if not file_path:
            raise ValueError(f"日志不存在或文件路径为空: {log_id}")

        use_subprocess = USE_SUBPROCESS_PARSE and sys.platform != "win32"

        if use_subprocess:
            _do_parse_single_log_subprocess(task_id, log_id, file_path)
        else:
            # Windows 或不启用子进程时，使用线程池 + 超时
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
        # 解析完成后深度清理内存
        _deep_gc(f"parse_end_log_{log_id}")


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
        elif "日志不存在" in error_str or "正在解析" in error_str:
            error_code = "invalid_state"

        if error_code in ("parse_error", "invalid_state"):
            log_service.update_parse_status(db, log_id, ParseStatus.FAILED, error_str)
            BatchParseService.update_task_item_status(
                db, task_id, log_id, "failed", error_str, error_code
            )
            db.commit()
        else:
            should_retry = BatchParseService.mark_item_for_retry(
                db, task_id, log_id, error_str, error_code, retry_after
            )
            if not should_retry:
                log_service.update_parse_status(db, log_id, ParseStatus.FAILED, error_str)
                db.commit()
    except Exception as inner_e:
        logger.error(f"[batch] 更新失败状态也失败? {inner_e}")
    finally:
        db.close()
