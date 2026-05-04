# -*- coding: utf-8 -*-
# 模块功能：AI提示词模板管理与响应优化
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01
# 依赖说明：无

import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class AnalysisType(str, Enum):
    FIGHT_ANALYSIS = "fight_analysis"
    SKILL_ROTATION = "skill_rotation"
    BUILD_OPTIMIZATION = "build_optimization"
    TREND_ANALYSIS = "trend_analysis"
    TEAM_INSIGHTS = "team_insights"


class ResponseFormat(str, Enum):
    JSON = "json"
    TEXT = "text"
    HTML = "html"


class PromptTemplate:
    """提示词模板"""

    def __init__(
        self,
        template_id: str,
        system_prompt: str,
        user_prompt_template: str,
        analysis_type: AnalysisType,
        response_format: ResponseFormat = ResponseFormat.JSON,
        output_schema: Optional[Dict] = None,
    ):
        self.template_id = template_id
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.analysis_type = analysis_type
        self.response_format = response_format
        self.output_schema = output_schema

    def format_user_prompt(self, **kwargs) -> str:
        """格式化用户提示词"""
        try:
            return self.user_prompt_template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"提示词模板缺少变量: {e}")
            return self.user_prompt_template

    def to_messages(self, **kwargs) -> List[Dict]:
        """转换为消息列表"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.format_user_prompt(**kwargs)},
        ]


class PromptTemplateRegistry:
    """提示词模板注册表"""

    _templates: Dict[str, PromptTemplate] = {}

    @classmethod
    def register(cls, template: PromptTemplate) -> None:
        """注册模板"""
        cls._templates[template.template_id] = template
        logger.info(f"提示词模板已注册: {template.template_id}")

    @classmethod
    def get(cls, template_id: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return cls._templates.get(template_id)

    @classmethod
    def get_by_analysis_type(cls, analysis_type: AnalysisType) -> List[PromptTemplate]:
        """根据分析类型获取模板"""
        return [t for t in cls._templates.values() if t.analysis_type == analysis_type]

    @classmethod
    def list_all(cls) -> Dict[str, PromptTemplate]:
        """获取所有模板"""
        return cls._templates.copy()


# ==================== 预定义提示词模板 ====================

FIGHT_ANALYSIS_SYSTEM = """你是激战2 WvW战场的专业战术分析师，负责分析团队战斗数据。
你的回答应该专业、准确、实用，所有建议都应该针对WvW战斗场景。
请以JSON格式输出分析结果，包含以下字段：
{
    "summary": "战斗整体总结",
    "team_strengths": ["优势1", "优势2"],
    "team_weaknesses": ["劣势1", "劣势2"],
    "buff_analysis": ["buff覆盖分析"],
    "cc_analysis": ["控制技能分析"],
    "skill_rotation_notes": ["技能循环建议"],
    "recommendations": ["具体改进建议"],
    "priority_score": 0-100的优先级评分,
    "ai_score": 0-100的整体评分
}"""

FIGHT_ANALYSIS_USER = """请分析以下战斗数据:
战斗时长: {duration}秒
总伤害: {total_damage}
总治疗: {total_healing}
击杀数: {kills}
死亡数: {deaths}
参与成员: {players}
详细数据摘要: {data_summary}

请给出专业的WvW战斗分析报告。"""

# 注册战斗分析模板
PromptTemplateRegistry.register(
    PromptTemplate(
        template_id="fight_analysis_v1",
        system_prompt=FIGHT_ANALYSIS_SYSTEM,
        user_prompt_template=FIGHT_ANALYSIS_USER,
        analysis_type=AnalysisType.FIGHT_ANALYSIS,
        response_format=ResponseFormat.JSON,
    )
)

SKILL_ROTATION_SYSTEM = """你是激战2技能循环优化专家，精通各职业的技能循环和操作技巧。
请分析玩家的技能使用数据，找出问题并给出优化建议。
输出格式为JSON:
{
    "total_events": 总事件数,
    "mistake_count": 失误数,
    "burst_count": 爆发次数,
    "rotation_score": 0-100评分,
    "mistakes": [
        {
            "type": "missed_skill|wrong_order|timing|energy",
            "severity": "high|medium|low",
            "description": "问题描述",
            "skill": "技能名称",
            "timestamp": 时间戳
        }
    ],
    "suggestions": ["建议1", "建议2"],
    "optimal_rotation": "最优循环描述"
}"""

SKILL_ROTATION_USER = """请分析以下技能循环数据:
职业: {profession}
专精: {specialization}
技能事件: {skill_events}
目标DPS: {target_dps}
实际DPS: {actual_dps}

