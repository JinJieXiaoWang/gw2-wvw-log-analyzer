# -*- coding: utf-8 -*-
"""AI深度分析引擎 - 集成服务层

功能：统一入口，协调5个分析器的调用，管理AI报告生成
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.ai_prompt_templates import AnalysisType
from app.models.system.ai_report import AIReport
from app.services.ai_analysis.analyzers import (
    BuildExecutionAnalyzer,
    CriticalMomentsAnalyzer,
    DeathAttributionAnalyzer,
    PersonalGrowthAnalyzer,
    SquadSynergyAnalyzer,
)
from app.services.system.ai_service import AIOrchestrator, get_ai_service
from app.utils.logger import logger


class AIAnalysisService:
    """AI深度分析集成服务"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = get_ai_service()
        self.orchestrator = AIOrchestrator()

    # ==================== 五大分析入口 ====================

    async def analyze_personal_growth(
        self,
        account: str,
        fight_count: int = 30,
    ) -> Dict[str, Any]:
        """个人战力成长档案分析"""
        analyzer = PersonalGrowthAnalyzer(self.db, self.orchestrator)
        result = await analyzer.analyze(account, fight_count)
        return result

    async def analyze_death_attribution(
        self,
        account: str,
        fight_id: Optional[int] = None,
        log_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """死亡归因与生存分析"""
        analyzer = DeathAttributionAnalyzer(self.db, self.orchestrator)
        result = await analyzer.analyze(account, fight_id, log_id)
        return result

    async def analyze_squad_synergy(
        self,
        fight_id: int,
        group_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """小队协同效能诊断"""
        analyzer = SquadSynergyAnalyzer(self.db, self.orchestrator)
        result = await analyzer.analyze(fight_id, group_id)
        return result

    async def analyze_build_execution(
        self,
        account: str,
        build_id: Optional[int] = None,
        fight_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build执行效能验证"""
        analyzer = BuildExecutionAnalyzer(self.db, self.orchestrator)
        result = await analyzer.analyze(account, build_id, fight_id)
        return result

    async def analyze_critical_moments(
        self,
        fight_id: int,
        account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """战斗关键片段复盘"""
        analyzer = CriticalMomentsAnalyzer(self.db, self.orchestrator)
        result = await analyzer.analyze(fight_id, account)
        return result

    # ==================== 报告管理 ====================

    def create_report(
        self,
        report_type: AnalysisType,
        target_type: str,
        target_id: str,
        content: Dict[str, Any],
        summary: Optional[str] = None,
        ai_score: Optional[int] = None,
    ) -> AIReport:
        """创建AI分析报告"""
        import json

        report = AIReport(
            report_type=report_type.value,
            target_type=target_type,
            target_id=str(target_id),
            content=json.dumps(content, ensure_ascii=False, default=str),
            summary=summary or content.get("summary", "") or "AI分析报告",
            ai_score=ai_score or content.get("overall_score") or content.get("execution_score") or content.get("survival_score") or content.get("synergy_score", 0),
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info(f"AI报告已创建: id={report.id}, type={report_type.value}")
        return report
