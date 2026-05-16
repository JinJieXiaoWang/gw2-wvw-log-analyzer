# -*- coding: utf-8 -*-
"""文件清理服务模块"""
import os
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.log.log import Log
from app.utils.logger import logger


def cleanup_file(db: Session, log_id: int) -> Dict[str, Any]:
    """显式清理指定日志的源文件

    功能：删除已解析日志的源文件
    参数：log_id - 日志ID
    返回：成功返回{"success": True}，失败返回{"success": False, "error": 错误信息}

    说明：
    - 用户在确认解析数据正确后，可调用此方法删除源文件
    - 如果解析数据有误，用户可以保留源文件重新解析
    - 文件删除后，log.file_path 将被设置为 None
    """
    try:
        log = db.query(Log).filter(Log.id == log_id).first()
        if not log:
            return {"success": False, "error": f"日志不存在 {log_id}"}

        file_path = log.file_path
        if not file_path:
            return {"success": False, "error": "文件路径为空，可能已被删除"}

        if not os.path.exists(file_path):
            log.file_path = None
            db.commit()
            return {"success": True, "message": "文件不存在，已更新数据库记录"}

        os.remove(file_path)
        logger.info(f"已删除日志文? log_id={log_id}, path={file_path}")

        log.file_path = None
        db.commit()

        return {"success": True, "message": f"文件已删除 {file_path}"}

    except Exception as e:
        logger.error(f"清理文件失败 log_id={log_id}: {e}", exc_info=True)
        db.rollback()
        return {"success": False, "error": str(e)}


def cleanup_files_batch(log_ids: List[int]) -> Dict[str, Any]:
    """批量清理指定日志的源文件

    功能：批量删除多个日志的源文件
    参数：log_ids - 日志ID列表
    返回：{"success": True, "deleted_count": N, "failed_count": M, "errors": [...]}
    """
    db = SessionLocal()
    deleted_count = 0
    failed_count = 0
    errors = []

    try:
        for log_id in log_ids:
            try:
                log = db.query(Log).filter(Log.id == log_id).first()
                if not log:
                    errors.append(f"log_id={log_id}: 日志不存在")
                    failed_count += 1
                    continue

                file_path = log.file_path
                if not file_path:
                    errors.append(f"log_id={log_id}: 文件路径为空")
                    failed_count += 1
                    continue

                if not os.path.exists(file_path):
                    log.file_path = None
                    deleted_count += 1
                    continue

                os.remove(file_path)
                log.file_path = None
                deleted_count += 1
                logger.info(f"批量删除日志文件: log_id={log_id}")

            except Exception as e:
                errors.append(f"log_id={log_id}: {str(e)}")
                failed_count += 1

        db.commit()
        return {
            "success": failed_count == 0,
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"批量清理文件异常: {e}", exc_info=True)
        db.rollback()
        return {
            "success": False,
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "errors": errors + [str(e)],
        }
    finally:
        db.close()


def _delete_file(file_path: str):
    """内部方法：安全删除文件（私有方法，不建议外部调用）"""
    try:
        os.remove(file_path)
        logger.info(f"已删除解析文件 {file_path}")
    except Exception as e:
        logger.warning(f"删除文件失败 {file_path}: {e}")
