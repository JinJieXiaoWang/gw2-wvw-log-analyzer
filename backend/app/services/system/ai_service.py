# -*- coding: utf-8 -*-
# 模块功能：AI分析业务总服务 增强：
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01
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
from app.constants.dict_values import RoleType
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
    # 功能：删除AI报告（软删除）
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
            return None, None, "AI功能未启用"

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
                logger.warning("LLM响应无法解析为JSON，使用原始文本")
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
            return None, None, "LLM调用失败且禁用降级"

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
    """获取AI编排器"""
    return _ai_orchestrator


# ==================== 业务分析函数（已停用?====================


# ==================== 业务分析函数 ====================


def _prepare_fight_analysis_context(db: Session, fight_id: int) -> Optional[Dict[str, Any]]:
    """
    准备战斗分析上下文数据

    参数:
        db: 数据库会话
        fight_id: 战斗ID

    返回:
        分析所需的上下文数据字典
    """
    from app.models.log.fight import Fight
    from app.models.log.fight_stats import FightStats

    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        return None

    stats = db.query(FightStats).filter(FightStats.fight_id == fight_id).all()
    if not stats:
        return None

    total_damage = sum(s.damage or 0 for s in stats)
    total_healing = sum(s.healing or 0 for s in stats)
    total_kills = sum(s.killed or 0 for s in stats)
    total_deaths = sum(s.dead_count or 0 for s in stats)

    player_data = []
    for s in stats:
        if not s.account:
            continue
        player_data.append({
            "account": s.account,
            "character": s.character_name or s.account,
            "profession": s.profession or "Unknown",
            "damage": s.damage or 0,
            "dps": s.dps or 0,
            "healing": s.healing or 0,
            "kills": s.killed or 0,
            "dead_count": s.dead_count or 0,
            "might_uptime": float(s.might_uptime or 0),
            "quickness_uptime": float(s.quickness_uptime or 0),
            "alacrity_uptime": float(s.alacrity_uptime or 0),
            "has_commander_tag": bool(s.has_commander_tag),
        })

    data_summary = {
        "duration": fight.duration_sec or 0,
        "map": fight.map_name or "Unknown",
        "server": fight.server_name or "Unknown",
        "player_count": len(player_data),
        "total_damage": total_damage,
        "total_healing": total_healing,
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "avg_dps": total_damage // max(fight.duration_sec or 1, 1),
        "kill_death_ratio": total_kills / max(total_deaths, 1),
    }

    return {
        "fight_id": fight_id,
        "fight": {
            "duration": fight.duration_sec or 0,
            "map_name": fight.map_name or "Unknown",
            "server_name": fight.server_name or "Unknown",
            "start_time": fight.start_time.isoformat() if fight.start_time else "",
        },
        "summary": data_summary,
        "players": player_data[:20],
        "total_players": len(player_data),
    }


def _prepare_build_analysis_context(db: Session, build_id: int) -> Optional[Dict[str, Any]]:
    """
    准备Build分析上下文数据

    参数:
        db: 数据库会话
        build_id: Build ID

    返回:
        分析所需的上下文数据字典
    """
    from app.models.game.build import Build

    build = db.query(Build).filter(Build.id == build_id).first()
    if not build:
        return None

    return {
        "build_id": build_id,
        "build": {
            "title": build.title or "Unknown",
            "profession": build.profession or "Unknown",
            "elite_spec": build.elite_spec or "",
            "role": build.role or RoleType.DPS,
            "weapons": build.weapons or [],
            "rune": build.rune or "",
            "food": build.food or "",
            "relic": build.relic or "",
            "trait_lines": build.trait_lines or [],
            "bd_code": build.bd_code or "",
            "author": build.author or "Unknown",
            "is_meta": build.is_meta,
        },
        "use_case": "WvW",
    }