请给出技能循环的优化建议。"""

PromptTemplateRegistry.register(
    PromptTemplate(
        template_id="skill_rotation_v1",
        system_prompt=SKILL_ROTATION_SYSTEM,
        user_prompt_template=SKILL_ROTATION_USER,
        analysis_type=AnalysisType.SKILL_ROTATION,
        response_format=ResponseFormat.JSON,
    )
)

BUILD_OPTIMIZATION_SYSTEM = """你是激战2 Build配置专家，精通WvW场景下的Build优化。
请分析Build配置，给出适配WvW的优化建议。
输出格式为JSON:
{
    "current_build": {
        "profession": "职业",
        "build_name": "配置名称",
        "weapons": ["武器1", "武器2"],
        "traits": ["特性1"],
        "stats": "属性配置"
    },
    "wvw_appropriateness": 0-100评分,
    "strengths": ["优势1"],
    "weaknesses": ["劣势1"],
    "suggestions": ["具体建议"],
    "alternative_builds": [
        {
            "name": "备选配置名称",
            "description": "描述",
            "fit_score": 0-100适配度
        }
    ]
}"""

BUILD_OPTIMIZATION_USER = """请分析以下Build配置:
职业: {profession}
Build名称: {build_name}
武器: {weapons}
特性: {traits}
符文: {runes}
食物: {food}
属性: {stats}
主要用途: {use_case}

请给出针对WvW场景的优化建议。"""

PromptTemplateRegistry.register(
    PromptTemplate(
        template_id="build_optimization_v1",
        system_prompt=BUILD_OPTIMIZATION_SYSTEM,
        user_prompt_template=BUILD_OPTIMIZATION_USER,
        analysis_type=AnalysisType.BUILD_OPTIMIZATION,
        response_format=ResponseFormat.JSON,
    )
)

TREND_ANALYSIS_SYSTEM = """你是激战2数据分析专家，负责分析团队的战斗趋势。
输出格式为JSON:
{
    "data_points": 数据点数,
    "total_damage": 总伤害,
    "total_kills": 总击杀,
    "avg_duration": 平均时长,
    "trend": "上升|稳定|下降",
    "trend_confidence": 0-100置信度,
    "predictions": ["预测1"],
    "anomalies": [
        {
            "type": "anomaly_type",
            "description": "描述",
            "timestamp": 时间
        }
    ],
    "insights": ["洞察1"],
    "recommendations": ["建议1"]
}"""

TREND_ANALYSIS_USER = """请分析以下历史战斗数据:
战斗数量: {fight_count}
时间范围: {time_range}
数据摘要: {data_summary}

请给出趋势分析和预测。"""

PromptTemplateRegistry.register(
    PromptTemplate(
        template_id="trend_analysis_v1",
        system_prompt=TREND_ANALYSIS_SYSTEM,
        user_prompt_template=TREND_ANALYSIS_USER,
        analysis_type=AnalysisType.TREND_ANALYSIS,
        response_format=ResponseFormat.JSON,
    )
)


class ResponseOptimizer:
    """AI响应优化器"""

    @staticmethod
    def parse_json_response(content: str) -> Optional[Dict]:
        """解析JSON响应"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            try:
                # 查找第一个 { 和最后一个 }
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            # 尝试修复常见的JSON格式问题
            try:
                fixed = ResponseOptimizer._fix_common_json_issues(content)
                return json.loads(fixed)
            except Exception:
                pass

        logger.warning("无法解析AI响应为JSON")
        return None

    @staticmethod
    def _fix_common_json_issues(content: str) -> str:
        """修复常见的JSON格式问题"""
        # 修复换行问题
        content = re.sub(r"[\r\n]", " ", content)
        # 修复单引号问题
        content = content.replace("'", '"')
        # 修复尾部逗号
        content = re.sub(r",\s*([}\]])", r"\1", content)
        return content

    @staticmethod
    def validate_response_schema(content: Dict, schema: Dict) -> bool:
        """验证响应是否符合Schema"""
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in content:
                logger.warning(f"响应缺少必填字段: {field}")
                return False
        return True

    @staticmethod
    def optimize_text_response(content: str) -> str:
        """优化文本响应"""
        # 移除多余的空白
        content = re.sub(r"\s+", " ", content).strip()
        # 规范化标点符号
        content = re.sub(r"，", "，", content)
        content = re.sub(r"。", "。", content)
        return content

    @staticmethod
    def extract_key_info(content: Dict, key_map: Dict[str, str]) -> Dict:
        """提取关键信息"""
        result = {}
        for target_key, source_key in key_map.items():
            if source_key in content:
                result[target_key] = content[source_key]
        return result


