# -*- coding: utf-8 -*-
"""
数据初始化核心框架

功能：提供种子数据初始化全流程的校验、重试、日志、版本控制等基础设施
不依赖外部文件，优先从 _generated.seed_modules 加载，回退到内嵌数据

作者：帅妹妹丶.8297
创建日期：2026-05-15
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import Session

from app.utils.logger import logger


# =============================================================================
# 1. 自定义异常
# =============================================================================


class InitializationError(Exception):
    """初始化失败异常——抛出后必须终止启动"""

    def __init__(
        self,
        message: str,
        step: str = "",
        error_type: str = "",
        data_snippet: Any = None,
        suggestion: str = "",
    ):
        super().__init__(message)
        self.step = step
        self.error_type = error_type
        self.data_snippet = data_snippet
        self.suggestion = suggestion
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": str(self),
            "step": self.step,
            "error_type": self.error_type,
            "timestamp": self.timestamp,
            "data_snippet": self._safe_snippet(),
            "suggestion": self.suggestion,
        }

    def _safe_snippet(self) -> Any:
        try:
            if self.data_snippet is None:
                return None
            snippet = json.dumps(self.data_snippet, ensure_ascii=False, default=str)
            if len(snippet) > 2000:
                return snippet[:2000] + "... [截断]"
            return self.data_snippet
        except Exception:
            return str(self.data_snippet)[:500]


class ValidationError(InitializationError):
    """数据校验失败"""

    def __init__(self, message: str, step: str = "", data_snippet: Any = None):
        super().__init__(
            message=message,
            step=step,
            error_type="VALIDATION_ERROR",
            data_snippet=data_snippet,
            suggestion="请检查种子数据格式是否完整，或运行 `python scripts/validate_seeds.py` 进行详细校验",
        )


class RetryExhaustedError(InitializationError):
    """重试耗尽后仍失败"""

    def __init__(self, message: str, step: str = "", attempts: int = 0, last_error: str = ""):
        super().__init__(
            message=message,
            step=step,
            error_type="RETRY_EXHAUSTED",
            data_snippet={"attempts": attempts, "last_error": last_error},
            suggestion="请检查数据库连接状态和网络稳定性，确认数据库服务正常运行",
        )


class VersionConflictError(InitializationError):
    """版本冲突——已应用的数据版本与当前不一致"""

    def __init__(self, message: str, expected: str = "", actual: str = ""):
        super().__init__(
            message=message,
            step="version_check",
            error_type="VERSION_CONFLICT",
            data_snippet={"expected": expected, "actual": actual},
            suggestion="如需强制重新初始化，请调用 API `POST /system/initialization/run?force=true`",
        )


# =============================================================================
# 2. 重试机制（纯标准库实现，不依赖 tenacity）
# =============================================================================


@dataclass
class RetryConfig:
    """重试配置"""

    max_attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (OperationalError, IntegrityError, ConnectionError, TimeoutError)
    )
    on_retry: Optional[Callable[[int, Exception, float], None]] = None


def retry_with_backoff(config: Optional[RetryConfig] = None):
    """重试装饰器——指数退避 + 抖动"""
    cfg = config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, cfg.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not any(isinstance(e, exc_cls) for exc_cls in cfg.retryable_exceptions):
                        raise
                    if attempt >= cfg.max_attempts:
                        break
                    # 指数退避 + 随机抖动
                    delay = min(
                        cfg.base_delay * (cfg.exponential_base ** (attempt - 1)),
                        cfg.max_delay,
                    )
                    jitter = os.urandom(1)[0] / 255.0 * 0.3 * delay  # 0~30% 抖动
                    sleep_time = delay + jitter
                    if cfg.on_retry:
                        cfg.on_retry(attempt, e, sleep_time)
                    else:
                        logger.warning(
                            f"[{func.__name__}] 第 {attempt} 次尝试失败: {e}，"
                            f"{sleep_time:.1f}秒后重试..."
                        )
                    time.sleep(sleep_time)
            raise RetryExhaustedError(
                message=f"{func.__name__} 在 {cfg.max_attempts} 次尝试后仍失败",
                step=func.__name__,
                attempts=cfg.max_attempts,
                last_error=str(last_exception),
            )

        return wrapper

    return decorator


# =============================================================================
# 3. 种子数据加载器（优先模块，回退文件，最后内嵌）
# =============================================================================


class SeedDataLoader:
    """种子数据加载器——三级回退策略"""

    # 种子名称到 JSON 文件路径的映射
    SEED_FILE_MAP: Dict[str, str] = {
        "sys_menu": "v1.0.0/001_sys_menu.json",
        "sys_dict_type": "v1.0.0/002_sys_dict_type.json",
        "sys_dict_data": "v1.0.0/003_sys_dict_data.json",
        "gw_role_type": "v1.0.0/004_gw_role_type.json",
        "gw_profession": "v1.0.0/005_gw_profession.json",
        "gw_elite_specialization": "v1.0.0/006_gw_elite_specialization.json",
        "game_static_bdcode_skills": "v1.0.0/007_game_static_data_bdcode_skills.json",
        "game_static_bdcode_specializations": "v1.0.0/007_game_static_data_bdcode_specializations.json",
        "game_static_bdcode_traits": "v1.0.0/007_game_static_data_bdcode_traits.json",
        "game_static_skill_palettes": "v1.0.0/007_game_static_data_skill_palettes.json",
        "game_static_buffs": "v1.0.0/007_game_static_data_buffs.json",
        "builds_initial": "v1.0.0/007_game_static_data_builds_initial_data.json",
    }

    @classmethod
    def load(cls, seed_name: str, fallback_data: Any = None) -> Any:
        """
        三级回退加载种子数据：
        1. _generated.seed_modules (运行时零依赖)
        2. seeds/ 目录下的原始 JSON 文件
        3. 调用方提供的 fallback_data
        """
        errors: List[str] = []

        # Level 1: 从构建模块加载
        try:
            from app.data._generated.seed_modules import load_seed as _module_load
            file_path = cls.SEED_FILE_MAP.get(seed_name)
            if file_path:
                data = _module_load(file_path)
                logger.debug(f"[SeedLoader] 从 seed_modules 加载 '{seed_name}'")
                return data.get("data", data)
        except ImportError:
            errors.append("seed_modules 未生成")
        except Exception as e:
            errors.append(f"seed_modules 加载失败: {e}")

        # Level 2: 从原始 JSON 文件加载
        try:
            file_path = cls.SEED_FILE_MAP.get(seed_name)
            if file_path:
                full_path = os.path.join("backend/app/data/seeds", file_path)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    logger.debug(f"[SeedLoader] 从 JSON 文件加载 '{seed_name}'")
                    return data.get("data", data)
        except Exception as e:
            errors.append(f"JSON 文件加载失败: {e}")

        # Level 3: 回退数据
        if fallback_data is not None:
            logger.warning(
                f"[SeedLoader] '{seed_name}' 回退到内嵌数据（原因: {'; '.join(errors)}）"
            )
            return fallback_data

        raise InitializationError(
            message=f"无法加载种子数据 '{seed_name}'",
            step="seed_load",
            error_type="SEED_LOAD_FAILED",
            data_snippet={"seed_name": seed_name, "errors": errors},
            suggestion="请运行 `python scripts/build_seeds.py` 生成 seed_modules.py",
        )


# =============================================================================
# 4. 强制校验器
# =============================================================================


class SeedDataValidator:
    """种子数据强制校验器"""

    # 各种子数据期望的必填字段（与实际 JSON 结构匹配）
    REQUIRED_FIELDS: Dict[str, List[str]] = {
        "sys_menu": ["menu_name", "parent_id", "order_num"],
        "sys_dict_type": ["dict_name", "dict_type"],
        # sys_dict_data 特殊结构：{"dict_type": [[value, label, color], ...]}
        "gw_role_type": ["role_key", "role_name"],
        "gw_profession": ["profession_key", "profession_name", "icon"],
        "gw_elite_specialization": ["spec_key", "spec_name", "profession_key"],
        "builds_initial": ["name", "profession", "elite_spec"],
    }

    # 字段类型期望（与实际 JSON 结构匹配）
    FIELD_TYPES: Dict[str, Dict[str, type]] = {
        "sys_menu": {
            "menu_name": str,
            "parent_id": int,
            "order_num": int,
            "status": (str, int),  # 允许 str 或 int
        },
        "sys_dict_type": {
            "dict_name": str,
            "dict_type": str,
            "status": (str, int),  # 允许 str 或 int
        },
        "gw_profession": {
            "profession_key": str,
            "profession_name": str,
            "icon": str,
        },
        "gw_role_type": {
            "role_key": str,
            "role_name": str,
        },
        "gw_elite_specialization": {
            "spec_key": str,
            "spec_name": str,
            "profession_key": str,
        },
    }

    @classmethod
    def validate_seed(cls, seed_name: str, data: Any) -> List[str]:
        """
        校验种子数据，返回错误列表（空列表表示通过）
        """
        errors: List[str] = []

        # 1. 基础结构校验
        if data is None:
            errors.append(f"种子 '{seed_name}' 数据为 None")
            return errors

        # sys_dict_data 特殊结构：{"dict_type": [[value, label, color], ...]}
        if seed_name == "sys_dict_data":
            return cls._validate_dict_data(data)

        if not isinstance(data, list):
            errors.append(f"种子 '{seed_name}' 期望 list 类型，实际为 {type(data).__name__}")
            return errors

        if len(data) == 0:
            logger.info(f"[Validator] '{seed_name}' 种子数据为空列表，跳过字段校验")
            return errors

        # 2. 必填字段校验
        required = cls.REQUIRED_FIELDS.get(seed_name, [])
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                errors.append(f"[{seed_name}][{idx}] 期望 dict 类型，实际为 {type(item).__name__}")
                continue
            for field_name in required:
                if field_name not in item:
                    errors.append(f"[{seed_name}][{idx}] 缺少必填字段 '{field_name}'")
                elif item[field_name] is None or item[field_name] == "":
                    errors.append(f"[{seed_name}][{idx}] 必填字段 '{field_name}' 为空值")

        # 3. 字段类型校验（抽样前3条）
        type_expectations = cls.FIELD_TYPES.get(seed_name, {})
        for idx, item in enumerate(data[:3]):
            if not isinstance(item, dict):
                continue
            for field_name, expected_type in type_expectations.items():
                if field_name not in item:
                    continue
                val = item[field_name]
                if val is None:
                    continue
                # 支持元组类型的期望（如 (str, int) 表示允许多种类型）
                if isinstance(expected_type, tuple):
                    if not any(isinstance(val, t) for t in expected_type):
                        type_names = "/".join(t.__name__ for t in expected_type)
                        errors.append(
                            f"[{seed_name}][{idx}] 字段 '{field_name}' 期望 {type_names}，"
                            f"实际为 {type(val).__name__}({val!r})"
                        )
                elif expected_type is int:
                    if not isinstance(val, int) and not (
                        isinstance(val, str) and val.lstrip("-").isdigit()
                    ):
                        errors.append(
                            f"[{seed_name}][{idx}] 字段 '{field_name}' 期望 int，"
                            f"实际为 {type(val).__name__}({val!r})"
                        )
                elif not isinstance(val, expected_type):
                    errors.append(
                        f"[{seed_name}][{idx}] 字段 '{field_name}' 期望 {expected_type.__name__}，"
                        f"实际为 {type(val).__name__}({val!r})"
                    )

        return errors

    @classmethod
    def _validate_dict_data(cls, data: Any) -> List[str]:
        """校验 sys_dict_data 的特殊结构"""
        errors: List[str] = []
        if not isinstance(data, dict):
            errors.append(f"sys_dict_data 期望 dict 类型，实际为 {type(data).__name__}")
            return errors
        for dict_type, items in data.items():
            if not isinstance(items, list):
                errors.append(f"sys_dict_data['{dict_type}'] 期望 list 类型")
                continue
            for idx, item in enumerate(items):
                if not isinstance(item, (list, tuple)):
                    errors.append(f"sys_dict_data['{dict_type}'][{idx}] 期望 tuple/list")
                    continue
                if len(item) < 3:
                    errors.append(
                        f"sys_dict_data['{dict_type}'][{idx}] 至少需要3个元素 (value, label, color)"
                    )
        return errors

    @classmethod
    def _validate_dict_references(cls, dict_data: Any) -> List[str]:
        """校验字典数据引用的 dict_type 是否存在"""
        errors: List[str] = []
        if not isinstance(dict_data, dict):
            return errors
        try:
            from app.data._generated.seed_modules import load_seed as _module_load
            dt_seed = _module_load("v1.0.0/002_sys_dict_type.json")
            dt_data = dt_seed.get("data", dt_seed)
            valid_types = {str(item.get("dict_type", "")) for item in dt_data if isinstance(item, dict)}
        except Exception:
            return errors

        for dict_type in dict_data.keys():
            if dict_type and dict_type not in valid_types:
                errors.append(
                    f"[sys_dict_data] dict_type '{dict_type}' 在 sys_dict_type 种子中不存在"
                )
        return errors

    @classmethod
    def validate_all(cls, seeds: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        批量校验所有种子数据
        Returns: (errors, warnings)
        """
        all_errors: List[str] = []
        all_warnings: List[str] = []

        for seed_name, data in seeds.items():
            errors = cls.validate_seed(seed_name, data)
            if errors:
                all_errors.extend(errors)
            # 记录统计信息
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict):
                count = len(data)
            else:
                count = 0
            logger.info(f"[Validator] '{seed_name}' 校验完成: {count} 条目, {len(errors)} 个错误")

        # 元数据校验
        if not all_errors:
            all_warnings.extend(cls._validate_meta_consistency(seeds))

        return all_errors, all_warnings

    @classmethod
    def _validate_meta_consistency(cls, seeds: Dict[str, Any]) -> List[str]:
        """校验跨种子数据的一致性"""
        warnings: List[str] = []
        # 可以在这里添加更多的跨表一致性检查
        return warnings


