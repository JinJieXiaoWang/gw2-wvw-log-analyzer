# 模块功能：日志记录工具
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：logging, os

import logging
import os
from datetime import datetime


# 懒加载的logger包装器
class _LazyLogger:
    """延迟初始化的logger包装器，避免循环导入"""

    _logger = None

    def _get_logger(self):
        if self._logger is None:
            self._setup_logger()
        return self._logger

    def _setup_logger(self):
        # 延迟导入settings
        from app.config.settings import settings

        # 创建日志目录
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # 获取日志记录器
        self._logger = logging.getLogger("app")
        self._logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # 避免重复添加handler
        if self._logger.handlers:
            return

        # 日志格式
        log_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 文件handler
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(log_format)
        self._logger.addHandler(file_handler)

        # 控制台handler（调试模式）
        if settings.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            self._logger.addHandler(console_handler)

    def debug(self, msg, *args, **kwargs):
        self._get_logger().debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._get_logger().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._get_logger().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._get_logger().error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._get_logger().exception(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._get_logger().critical(msg, *args, **kwargs)


# 创建全局日志记录器（延迟初始化）
logger = _LazyLogger()
