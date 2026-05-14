# -*- coding: utf-8 -*-
# 模块功能：FastAPI 统一配置管理（遵循 FastAPI 官方最佳实践）
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-04
# 说明：
#   1. 使用单个 BaseSettings 类聚合全部配置，避免重复加载 .env
#   2. 使用 @lru_cache 缓存 Settings 实例，只解析一次 .env
#   3. 使用 SettingsConfigDict（Pydantic V2 风格）替代 class Config
#   4. 提供 get_settings() 依赖函数，供 FastAPI 依赖注入使用
#   5. 向后兼容：保留原有的 db_settings / settings / ai_config 模块级变量

from __future__ import annotations

import os
import urllib.parse
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================================
# 枚举定义
# ============================================================================


class DatabaseType(str, Enum):
    """数据库类型"""

    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"

    @classmethod
    def _missing_(cls, value):
        """支持不区分大小写"""
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None


class ModelProvider(str, Enum):
    """AI 模型提供商"""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    CUSTOM = "custom"


# ============================================================================
# 统一配置类
# ============================================================================


class Settings(BaseSettings):
    """
    FastAPI 统一配置类

    聚合应用、数据库、AI 等全部配置，通过单个 BaseSettings 实例从 .env 加载，
    避免多个子类重复解析 .env 文件。
    """

    # ------------------------------------------------------------------
    # Pydantic V2 配置（替代 class Config）
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ==================================================================
    # 1. 应用基础配置
    # ==================================================================
    APP_NAME: str = Field(default="GW2 WvW 日志系统", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    DEBUG: bool = Field(default=True, description="调试模式")
    API_PREFIX: str = Field(default="/api/v1", description="API 路由前缀")

    # 安全提示：生产环境必须通过 .env 文件设置强密钥，此处留空作为强制提醒
    SECRET_KEY: str = Field(
        default="",
        description="JWT/Session 签名密钥（生产环境必须设置至少32位随机字符串）",
    )

    # CORS 配置
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "https://gw2-log-analyzer.top",
            "http://gw2-log-analyzer.top",
            "https://www.gw2-log-analyzer.top",
            "http://www.gw2-log-analyzer.top",
        ],
        description="允许的跨域来源",
    )

    # ==================================================================
    # 2. 日志配置
    # ==================================================================
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="./logs/app.log", description="日志文件路径")

    # ==================================================================
    # 3. 文件上传配置
    # ==================================================================
    UPLOAD_DIR: str = Field(default="./uploads", description="文件上传目录")
    MAX_UPLOAD_SIZE: int = Field(
        default=104_857_600,  # 100MB
        description="最大上传文件大小（字节）",
    )

    # ==================================================================
    # 4. 测试数据配置
    # ==================================================================
    TEST_DATA_DIR: str = Field(default="./tests/data", description="测试数据目录")
    TEST_JSON_FILE: str = Field(
        default="20260426-212600_detailed_wvw_kill.json",
        description="测试 JSON 文件名",
    )

    # ==================================================================
    # 5. 管理员初始化配置
    # ==================================================================
    # 预置管理员（用户名固定为 admin）的初始密码。
    # 若未设置或留空，系统首次启动时自动生成随机密码并输出到日志。
    ADMIN_INITIAL_PASSWORD: Optional[str] = Field(
        default=None,
        description="管理员初始密码（留空则自动生成随机密码）",
    )
    # 生产环境 Docker 重新部署时，若 ADMIN_INITIAL_PASSWORD 明确设置，
    # 是否强制同步更新已存在预置管理员的密码（解决密码不一致问题）
    ADMIN_PASSWORD_SYNC: bool = Field(
        default=False,
        description="是否强制同步预置管理员密码（生产环境 Docker 部署建议开启）",
    )

    # ==================================================================
    # 6. 文件存储管理配置
    # ==================================================================
    FILE_RETENTION_DAYS: int = Field(default=30, description="文件保留天数")
    MAX_STORAGE_SIZE: int = Field(
        default=10 * 1024 * 1024 * 1024,  # 10GB
        description="最大存储容量（字节）",
    )
    STORAGE_WARNING_THRESHOLD: float = Field(
        default=80.0,
        description="存储警告阈值（百分比）",
    )
    AUTO_CLEANUP_ENABLED: bool = Field(default=True, description="自动清理启用状态")
    AUTO_CLEANUP_INTERVAL: int = Field(
        default=24,
        description="自动清理执行间隔（小时）",
    )
    KEEP_RAW_FILE_AFTER_PARSE: bool = Field(
        default=True,
        description="解析完成后是否保留原始文件",
    )
    FILE_COMPRESSION_ENABLED: bool = Field(
        default=False,
        description="是否启用文件压缩",
    )

    # ==================================================================
    # 7. 数据库配置
    # ==================================================================
    DB_TYPE: DatabaseType = Field(
        default=DatabaseType.SQLITE,
        description="数据库类型（sqlite/mysql/postgresql）",
    )

    # --- SQLite ---
    SQLITE_DB_PATH: str = Field(
        default="./database/app.db",
        description="SQLite 数据库文件路径",
    )

    # --- MySQL ---
    MYSQL_HOST: str = Field(default="localhost", description="MySQL 主机地址")
    MYSQL_PORT: int = Field(default=3306, description="MySQL 端口")
    MYSQL_USER: str = Field(default="root", description="MySQL 用户名")
    # 安全提示：必须从环境变量注入，禁止硬编码密码
    MYSQL_PASSWORD: str = Field(
        default="",
        description="MySQL 密码（禁止硬编码，请通过 .env 注入）",
    )
    MYSQL_DATABASE: str = Field(
        default="gw2_log_system",
        description="MySQL 数据库名",
    )
    MYSQL_CHARSET: str = Field(default="utf8mb4", description="MySQL 字符集")
    MYSQL_POOL_SIZE: int = Field(
        default=10,
        description="MySQL 连接池大小",
    )
    MYSQL_MAX_OVERFLOW: int = Field(
        default=20,
        description="MySQL 连接池溢出上限",
    )
    MYSQL_LOCK_WAIT_TIMEOUT: int = Field(
        default=30,
        description="MySQL 锁等待超时时间（秒）",
    )

    # --- PostgreSQL ---
    POSTGRESQL_HOST: str = Field(default="localhost", description="PostgreSQL 主机地址")
    POSTGRESQL_PORT: int = Field(default=5432, description="PostgreSQL 端口")
    POSTGRESQL_USER: str = Field(default="postgres", description="PostgreSQL 用户名")
    # 安全提示：必须从环境变量注入，禁止硬编码密码
    POSTGRESQL_PASSWORD: str = Field(
        default="",
        description="PostgreSQL 密码（禁止硬编码，请通过 .env 注入）",
    )
    POSTGRESQL_DATABASE: str = Field(
        default="gw2_log_system",
        description="PostgreSQL 数据库名",
    )
    POSTGRESQL_POOL_SIZE: int = Field(
        default=10,
        description="PostgreSQL 连接池大小",
    )
    POSTGRESQL_MAX_OVERFLOW: int = Field(
        default=20,
        description="PostgreSQL 连接池溢出上限",
    )

    # --- 连接池通用配置 ---
    POOL_PRE_PING: bool = Field(default=True, description="连接池 pre_ping 检测")
    POOL_RECYCLE: int = Field(
        default=300,
        description="连接回收时间（秒）",
    )
    CONNECT_TIMEOUT: int = Field(
        default=10,
        description="数据库连接超时时间（秒）",
    )

    # --- 自动建表 / 迁移 ---
    AUTO_CREATE_TABLES: bool = Field(
        default=True,
        description="是否自动创建缺失的数据表",
    )
    AUTO_MIGRATE: bool = Field(
        default=False,
        description="是否自动执行迁移（生产环境建议关闭）",
    )

    # ==================================================================
    # 8. AI 模型配置
    # ==================================================================
    AI_ENABLED: bool = Field(default=True, description="AI 功能启用状态")
    AI_MODEL_PROVIDER: ModelProvider = Field(
        default=ModelProvider.DEEPSEEK,
        description="默认 AI 模型提供商",
    )

    # --- OpenAI ---
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API 密钥")
    OPENAI_API_BASE: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API 基础地址",
    )
    OPENAI_MODEL: str = Field(default="gpt-4-turbo", description="OpenAI 模型名称")
    OPENAI_MAX_TOKENS: int = Field(default=4000, description="OpenAI 最大 Token 数")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI 温度参数")

    # --- DeepSeek ---
    DEEPSEEK_API_KEY: Optional[str] = Field(
        default=None,
        description="DeepSeek API 密钥",
    )
    DEEPSEEK_API_BASE: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API 基础地址",
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat", description="DeepSeek 模型名称"
    )
    DEEPSEEK_MAX_TOKENS: int = Field(default=4000, description="DeepSeek 最大 Token 数")
    DEEPSEEK_TEMPERATURE: float = Field(default=0.7, description="DeepSeek 温度参数")

    # --- 通义千问 ---
    QWEN_API_KEY: Optional[str] = Field(default=None, description="通义千问 API 密钥")
    QWEN_API_BASE: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="通义千问 API 基础地址",
    )
    QWEN_MODEL: str = Field(default="qwen-turbo", description="通义千问模型名称")
    QWEN_MAX_TOKENS: int = Field(default=4000, description="通义千问最大 Token 数")
    QWEN_TEMPERATURE: float = Field(default=0.7, description="通义千问温度参数")

    # --- 自定义模型 ---
    CUSTOM_API_KEY: Optional[str] = Field(
        default=None, description="自定义模型 API 密钥"
    )
    CUSTOM_API_BASE: Optional[str] = Field(
        default=None, description="自定义模型 API 基础地址"
    )
    CUSTOM_MODEL: Optional[str] = Field(default=None, description="自定义模型名称")

    # --- 请求配置 ---
    AI_REQUEST_TIMEOUT: int = Field(default=60, description="AI 请求超时时间（秒）")
    AI_MAX_RETRIES: int = Field(default=3, description="AI 请求最大重试次数")
    AI_RETRY_DELAY: float = Field(default=1.0, description="AI 请求重试间隔（秒）")
    AI_CONCURRENT_LIMIT: int = Field(default=5, description="AI 并发请求限制")

    # --- 缓存配置 ---
    AI_CACHE_ENABLED: bool = Field(default=True, description="AI 缓存启用状态")
    AI_CACHE_TTL: int = Field(default=3600, description="AI 缓存 TTL（秒）")

    # --- 降级策略 ---
    AI_FALLBACK_ENABLED: bool = Field(default=True, description="AI 降级启用状态")
    AI_FALLBACK_PROVIDER_ORDER: List[str] = Field(
        default=["deepseek", "qwen", "openai"],
        description="AI 降级提供商优先级列表",
    )

    # --- 质量评估 ---
    AI_QUALITY_CHECK_ENABLED: bool = Field(
        default=True, description="AI 质量检查启用状态"
    )
    AI_MIN_ACCURACY_SCORE: float = Field(default=0.6, description="AI 最低准确度分数")
    AI_MIN_RELEVANCE_SCORE: float = Field(default=0.7, description="AI 最低相关性分数")
    AI_MAX_RESPONSE_TIME: float = Field(
        default=30.0, description="AI 最大响应时间（秒）"
    )

    # --- 分析维度 ---
    AI_ANALYSIS_DIMENSIONS: List[str] = Field(
        default=[
            "team_performance",
            "individual_skills",
            "build_optimization",
            "trend_analysis",
            "suggestions",
        ],
        description="AI 分析维度列表",
    )

    # --- 提示词模板 ---
    AI_PROMPT_TEMPLATES_DIR: str = Field(
        default="./app/platform/data/prompts",
        description="AI 提示词模板目录",
    )

    # ------------------------------------------------------------------
    # 字段校验
    # ------------------------------------------------------------------
    @field_validator("DB_TYPE", mode="before")
    @classmethod
    def _validate_db_type(cls, v: Any) -> DatabaseType:
        """支持大小写不敏感的数据库类型"""
        if isinstance(v, str):
            normalized = v.lower()
            for member in DatabaseType:
                if member.value == normalized:
                    return member
        return v

    @field_validator("AI_MODEL_PROVIDER", mode="before")
    @classmethod
    def _validate_ai_provider(cls, v: Any) -> ModelProvider:
        """支持大小写不敏感的 AI 提供商"""
        if isinstance(v, str):
            normalized = v.lower()
            for member in ModelProvider:
                if member.value == normalized:
                    return member
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        """生产环境强制要求强密钥"""
        if not v:
            raise ValueError("SECRET_KEY 不能为空，请在 .env 中设置至少32位随机字符串")
        if len(v) < 32:
            raise ValueError(f"SECRET_KEY 长度必须至少32位，当前仅 {len(v)} 位")
        return v

    # ==================================================================
    # 数据库相关方法
    # ==================================================================

    @property
    def DATABASE_URL(self) -> str:
        """动态生成数据库连接 URL（向后兼容）"""
        return self.get_database_url()

    def get_database_url(self) -> str:
        """获取数据库连接 URL"""
        if self.DB_TYPE == DatabaseType.SQLITE:
            return f"sqlite:///{self.SQLITE_DB_PATH}"

        if self.DB_TYPE == DatabaseType.MYSQL:
            password_part = ""
            if self.MYSQL_PASSWORD:
                encoded_pwd = self._url_encode_password(self.MYSQL_PASSWORD)
                password_part = f":{encoded_pwd}"
            return (
                f"mysql+pymysql://{self.MYSQL_USER}{password_part}@"
                f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
                f"?charset={self.MYSQL_CHARSET}"
            )

        if self.DB_TYPE == DatabaseType.POSTGRESQL:
            password_part = ""
            if self.POSTGRESQL_PASSWORD:
                encoded_pwd = self._url_encode_password(self.POSTGRESQL_PASSWORD)
                password_part = f":{encoded_pwd}"
            return (
                f"postgresql+psycopg2://{self.POSTGRESQL_USER}{password_part}@"
                f"{self.POSTGRESQL_HOST}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DATABASE}"
            )

        raise ValueError(f"不支持的数据库类型: {self.DB_TYPE}")

    def _url_encode_password(self, password: str) -> str:
        """对密码进行 URL 编码"""
        return urllib.parse.quote_plus(password)

    def get_engine_kwargs(self) -> Dict[str, Any]:
        """获取 SQLAlchemy 引擎初始化参数"""
        kwargs: Dict[str, Any] = {
            "echo": False,
            "pool_pre_ping": self.POOL_PRE_PING,
            "pool_recycle": self.POOL_RECYCLE,
            "connect_args": {},
        }

        if self.DB_TYPE == DatabaseType.SQLITE:
            kwargs["connect_args"]["check_same_thread"] = False
        elif self.DB_TYPE == DatabaseType.MYSQL:
            kwargs["pool_size"] = self.MYSQL_POOL_SIZE
            kwargs["max_overflow"] = self.MYSQL_MAX_OVERFLOW
            kwargs["connect_args"]["connect_timeout"] = self.CONNECT_TIMEOUT
            kwargs["connect_args"][
                "init_command"
            ] = f"SET SESSION lock_wait_timeout={self.MYSQL_LOCK_WAIT_TIMEOUT}"
        elif self.DB_TYPE == DatabaseType.POSTGRESQL:
            kwargs["pool_size"] = self.POSTGRESQL_POOL_SIZE
            kwargs["max_overflow"] = self.POSTGRESQL_MAX_OVERFLOW
            kwargs["connect_args"]["connect_timeout"] = self.CONNECT_TIMEOUT

        return kwargs

    def validate_config(self) -> bool:
        """验证数据库配置有效性"""
        from app.utils.logger import logger

        if self.DB_TYPE == DatabaseType.MYSQL:
            if not self.MYSQL_USER:
                logger.error("MySQL 用户名未配置")
                return False
            if not self.MYSQL_PASSWORD:
                logger.error("MySQL 密码未配置（禁止硬编码，请通过 .env 注入）")
                return False
            if not self.MYSQL_DATABASE:
                logger.error("MySQL 数据库名未配置")
                return False

        elif self.DB_TYPE == DatabaseType.POSTGRESQL:
            if not self.POSTGRESQL_USER:
                logger.error("PostgreSQL 用户名未配置")
                return False
            if not self.POSTGRESQL_PASSWORD:
                logger.error("PostgreSQL 密码未配置（禁止硬编码，请通过 .env 注入）")
                return False
            if not self.POSTGRESQL_DATABASE:
                logger.error("PostgreSQL 数据库名未配置")
                return False

        logger.info(f"数据库配置验证通过: {self.DB_TYPE}")
        return True

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要（不含密码）"""
        summary: Dict[str, Any] = {
            "type": self.DB_TYPE.value,
            "auto_create_tables": self.AUTO_CREATE_TABLES,
            "auto_migrate": self.AUTO_MIGRATE,
        }

        if self.DB_TYPE == DatabaseType.SQLITE:
            summary["path"] = self.SQLITE_DB_PATH
        elif self.DB_TYPE == DatabaseType.MYSQL:
            summary["host"] = self.MYSQL_HOST
            summary["port"] = self.MYSQL_PORT
            summary["user"] = self.MYSQL_USER
            summary["database"] = self.MYSQL_DATABASE
        elif self.DB_TYPE == DatabaseType.POSTGRESQL:
            summary["host"] = self.POSTGRESQL_HOST
            summary["port"] = self.POSTGRESQL_PORT
            summary["user"] = self.POSTGRESQL_USER
            summary["database"] = self.POSTGRESQL_DATABASE

        return summary

    # ==================================================================
    # AI 相关方法
    # ==================================================================

    def get_active_provider_config(self) -> Dict[str, Any]:
        """获取当前激活的 AI 提供商配置"""
        configs: Dict[ModelProvider, Dict[str, Any]] = {
            ModelProvider.OPENAI: {
                "api_key": self.OPENAI_API_KEY,
                "api_base": self.OPENAI_API_BASE,
                "model": self.OPENAI_MODEL,
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "temperature": self.OPENAI_TEMPERATURE,
            },
            ModelProvider.DEEPSEEK: {
                "api_key": self.DEEPSEEK_API_KEY,
                "api_base": self.DEEPSEEK_API_BASE,
                "model": self.DEEPSEEK_MODEL,
                "max_tokens": self.DEEPSEEK_MAX_TOKENS,
                "temperature": self.DEEPSEEK_TEMPERATURE,
            },
            ModelProvider.QWEN: {
                "api_key": self.QWEN_API_KEY,
                "api_base": self.QWEN_API_BASE,
                "model": self.QWEN_MODEL,
                "max_tokens": self.QWEN_MAX_TOKENS,
                "temperature": self.QWEN_TEMPERATURE,
            },
            ModelProvider.CUSTOM: {
                "api_key": self.CUSTOM_API_KEY,
                "api_base": self.CUSTOM_API_BASE,
                "model": self.CUSTOM_MODEL,
                "max_tokens": 2000,
                "temperature": 0.7,
            },
        }
        return configs[self.AI_MODEL_PROVIDER]

    def is_config_valid(self) -> bool:
        """检查 AI 配置是否有效（当前激活的提供商有 API Key）"""
        config = self.get_active_provider_config()
        return config["api_key"] is not None and (
            config["api_base"] is not None
            or self.AI_MODEL_PROVIDER != ModelProvider.CUSTOM
        )


# ============================================================================
# FastAPI 推荐：使用 @lru_cache 缓存 Settings 实例
# ============================================================================


@lru_cache
def get_settings() -> Settings:
    """
    FastAPI 官方推荐：缓存 Settings 实例

    使用 lru_cache 确保 .env 文件只被解析一次，提升性能并保证配置一致性。
    可在 FastAPI 依赖注入中使用：

        from fastapi import Depends
        from app.core.config import get_settings

        @app.get("/info")
        def info(settings: Settings = Depends(get_settings)):
            return {"app_name": settings.APP_NAME}
    """
    return Settings()


# ============================================================================
# 向后兼容：模块级全局实例
# ============================================================================
# 旧代码中大量使用了模块级变量（如 from app.config.settings import settings），
# 以下变量提供向后兼容，新代码推荐使用 get_settings() 或依赖注入。

settings = get_settings()
