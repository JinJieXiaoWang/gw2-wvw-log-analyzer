# 模块功能：文件存储管理服务
# 作者：系统
# 创建日期：2026-04-30
# 依赖说明：SQLAlchemy, os, datetime

import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.log import Log
from app.models.storage import StorageCleanupRecord, StorageMonitorRecord
from app.utils.logger import logger


class FileCleanupService:
    # 功能：文件清理服务
    @staticmethod
    def _calculate_storage_usage() -> Tuple[int, int, int]:
        # 功能：计算存储使用情况
        # 返回：(总大小字节, 文件总数, 日志文件数)
        total_size = 0
        file_count = 0
        log_file_count = 0

        upload_dir = settings.UPLOAD_DIR
        if os.path.exists(upload_dir):
            for dirpath, _, filenames in os.walk(upload_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        size = os.path.getsize(filepath)
                        total_size += size
                        file_count += 1
                        if filename.endswith((".zevtc", ".evtc", ".zip")):
                            log_file_count += 1

        return total_size, file_count, log_file_count

    @staticmethod
    def _create_cleanup_record(
        db: Session, cleanup_type: str, triggered_by: Optional[str] = None
    ) -> StorageCleanupRecord:
        # 功能：创建清理记录
        record = StorageCleanupRecord(
            cleanup_type=cleanup_type, status="in_progress", triggered_by=triggered_by
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def _update_cleanup_record(
        db: Session,
        record_id: int,
        files_deleted: int,
        space_freed: float,
        status: str = "completed",
        error_message: Optional[str] = None,
    ):
        # 功能：更新清理记录
        record = (
            db.query(StorageCleanupRecord)
            .filter(StorageCleanupRecord.id == record_id)
            .first()
        )
        if record:
            record.files_deleted = files_deleted
            record.space_freed = space_freed
            record.status = status
            record.end_time = datetime.now()
            if error_message:
                record.error_message = error_message
            db.commit()

    @staticmethod
    def cleanup_by_age(
        db: Session, days: Optional[int] = None, triggered_by: Optional[str] = None
    ) -> Dict:
        # 功能：按文件保留天数清理
        if days is None:
            days = settings.FILE_RETENTION_DAYS

        record = FileCleanupService._create_cleanup_record(
            db, "age_based", triggered_by
        )
        logger.info(f"开始按保留天数清理文件，保留天数: {days}")

        cutoff_date = datetime.now() - timedelta(days=days)
        files_deleted = 0
        space_freed = 0

        try:
            # 查询需要清理的日志记录
            logs_to_cleanup = (
                db.query(Log)
                .filter(
                    and_(Log.upload_time < cutoff_date, Log.parse_status == "completed")
                )
                .all()
            )

            for log in logs_to_cleanup:
                # 删除物理文件
                if log.file_path and os.path.exists(log.file_path):
                    try:
                        file_size = os.path.getsize(log.file_path)
                        os.remove(log.file_path)
                        space_freed += file_size
                        logger.info(f"已删除文件: {log.file_path}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {log.file_path}: {e}")

                # 删除数据库记录（级联删除相关数据）
                from app.services.zevtc.log_service import delete_log

                if delete_log(db, log.id):
                    files_deleted += 1

            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "completed"
            )
            logger.info(
                f"按天数清理完成，删除文件数: {files_deleted}，释放空间: {space_freed} 字节"
            )

            return {
                "success": True,
                "files_deleted": files_deleted,
                "space_freed": space_freed,
                "record_id": record.id,
            }

        except Exception as e:
            logger.error(f"按天数清理失败: {e}", exc_info=True)
            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "failed", str(e)
            )
            return {"success": False, "error": str(e), "record_id": record.id}

    @staticmethod
    def cleanup_by_storage_limit(
        db: Session, max_size: Optional[int] = None, triggered_by: Optional[str] = None
    ) -> Dict:
        # 功能：按存储容量限制清理
        if max_size is None:
            max_size = settings.MAX_STORAGE_SIZE

        record = FileCleanupService._create_cleanup_record(
            db, "storage_limit", triggered_by
        )
        logger.info(f"开始按存储容量限制清理，最大容量: {max_size} 字节")

        total_size, _, _ = FileCleanupService._calculate_storage_usage()
        if total_size <= max_size:
            FileCleanupService._update_cleanup_record(db, record.id, 0, 0, "completed")
            logger.info("当前存储使用量在限制范围内，无需清理")
            return {
                "success": True,
                "files_deleted": 0,
                "space_freed": 0,
                "record_id": record.id,
                "message": "存储使用量在限制范围内",
            }

        files_deleted = 0
        space_freed = 0
        target_size = max_size * 0.9  # 清理到限制的90%

        try:
            # 从最旧的已解析日志开始清理
            logs_to_cleanup = (
                db.query(Log)
                .filter(Log.parse_status == "completed")
                .order_by(Log.upload_time)
                .all()
            )

            for log in logs_to_cleanup:
                if total_size - space_freed <= target_size:
                    break

                # 删除物理文件
                if log.file_path and os.path.exists(log.file_path):
                    try:
                        file_size = os.path.getsize(log.file_path)
                        os.remove(log.file_path)
                        space_freed += file_size
                        logger.info(f"已删除文件: {log.file_path}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {log.file_path}: {e}")
                        continue

                # 删除数据库记录
                from app.services.zevtc.log_service import delete_log

                if delete_log(db, log.id):
                    files_deleted += 1

            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "completed"
            )
            logger.info(
                f"按容量限制清理完成，删除文件数: {files_deleted}，释放空间: {space_freed} 字节"
            )

            return {
                "success": True,
                "files_deleted": files_deleted,
                "space_freed": space_freed,
                "record_id": record.id,
            }

        except Exception as e:
            logger.error(f"按容量限制清理失败: {e}", exc_info=True)
            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "failed", str(e)
            )
            return {"success": False, "error": str(e), "record_id": record.id}

    @staticmethod
    def cleanup_parsed_files(db: Session, triggered_by: Optional[str] = None) -> Dict:
        # 功能：清理已解析的日志文件（保留数据库数据）
        record = FileCleanupService._create_cleanup_record(
            db, "parsed_only", triggered_by
        )
        logger.info("开始清理已解析日志的原始文件")

        files_deleted = 0
        space_freed = 0

        try:
            logs_to_cleanup = (
                db.query(Log)
                .filter(
                    and_(Log.parse_status == "completed", Log.file_path.isnot(None))
                )
                .all()
            )

            for log in logs_to_cleanup:
                if log.file_path and os.path.exists(log.file_path):
                    try:
                        file_size = os.path.getsize(log.file_path)
                        os.remove(log.file_path)
                        log.file_path = None
                        space_freed += file_size
                        files_deleted += 1
                        logger.info(f"已删除原始文件: {log.filename}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {log.file_path}: {e}")

            db.commit()
            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "completed"
            )
            logger.info(
                f"清理已解析文件完成，删除文件数: {files_deleted}，释放空间: {space_freed} 字节"
            )

            return {
                "success": True,
                "files_deleted": files_deleted,
                "space_freed": space_freed,
                "record_id": record.id,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"清理已解析文件失败: {e}", exc_info=True)
            FileCleanupService._update_cleanup_record(
                db, record.id, files_deleted, space_freed, "failed", str(e)
            )
            return {"success": False, "error": str(e), "record_id": record.id}

    @staticmethod
    def get_cleanup_records(
        db: Session, skip: int = 0, limit: int = 50
    ) -> Tuple[List[StorageCleanupRecord], int]:
        # 功能：获取清理记录
        query = db.query(StorageCleanupRecord)
        total = query.count()
        records = (
            query.order_by(desc(StorageCleanupRecord.start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total


class StorageMonitorService:
    # 功能：存储监控服务
    @staticmethod
    def get_storage_status(db: Session) -> Dict:
        # 功能：获取当前存储状态
        total_size, file_count, log_file_count = (
            FileCleanupService._calculate_storage_usage()
        )

        max_size = settings.MAX_STORAGE_SIZE
        usage_percent = (total_size / max_size) * 100 if max_size > 0 else 0
        warning_triggered = usage_percent >= settings.STORAGE_WARNING_THRESHOLD

        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "max_size_bytes": max_size,
            "max_size_gb": round(max_size / (1024 * 1024 * 1024), 2),
            "usage_percent": round(usage_percent, 2),
            "file_count": file_count,
            "log_file_count": log_file_count,
            "warning_triggered": warning_triggered,
            "warning_threshold": settings.STORAGE_WARNING_THRESHOLD,
        }

    @staticmethod
    def record_monitor_data(db: Session) -> StorageMonitorRecord:
        # 功能：记录监控数据
        status = StorageMonitorService.get_storage_status(db)
        record = StorageMonitorRecord(
            total_size=status["total_size_bytes"],
            file_count=status["file_count"],
            log_file_count=status["log_file_count"],
            warning_triggered=status["warning_triggered"],
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(
            f"存储监控数据已记录: 使用 {status['total_size_gb']}GB / {status['max_size_gb']}GB"
        )
        return record

    @staticmethod
    def get_monitor_records(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Tuple[List[StorageMonitorRecord], int]:
        # 功能：获取监控记录
        query = db.query(StorageMonitorRecord)

        if start_time:
            query = query.filter(StorageMonitorRecord.record_time >= start_time)
        if end_time:
            query = query.filter(StorageMonitorRecord.record_time <= end_time)

        total = query.count()
        records = (
            query.order_by(desc(StorageMonitorRecord.record_time))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total
