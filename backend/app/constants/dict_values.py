# -*- coding: utf-8 -*-
"""
字典业务常量模块
功能：将系统中频繁使用的字典值定义为 Enum 常量，替代硬编码字符串
使用原则：
  1. 后端代码中判断状态/类型时，优先使用本模块常量，禁止直接写死字符串
  2. 新增字典类型时，如需要在代码中判断，应同步在本模块定义对应 Enum
  3. 常量值必须与 database/init_all.py 中的种子数据保持一致

作者：系统
创建日期：2026-05-15
"""

from enum import Enum


# =============================================================================
# 批量解析任务状态 (batch_parse_task / batch_parse_task_item)
# 与 ParseStatus 不同：BatchTask 有 partial（任务级）和 retrying（子项级）
# =============================================================================

class BatchTaskStatus(str, Enum):
    """批量解析任务状态"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    RETRYING = "retrying"

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """是否为终态"""
        return status in (cls.COMPLETED.value, cls.FAILED.value, cls.PARTIAL.value)

    @classmethod
    def is_processing(cls, status: str) -> bool:
        """是否处理中"""
        return status in (cls.PROCESSING.value, cls.RETRYING.value)


# =============================================================================
# 解析状态 (parse_status)
# =============================================================================

class ParseStatus(str, Enum):
    """日志解析状态"""

    PENDING = "pending"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    PARTIAL = "partial"

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """是否为终态"""
        return status in (cls.COMPLETED.value, cls.FAILED.value, cls.PARTIAL.value)

    @classmethod
    def is_processing(cls, status: str) -> bool:
        """是否处理中"""
        return status in (cls.PARSING.value, cls.RETRYING.value)


# =============================================================================
# 通用状态 (sys_normal_disable)
# 注意：dict_value 字段为字符串类型，故使用 str Enum
# =============================================================================

class NormalDisable(str, Enum):
    """通用启用/禁用状态"""

    ENABLED = "0"
    DISABLED = "1"

    @classmethod
    def is_enabled(cls, status: str) -> bool:
        return status == cls.ENABLED.value

    @classmethod
    def is_disabled(cls, status: str) -> bool:
        return status == cls.DISABLED.value


# =============================================================================
# 是/否 (sys_yes_no)
# =============================================================================

class YesNo(str, Enum):
    """通用是/否"""

    YES = "Y"
    NO = "N"

    @classmethod
    def is_yes(cls, value: str) -> bool:
        return value == cls.YES.value


# =============================================================================
# 评分等级 (grade_level)
# =============================================================================

class GradeLevel(str, Enum):
    """评分等级"""

    S = "s"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    F = "f"

    @property
    def label(self) -> str:
        """评分等级中文标签"""
        labels = {
            "s": "S级",
            "a": "A级",
            "b": "B级",
            "c": "C级",
            "d": "D级",
            "f": "F级",
        }
        return labels.get(self.value, self.value.upper())


# 评分等级阈值（与 grade_level 字典对应，后续可从配置表加载）
GRADE_THRESHOLDS = [
    (90, GradeLevel.S),
    (80, GradeLevel.A),
    (70, GradeLevel.B),
    (60, GradeLevel.C),
    (40, GradeLevel.D),
]


def get_grade(score: float) -> str:
    """根据分数获取等级"""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade.value
    return GradeLevel.F.value


def get_grade_label(grade: str) -> str:
    """根据等级获取中文标签（从字典表读取，消灭硬编码）"""
    from app.utils.db.dict_utils import get_dict_label
    return get_dict_label("grade_level", grade.lower()) or grade.upper()


# =============================================================================
# 评分规则版本状态 (scoring_rule_status)
# =============================================================================

class ScoringRuleStatus(str, Enum):
    """评分规则版本状态"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# 菜单状态 (sys_menu_status)
# =============================================================================

class MenuStatus(str, Enum):
    """菜单状态"""

    NORMAL = "0"
    DISABLED = "1"


class MenuVisible(str, Enum):
    """菜单可见性"""

    SHOW = "0"
    HIDDEN = "1"


class MenuType(str, Enum):
    """菜单类型"""

    DIRECTORY = "M"
    MENU = "C"
    BUTTON = "F"


class MenuYesNo(int, Enum):
    """菜单是/否（用于 INTEGER 字段）"""

    NO = 0
    YES = 1


# =============================================================================
# 通知状态 (sys_notice_status)
# =============================================================================

class NoticeStatus(str, Enum):
    """通知状态"""

    NORMAL = "0"
    DISABLED = "1"


class NoticeType(str, Enum):
    """通知类型"""

    NOTICE = "1"
    ANNOUNCEMENT = "2"


# =============================================================================
# AI 分析模块 Build 类型 (ai_build_type)
# =============================================================================

class AiBuildType(str, Enum):
    """AI Build 执行分析类型"""

    POWER = "power"
    CONDI = "condi"
    SUPPORT = "support"
    TANK = "tank"


class SquadRole(str, Enum):
    """AI 小队协同分析角色类型"""

    DAMAGE = "damage"
    SUPPORT = "support"
    CONTROL = "control"
    TANK = "tank"


class CheckStatus(str, Enum):
    """AI 分析检查结果状态"""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class AiRating(str, Enum):
    """AI 分析评级"""

    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    CRITICAL = "critical"


class TrendStatus(str, Enum):
    """趋势状态"""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


class ImportanceLevel(str, Enum):
    """重要性级别"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeathCategory(str, Enum):
    """死亡归因分类"""

    FOCUSED_FIRE = "focused_fire"
    POSITIONING_ERROR = "positioning_error"
    BUFF_GAP = "buff_gap"
    COOLDOWN_MISMATCH = "cooldown_mismatch"
    HEALING_DEFICIT = "healing_deficit"
    CC_CHAIN = "cc_chain"
