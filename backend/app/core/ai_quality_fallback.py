# -*- coding: utf-8 -*-
# 模块功能：AI质量评估与降级处理
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01
# 依赖说明：无

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.config.ai_config import ai_config
from app.core.ai_model_client import AIResponse, RequestStatus
from app.utils.logger import logger


class QualityMetric(str, Enum):
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    RESPONSE_TIME = "response_time"


class QualityLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class QualityAssessment:
    """质量评估结果"""

    overall_score: float
    metrics: Dict[QualityMetric, float]
    level: QualityLevel
    passed: bool
    issues: List[str]
    suggestions: List[str]
    timestamp: float

    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "metrics": {k.value: v for k, v in self.metrics.items()},
            "level": self.level.value,
            "passed": self.passed,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp,
        }


class QualityEvaluator:
    """AI响应质量评估器"""

    # 评分标准
    SCORING_CRITERIA = {
        QualityMetric.ACCURACY: {
            "weight": 0.3,
            "threshold": ai_config.AI_MIN_ACCURACY_SCORE,
            "description": "内容准确性",
        },
        QualityMetric.RELEVANCE: {
            "weight": 0.3,
            "threshold": ai_config.AI_MIN_RELEVANCE_SCORE,
            "description": "内容相关性",
        },
        QualityMetric.COMPLETENESS: {
            "weight": 0.2,
            "threshold": 0.6,
            "description": "内容完整性",
        },
        QualityMetric.CONSISTENCY: {
            "weight": 0.1,
            "threshold": 0.7,
            "description": "内容一致性",
        },
        QualityMetric.RESPONSE_TIME: {
            "weight": 0.1,
            "threshold": ai_config.AI_MAX_RESPONSE_TIME,
            "description": "响应时间",
        },
    }

    @classmethod
    def evaluate(
        cls,
        response: AIResponse,
        expected_type: str = "fight_analysis",
        context: Optional[Dict] = None,
    ) -> QualityAssessment:
        """
        评估AI响应质量

        参数:
            response: AI响应对象
            expected_type: 期望的分析类型
            context: 上下文信息
        """
        metrics = {}
        issues = []
        suggestions = []

        # 1. 基本状态检查
        if not response.is_success:
            return cls._create_failed_assessment(response.error or "请求失败")

        # 2. 评估响应时间
        time_score = cls._evaluate_response_time(response.response_time)
        metrics[QualityMetric.RESPONSE_TIME] = time_score
        if time_score < cls.SCORING_CRITERIA[QualityMetric.RESPONSE_TIME]["threshold"]:
            issues.append(f"响应时间过长: {response.response_time:.2f}秒")
            suggestions.append("考虑使用更快的模型或简化请求")

        # 3. 评估内容完整性
        completeness_score = cls._evaluate_completeness(response.content, expected_type)
        metrics[QualityMetric.COMPLETENESS] = completeness_score
        if (
            completeness_score
            < cls.SCORING_CRITERIA[QualityMetric.COMPLETENESS]["threshold"]
        ):
            issues.append("内容不够完整")
            suggestions.append("检查提示词是否完整")

        # 4. 评估内容一致性
        consistency_score = cls._evaluate_consistency(response.content)
        metrics[QualityMetric.CONSISTENCY] = consistency_score
        if (
            consistency_score
            < cls.SCORING_CRITERIA[QualityMetric.CONSISTENCY]["threshold"]
        ):
            issues.append("内容存在不一致")

        # 5. 评估相关性
        relevance_score = cls._evaluate_relevance(
            response.content, expected_type, context
        )
        metrics[QualityMetric.RELEVANCE] = relevance_score
        if relevance_score < cls.SCORING_CRITERIA[QualityMetric.RELEVANCE]["threshold"]:
            issues.append("内容与请求相关性不足")
            suggestions.append("优化提示词以获得更相关的回答")

        # 6. 评估准确性（基于内容的合理性）
        accuracy_score = cls._evaluate_accuracy(response.content, expected_type)
        metrics[QualityMetric.ACCURACY] = accuracy_score
        if accuracy_score < cls.SCORING_CRITERIA[QualityMetric.ACCURACY]["threshold"]:
            issues.append("内容准确性待验证")
            suggestions.append("人工审核重要建议")

        # 计算总分数
        overall_score = cls._calculate_overall_score(metrics)

        # 确定质量等级
        level = cls._determine_quality_level(overall_score)

        # 检查是否通过
        passed = cls._check_passed(metrics)

        assessment = QualityAssessment(
            overall_score=overall_score,
            metrics=metrics,
            level=level,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            timestamp=time.time(),
        )

        # 更新响应中的评分
        response.quality_score = accuracy_score
        response.relevance_score = relevance_score

        logger.info(f"质量评估完成: {level.value}, 总分: {overall_score:.2f}")
        return assessment

    @classmethod
    def _evaluate_response_time(cls, response_time: float) -> float:
        """评估响应时间"""
        threshold = ai_config.AI_MAX_RESPONSE_TIME
        if response_time <= 5:
            return 1.0
        elif response_time <= threshold:
            return 1.0 - (response_time - 5) / (threshold - 5) * 0.3
        else:
            return max(0.0, 1.0 - (response_time - threshold) / 30.0)

    @classmethod
    def _evaluate_completeness(cls, content: str, expected_type: str) -> float:
        """评估内容完整性"""
        if not content or len(content.strip()) < 20:
            return 0.0

        content_lower = content.lower()
        required_keywords = {
            "fight_analysis": [
                "分析",
                "建议",
                "优势",
                "劣势",
                "recommendations",
                "suggestions",
            ],
            "skill_rotation": [
                "技能",
                "循环",
                "失误",
                "优化",
                "skill",
                "rotation",
                "mistake",
            ],
            "build_optimization": ["配置", "build", "建议", "优化", "特性", "装备"],
        }

        keywords = required_keywords.get(expected_type, [])
        if not keywords:
            return 0.5

        matched = sum(1 for kw in keywords if kw in content_lower)
        return min(1.0, matched / max(len(keywords), 1))

    @classmethod
    def _evaluate_consistency(cls, content: str) -> float:
        """评估内容一致性"""
        # 检查是否有明显的矛盾
        if ("伤害很高" in content and "伤害不足" in content) or (
            "治疗充足" in content and "治疗缺乏" in content
        ):
            return 0.3

        # 检查内容结构的一致性
        if len(content) > 1000 and content.count('"') % 2 != 0:
            return 0.5

        return 0.9

    @classmethod
    def _evaluate_relevance(
        cls, content: str, expected_type: str, context: Optional[Dict]
    ) -> float:
        """评估内容相关性"""
        relevance_keywords = {
            "fight_analysis": [
                "激战2",
                "wvw",
                "战场",
                "战斗",
                "伤害",
                "治疗",
                "buff",
                "技能",
            ],
            "skill_rotation": ["技能", "循环", "职业", "dps", "爆发", "操作"],
            "build_optimization": ["配置", "build", "装备", "特性", "符文", "属性"],
            "trend_analysis": ["趋势", "分析", "预测", "数据"],
        }

        keywords = relevance_keywords.get(expected_type, [])
        content_lower = content.lower()

        if not keywords:
            return 0.5

        matched = sum(1 for kw in keywords if kw.lower() in content_lower)
        relevance_score = min(1.0, matched / min(len(keywords), 5))

        # 如果有上下文信息，结合上下文评估
        if context:
            context_terms = [
                str(v).lower() for v in context.values() if isinstance(v, str)
            ]
            context_matches = sum(1 for term in context_terms if term in content_lower)
            if context_terms:
                relevance_score = (
                    relevance_score + context_matches / len(context_terms)
                ) / 2

        return relevance_score

    @classmethod
    def _evaluate_accuracy(cls, content: str, expected_type: str) -> float:
        """评估内容准确性"""
        # 基本检查
        if "抱歉" in content or "不知道" in content or "无法" in content:
            return 0.3

        # 检查是否有数值合理性
        import re

        numbers = re.findall(r"\d+\.?\d*", content)
        if len(numbers) > 0:
            # 检查是否有异常大的数值
            suspicious = sum(1 for n in numbers if float(n) > 1000000)
            if suspicious > 0:
                return 0.6

        # 检查是否包含合理的游戏术语
        game_terms = [
            "守护",
            "战士",
            "元素",
            "幻术",
            "盗贼",
            "游侠",
            "死灵",
            "工程",
            "魂武",
        ]
        content_lower = content.lower()
        has_terms = any(term in content_lower for term in game_terms)

        return 0.8 if has_terms else 0.6

    @classmethod
    def _calculate_overall_score(cls, metrics: Dict[QualityMetric, float]) -> float:
        """计算总分数"""
        total = 0.0
        total_weight = 0.0

        for metric, value in metrics.items():
            criteria = cls.SCORING_CRITERIA.get(metric)
            if criteria:
                weight = criteria["weight"]
                total += value * weight
                total_weight += weight

        return total / max(total_weight, 1.0) if total_weight > 0 else 0.0

    @classmethod
    def _determine_quality_level(cls, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.4:
            return QualityLevel.POOR
        else:
            return QualityLevel.INVALID

    @classmethod
    def _check_passed(cls, metrics: Dict[QualityMetric, float]) -> bool:
        """检查是否通过评估"""
        for metric, value in metrics.items():
            criteria = cls.SCORING_CRITERIA.get(metric)
            if criteria and value < criteria["threshold"]:
                return False
        return True

    @classmethod
    def _create_failed_assessment(cls, error: str) -> QualityAssessment:
        """创建失败的评估"""
        return QualityAssessment(
            overall_score=0.0,
            metrics={m: 0.0 for m in QualityMetric},
            level=QualityLevel.INVALID,
            passed=False,
            issues=[error],
            suggestions=["检查模型配置和网络连接"],
            timestamp=time.time(),
        )


class FallbackStrategy(str, Enum):
    """降级策略"""

    PROVIDER_SWITCH = "provider_switch"
    CACHE_FALLBACK = "cache_fallback"
    RULE_BASED = "rule_based"
    SIMPLIFIED = "simplified"


class FallbackHandler:
    """降级处理管理器"""

    def __init__(self):
        self.strategies: Dict[FallbackStrategy, Callable] = {
            FallbackStrategy.PROVIDER_SWITCH: self._provider_switch_fallback,
            FallbackStrategy.CACHE_FALLBACK: self._cache_fallback,
            FallbackStrategy.RULE_BASED: self._rule_based_fallback,
            FallbackStrategy.SIMPLIFIED: self._simplified_fallback,
        }
        self.fallback_stats: Dict[str, int] = {}

    def handle_fallback(
        self,
        failed_response: AIResponse,
        request_context: Dict,
        strategy_order: Optional[List[FallbackStrategy]] = None,
    ) -> Optional[AIResponse]:
        """
        处理降级请求

        参数:
            failed_response: 失败的响应
            request_context: 请求上下文
            strategy_order: 降级策略顺序
        """
        if strategy_order is None:
            strategy_order = [
                FallbackStrategy.CACHE_FALLBACK,
                FallbackStrategy.PROVIDER_SWITCH,
                FallbackStrategy.RULE_BASED,
                FallbackStrategy.SIMPLIFIED,
            ]

        for strategy in strategy_order:
            logger.info(f"尝试降级策略: {strategy}")
            fallback_response = self.strategies[strategy](
                failed_response, request_context
            )
            if fallback_response and fallback_response.is_success:
                self._record_fallback(strategy)
                fallback_response.is_fallback = True
                logger.info(f"降级成功: {strategy}")
                return fallback_response

        logger.warning("所有降级策略均失败")
        return None

    def _provider_switch_fallback(
        self, failed_response: AIResponse, request_context: Dict
    ) -> Optional[AIResponse]:
        """提供商切换降级（在ai_model_client中已实现）"""
        # 这里主要是记录和提示
        return None

    def _cache_fallback(
        self, failed_response: AIResponse, request_context: Dict
    ) -> Optional[AIResponse]:
        """缓存降级"""
        from app.core.ai_model_client import get_cache

        cache = get_cache()
        # 尝试查找类似的缓存
        # 这里简化处理，实际可以实现更智能的缓存匹配
        logger.debug("缓存降级策略需要具体缓存键实现")
        return None

    def _rule_based_fallback(
        self, failed_response: AIResponse, request_context: Dict
    ) -> Optional[AIResponse]:
        """规则降级"""
        analysis_type = request_context.get("analysis_type", "fight_analysis")

        # 根据分析类型生成规则化响应
        if analysis_type == "fight_analysis":
            content = self._generate_rule_based_fight_analysis(request_context)
        elif analysis_type == "skill_rotation":
            content = self._generate_rule_based_skill_analysis(request_context)
        elif analysis_type == "build_optimization":
            content = self._generate_rule_based_build_analysis(request_context)
        else:
            content = self._generate_generic_fallback(request_context)

        return AIResponse(
            content=json.dumps(content, ensure_ascii=False),
            provider=failed_response.provider,
            model="rule_based_fallback",
            status=RequestStatus.SUCCESS,
            response_time=0.1,
        )

    def _simplified_fallback(
        self, failed_response: AIResponse, request_context: Dict
    ) -> Optional[AIResponse]:
        """简化降级"""
        content = {
            "summary": "由于AI服务暂时不可用，提供简化分析",
            "recommendations": ["建议检查数据完整性", "稍后再试"],
            "team_strengths": ["数据已记录"],
            "team_weaknesses": ["AI分析暂时不可用"],
            "ai_score": 50.0,
            "is_fallback": True,
        }

        return AIResponse(
            content=json.dumps(content, ensure_ascii=False),
            provider=failed_response.provider,
            model="simplified_fallback",
            status=RequestStatus.SUCCESS,
            response_time=0.05,
        )

    def _generate_rule_based_fight_analysis(self, context: Dict) -> Dict:
        """生成规则化的战斗分析"""
        total_damage = context.get("total_damage", 0)
        deaths = context.get("deaths", 0)
        kills = context.get("kills", 0)

        score = 50
        if total_damage > 1000000:
            score += 20
        if kills > 10:
            score += 15
        if deaths < 5:
            score += 10

        return {
            "summary": f"战斗数据分析: 总伤害{total_damage}, 击杀{kills}, 死亡{deaths}",
            "team_strengths": [
                "团队伤害输出" + ("较高" if total_damage > 500000 else "一般"),
                "击杀表现" + ("优秀" if kills > 10 else "尚可"),
            ],
            "team_weaknesses": ["需要注意生存" if deaths > 10 else "生存能力不错"],
            "recommendations": ["提升团队配合", "优化技能循环", "加强沟通协调"],
            "ai_score": min(100, score),
            "priority_score": 70,
        }

    def _generate_rule_based_skill_analysis(self, context: Dict) -> Dict:
        """生成规则化的技能分析"""
        return {
            "total_events": context.get("total_events", 0),
            "mistake_count": 0,
            "burst_count": 0,
            "rotation_score": 60.0,
            "mistakes": [],
            "suggestions": ["保持技能循环连贯性", "注意能量/资源管理", "优化爆发时机"],
            "optimal_rotation": "建议参考职业标准循环",
        }

    def _generate_rule_based_build_analysis(self, context: Dict) -> Dict:
        """生成规则化的Build分析"""
        return {
            "current_build": {
                "profession": context.get("profession", "未知"),
                "build_name": context.get("build_name", "未知配置"),
            },
            "wvw_appropriateness": 70.0,
            "strengths": ["配置基本完整"],
            "weaknesses": ["建议根据实战调整"],
            "suggestions": [
                "根据团队定位调整Build",
                "测试不同的装备组合",
                "关注WvW最新Meta配置",
            ],
            "alternative_builds": [],
        }

    def _generate_generic_fallback(self, context: Dict) -> Dict:
        """生成通用降级响应"""
        return {
            "summary": "服务暂时不可用，已记录您的请求",
            "recommendations": ["稍后重试", "检查数据格式", "联系管理员"],
        }

    def _record_fallback(self, strategy: FallbackStrategy) -> None:
        """记录降级使用"""
        key = strategy.value
        self.fallback_stats[key] = self.fallback_stats.get(key, 0) + 1
        logger.info(f"降级统计: {self.fallback_stats}")

    def get_stats(self) -> Dict[str, Any]:
        """获取降级统计"""
        return {
            "total_fallbacks": sum(self.fallback_stats.values()),
            "strategy_stats": self.fallback_stats.copy(),
        }


import json

_fallback_handler = FallbackHandler()


def get_fallback_handler() -> FallbackHandler:
    """获取降级处理器"""
    return _fallback_handler