class ResponseValidator:
    """响应验证器"""

    @staticmethod
    def has_required_content(content: str, min_length: int = 10) -> bool:
        """检查是否有足够的内容"""
        if not content or len(content.strip()) < min_length:
            logger.warning("响应内容过短")
            return False
        return True

    @staticmethod
    def contains_relevant_keywords(content: str, keywords: List[str]) -> float:
        """检查是否包含相关关键词，返回匹配分数"""
        if not keywords:
            return 1.0

        content_lower = content.lower()
        matched = sum(1 for kw in keywords if kw.lower() in content_lower)
        return matched / len(keywords)

    @staticmethod
    def check_quality(content: Dict, expected_type: str) -> Dict[str, Any]:
        """检查响应质量"""
        quality_metrics = {
            "is_valid": True,
            "completeness_score": 1.0,
            "consistency_score": 1.0,
            "relevance_score": 1.0,
        }

        # 检查完整性
        expected_fields = {
            "fight_analysis": [
                "summary",
                "team_strengths",
                "team_weaknesses",
                "recommendations",
            ],
            "skill_rotation": ["rotation_score", "mistakes", "suggestions"],
            "build_optimization": ["wvw_appropriateness", "suggestions"],
        }

        fields = expected_fields.get(expected_type, [])
        missing = [f for f in fields if f not in content]
        if missing:
            quality_metrics["completeness_score"] = 1 - len(missing) / len(fields)
            quality_metrics["is_valid"] = quality_metrics["completeness_score"] >= 0.7

        return quality_metrics


class ResponseAdjuster:
    """响应调整器 - 根据规则动态优化"""

    # 调整规则
    ADJUSTMENT_RULES = {
        "wvw_context": {
            "add_keywords": ["WvW", "战场", "团战", "公会", "战术"],
            "remove_keywords": ["PvE", "副本", "碎层", "PvP"],
        },
        "tone_adjustment": {"professional": True, "friendly": False, "concise": True},
        "scoring_rules": {
            "damage_weight": 0.35,
            "survival_weight": 0.25,
            "support_weight": 0.25,
            "other_weight": 0.15,
        },
    }

    @classmethod
    def apply_rules(cls, content: Dict, analysis_type: str) -> Dict:
        """应用调整规则"""
        result = content.copy()

        # 添加WvW上下文信息
        if analysis_type in ["fight_analysis", "build_optimization"]:
            result = cls._ensure_wvw_context(result)

        # 调整评分逻辑
        if "ai_score" in result or "rotation_score" in result:
            result = cls._adjust_scoring(result, analysis_type)

        # 优化建议内容
        if "recommendations" in result or "suggestions" in result:
            result = cls._optimize_suggestions(result)

        return result

    @classmethod
    def _ensure_wvw_context(cls, content: Dict) -> Dict:
        """确保有WvW相关内容"""
        if "recommendations" in content:
            recs = content["recommendations"]
            if not any("WvW" in r or "战场" in r or "团战" in r for r in recs):
                recs.append("建议根据WvW团战场景调整战术")
        return content

    @classmethod
    def _adjust_scoring(cls, content: Dict, analysis_type: str) -> Dict:
        """调整评分逻辑"""
        score_key = "ai_score" if "ai_score" in content else "rotation_score"
        if score_key not in content:
            return content

        original_score = content[score_key]

        # 根据战场表现微调
        if "team_strengths" in content:
            strength_bonus = min(len(content["team_strengths"]) * 2, 10)
            content[score_key] = min(100, original_score + strength_bonus)

        return content

    @classmethod
    def _optimize_suggestions(cls, content: Dict) -> Dict:
        """优化建议内容"""
        key = "recommendations" if "recommendations" in content else "suggestions"
        if key not in content:
            return content

        suggestions = content[key]

        # 确保建议具体且可操作
        optimized = []
        for s in suggestions:
            if len(s) < 10:
                s = f"建议: {s}"
            if not any(s.endswith(p) for p in ["。", "！", "？", ".", "!", "?"]):
                s += "。"
            optimized.append(s)

        content[key] = optimized
        return content
