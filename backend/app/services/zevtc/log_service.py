# -*- coding: utf-8 -*-
# 模块功能：日志文件业务逻辑服务
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.log.batch_parse import BatchParseTaskItem
from app.models.log.ei_report import EiReport
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.models.log.log import Log
from app.models.log.zevtc_data import EiPhase, EiPlayer, EiSkillMap, EiTarget
from app.models.system.ai_report import AIReport
from app.schemas.log import LogCreate, LogUpdate
from app.utils.logger import logger


def get_log_by_id(db: Session, log_id: int) -> Optional[Log]:
    # 功能：根据ID获取日志
    # 参数：db - 数据库会话；log_id - 日志ID
    # 返回：日志对象或None
    return db.query(Log).filter(Log.id == log_id).first()


def get_logs(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    parse_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
) -> Tuple[List[Log], int]:
    # 功能：获取日志列表（支持筛选和分页）
    # 参数：db - 数据库会话；skip - 跳过数量；limit - 限制数量
    #       parse_status - 解析状态
    #       start_date - 开始日期；end_date - 结束日期
    #       search - 文件名模糊搜索
    # 返回：日志列表, 总数
    query = db.query(Log)

    if parse_status:
        query = query.filter(Log.parse_status == parse_status)
    if start_date:
        query = query.filter(Log.upload_time >= start_date)
    if end_date:
        query = query.filter(Log.upload_time <= end_date)
    if search:
        query = query.filter(Log.filename.ilike(f"%{search}%"))

    total = query.count()
    logs = query.order_by(Log.upload_time.desc()).offset(skip).limit(limit).all()
    return logs, total


def create_log(db: Session, log_data, uploaded_by: Optional[int] = None) -> Log:
    # 功能：创建日志记录
    # 参数：db - 数据库会话；log_data - 日志数据（字典或LogCreate）；uploaded_by - 上传者ID
    # 返回：创建的日志对象
    if isinstance(log_data, dict):
        # 从字典创建
        log = Log(**log_data, uploaded_by=uploaded_by)
        filename = log_data.get("filename", "unknown")
    else:
        # 从LogCreate创建
        log = Log(**log_data.model_dump(), uploaded_by=uploaded_by)
        filename = log_data.filename

    db.add(log)
    db.commit()
    db.refresh(log)
    logger.info(f"创建日志: {filename}")
    return log


def update_log(db: Session, log_id: int, log_update: LogUpdate) -> Optional[Log]:
    # 功能：更新日志
    # 参数：db - 数据库会话；log_id - 日志ID；log_update - 更新数据
    # 返回：更新后的日志对象或None
    log = get_log_by_id(db, log_id)
    if not log:
        return None

    update_data = log_update.model_dump(exclude_unset=True)
    if "parse_status" in update_data and update_data["parse_status"] == "completed":
        log.parsed_at = datetime.now()

    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    logger.info(f"更新日志: {log.filename}")
    return log


