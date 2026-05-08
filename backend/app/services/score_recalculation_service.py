# -*- coding: utf-8 -*-
# 模块功能：评分重算任务管理服务
# 说明：管理评分规则变更后的历史数据后台重算任务

import asyncio
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.scoring_rule_version import ScoringRuleVersion
from app.services.score_query_service import _clear_rules_cache
from app.services.scoring_rule_service import ScoringRuleService
from app.services.wvw.scoring_service import ScoringService
from app.utils.logger import logger


class ScoreRecalculationService:
    """评分重算任务管理服务"""

    @staticmethod
    def create_task(db: Session, filters: dict, description: str = "") -> ScoringRuleVersion:
        """创建重算任务，返回版本记录
        
        Args:
            db: 数据库会话
            filters: 重算筛选条件
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
        
        在后台线程池中执行同步数据库操作，避免阻塞主事件循环。
        
        Args:
            version_id: 版本记录ID
            filters: 重算筛选条件
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
            filters: 重算筛选条件
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
                    f"重算任务被拒绝: 已有任务在执行中 (version_id={running.id})"
                )
                return

            version.status = "processing"
            db.commit()

            # 统计总记录数
            from app.models.fight_stats import FightStats
            from app.models.fight import Fight

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

            logger.info(f"重算任务开始: version_id={version_id}, 共 {total} 条记录")

            # 【v4.0】评分改为查询时实时计算，不再存储在数据库中。
            # 重算任务变为"刷新评分规则缓存"，使新规则立即对所有查询生效。
            _clear_rules_cache()

            # 为了向前兼容，仍然遍历统计记录数并模拟进度
            batch_size = 1000
            total_batches = (total + batch_size - 1) // batch_size
            updated = 0

            for batch_idx in range(total_batches):
                updated = min((batch_idx + 1) * batch_size, total)
                version.updated_records = updated
                db.commit()
                # 小延迟模拟处理，让前端能看到进度
                import time
                time.sleep(0.1)

            version.status = "completed"
            version.completed_at = datetime.now()
            version.updated_records = total
            db.commit()
            logger.info(
                f"重算任务完成: version_id={version_id}, "
                f"评分规则缓存已刷新，共影响 {total} 条记录的后续查询"
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
            任务状态字典，或 None（记录不存在）
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
            True 如果有 processing 状态的任务
        """
        return (
            db.query(ScoringRuleVersion)
            .filter(ScoringRuleVersion.status == "processing")
            .first()
            is not None
        )
