# -*- coding: utf-8 -*-
# 模块功能：评分重算任务管理服务
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-09
# 说明：管理评分规则变更后的历史数据后台重算任务

import asyncio
from datetime import datetime
from typing import Dict, Optional

from app.config.database import SessionLocal
from app.models.scoring.scoring_rule_version import ScoringRuleVersion
from app.services.scoring.score_query_service import _clear_rules_cache
from app.services.scoring.scoring_rule_service import ScoringRuleService
from app.utils.logger import logger
from sqlalchemy import func
from sqlalchemy.orm import Session


class ScoreRecalculationService:
    """评分重算任务管理服务"""

    @staticmethod
    def create_task(db: Session, filters: dict, description: str = "") -> ScoringRuleVersion:
        """创建重算任务，返回版本记录
        
        Args:
            db: 数据库会话
            filters: 重算筛选条件，格式为 {"field": "value"}
            description: 任务描述
            
        Returns:
            新创建的版本记录
        """
        service = ScoringRuleService(db)
        version = service.bump_version(description)
        return version

    @staticmethod
    async def execute_recalculation_async(version_id: int, filters: dict):
        """异步执行重算任务
        
        在后台线程池中执行同步数据库操作，避免阻塞主事件循环
        
        Args:
            version_id: 版本记录ID
            filters: 重算筛选条件，格式为 {"field": "value"}
        
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            ScoreRecalculationService._execute_recalculation_sync,
            version_id,
            filters,
        )

    @staticmethod
    def _execute_recalculation_sync(version_id: int, filters: dict):
        """同步执行重算任务（在线程池中运行）
        
        Args:
            version_id: 版本记录ID
            filters: 重算筛选条件，格式为 {"field": "value"}
        
        """
        db = SessionLocal()
        version: Optional[ScoringRuleVersion] = None

        try:
            version = db.query(ScoringRuleVersion).get(version_id)
            if not version:
                logger.error(f"重算任务失败: 版本记录 {version_id} 不存在")
                return

            # 并发控制：检查是否已有任务在执行中
            running = (
                db.query(ScoringRuleVersion)
                .filter(ScoringRuleVersion.status == "processing")
                .first()
            )
            if running and running.id != version_id:
                version.status = "failed"
                db.commit()
                logger.warning(
                    f"重算任务被拒? 已有任务在执行中 (version_id={running.id})"
                )
                return

            version.status = "processing"
            db.commit()

            # 统计总记录数
            from app.models.log.fight import Fight
            from app.models.log.fight_stats import FightStats

            query = db.query(FightStats)
            if filters.get("fight_ids"):
                query = query.filter(FightStats.fight_id.in_(filters["fight_ids"]))
            if filters.get("professions"):
                query = query.filter(FightStats.profession.in_(filters["professions"]))
            if filters.get("account_names"):
                query = query.filter(FightStats.account.in_(filters["account_names"]))
            if filters.get("date_from") or filters.get("date_to"):
                query = query.join(Fight, FightStats.fight_id == Fight.id)
                if filters.get("date_from"):
                    query = query.filter(
                        func.date(Fight.start_time) >= filters["date_from"]
                    )
                if filters.get("date_to"):
                    query = query.filter(
                        func.date(Fight.start_time) <= filters["date_to"]
                    )

            total = query.count()
            version.total_records = total
            db.commit()

            if total == 0:
                version.status = "completed"
                version.completed_at = datetime.now()
                db.commit()
                logger.info(f"重算任务完成: version_id={version_id}, 无匹配记录")
                return

            logger.info(f"重算任务开始 version_id={version_id}, 共 {total} 条记录")

            # 执行真正的评分重算
            from app.services.wvw.scoring_service import ScoringService
            updated = ScoringService.recalculate_scores_by_filters(
                db=db,
                filters=filters,
                version=version.version,
                batch_size=1000,
                progress_callback=None
            )
            logger.info(f"重算任务完成: version_id={version_id}, 更新 {updated.get('updated_count', 0)} 条记录")

            # 清除规则缓存，确保后续查询使用新规则
            _clear_rules_cache()

            version.status = "completed"
            version.completed_at = datetime.now()
            version.updated_records = updated.get('updated_count', 0)
            db.commit()
            logger.info(
                f"重算任务完成: version_id={version_id}, "
                f"已更?{version.updated_records} 条记录的评分"
            )

        except Exception as e:
            if version is not None:
                try:
                    version.status = "failed"
                    db.commit()
                except Exception:
                    pass
            logger.error(f"重算任务失败: version_id={version_id}, error={e}", exc_info=True)
        finally:
            db.close()

    @staticmethod
    def get_task_status(db: Session, version_id: int) -> Optional[Dict]:
        """获取任务进度
        
        Args:
            db: 数据库会话
            version_id: 版本记录ID
            
        Returns:
            任务状态字典，或 None 如果记录不存在
        """
        version = db.query(ScoringRuleVersion).get(version_id)
        if not version:
            return None

        progress = 0.0
        if version.total_records > 0:
            progress = round(version.updated_records / version.total_records * 100, 2)

        return {
            "version_id": version.id,
            "version": version.version,
            "status": version.status,
            "total_records": version.total_records,
            "updated_records": version.updated_records,
            "failed_records": version.failed_records,
            "progress_percent": progress,
            "created_at": version.created_at,
            "completed_at": version.completed_at,
        }

    @staticmethod
    def is_task_running(db: Session) -> bool:
        """检查是否有重算任务在执行中
        
        Args:
            db: 数据库会话
            
        Returns:
            True 如果有 processing 状态的任务，否则 False
        """
        return (
            db.query(ScoringRuleVersion)
            .filter(ScoringRuleVersion.status == "processing")
            .first()
            is not None
        )

    @staticmethod
    def start_recalculation_task(version_id: int, filters: dict) -> None:
        """启动后台重算任务（自动选择 APScheduler 或 asyncio）

        Args:
            version_id: 版本记录ID
            filters: 重算筛选条件，格式为 {"field": "value"}
        
        """
        from app.core.task_scheduler import scheduler

        if scheduler and scheduler.running:
            scheduler.add_job(
                ScoreRecalculationService.execute_recalculation_async,
                args=[version_id, filters],
                id=f"recalc_{version_id}",
                replace_existing=False,
            )
        else:
            import asyncio
            asyncio.create_task(
                ScoreRecalculationService.execute_recalculation_async(version_id, filters)
            )