def delete_log(db: Session, log_id: int) -> bool:
    # 功能：删除日志（包含级联删除相关数据和文件）
    # 参数：db - 数据库会话；log_id - 日志ID
    # 返回：删除是否成功
    try:
        log = get_log_by_id(db, log_id)
        if not log:
            logger.warning(f"删除失败：日志ID {log_id} 不存在")
            return False

        logger.info(f"开始删除日志ID {log_id}: {log.filename}")

        # 1. 删除批量解析任务关联记录（必须最先删除，否则有外键约束）
        batch_item_count = db.query(BatchParseTaskItem).filter(
            BatchParseTaskItem.log_id == log_id
        ).delete()
        logger.info(f"删除了 {batch_item_count} 条批量解析任务关联记录")

        # 2. 查询EI报告记录，获取需要删除的物理文件路径
        ei_file_paths = []
        ei_reports = db.query(EiReport).filter(EiReport.log_id == log_id).all()
        for ei_report in ei_reports:
            for path_attr in ['log_data_path', 'graph_data_path', 'cr_data_path']:
                file_path = getattr(ei_report, path_attr, None)
                if file_path:
                    ei_file_paths.append(file_path)
        
        # 3. 删除 AI 报告（使用 target_type 和 target_id）
        ai_delete_count = db.query(AIReport).filter(
            AIReport.target_type == "log",
            AIReport.target_id == log_id
        ).delete()
        logger.info(f"删除了 {ai_delete_count} 条 AI 报告")

        # 4. 删除 EI 报告
        ei_delete_count = db.query(EiReport).filter(EiReport.log_id == log_id).delete()
        logger.info(f"删除了 {ei_delete_count} 条 EI 报告")

        # 5. 删除 EI 相关数据（使用 ON DELETE CASCADE 或手动删除）
        # EiPlayer, EiTarget, EiSkillMap, EiPhase
        ei_player_delete = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).delete()
        ei_target_delete = db.query(EiTarget).filter(EiTarget.log_id == log_id).delete()
        ei_skill_map_delete = db.query(EiSkillMap).filter(EiSkillMap.log_id == log_id).delete()
        ei_phase_delete = db.query(EiPhase).filter(EiPhase.log_id == log_id).delete()
        logger.info(f"删除了 EI 数据: player={ei_player_delete}, target={ei_target_delete}, skill={ei_skill_map_delete}, phase={ei_phase_delete}")

        # 6. 删除战斗统计数据
        # 先获取 fight_ids
        fight_ids = [f.id for f in db.query(Fight.id).filter(Fight.log_id == log_id).all()]
        if fight_ids:
            db.query(FightStats).filter(FightStats.fight_id.in_(fight_ids)).delete()
            logger.info(f"删除了战斗统计数据")

        # 7. 删除战斗记录
        fight_delete_count = db.query(Fight).filter(Fight.log_id == log_id).delete()
        logger.info(f"删除了 {fight_delete_count} 条战斗记录")

        # 8. 删除物理文件
        # 删除 EI 报告存储的大文件
        for file_path in ei_file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"删除了 EI 文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除 EI 文件失败: {file_path}, 错误: {str(e)}")

        # 删除日志主文件
        if log.file_path and os.path.exists(log.file_path):
            try:
                os.remove(log.file_path)
                logger.info(f"删除了日志文件: {log.file_path}")
            except Exception as e:
                logger.warning(f"删除日志文件失败: {log.file_path}, 错误: {str(e)}")
        
        # 同时检查上传目录中是否还有该文件的其他副本
        upload_dir = settings.UPLOAD_DIR or './uploads'
        if log.filename:
            alternate_path = os.path.join(upload_dir, log.filename)
            if os.path.exists(alternate_path) and alternate_path != log.file_path:
                try:
                    os.remove(alternate_path)
                    logger.info(f"删除了备用文件: {alternate_path}")
                except Exception as e:
                    logger.warning(f"删除备用文件失败: {alternate_path}, 错误: {str(e)}")

        # 9. 最后删除Log记录
        db.delete(log)
        db.commit()
        logger.info(f"成功删除日志: {log.filename}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"删除日志异常: {str(e)}")
        raise


def update_parse_status(
    db: Session, log_id: int, status: str, error_message: Optional[str] = None
) -> Optional[Log]:
    # 功能：更新解析状态
    # 参数：db - 数据库会话；log_id - 日志ID；status - 状态；error_message - 错误消息
    # 返回：更新的日志对象或None
    log = get_log_by_id(db, log_id)
    if not log:
        return None
    log.parse_status = status
    if error_message is not None:
        log.error_message = error_message
    if status == "parsing":
        log.parse_started_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(log)
    return log


def handle_upload_duplicate(
    db: Session, file_sha256: str, filename: str, file_path: str
) -> Optional[Log]:
    # 功能：处理重复上传
    # 参数：db - 数据库会话；file_sha256 - 文件SHA256哈希；filename - 文件名；file_path - 文件路径
    # 返回：已存在的日志对象或None
    # 检查是否已存在相同SHA256的日志
    existing_log = db.query(Log).filter(Log.file_sha256 == file_sha256).first()
    
    if existing_log:
        logger.info(f"检测到重复上传：{filename} (SHA256: {file_sha256})")
        return existing_log
    
    return None


def delete_log_entry(db: Session, log_id: int) -> bool:
    # 功能：删除日志记录（仅删除数据库记录，不删除文件）
    # 参数：db - 数据库会话；log_id - 日志ID
    # 返回：删除是否成功
    log = get_log_by_id(db, log_id)
    if not log:
        logger.warning(f"删除失败：日志ID {log_id} 不存在")
        return False
    
    db.delete(log)
    db.commit()
    logger.info(f"删除日志记录: {log.filename}")
    return True


async def parse_log_background(log_id: int, db_url: str, save_to_db: bool = True):
    # 功能：后台解析日志文件
    # 参数：log_id - 日志ID；db_url - 数据库连接URL；save_to_db - 是否保存到数据库
    # 返回：无
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.services.zevtc.log_import_service import LogImportService
    
    try:
        # 创建新的数据库连接（后台任务不能共享请求的连接）
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            log = get_log_by_id(db, log_id)
            if not log:
                logger.error(f"解析失败：日志ID {log_id} 不存在")
                return
            
            logger.info(f"开始后台解析日志: {log.filename}")
            
            if save_to_db:
                import_service = LogImportService(db)
                result = import_service.import_log(log_id, log.file_path)
                
                if result.get("success", False):
                    update_parse_status(db, log_id, "completed")
                    logger.info(f"后台解析完成: {log.filename}")
                    
                    # 解析成功后自动执行入库评分
                    try:
                        from app.services.wvw.scoring_service import ScoringService
                        fights = db.query(Fight).filter(Fight.log_id == log_id).all()
                        for fight in fights:
                            scoring_result = ScoringService.recalculate_fight_scores(
                                fight.id, db
                            )
                            logger.info(
                                f"日志 {log_id} 战斗 {fight.id} 评分完成: "
                                f"更新 {scoring_result.get('updated_count', 0)} 条记录"
                            )
                    except Exception as score_err:
                        logger.error(
                            f"日志 {log_id} 自动评分失败: {score_err}", exc_info=True
                        )
                else:
                    error_msg = result.get("error", "未知错误")
                    update_parse_status(db, log_id, "failed", error_msg)
                    logger.error(f"后台解析失败: {log.filename}, 错误: {error_msg}")
            else:
                logger.info(f"跳过数据库保存: {log.filename}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"后台解析异常: {str(e)}", exc_info=True)


def batch_delete_logs(db: Session, log_ids: list[int], user_id: Optional[int] = None) -> Dict[str, Any]:
    # 功能：批量删除日志
    # 参数：db - 数据库会话；log_ids - 日志ID列表；user_id - 用户ID
    # 返回：删除结果字典
    deleted_count = 0
    failed_ids = []
    
    for log_id in log_ids:
        try:
            if delete_log(db, log_id):
                deleted_count += 1
            else:
                failed_ids.append(log_id)
        except Exception as e:
            logger.error(f"批量删除日志ID {log_id} 失败: {str(e)}")
            failed_ids.append(log_id)
    
    logger.info(f"批量删除完成: 删除 {deleted_count} 个，失败 {len(failed_ids)} 个")
    return {
        "deleted_count": deleted_count,
        "failed_ids": failed_ids,
    }