def analyze_fight(
    db: Session, fight_id: int, created_by: Optional[int] = None, use_llm: bool = True
) -> dict:
    """
    AI分析战斗数据

    参数:
        db: 数据库会话
        fight_id: 战斗ID
        created_by: 创建者ID
        use_llm: 是否使用LLM分析

    返回:
        分析结果字典
    """
    context = _prepare_fight_analysis_context(db, fight_id)
    if not context:
        return {"error": f"战斗ID {fight_id} 不存在或无数据"}

    if use_llm and ai_config.AI_ENABLED:
        try:
            orchestrator = get_ai_orchestrator()
            result, assessment, error = orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.FIGHT_ANALYSIS,
                template_id="fight_analysis_v1",
                context={
                    "duration": context["summary"]["duration"],
                    "total_damage": context["summary"]["total_damage"],
                    "total_healing": context["summary"]["total_healing"],
                    "kills": context["summary"]["total_kills"],
                    "deaths": context["summary"]["total_deaths"],
                    "players": len(context["players"]),
                    "data_summary": str(context["summary"]),
                },
                use_cache=True,
                use_quality_check=True,
            )

            if error:
                logger.warning(f"AI分析战斗失败: {error}")
            elif result:
                ai_score = result.get("ai_score", 0) or result.get("priority_score", 0)
                report = create_report(
                    db=db,
                    report_type="fight_analysis",
                    target_type="fight",
                    target_id=fight_id,
                    content=result,
                    summary=result.get("summary", ""),
                    ai_score=ai_score,
                    created_by=created_by,
                    is_public=True,
                    metadata={
                        "fight_id": fight_id,
                        "player_count": context["total_players"],
                        "map_name": context["fight"]["map_name"],
                    },
                )

                from app.models.log.fight import Fight
                fight = db.query(Fight).filter(Fight.id == fight_id).first()
                if fight:
                    fight.is_ai_analyzed = True
                    db.commit()

                return {
                    "success": True,
                    "report_id": report.id,
                    "ai_score": ai_score,
                    "summary": result.get("summary", ""),
                    "team_strengths": result.get("team_strengths", []),
                    "team_weaknesses": result.get("team_weaknesses", []),
                    "recommendations": result.get("recommendations", []),
                    "quality_score": assessment.overall_score if assessment else None,
                    "is_fallback": result.get("_is_fallback", False),
                }

        except Exception as e:
            logger.error(f"AI分析战斗异常: {str(e)}", exc_info=True)
            return {"error": f"AI分析失败: {str(e)}"}

    return _generate_rule_based_fight_analysis(context, db, fight_id, created_by)


def _generate_rule_based_fight_analysis(
    context: Dict, db: Session, fight_id: int, created_by: Optional[int]
) -> dict:
    """生成基于规则的战�单分析（当AI不可用时）"""
    summary = context["summary"]
    players = context["players"]

    strengths = []
    weaknesses = []
    recommendations = []

    if summary["total_kills"] > summary["total_deaths"]:
        strengths.append("击杀/死亡比良好，团队输出能力较强")
    else:
        weaknesses.append("死亡次数过多，需要注意生存能力")

    if summary["avg_dps"] > 50000:
        strengths.append(f"场均DPS较高 ({summary['avg_dps']})")
    elif summary["avg_dps"] < 20000:
        weaknesses.append(f"场均DPS偏低 ({summary['avg_dps']})，需要提升输出")

    commander_players = [p for p in players if p.get("has_commander_tag")]
    if commander_players:
        strengths.append(f"有指挥官参与战斗 ({commander_players[0]['character']})")
    else:
        recommendations.append("建议在WVW战斗中配备指挥官")

    high_dps_players = sorted(players, key=lambda x: x.get("dps", 0), reverse=True)[:3]
    if high_dps_players:
        top_dps = high_dps_players[0]
        recommendations.append(f"优秀输出: {top_dps['character']} ({top_dps['profession']}) DPS: {top_dps['dps']}")

    low_might = [p for p in players if p.get("might_uptime", 0) < 50]
    if low_might:
        weaknesses.append(f"{len(low_might)}名玩家威能覆盖不足")

    ai_score = min(100, int(summary["avg_dps"] / 1000 + summary["total_kills"] * 5 - summary["total_deaths"] * 3))

    result = {
        "summary": f"战斗时长{summary['duration']}秒，击杀{summary['total_kills']}人，死亡{summary['total_deaths']}人",
        "team_strengths": strengths,
        "team_weaknesses": weaknesses,
        "buff_analysis": [f"威能覆盖: {sum(p.get('might_uptime', 0) for p in players) / max(len(players), 1):.1f}%"],
        "cc_analysis": ["控制技能数据需进一步分析"],
        "skill_rotation_notes": ["建议优化技能循环"],
        "recommendations": recommendations,
        "priority_score": ai_score,
        "ai_score": ai_score,
    }

    report = create_report(
        db=db,
        report_type="fight_analysis",
        target_type="fight",
        target_id=fight_id,
        content=result,
        summary=result["summary"],
        ai_score=ai_score,
        created_by=created_by,
        is_public=True,
        metadata={"analysis_mode": "rule_based", "fight_id": fight_id},
    )

    from app.models.log.fight import Fight
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if fight:
        fight.is_ai_analyzed = True
        db.commit()

    return {
        "success": True,
        "report_id": report.id,
        "ai_score": ai_score,
        "summary": result["summary"],
        "team_strengths": strengths,
        "team_weaknesses": weaknesses,
        "recommendations": recommendations,
        "quality_score": None,
        "is_fallback": False,
    }


