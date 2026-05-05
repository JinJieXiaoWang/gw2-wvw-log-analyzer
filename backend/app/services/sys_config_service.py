# -*- coding: utf-8 -*-
# 模块功能：系统参数配置服务
# 说明：基于 sys_config 表读写全局系统配置，替代 app_config.json

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.sys_config import SysConfig
from app.utils.logger import logger

# 默认系统设置（首次初始化时插入数据库）
DEFAULT_CONFIGS = [
    {"config_key": "theme", "config_value": "light", "config_name": "界面主题", "config_type": "Y"},
    {"config_key": "default_server", "config_value": "Tarnished Coast", "config_name": "默认服务器", "config_type": "Y"},
    {"config_key": "parse_parallel", "config_value": "1", "config_name": "解析并行数", "config_type": "Y"},
    {"config_key": "export_format", "config_value": "json", "config_name": "导出格式", "config_type": "Y"},
    {"config_key": "auto_backup", "config_value": "true", "config_name": "自动备份", "config_type": "Y"},
    {"config_key": "retention_days", "config_value": "365", "config_name": "数据保留天数", "config_type": "Y"},
    {"config_key": "watermark_enabled", "config_value": "false", "config_name": "页面水印开关", "config_type": "N"},
    {"config_key": "watermark_text", "config_value": "", "config_name": "水印内容", "config_type": "N"},
    {"config_key": "watermark_screenshot_enabled", "config_value": "true", "config_name": "截图水印开关", "config_type": "N"},
]


class SysConfigService:
    """系统参数配置服务"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def init_default_configs(db: Session):
        """初始化默认配置（数据库为空时插入）"""
        for cfg in DEFAULT_CONFIGS:
            exists = (
                db.query(SysConfig)
                .filter(SysConfig.config_key == cfg["config_key"])
                .first()
            )
            if not exists:
                db.add(SysConfig(**cfg))
        db.commit()
        logger.info(f"[SysConfig] 初始化默认配置完成，共 {len(DEFAULT_CONFIGS)} 项")

    def get_config(self, key: str, default: Any = None) -> Any:
        """读取单个配置值，自动尝试 JSON 解析"""
        item = (
            self.db.query(SysConfig)
            .filter(SysConfig.config_key == key)
            .first()
        )
        if not item:
            return default
        return self._parse_value(item.config_value, default)

    def get_configs(self, keys: List[str]) -> Dict[str, Any]:
        """批量读取配置"""
        items = (
            self.db.query(SysConfig)
            .filter(SysConfig.config_key.in_(keys))
            .all()
        )
        result = {}
        for item in items:
            result[item.config_key] = self._parse_value(item.config_value)
        return result

    def get_all_settings(self) -> Dict[str, Any]:
        """读取所有系统设置（兼容现有接口）"""
        items = self.db.query(SysConfig).all()
        result = {}
        for item in items:
            result[item.config_key] = self._parse_value(item.config_value)
        return result

    def set_config(self, key: str, value: Any, config_name: str = "", config_type: str = "N") -> bool:
        """设置单个配置值"""
        try:
            str_value = self._stringify_value(value)
            item = (
                self.db.query(SysConfig)
                .filter(SysConfig.config_key == key)
                .first()
            )
            if item:
                item.config_value = str_value
                if config_name:
                    item.config_name = config_name
            else:
                self.db.add(
                    SysConfig(
                        config_key=key,
                        config_value=str_value,
                        config_name=config_name or key,
                        config_type=config_type,
                    )
                )
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"[SysConfig] 保存配置 {key} 失败: {e}")
            return False

    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """批量更新设置"""
        try:
            for key, value in settings.items():
                self.set_config(key, value)
            return True
        except Exception as e:
            logger.error(f"[SysConfig] 批量更新配置失败: {e}")
            return False

    @staticmethod
    def _parse_value(value: str, default: Any = None) -> Any:
        """将字符串配置值解析为对应类型"""
        if value is None:
            return default
        # 尝试 bool
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        # 尝试 int
        try:
            return int(value)
        except ValueError:
            pass
        # 尝试 float
        try:
            return float(value)
        except ValueError:
            pass
        # 尝试 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass
        # 默认字符串
        return value

    @staticmethod
    def _stringify_value(value: Any) -> str:
        """将任意值序列化为字符串"""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)
