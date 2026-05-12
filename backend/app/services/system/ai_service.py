# -*- coding: utf-8 -*-
# 模块功能：AI分析业务总服?- 增强?
# 作者：帅妹妹丶.8297
# 创建日期?2026-05-01
# 依赖说明：SQLAlchemy, json, LLM集成
# 注意：Fight、Member、Build模型已被移除，相关功能已停用

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.ai_config import ai_config
from app.core.ai_model_client import AIResponse, get_ai_service
from app.core.ai_prompt_templates import (
    AnalysisType,
    PromptTemplateRegistry,
    ResponseAdjuster,
    ResponseOptimizer,
)
from app.core.ai_quality_fallback import (
    FallbackHandler,
    QualityAssessment,
    QualityEvaluator,
    get_fallback_handler,
)
from app.models.system.ai_report import AIReport
from app.utils.logger import logger

# ==================== 基础报告管理 ====================


def get_report_by_id(db: Session, report_id: int) -> Optional[AIReport]:
    # 功能：根据ID获取AI报告
    return (
        db.query(AIReport)
        .filter(AIReport.id == report_id, AIReport.is_deleted == 0)
        .first()
    )


def get_reports(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    report_type: Optional[str] = None,
    target_type: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> Tuple[List[AIReport], int]:
    # 功能：获取AI报告列表
    query = db.query(AIReport).filter(AIReport.is_deleted == 0)

    if report_type:
        query = query.filter(AIReport.report_type == report_type)
    if target_type:
        query = query.filter(AIReport.target_type == target_type)
    if is_public is not None:
        query = query.filter(AIReport.is_public == (1 if is_public else 0))

    total = query.count()
    reports = query.order_by(AIReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports, total


def create_report(
    db: Session,
    report_type: str,
    target_type: str,
    target_id: int,
    content: dict,
    summary: Optional[str] = None,
    ai_score: Optional[float] = None,
    created_by: Optional[int] = None,
    is_public: bool = True,
    metadata: Optional[Dict] = None,
) -> AIReport:
    # 功能：创建AI报告
    content_dict = content.copy()
    if metadata:
        content_dict["_metadata"] = metadata

    report = AIReport(
        report_type=report_type,
        target_type=target_type,
        target_id=target_id,
        content=json.dumps(content_dict, ensure_ascii=False),
        summary=summary,
        ai_score=ai_score,
        created_by=created_by,
        is_public=1 if is_public else 0,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    logger.info(f"创建AI报告: {report_type} - {target_type}:{target_id}")
    return report


def delete_report(db: Session, report_id: int) -> bool:
    # 功能：删除AI报告（软删除?
    report = get_report_by_id(db, report_id)
    if not report:
        return False

    report.is_deleted = 1
    db.commit()
    logger.info(f"删除AI报告: ID {report_id}")
    return True


# ==================== AI增强分析功能 ====================


class AIOrchestrator:
    """AI分析编排?- 协调各个模块"""

    def __init__(self):
        self.ai_service = get_ai_service()
        self.fallback_handler = get_fallback_handler()

    async def analyze_with_llm(
        self,
        analysis_type: AnalysisType,
        template_id: str,
        context: Dict,
        use_cache: bool = True,
        use_quality_check: bool = True,
    ) -> Tuple[Optional[Dict], Optional[QualityAssessment], Optional[str]]:
        """
        使用LLM执行分析

        参数:
            analysis_type: 分析类型
            template_id: 提示词模板ID
            context: 上下文数据
            use_cache: 是否使用缓存
            use_quality_check: 是否进行质量检?

        返回:
            (分析结果, 质量评估, 错误信息)
        """
        if not ai_config.AI_ENABLED:
            logger.info("AI功能未启用，使用规则分析")
            return None, None, "AI功能未启?

        template = PromptTemplateRegistry.get(template_id)
        if not template:
            logger.error(f"提示词模板不存在: {template_id}")
            return None, None, "提示词模板不存在"

        try:
            # 1. 准备消息
            messages = template.to_messages(**context)

            # 2. 调用LLM
            logger.info(f"调用LLM进行{analysis_type}分析")
            ai_response = await self.ai_service.chat(
                messages=messages, use_cache=use_cache
            )

            if not ai_response.is_success:
                logger.warning(f"LLM调用失败: {ai_response.error}")
                return await self._handle_llm_failure(
                    ai_response, analysis_type, context
                )

            # 3. 解析和优化响?
            parsed = ResponseOptimizer.parse_json_response(ai_response.content)
            if not parsed:
                logger.warning("LLM响应无法解析为JSON，使用原始文?)
                parsed = {"raw_content": ai_response.content}

            # 4. 应用响应调整规则
            optimized = ResponseAdjuster.apply_rules(parsed, analysis_type.value)

            # 5. 质量评估
            assessment = None
            if use_quality_check and ai_config.AI_QUALITY_CHECK_ENABLED:
                assessment = QualityEvaluator.evaluate(
                    ai_response, analysis_type.value, context
                )

                if not assessment.passed:
                    logger.warning(f"质量检查未通过: {assessment.issues}")

            # 6. 准备元数据
            metadata = {
                "llm_provider": ai_response.provider.value,
                "model": ai_response.model,
                "response_time": ai_response.response_time,
                "is_cached": ai_response.cache_hit,
                "is_fallback": ai_response.is_fallback,
                "quality_score": assessment.overall_score if assessment else None,
            }

            return optimized, assessment, None

        except Exception as e:
            logger.error(f"AI分析异常: {str(e)}", exc_info=True)
            return None, None, str(e)

    async def _handle_llm_failure(
        self, failed_response: AIResponse, analysis_type: AnalysisType, context: Dict
    ) -> Tuple[Optional[Dict], Optional[QualityAssessment], Optional[str]]:
        """处理LLM失败"""
        if not ai_config.AI_FALLBACK_ENABLED:
            return None, None, "LLM调用失败且禁用降?

        fallback_response = self.fallback_handler.handle_fallback(
            failed_response, {"analysis_type": analysis_type.value, **context}
        )

        if fallback_response and fallback_response.is_success:
            parsed = ResponseOptimizer.parse_json_response(fallback_response.content)
            return parsed, None, None

        return None, None, "降级处理失败"


# 全局编排器实?
_ai_orchestrator = AIOrchestrator()


def get_ai_orchestrator() -> AIOrchestrator:
    """获取AI编排?""
    return _ai_orchestrator


# ==================== 业务分析函数（已停用?====================


def analyze_fight(
    db: Session, fight_id: int, created_by: Optional[int] = None, use_llm: bool = True
) -> dict:
    # 功能：AI分析战斗数据（已停用?
    # 说明：Fight模型已被移除，接口保留以维持API兼容?
    return {"error": "Fight模块已停用，无法进行战斗分析"}


def analyze_build(
    db: Session, build_id: int, created_by: Optional[int] = None, use_llm: bool = True
) -> dict:
    # 功能：AI分析Build配置（已停用?
    # 说明：Build模型已被移除，接口保留以维持API兼容?
    return {"error": "Build模块已停用，无法进行Build分析"}


def get_trend_analysis(db: Session) -> dict:
    # 功能：获取AI趋势分析
    metadata = {"analysis_mode": "rule_based"}
    if ai_config.AI_ENABLED:
        metadata["analysis_mode"] = "hybrid"

    return {
        "data_points": 0,
        "total_damage": 0,
        "total_kills": 0,
        "avg_duration": 0,
        "trend": "无数据,
        "predictions": [],
        "anomalies": [],
        "insights": ["暂无趋势数据（Fight模型已移除）"],
        "_metadata": metadata,
    }


def get_suggestions(db: Session) -> dict:
    # 功能：获取AI优化建议
    suggestions = [
        {"type": "general", "priority": "high", "content": "建议提升团队配合?},
        {"type": "skill", "priority": "medium", "content": "技能循环存在优化空?},
        {"type": "build", "priority": "low", "content": "部分Build配置可进一步优?},
    ]

    return {
        "suggestions": [s["content"] for s in suggestions],
        "high_priority": [s["content"] for s in suggestions if s["priority"] == "high"],
        "_metadata": {"analysis_mode": "rule_based"},
    }


# ==================== 管理功能 ====================


def clear_ai_cache() -> Dict[str, Any]:
    """清除AI缓存"""
    from app.core.ai_model_client import get_cache

    cache = get_cache()
    stats_before = cache.get_cache_stats()
    cache.clear()
    logger.info("AI缓存已清?)
    return {"success": True, "before": stats_before}


def get_ai_stats() -> Dict[str, Any]:
    """获取AI统计"""
    from app.core.ai_model_client import get_cache
    from app.core.ai_quality_fallback import get_fallback_handler

    cache = get_cache()
    fallback = get_fallback_handler()

    return {
        "config": {
            "enabled": ai_config.AI_ENABLED,
            "provider": ai_config.AI_MODEL_PROVIDER.value,
            "cache_enabled": ai_config.AI_CACHE_ENABLED,
            "fallback_enabled": ai_config.AI_FALLBACK_ENABLED,
        },
        "cache": cache.get_cache_stats(),
        "fallback": fallback.get_stats(),
    }


def test_ai_configuration() -> Dict[str, Any]:
    """测试AI配置"""
    is_valid = ai_config.is_config_valid()

    return {
        "valid": is_valid,
        "config": {
            "enabled": ai_config.AI_ENABLED,
            "provider": ai_config.AI_MODEL_PROVIDER.value,
            "has_api_key": bool(ai_config.get_active_provider_config()["api_key"]),
        },
    }
