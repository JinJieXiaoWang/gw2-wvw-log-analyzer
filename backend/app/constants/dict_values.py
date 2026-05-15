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
# 角色定位 (role)
# =============================================================================

class RoleType(str, Enum):
    """角色定位类型"""

    DPS = "dps"
    SUPPORT = "support"
    TANK = "tank"
    CONDITION = "condition"
    HEALING = "healing"
    CONTROL = "control"
    UTILITY = "utility"

    @classmethod
    def get_default(cls) -> str:
        """获取默认角色类型"""
        return cls.DPS.value

    @classmethod
    def is_damage_role(cls, role_type: str) -> bool:
        """是否为输出向角色"""
        return role_type in (cls.DPS.value, cls.CONDITION.value)

    @classmethod
    def is_support_role(cls, role_type: str) -> bool:
        """是否为辅助向角色"""
        return role_type in (cls.SUPPORT.value, cls.HEALING.value, cls.TANK.value)


# =============================================================================
# 通用状态 (sys_normal_disable)
# =============================================================================

class NormalDisable(int, Enum):
    """通用启用/禁用状态"""

    ENABLED = 0
    DISABLED = 1

    @classmethod
    def is_enabled(cls, status: int) -> bool:
        return status == cls.ENABLED.value

    @classmethod
    def is_disabled(cls, status: int) -> bool:
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


# 评分等级阈值（与 grade_level 字典对应，后续可从配置表加载）
GRADE_THRESHOLDS = [
    (90, GradeLevel.S),
    (80, GradeLevel.A),
    (70, GradeLevel.B),
    (60, GradeLevel.C),
    (40, GradeLevel.D),
]

# 评分等级中文标签映射
GRADE_LABELS = {
    GradeLevel.S: "S级",
    GradeLevel.A: "A级",
    GradeLevel.B: "B级",
    GradeLevel.C: "C级",
    GradeLevel.D: "D级",
    GradeLevel.F: "F级",
}


def get_grade(score: float) -> str:
    """根据分数获取等级"""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade.value
    return GradeLevel.F.value


def get_grade_label(grade: str) -> str:
    """根据等级获取中文标签"""
    return GRADE_LABELS.get(grade.lower(), grade.upper())


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
