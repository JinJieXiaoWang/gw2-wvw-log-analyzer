# -*- coding: utf-8 -*-
# 模块功能：AI分析页面状态管理与业务逻辑
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-04
# 说明：集中管理AI分析页面的状态和数据加载逻辑，支持按模块逐步分析

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.log.fight import Fight
from app.models.log.fight_stats import FightStats
from app.models.system.ai_report import AIReport
from app.services.auth.auth_service import get_current_user_optional
from app.services.system.ai_service import (
    analyze_build,
    analyze_fight,
    clear_ai_cache,
    get_ai_stats,
    get_reports,
    get_suggestions,
    get_trend_analysis,
    test_ai_configuration,
    test_ai_configuration_with_key,
)
from app.schemas.auth.common import ApiResponse
from app.utils.error.exceptions import InternalServerErrorException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/ai", tags=["AI分析"])


class AiStatusResponse(BaseModel):
    """AI状态响应"""
    config: Dict[str, Any]
    cache: Dict[str, Any]
    fallback: Dict[str, Any]


class AnalyzeRequest(BaseModel):
    """分析请求基类"""
    pass


class FightAnalysisRequest(AnalyzeRequest):
    """战斗分析请求"""
    fight_id: int
    analysis_scope: str = "current"  # current=当前选中, full=全面分析


class MemberAnalysisRequest(AnalyzeRequest):
    """玩家分析请求"""
    member_id: int
    analysis_scope: str = "current"


class BuildAnalysisRequest(AnalyzeRequest):
    """Build分析请求"""
    build_id: int


class ReportResponse(BaseModel):
    """报告响应"""
    id: int
    report_type: str
    target_type: str
    target_id: int
    summary: str
    ai_score: Optional[float]
    created_at: datetime
    is_public: bool


class AnalysisResultResponse(BaseModel):
    """分析结果响应"""
    success: bool
    report_id: int
    analysis_type: str
    scope: str
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    data_summary: Dict[str, Any]


def parse_time_range(time_range: str) -> int:
    """解析时间范围字符串"""
    if time_range == "7d":
        return 7
    elif time_range == "30d":
        return 30
    elif time_range == "90d":
        return 90
    return 7


@router.get("/status", response_model=ApiResponse, summary="获取AI服务状态")
def get_status():
    """
    获取AI服务状态
    
    返回AI配置信息、缓存统计、降级策略状态
    """
    stats = get_ai_stats()
    return ApiResponse.success_response(
        data=stats,
        message="获取AI状态成功",
    )