def analyze_build(
    db: Session, build_id: int, created_by: Optional[int] = None, use_llm: bool = True
) -> dict:
    """
    AI分析Build配置

    参数:
        db: 数据库会话
        build_id: Build ID
        created_by: 创建者ID
        use_llm: 是否使用LLM分析

    返回:
        分析结果字典
    """
    context = _prepare_build_analysis_context(db, build_id)
    if not context:
        return {"error": f"Build ID {build_id} 不存在"}

    if use_llm and ai_config.AI_ENABLED:
        try:
            orchestrator = get_ai_orchestrator()
            result, assessment, error = orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.BUILD_OPTIMIZATION,
                template_id="build_optimization_v1",
                context={
                    "profession": context["build"]["profession"],
                    "build_name": context["build"]["title"],
                    "weapons": ", ".join(context["build"]["weapons"]) if context["build"]["weapons"] else "未设置",
                    "traits": ", ".join(str(t) for t in context["build"]["trait_lines"]) if context["build"]["trait_lines"] else "未设置",
                    "runes": context["build"]["rune"] or "未设置",
                    "food": context["build"]["food"] or "未设置",
                    "stats": f"职业: {context['build']['profession']}, 专精: {context['build']['elite_spec']}",
                    "use_case": context["use_case"],
                },
                use_cache=True,
                use_quality_check=True,
            )

            if error:
                logger.warning(f"AI分析Build失败: {error}")
            elif result:
                wvw_score = result.get("wvw_appropriateness", 0) or 70
                report = create_report(
                    db=db,
                    report_type="build_analysis",
                    target_type="build",
                    target_id=build_id,
                    content=result,
                    summary=result.get("current_build", {}).get("build_name", ""),
                    ai_score=wvw_score,
                    created_by=created_by,
                    is_public=True,
                    metadata={
                        "build_id": build_id,
                        "profession": context["build"]["profession"],
                        "role": context["build"]["role"],
                    },
                )

                return {
                    "success": True,
                    "report_id": report.id,
                    "ai_score": wvw_score,
                    "build_name": result.get("current_build", {}).get("build_name", ""),
                    "wvw_appropriateness": wvw_score,
                    "strengths": result.get("strengths", []),
                    "weaknesses": result.get("weaknesses", []),
                    "suggestions": result.get("suggestions", []),
                    "alternative_builds": result.get("alternative_builds", []),
                    "quality_score": assessment.overall_score if assessment else None,
                }

        except Exception as e:
            logger.error(f"AI分析Build异常: {str(e)}", exc_info=True)
            return {"error": f"AI分析失败: {str(e)}"}

    return _generate_rule_based_build_analysis(context, db, build_id, created_by)