# =============================================================================
# 5. 版本管理器
# =============================================================================


class DataVersionManager:
    """数据版本管理器——基于 sys_data_version 表"""

    CURRENT_VERSION = "1.0.0"
    CURRENT_FILES = [
        "v1.0.0/001_sys_menu.json",
        "v1.0.0/002_sys_dict_type.json",
        "v1.0.0/003_sys_dict_data.json",
        "v1.0.0/004_gw_role_type.json",
        "v1.0.0/005_gw_profession.json",
        "v1.0.0/006_gw_elite_specialization.json",
        "v1.0.0/007_game_static_data_bdcode_skills.json",
        "v1.0.0/007_game_static_data_bdcode_specializations.json",
        "v1.0.0/007_game_static_data_bdcode_traits.json",
        "v1.0.0/007_game_static_data_skill_palettes.json",
        "v1.0.0/007_game_static_data_buffs.json",
        "v1.0.0/007_game_static_data_builds_initial_data.json",
    ]

    def __init__(self, db: Session):
        self.db = db

    def get_applied_version(self) -> Optional[Dict[str, Any]]:
        """获取已应用的数据版本记录"""
        try:
            from app.models.system.sys_data_version import SysDataVersion
            record = self.db.query(SysDataVersion).filter(
                SysDataVersion.version == self.CURRENT_VERSION
            ).first()
            if record:
                return {
                    "version": record.version,
                    "applied_at": record.applied_at.isoformat() if record.applied_at else None,
                    "files": json.loads(record.files) if record.files else [],
                    "description": record.description,
                }
            return None
        except Exception as e:
            logger.warning(f"[VersionManager] 查询已应用版本失败: {e}")
            return None

    def check_version(self, force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        检查当前版本是否需要应用
        Returns: (should_apply, reason)
        """
        if force:
            return True, "强制重新初始化"

        applied = self.get_applied_version()
        if applied is None:
            return True, "版本未应用"

        # 检查文件列表是否一致
        applied_files = set(applied.get("files", []))
        current_files = set(self.CURRENT_FILES)
        if applied_files != current_files:
            missing = current_files - applied_files
            extra = applied_files - current_files
            reason = f"文件列表不一致"
            if missing:
                reason += f"；缺失: {sorted(missing)}"
            if extra:
                reason += f"；多余: {sorted(extra)}"
            return True, reason

        return False, f"版本 {self.CURRENT_VERSION} 已应用"

    def compute_checksum(self, seeds: Dict[str, Any]) -> str:
        """计算种子数据的校验和"""
        hasher = hashlib.sha256()
        for key in sorted(seeds.keys()):
            hasher.update(f"{key}:".encode("utf-8"))
            hasher.update(json.dumps(seeds[key], ensure_ascii=False, sort_keys=True).encode("utf-8"))
        return hasher.hexdigest()

    def mark_applied(self, seeds: Dict[str, Any]) -> None:
        """标记当前版本已应用"""
        from app.models.system.sys_data_version import SysDataVersion
        checksum = self.compute_checksum(seeds)
        existing = self.db.query(SysDataVersion).filter(
            SysDataVersion.version == self.CURRENT_VERSION
        ).first()

        if existing:
            existing.files = json.dumps(self.CURRENT_FILES, ensure_ascii=False)
            existing.description = f"checksum: {checksum[:16]}..."
        else:
            record = SysDataVersion(
                version=self.CURRENT_VERSION,
                files=json.dumps(self.CURRENT_FILES, ensure_ascii=False),
                description=f"checksum: {checksum[:16]}...",
            )
            self.db.add(record)
        self.db.commit()
        logger.info(f"[VersionManager] 标记版本 {self.CURRENT_VERSION} 已应用")

    def clear_version(self) -> None:
        """清除版本记录（用于强制重新初始化）"""
        from app.models.system.sys_data_version import SysDataVersion
        self.db.query(SysDataVersion).filter(
            SysDataVersion.version == self.CURRENT_VERSION
        ).delete()
        self.db.commit()
        logger.info(f"[VersionManager] 清除版本 {self.CURRENT_VERSION} 记录")


# =============================================================================
# 6. 初始化日志上下文
# =============================================================================


@dataclass
class InitStepResult:
    """单个初始化步骤的结果"""

    step: str
    status: str  # "success" | "skipped" | "error"
    count: int = 0
    duration_ms: float = 0.0
    message: str = ""
    error: Optional[Dict[str, Any]] = None


class InitializationLogger:
    """初始化专用日志记录器——结构化日志，便于问题追踪"""

    def __init__(self):
        self.steps: List[InitStepResult] = []
        self.start_time = time.time()

    def log_step_start(self, step: str):
        logger.info(f"[Init] >>> 开始步骤: {step}")

    def log_step_success(self, step: str, count: int = 0, message: str = ""):
        duration = (time.time() - self.start_time) * 1000
        result = InitStepResult(
            step=step,
            status="success",
            count=count,
            duration_ms=duration,
            message=message or f"成功导入 {count} 条记录",
        )
        self.steps.append(result)
        logger.info(f"[Init] <<< 步骤完成: {step} | {result.message} | 耗时 {duration:.1f}ms")

    def log_step_skipped(self, step: str, reason: str = ""):
        result = InitStepResult(
            step=step, status="skipped", message=reason or "已跳过"
        )
        self.steps.append(result)
        logger.info(f"[Init] --- 步骤跳过: {step} | {result.message}")

    def log_step_error(self, step: str, error: Exception):
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
        }
        if isinstance(error, InitializationError):
            error_info.update(error.to_dict())
        result = InitStepResult(
            step=step, status="error", error=error_info, message=str(error)
        )
        self.steps.append(result)
        logger.error(f"[Init] !!! 步骤失败: {step} | {error}")
        # 打印详细诊断信息
        self._log_diagnostic(error)

    def _log_diagnostic(self, error: Exception):
        """打印诊断信息"""
        if isinstance(error, RetryExhaustedError):
            logger.error(f"[Init:诊断] 数据库写入重试耗尽，可能原因:")
            logger.error("  1. 数据库服务未启动或网络不可达")
            logger.error("  2. 数据库连接池已满")
            logger.error("  3. 数据库用户权限不足")
            logger.error("  4. 表级锁冲突（多 worker 并发）")
        elif isinstance(error, ValidationError):
            logger.error(f"[Init:诊断] 数据校验失败，请检查 seeds/ 目录下的 JSON 文件")
        elif isinstance(error, VersionConflictError):
            logger.error(f"[Init:诊断] 版本冲突，如需强制初始化请设置 force=true")

    def get_summary(self) -> Dict[str, Any]:
        """生成初始化摘要"""
        total = len(self.steps)
        success = sum(1 for s in self.steps if s.status == "success")
        skipped = sum(1 for s in self.steps if s.status == "skipped")
        errors = sum(1 for s in self.steps if s.status == "error")
        total_time = (time.time() - self.start_time) * 1000
        return {
            "total_steps": total,
            "success": success,
            "skipped": skipped,
            "errors": errors,
            "total_duration_ms": round(total_time, 2),
            "steps": [
                {
                    "step": s.step,
                    "status": s.status,
                    "count": s.count,
                    "duration_ms": round(s.duration_ms, 2),
                    "message": s.message,
                    "error": s.error,
                }
                for s in self.steps
            ],
        }


# =============================================================================
# 7. 重试数据库写入器
# =============================================================================


class RetryableDbWriter:
    """带重试机制的数据库批量写入器"""

    def __init__(self, db: Session, retry_config: Optional[RetryConfig] = None):
        self.db = db
        self.retry_config = retry_config or RetryConfig()

    def _write_with_retry(self, operation: Callable, description: str = "") -> Any:
        """执行带重试的数据库操作"""

        @retry_with_backoff(self.retry_config)
        def _do():
            return operation()

        try:
            return _do()
        except RetryExhaustedError as e:
            e.step = description or e.step
            raise

    def bulk_insert(self, model_class: type, items: List[Dict[str, Any]], description: str = "") -> int:
        """批量插入，带重试"""
        if not items:
            return 0

        def _insert():
            for item in items:
                self.db.add(model_class(**item))
            self.db.commit()
            return len(items)

        return self._write_with_retry(_insert, description or f"bulk_insert_{model_class.__name__}")

    def upsert(self, model_class: type, items: List[Dict[str, Any]], unique_field: str, description: str = "") -> Tuple[int, int]:
        """
        批量 upsert——先查询是否存在，存在则更新，不存在则插入
        Returns: (inserted_count, updated_count)
        """
        if not items:
            return 0, 0

        def _do_upsert():
            inserted = 0
            updated = 0
            for item in items:
                existing = self.db.query(model_class).filter(
                    getattr(model_class, unique_field) == item.get(unique_field)
                ).first()
                if existing:
                    for key, val in item.items():
                        if hasattr(existing, key):
                            setattr(existing, key, val)
                    updated += 1
                else:
                    self.db.add(model_class(**item))
                    inserted += 1
            self.db.commit()
            return inserted, updated

        return self._write_with_retry(_do_upsert, description or f"upsert_{model_class.__name__}")

    def execute_raw(self, sql: str, params: Optional[Dict] = None, description: str = "") -> Any:
        """执行原始 SQL，带重试"""
        def _exec():
            from sqlalchemy import text
            result = self.db.execute(text(sql), params or {})
            self.db.commit()
            return result

        return self._write_with_retry(_exec, description or "raw_sql")