@router.post("/analyze/fight/{fight_id}", response_model=Dict[str, Any], summary="AI分析战斗")
def analyze_fight_endpoint(
    fight_id: int,
    scope: str = Query("current", description="分析范围: current=当前选中数据, full=全面分析"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI分析战斗数据
    
    支持两种分析模式：
    - current: 基于当前选中的战斗数据进行精准分析
    - full: 对所有相关数据进行综合分析
    
    分析内容：
    - 战斗概述（时长、人数、击杀/死亡）
    - 输出统计（总伤害、场均DPS、伤害分布）
    - 治疗统计（总治疗、场均治疗）
    - 关键事件（重要技能使用、战术时机）
    - 改进建议
    """
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise NotFoundException(f"战斗ID {fight_id} 不存在")
    
    result = analyze_fight(db, fight_id, created_by=user.id if user else None)
    
    if "error" in result:
        raise InternalServerErrorException(result["error"])
    
    return {
        "success": True,
        "report_id": result.get("report_id"),
        "analysis_type": "fight_analysis",
        "scope": scope,
        "summary": result.get("summary", ""),
        "key_findings": result.get("team_strengths", [])[:5],
        "recommendations": result.get("recommendations", [])[:5],
        "data_summary": {
            "fight_id": fight_id,
            "duration": fight.duration if fight else 0,
            "player_count": db.query(FightStats).filter(FightStats.fight_id == fight_id).count(),
            "total_damage": result.get("total_damage", 0),
            "total_kills": result.get("total_kills", 0),
            "total_deaths": result.get("total_deaths", 0),
        },
    }


@router.post("/analyze/member/{member_id}", response_model=Dict[str, Any], summary="AI分析玩家")
def analyze_member_endpoint(
    member_id: int,
    scope: str = Query("current", description="分析范围: current=当前选中数据, full=全面分析"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI分析玩家表现
    
    支持两种分析模式：
    - current: 基于当前选中的战斗数据进行分析
    - full: 对玩家所有历史数据进行综合评估
    
    分析内容：
    - 玩家基本信息（职业、常用Build）
    - 输出表现（DPS、伤害占比、技能循环）
    - 生存能力（死亡次数、存活率）
    - 团队贡献（治疗量、增益覆盖）
    - 改进建议
    """
    stats = db.query(FightStats).filter(FightStats.id == member_id).first()
    if not stats:
        raise NotFoundException(f"玩家数据ID {member_id} 不存在")
    
    from app.services.system.ai_service import analyze_player
    result = analyze_player(db, member_id, created_by=user.id if user else None)
    
    if "error" in result:
        raise InternalServerErrorException(result["error"])
    
    return {
        "success": True,
        "report_id": result.get("report_id"),
        "analysis_type": "member_analysis",
        "scope": scope,
        "summary": result.get("summary", ""),
        "key_findings": result.get("strengths", [])[:5],
        "recommendations": result.get("suggestions", [])[:5],
        "data_summary": {
            "member_id": member_id,
            "account": stats.account,
            "profession": stats.profession,
            "total_damage": stats.damage or 0,
            "total_healing": stats.healing or 0,
            "fight_count": 1,
        },
    }


@router.post("/analyze/build/{build_id}", response_model=Dict[str, Any], summary="AI分析Build")
def analyze_build_endpoint(
    build_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI分析Build配置
    
    分析内容：
    - Build基本信息（职业、特性、装备）
    - 适用性评估（WVW、PVX、PVP）
    - 强度评分
    - 优化建议（特性调整、装备建议）
    - 替代Build推荐
    """
    from app.models.game.build import Build
    
    build = db.query(Build).filter(Build.id == build_id).first()
    if not build:
        raise NotFoundException(f"Build ID {build_id} 不存在")
    
    result = analyze_build(db, build_id, created_by=user.id if user else None)
    
    if "error" in result:
        raise InternalServerErrorException(result["error"])
    
    return {
        "success": True,
        "report_id": result.get("report_id"),
        "analysis_type": "build_analysis",
        "scope": "current",
        "summary": result.get("build_name", ""),
        "key_findings": result.get("strengths", [])[:5],
        "recommendations": result.get("suggestions", [])[:5],
        "data_summary": {
            "build_id": build_id,
            "wvw_score": result.get("wvw_appropriateness", 0),
            "alternative_builds": result.get("alternative_builds", [])[:3],
        },
    }


@router.get("/suggestions", response_model=Dict[str, Any], summary="获取AI优化建议")
def get_suggestions_endpoint(
    account: Optional[str] = Query(None, description="指定玩家账户"),
    limit: int = Query(10, ge=1, le=50, description="返回建议数量"),
    db: Session = Depends(get_db),
):
    """
    获取AI优化建议
    
    根据历史数据分析，生成个性化优化建议：
    - 输出优化建议
    - 生存能力建议
    - 团队配合建议
    - Build调整建议
    
    建议优先级：
    - high_priority: 高优先级，需要立即关注
    - suggestions: 常规优化建议
    """
    result = get_suggestions(db, account=account, limit=limit)
    return result


@router.get("/trend", response_model=Dict[str, Any], summary="获取AI趋势分析")
def get_trend(
    time_range: str = Query("7d", description="时间范围: 7d, 30d, 90d"),
    db: Session = Depends(get_db),
):
    """
    获取AI趋势分析
    
    基于时间维度的数据分析：
    - 战斗数量趋势
    - 伤害/治疗趋势
    - K/D比趋势
    - 异常检测
    - 预测和建议
    """
    days = parse_time_range(time_range)
    result = get_trend_analysis(db, days=days)
    return result


@router.get("/reports", response_model=Dict[str, Any], summary="获取AI报告列表")
def get_reports_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    report_type: Optional[str] = Query(None, description="报告类型: fight, player, build"),
    target_type: Optional[str] = Query(None, description="目标类型"),
    db: Session = Depends(get_db),
):
    """
    获取AI报告列表
    
    支持分页、类型筛选
    """
    skip = (page - 1) * page_size
    reports, total = get_reports(
        db,
        skip=skip,
        limit=page_size,
        report_type=report_type,
        target_type=target_type,
    )
    return {
        "items": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "target_type": r.target_type,
                "target_id": r.target_id,
                "summary": r.summary,
                "ai_score": r.ai_score,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "is_public": bool(r.is_public),
            }
            for r in reports
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/reports/{report_id}", response_model=Dict[str, Any], summary="获取报告详情")
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
):
    """获取报告详情"""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise NotFoundException(f"报告ID {report_id} 不存在")
    
    return {
        "id": report.id,
        "report_type": report.report_type,
        "target_type": report.target_type,
        "target_id": report.target_id,
        "summary": report.summary,
        "content": report.content,
        "ai_score": report.ai_score,
        "created_at": report.created_at,
        "metadata": report.metadata or {},
    }


@router.delete("/reports/{report_id}", summary="删除报告")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """删除报告（软删除）"""
    from app.services.system.ai_service import delete_report as delete_report_service
    
    success = delete_report_service(db, report_id)
    if not success:
        raise NotFoundException(f"报告ID {report_id} 不存在")
    
    return {"success": True, "message": "报告删除成功"}


@router.post("/test", response_model=Dict[str, Any], summary="测试AI配置")
async def test_configuration(
    provider: Optional[str] = Query(None, description="AI提供商"),
    api_key: Optional[str] = Query(None, description="API密钥"),
    db: Session = Depends(get_db),
):
    """
    测试AI配置
    
    不带参数：测试服务器端已保存的配置
    带参数：测试用户提供的配置
    """
    if provider and api_key:
        result = await test_ai_configuration_with_key(provider, api_key)
    else:
        result = test_ai_configuration()
    
    return result


@router.post("/cache/clear", summary="清除AI缓存")
def clear_cache():
    """清除AI分析缓存"""
    result = clear_ai_cache()
    return {"success": True, "message": "缓存已清空", "data": result}


# ==================== AI战术复盘与成长顾问系统 - 新增端点 ====================

from app.core.ai_prompt_templates import AnalysisType
from app.services.ai_analysis.ai_analysis_service import AIAnalysisService


@router.post("/analyze/personal-growth", response_model=Dict[str, Any], summary="个人战力成长档案")
async def analyze_personal_growth_endpoint(
    account: str = Query(..., description="玩家账号（如: user.1234）"),
    fight_count: int = Query(30, ge=5, le=100, description="历史战斗场次"),
    save_report: bool = Query(True, description="是否保存报告"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI个人战力成长档案分析
    
    基于玩家历史战斗数据，生成六维战力雷达图、公会百分位排名、成长趋势和可操作建议。
    
    分析维度：
    - 输出能力（DPS/直伤/症状/暴击）
    - 生存能力（承伤/格挡/闪避/倒地）
    - 辅助贡献（治疗/复活/清症/扒增益）
    - Buff管理（威能/急速/敏捷/愤怒覆盖）
    - 控制能力（CC时长/打断/解控）
    - 站位意识（堆叠距离/指挥官距离/侧击率）
    """
    service = AIAnalysisService(db)
    result = await service.analyze_personal_growth(account, fight_count)
    
    if "error" in result:
        return {"success": False, "error": result["error"], "data": result}
    
    report_id = None
    if save_report:
        report = service.create_report(
            report_type=AnalysisType.PERSONAL_GROWTH,
            target_type="player",
            target_id=account,
            content=result,
            summary=f"{account} 个人战力成长档案",
            ai_score=result.get("overall_score"),
        )
        report_id = report.id
    
    return {
        "success": True,
        "report_id": report_id,
        "analysis_type": "personal_growth",
        "data": result,
    }


@router.post("/analyze/death-attribution", response_model=Dict[str, Any], summary="死亡归因与生存分析")
async def analyze_death_attribution_endpoint(
    account: str = Query(..., description="玩家账号"),
    fight_id: Optional[int] = Query(None, description="指定战斗ID（可选）"),
    log_id: Optional[int] = Query(None, description="EI日志ID（用于获取death_recap）"),
    save_report: bool = Query(True, description="是否保存报告"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI死亡归因与生存分析
    
    分析玩家死亡原因，识别生存薄弱环节，提供个性化生存训练方案。
    
    归因分类：
    - 被集火：短时间内受到多个敌方目标高额伤害
    - 走位失误：脱离团队堆叠点
    - Buff断档：保护/稳固覆盖率不足
    - 技能未交：拥有生存技能但未使用
    - 治疗缺口：承伤超过治疗覆盖
    - 控制链：被连续控制无法操作
    """
    service = AIAnalysisService(db)
    result = await service.analyze_death_attribution(account, fight_id, log_id)
    
    if "error" in result:
        return {"success": False, "error": result["error"], "data": result}
    
    report_id = None
    if save_report:
        report = service.create_report(
            report_type=AnalysisType.DEATH_ATTRIBUTION,
            target_type="player",
            target_id=account,
            content=result,
            summary=f"{account} 死亡归因与生存分析",
            ai_score=result.get("survival_score"),
        )
        report_id = report.id
    
    return {
        "success": True,
        "report_id": report_id,
        "analysis_type": "death_attribution",
        "data": result,
    }


@router.post("/analyze/squad-synergy", response_model=Dict[str, Any], summary="小队协同效能诊断")
async def analyze_squad_synergy_endpoint(
    fight_id: int = Query(..., description="战斗ID"),
    group_id: Optional[int] = Query(None, description="指定小队编号（可选，默认分析所有小队）"),
    save_report: bool = Query(True, description="是否保存报告"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI小队协同效能诊断
    
    分析小队（Group）内部的协同效能，评估Buff互补性、角色配比和战术执行。
    
    诊断维度：
    - 角色识别（输出/辅助/控制/坦克）
    - Buff互补分析（急速/敏捷/威能/治疗覆盖）
    - 小队综合指标（总伤害/总治疗/总CC）
    - 协同评分与改进建议
    """
    service = AIAnalysisService(db)
    result = await service.analyze_squad_synergy(fight_id, group_id)
    
    if "error" in result:
        return {"success": False, "error": result["error"], "data": result}
    
    report_id = None
    if save_report:
        report = service.create_report(
            report_type=AnalysisType.SQUAD_SYNERGY,
            target_type="fight",
            target_id=str(fight_id),
            content=result,
            summary=f"战斗 {fight_id} 小队协同诊断",
            ai_score=result["squads"][0].get("synergy_score") if result.get("squads") else 0,
        )
        report_id = report.id
    
    return {
        "success": True,
        "report_id": report_id,
        "analysis_type": "squad_synergy",
        "data": result,
    }


@router.post("/analyze/build-execution", response_model=Dict[str, Any], summary="Build执行效能验证")
async def analyze_build_execution_endpoint(
    account: str = Query(..., description="玩家账号"),
    build_id: Optional[int] = Query(None, description="Build ID（可选，用于理论对比）"),
    fight_id: Optional[int] = Query(None, description="指定战斗ID（可选）"),
    save_report: bool = Query(True, description="是否保存报告"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI Build执行效能验证
    
    验证玩家实际战斗表现与Build设计意图的匹配度，识别执行层面的问题。
    
    验证项：
    - Build类型推断（直伤/症状/辅助/坦克）
    - 理论性能 vs 实际表现差距
    - 装备/食物/扳手配置检查
    - 技能施放活跃度
    """
    service = AIAnalysisService(db)
    result = await service.analyze_build_execution(account, build_id, fight_id)
    
    if "error" in result:
        return {"success": False, "error": result["error"], "data": result}
    
    report_id = None
    if save_report:
        report = service.create_report(
            report_type=AnalysisType.BUILD_EXECUTION,
            target_type="player",
            target_id=account,
            content=result,
            summary=f"{account} Build执行验证",
            ai_score=result.get("execution_score"),
        )
        report_id = report.id
    
    return {
        "success": True,
        "report_id": report_id,
        "analysis_type": "build_execution",
        "data": result,
    }


@router.post("/analyze/critical-moments", response_model=Dict[str, Any], summary="战斗关键片段复盘")
async def analyze_critical_moments_endpoint(
    fight_id: int = Query(..., description="战斗ID"),
    account: Optional[str] = Query(None, description="指定玩家（可选，默认分析全队）"),
    save_report: bool = Query(True, description="是否保存报告"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    """
    AI战斗关键片段复盘
    
    识别战斗中的关键片段（开场爆发/危机时刻/收尾决战/输出峰值/辅助高光），
    并对每个关键时刻的玩家表现进行评估。
    
    关键片段类型：
    - 开场爆发期（前20%时间）
    - 危机时刻（死亡集中时段）
    - 收尾决战（最后15%时间）
    - 输出峰值（DPS最高窗口）
    - 辅助高光（治疗/复活突出时段）
    """
    service = AIAnalysisService(db)
    result = await service.analyze_critical_moments(fight_id, account)
    
    if "error" in result:
        return {"success": False, "error": result["error"], "data": result}
    
    report_id = None
    if save_report:
        report = service.create_report(
            report_type=AnalysisType.CRITICAL_MOMENTS,
            target_type="fight",
            target_id=str(fight_id),
            content=result,
            summary=f"战斗 {fight_id} 关键片段复盘",
        )
        report_id = report.id
    
    return {
        "success": True,
        "report_id": report_id,
        "analysis_type": "critical_moments",
        "data": result,
    }
