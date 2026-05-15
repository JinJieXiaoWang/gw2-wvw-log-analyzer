# -*- coding: utf-8 -*-
"""
强化数据初始化服务

功能：整合校验、重试、日志、版本控制的统一数据初始化服务
启动时自动执行，失败则终止启动

作者：帅妹妹丶.8297
创建日期：2026-05-15
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.initialization import (
    DataVersionManager,
    InitializationError,
    InitializationLogger,
    RetryableDbWriter,
    RetryConfig,
    SeedDataLoader,
    SeedDataValidator,
    ValidationError,
    VersionConflictError,
)
from app.data.init_all import (
    _init_admin,
    _init_builds,
    _init_elite_specializations,
    _init_game_static_data,
    _init_professions,
    _init_role_types,
    _init_scoring_rules,
    _init_sys_config,
    _init_sys_dict_data,
    _init_sys_dict_type,
    _init_sys_menu,
    _load_dictionaries,
)
from app.utils.logger import logger


class InitializationService:
    """
    强化数据初始化服务

    核心流程：
    1. 加载所有种子数据（三级回退）
    2. 强制校验（失败则终止）
    3. 版本检查（避免重复初始化）
    4. 按顺序执行各模块初始化（带重试）
    5. 标记版本已应用
    6. 输出详细摘要
    """

    def __init__(
        self,
        db: Session,
        retry_config: Optional[RetryConfig] = None,
        force: bool = False,
    ):
        self.db = db
        self.force = force
        self.retry_config = retry_config or RetryConfig()
        self.writer = RetryableDbWriter(db, self.retry_config)
        self.version_manager = DataVersionManager(db)
        self.init_logger = InitializationLogger()
        self.seeds: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """
        执行完整的初始化流程

        Returns:
            初始化结果摘要（包含 skipped=True 标记当版本已应用时）

        Raises:
            InitializationError: 任何步骤失败时抛出，调用方必须终止启动
        """
        try:
            # Step 0: 版本检查
            self._step_version_check()

            # Step 1: 加载种子数据
            self._step_load_seeds()

            # Step 2: 强制校验
            self._step_validate()

            # Step 3: 执行各模块初始化
            results = self._step_initialize_modules()

            # Step 4: 标记版本
            self._step_mark_version()

            # Step 5: 输出摘要
            summary = self.init_logger.get_summary()
            summary["results"] = results
            summary["skipped"] = False
            logger.info(f"[InitializationService] 初始化完成摘要: {summary}")
            return summary

        except InitializationError as e:
            # 【关键】SKIPPED 不是错误，是正常状态——版本已应用，无需重复初始化
            if e.error_type == "SKIPPED":
                summary = self.init_logger.get_summary()
                summary["skipped"] = True
                summary["message"] = str(e)
                logger.info(f"[InitializationService] {e}")
                return summary
            raise
        except Exception as e:
            # 捕获所有未预料的异常，包装为 InitializationError
            self.init_logger.log_step_error("unknown", e)
            raise InitializationError(
                message=f"初始化过程中发生未预料错误: {e}",
                step="unknown",
                error_type="UNEXPECTED_ERROR",
                suggestion="请查看详细日志，检查数据库连接和种子数据完整性",
            ) from e

    # ==========================================================================
    # 各步骤实现
    # ==========================================================================

    def _step_version_check(self):
        """版本检查——决定是否执行初始化"""
        step = "version_check"
        self.init_logger.log_step_start(step)

        should_apply, reason = self.version_manager.check_version(force=self.force)
        if not should_apply:
            self.init_logger.log_step_skipped(step, reason)
            # 返回一个特殊的标记，让调用方知道无需继续
            raise InitializationError(
                message=f"跳过初始化: {reason}",
                step=step,
                error_type="SKIPPED",
            )

        self.init_logger.log_step_success(step, message=reason)

    def _step_load_seeds(self):
        """加载所有种子数据"""
        step = "load_seeds"
        self.init_logger.log_step_start(step)

        seed_names = [
            "sys_menu",
            "sys_dict_type",
            "sys_dict_data",
            "gw_role_type",
            "gw_profession",
            "gw_elite_specialization",
        ]

        for name in seed_names:
            try:
                self.seeds[name] = SeedDataLoader.load(name)
            except InitializationError:
                raise
            except Exception as e:
                raise InitializationError(
                    message=f"加载种子 '{name}' 失败: {e}",
                    step=step,
                    error_type="SEED_LOAD_ERROR",
                    data_snippet={"seed_name": name},
                ) from e

        # 游戏静态数据作为特殊处理（非列表结构）
        try:
            self.seeds["game_static_bdcode_skills"] = SeedDataLoader.load(
                "game_static_bdcode_skills", fallback_data=[]
            )
        except Exception:
            self.seeds["game_static_bdcode_skills"] = []

        total_records = sum(
            len(v) if isinstance(v, list) else 0 for v in self.seeds.values()
        )
        self.init_logger.log_step_success(step, count=total_records, message=f"加载 {len(self.seeds)} 个种子")

    def _step_validate(self):
        """强制校验种子数据"""
        step = "validate"
        self.init_logger.log_step_start(step)

        errors, warnings = SeedDataValidator.validate_all(self.seeds)

        for w in warnings:
            logger.warning(f"[Validator] {w}")

        if errors:
            error_msg = "种子数据校验失败:\n" + "\n".join(f"  - {e}" for e in errors)
            self.init_logger.log_step_error(step, ValidationError(error_msg, step=step))
            raise ValidationError(error_msg, step=step, data_snippet=errors)

        self.init_logger.log_step_success(step, message="所有种子数据校验通过")

    def _step_initialize_modules(self) -> Dict[str, Any]:
        """按顺序执行各模块初始化"""
        results: Dict[str, Any] = {}

        modules = [
            ("sys_menu", self._run_sys_menu),
            ("sys_dict_type", self._run_sys_dict_type),
            ("sys_dict_data", self._run_sys_dict_data),
            ("sys_config", self._run_sys_config),
            ("gw_role_type", self._run_role_types),
            ("gw_profession", self._run_professions),
            ("gw_elite_specialization", self._run_elite_specializations),
            ("game_static", self._run_game_static_data),
            ("builds", self._run_builds),
            ("admin", self._run_admin),
            ("scoring_rules", self._run_scoring_rules),
            ("dictionaries", self._run_dictionaries),
        ]

        for name, func in modules:
            try:
                self.init_logger.log_step_start(name)
                result = func()
                results[name] = result
                count = self._extract_count(result)
                self.init_logger.log_step_success(name, count=count)
            except InitializationError:
                raise
            except Exception as e:
                self.init_logger.log_step_error(name, e)
                raise InitializationError(
                    message=f"模块 '{name}' 初始化失败: {e}",
                    step=name,
                    error_type="MODULE_INIT_ERROR",
                    suggestion=f"请检查 {name} 相关模型和数据",
                ) from e

        return results

    def _step_mark_version(self):
        """标记版本已应用"""
        step = "mark_version"
        self.init_logger.log_step_start(step)
        self.version_manager.mark_applied(self.seeds)
        self.init_logger.log_step_success(step, message=f"版本 {DataVersionManager.CURRENT_VERSION} 已标记")

    # ==========================================================================
    # 各模块包装方法（调用 init_all.py 中的现有函数）
    # ==========================================================================

    def _run_sys_menu(self) -> int:
        return _init_sys_menu(self.db)

    def _run_sys_dict_type(self) -> int:
        return _init_sys_dict_type(self.db)

    def _run_sys_dict_data(self) -> int:
        return _init_sys_dict_data(self.db)

    def _run_sys_config(self) -> int:
        return _init_sys_config(self.db)

    def _run_role_types(self) -> int:
        return _init_role_types(self.db)

    def _run_professions(self) -> int:
        return _init_professions(self.db)

    def _run_elite_specializations(self) -> int:
        return _init_elite_specializations(self.db)

    def _run_game_static_data(self) -> Dict[str, int]:
        return _init_game_static_data(self.db)

    def _run_builds(self) -> Dict[str, Any]:
        return _init_builds(self.db)

    def _run_admin(self) -> Dict[str, Any]:
        return _init_admin(self.db)

    def _run_scoring_rules(self) -> Dict[str, Any]:
        return _init_scoring_rules(self.db)

    def _run_dictionaries(self) -> Dict[str, Any]:
        return _load_dictionaries(self.db)

    # ==========================================================================
    # 工具方法
    # ==========================================================================

    @staticmethod
    def _extract_count(v: Any) -> int:
        if isinstance(v, int):
            return v
        if isinstance(v, dict):
            if all(isinstance(x, int) for x in v.values()):
                return sum(v.values())
            return v.get("count", 0)
        return 0


# =============================================================================
# 兼容层：保持 init_all.py 的 initialize_all 可用
# =============================================================================

def initialize_all_hardened(
    db: Session,
    force: bool = False,
    retry_config: Optional[RetryConfig] = None,
) -> Dict[str, Any]:
    """
    强化版统一数据初始化入口

    Args:
        db: 数据库会话
        force: 是否强制重新初始化（忽略版本记录）
        retry_config: 自定义重试配置，None 使用默认

    Returns:
        初始化结果摘要

    Raises:
        InitializationError: 任何步骤失败时抛出，必须终止启动
    """
    service = InitializationService(db, retry_config=retry_config, force=force)
    return service.run()
