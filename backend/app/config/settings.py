# -*- coding: utf-8 -*-
# 模块功能：应用配置管理（向后兼容入口）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新日期：2026-05-04
# 说明：
#   本文件已重构为向后兼容入口，实际配置逻辑迁移到 app.core.config。
#   遵循 FastAPI 最佳实践：统一配置、@lru_cache 缓存、SettingsConfigDict。
#   新代码建议直接从 app.core.config 导入，或依赖注入 get_settings()。

from app.core.config import (
    DatabaseType,
    ModelProvider,
    Settings,
    get_settings,
)

# 向后兼容：模块级全局实例
settings = get_settings()