def _generate_rule_based_build_analysis(
    context: Dict, db: Session, build_id: int, created_by: Optional[int]
) -> dict:
    """生成基于规则的Build分析"""
    build = context["build"]
    strengths = []
    weaknesses = []
    suggestions = []

    if build["is_meta"]:
        strengths.append("该Build被标记为推荐配置")
    else:
        suggestions.append("建议使用当前版本的Meta Build以获得最佳效果")

    if build["weapons"] and len(build["weapons"]) >= 2:
        strengths.append(f"双武器配置: {', '.join(build['weapons'])}")
    else:
        weaknesses.append("武器配置不完整")

    if build["rune"] and build["rune"] != "未设置":
        strengths.append(f"符文: {build['rune']}")
    else:
        suggestions.append("建议配置合适的符文以提升属性")

    if build["food"] and build["food"] != "未设置":
        strengths.append(f"食物: {build['food']}")
    else:
        suggestions.append("建议配置合适的食物以提升战斗表现")

    if build["trait_lines"] and len(build["trait_lines"]) >= 3:
        strengths.append(f"特性线: {len(build['trait_lines'])}条已配置")
    else:
        weaknesses.append("特性线配置不完整")

    profession = build["profession"].lower()
    role = build["role"].lower()

    if profession in ["guardian", "firebrand"] and role == RoleType.SUPPORT:
        suggestions.append("守护者作为辅助时注意维持增益覆盖")
    elif profession in ["warrior", "berserker"] and role == RoleType.DPS:
        suggestions.append("战士输出时注意保持武器强度增益")

    wvw_score = 60 + len(strengths) * 5 - len(weaknesses) * 5
    wvw_score = max(0, min(100, wvw_score))

    result = {
        "current_build": {
            "profession": build["profession"],
            "build_name": build["title"],
            "weapons": build["weapons"] or [],
            "traits": build["trait_lines"] or [],
            "stats": f"职业: {build['profession']}, 专精: {build['elite_spec']}",
        },
        "wvw_appropriateness": wvw_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "alternative_builds": [],
    }

    report = create_report(
        db=db,
        report_type="build_analysis",
        target_type="build",
        target_id=build_id,
        content=result,
        summary=build["title"],
        ai_score=wvw_score,
        created_by=created_by,
        is_public=True,
        metadata={"analysis_mode": "rule_based", "build_id": build_id},
    )

    return {
        "success": True,
        "report_id": report.id,
        "ai_score": wvw_score,
        "build_name": build["title"],
        "wvw_appropriateness": wvw_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "alternative_builds": [],
        "quality_score": None,
    }


def get_trend_analysis(db: Session, days: int = 30) -> dict:
    """
    获取AI趋势分析

    参数:
        db: 数据库会话
        days: 分析天数范围

    返回:
        趋势分析结果
    """
    from datetime import datetime, timedelta
    from app.models.log.fight import Fight
    from app.models.log.fight_stats import FightStats

    start_date = datetime.now() - timedelta(days=days)

    fights = db.query(Fight).filter(Fight.start_time >= start_date).all()
    if not fights:
        return {
            "data_points": 0,
            "total_damage": 0,
            "total_kills": 0,
            "avg_duration": 0,
            "trend": "无数据",
            "predictions": [],
            "anomalies": [],
            "insights": ["近期无战斗数据"],
            "time_series": [],
            "_metadata": {"analysis_mode": "rule_based", "days": days},
        }

    fight_ids = [f.id for f in fights]
    stats = db.query(FightStats).filter(FightStats.fight_id.in_(fight_ids)).all()

    total_damage = sum(s.damage or 0 for s in stats)
    total_kills = sum(s.killed or 0 for s in stats)
    total_deaths = sum(s.dead_count or 0 for s in stats)
    total_healing = sum(s.healing or 0 for s in stats)
    avg_duration = sum(f.duration_sec or 0 for f in fights) / max(len(fights), 1)

    damage_per_day = total_damage / max(days, 1)
    kills_per_day = total_kills / max(days, 1)
    kd_ratio = total_kills / max(total_deaths, 1)

    # 按天聚合时间序列数据
    from collections import defaultdict
    daily = defaultdict(lambda: {"damage": 0, "kills": 0, "deaths": 0, "duration": 0, "count": 0})
    for f in fights:
        day_key = f.start_time.strftime("%m-%d") if f.start_time else "unknown"
        daily[day_key]["damage"] += f.total_damage or 0
        daily[day_key]["duration"] += f.duration_sec or 0
        daily[day_key]["count"] += 1
    for s in stats:
        # 关联到战斗日期
        fight = next((f for f in fights if f.id == s.fight_id), None)
        if fight and fight.start_time:
            day_key = fight.start_time.strftime("%m-%d")
            daily[day_key]["kills"] += s.killed or 0
            daily[day_key]["deaths"] += s.dead_count or 0

    time_series = [
        {
            "date": day,
            "damage": vals["damage"],
            "kills": vals["kills"],
            "deaths": vals["deaths"],
            "duration": round(vals["duration"] / max(vals["count"], 1), 1),
        }
        for day, vals in sorted(daily.items())
    ]

    if kd_ratio > 1.5:
        trend = "上升"
        insights = ["团队表现呈上升趋势", f"击杀/死亡比 {kd_ratio:.2f} 表现优秀"]
    elif kd_ratio > 1.0:
        trend = "稳定"
        insights = ["团队表现稳定", f"击杀/死亡比 {kd_ratio:.2f}"]
    else:
        trend = "下降"
        insights = ["团队表现有下降趋势", f"击杀/死亡比 {kd_ratio:.2f} 需要改善"]

    if damage_per_day > 10000000:
        insights.append("场均伤害较高，输出能力强")

    insights.append(f"共分析 {len(fights)} 场战斗，{len(stats)} 名玩家数据")

    predictions = []
    if trend == "上升":
        predictions.append("预计下期表现持续向好")
    elif trend == "稳定":
        predictions.append("建议关注细节优化以突破瓶颈")
    else:
        predictions.append("建议进行团队训练提升配合")

    result = {
        "data_points": len(fights),
        "total_damage": total_damage,
        "total_healing": total_healing,
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "avg_duration": round(avg_duration, 1),
        "trend": trend,
        "trend_confidence": 75,
        "predictions": predictions,
        "anomalies": [],
        "insights": insights,
        "time_series": time_series,
        "_metadata": {
            "analysis_mode": "rule_based",
            "days": days,
            "damage_per_day": round(damage_per_day, 0),
            "kills_per_day": round(kills_per_day, 2),
            "kd_ratio": round(kd_ratio, 2),
        },
    }

    if ai_config.AI_ENABLED:
        try:
            orchestrator = get_ai_orchestrator()
            ai_result, _, error = orchestrator.analyze_with_llm(
                analysis_type=AnalysisType.TREND_ANALYSIS,
                template_id="trend_analysis_v1",
                context={
                    "fight_count": len(fights),
                    "time_range": f"最近{days}天",
                    "data_summary": str({
                        "total_damage": total_damage,
                        "total_kills": total_kills,
                        "avg_duration": avg_duration,
                        "kd_ratio": kd_ratio,
                    }),
                },
                use_cache=True,
                use_quality_check=False,
            )

            if not error and ai_result:
                result.update(ai_result)
                result["_metadata"]["analysis_mode"] = "hybrid"

        except Exception as e:
            logger.warning(f"AI趋势分析失败: {e}")

    return result


def get_suggestions(db: Session, account: Optional[str] = None, limit: int = 10) -> dict:
    """
    获取AI优化建议

    参数:
        db: 数据库会话
        account: 指定玩家账户（可选）
        limit: 返回建议数量

    返回:
        优化建议列表
    """
    from app.models.log.fight_stats import FightStats

    query = db.query(FightStats)
    if account:
        query = query.filter(FightStats.account == account)

    stats = query.order_by(FightStats.damage.desc()).limit(100).all()

    if not stats:
        return {
            "suggestions": [
                "暂无足够数据生成建议",
                "建议先上传并解析战斗日志",
            ],
            "high_priority": [],
            "_metadata": {"count": 0, "account": account},
        }

    suggestions = []
    high_priority = []

    damage_values = [s.damage or 0 for s in stats]
    avg_damage = sum(damage_values) / max(len(damage_values), 1)

    low_performers = [s for s in stats if (s.damage or 0) < avg_damage * 0.5]
    if low_performers:
        low_count = len(low_performers)
        suggestions.append(f"有{low_count}名玩家输出偏低，建议关注")
        high_priority.append("部分玩家输出不足，建议进行针对性训练")

    low_might_players = [s for s in stats if float(s.might_uptime or 0) < 50]
    if low_might_players:
        suggestions.append(f"{len(low_might_players)}名玩家威能覆盖不足")
        high_priority.append("威能覆盖普遍偏低，注意团队增益叠加")

    low_healing = [s for s in stats if s.healing and s.healing > 0]
    if not low_healing and any("support" in s.profession.lower() or "heal" in s.profession.lower() for s in stats if s.profession):
        suggestions.append("辅助职业治疗量偏低")

    high_death = [s for s in stats if (s.dead_count or 0) > 5]
    if high_death:
        suggestions.append(f"{len(high_death)}名玩家死亡次数过多，需要注意走位")
        high_priority.append("部分玩家生存能力需提升")

    professions = {}
    for s in stats:
        prof = s.profession or "Unknown"
        if prof not in professions:
            professions[prof] = {"count": 0, "total_damage": 0}
        professions[prof]["count"] += 1
        professions[prof]["total_damage"] += s.damage or 0

    if len(professions) > 1:
        prof_strs = [f"{k}({v['count']})" for k, v in professions.items()]
        suggestions.append(f"团队职业分布: {', '.join(prof_strs)}")

    if not high_priority:
        suggestions.append("团队整体表现良好，继续保持")
        high_priority.append("输出和生存指标正常")

    suggestions.append("建议定期分析战斗数据持续优化")

    return {
        "suggestions": suggestions[:limit],
        "high_priority": high_priority[:3],
        "_metadata": {
            "count": len(suggestions),
            "account": account,
            "analyzed_players": len(stats),
            "analysis_mode": "rule_based",
        },
    }


# ==================== 管理功能 ====================


def clear_ai_cache() -> Dict[str, Any]:
    """清除AI缓存"""
    from app.core.ai_model_client import get_cache

    cache = get_cache()
    stats_before = cache.get_cache_stats()
    cache.clear()
    logger.info("AI缓存已清空")
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
            "has_api_key": bool(ai_config.get_active_provider_config()["api_key"]),
        },
        "cache": cache.get_cache_stats(),
        "fallback": fallback.get_stats(),
    }


def test_ai_configuration() -> Dict[str, Any]:
    """测试AI配置（检查服务器端配置）"""
    is_valid = ai_config.is_config_valid()

    return {
        "valid": is_valid,
        "config": {
            "enabled": ai_config.AI_ENABLED,
            "provider": ai_config.AI_MODEL_PROVIDER.value,
            "has_api_key": bool(ai_config.get_active_provider_config()["api_key"]),
        },
    }


async def test_ai_configuration_with_key(provider: str, api_key: str) -> Dict[str, Any]:
    """测试AI配置（使用用户提供的密钥）"""
    from app.core.config import ModelProvider
    from app.core.ai_model_client import test_provider_connection
    
    try:
        # 将字符串转换为枚举
        provider_enum = ModelProvider(provider.lower())
        
        # 获取该提供商的配置模板
        provider_configs: Dict[ModelProvider, Dict[str, Any]] = {
            ModelProvider.OPENAI: {
                "api_key": api_key,
                "api_base": ai_config.OPENAI_API_BASE,
                "model": ai_config.OPENAI_MODEL,
                "max_tokens": ai_config.OPENAI_MAX_TOKENS,
                "temperature": ai_config.OPENAI_TEMPERATURE,
            },
            ModelProvider.DEEPSEEK: {
                "api_key": api_key,
                "api_base": ai_config.DEEPSEEK_API_BASE,
                "model": ai_config.DEEPSEEK_MODEL,
                "max_tokens": ai_config.DEEPSEEK_MAX_TOKENS,
                "temperature": ai_config.DEEPSEEK_TEMPERATURE,
            },
            ModelProvider.QWEN: {
                "api_key": api_key,
                "api_base": ai_config.QWEN_API_BASE,
                "model": ai_config.QWEN_MODEL,
                "max_tokens": ai_config.QWEN_MAX_TOKENS,
                "temperature": ai_config.QWEN_TEMPERATURE,
            },
        }
        
        config = provider_configs.get(provider_enum)
        if not config:
            return {
                "success": False,
                "valid": False,
                "message": f"不支持的提供商: {provider}",
                "provider": provider,
            }
        
        # 直接调用异步测试函数
        response = await test_provider_connection(provider_enum, config)
        
        if response.is_success:
            return {
                "success": True,
                "valid": True,
                "message": "API密钥有效，AI服务连接成功",
                "provider": provider,
                "response_sample": response.content[:100] if response.content else None,
            }
        else:
            return {
                "success": False,
                "valid": False,
                "message": f"API调用失败: {response.error}",
                "provider": provider,
            }
            
    except ValueError as e:
        return {
            "success": False,
            "valid": False,
            "message": f"无效的提供商: {provider}",
            "provider": provider,
        }
    except Exception as e:
        logger.error(f"测试AI配置失败: {e}")
        return {
            "success": False,
            "valid": False,
            "message": f"测试失败: {str(e)}",
            "provider": provider,
        }
