# -*- coding: utf-8 -*-
# 模块功能：EI JSON 结果缓存服务
# 说明：基于 evtc_log.ei_json_cache 字段，使用 gzip + base64 压缩存储 EI JSON
#   - 避免相同文件的重复 dps.report API 调用
#   - 支持按 SHA256 查找缓存（上传时复用）
#   - 支持 TTL 过期检查

import base64
import gzip
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.log.log import Log
from app.utils.logger import logger


def compress_ei_json(ei_json: Dict[str, Any]) -> str:
    """将 EI JSON 压缩为 gzip + base64 字符串。"""
    raw = json.dumps(ei_json, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=6)
    return base64.b64encode(compressed).decode("ascii")


def decompress_ei_json(compressed: str) -> Optional[Dict[str, Any]]:
    """将 gzip + base64 字符串解压为 EI JSON 字典。"""
    try:
        compressed_bytes = base64.b64decode(compressed.encode("ascii"))
        raw = gzip.decompress(compressed_bytes)
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        logger.warning(f"[cache] EI JSON 缓存解压失败: {e}")
        return None


def is_cache_valid(log: Log, ttl_hours: int = 720) -> bool:
    """检查日志的 EI JSON 缓存是否有效（未过期且存在）。"""
    if not log.ei_json_cache or not log.ei_json_cached_at:
        return False
    if ttl_hours <= 0:
        return True
    expiry = log.ei_json_cached_at.timestamp() + (ttl_hours * 3600)
    return datetime.now(timezone.utc).timestamp() < expiry


def store_ei_json_cache(db: Session, log_id: int, ei_json: Dict[str, Any]) -> bool:
    """存储 EI JSON 到日志缓存字段。

    Returns:
        bool: 是否存储成功
    """
    try:
        compressed = compress_ei_json(ei_json)
        log = db.query(Log).filter(Log.id == log_id).first()
        if log:
            log.ei_json_cache = compressed
            log.ei_json_cached_at = datetime.now(timezone.utc)
            db.flush()
            # 计算压缩率用于日志
            raw_len = len(json.dumps(ei_json, ensure_ascii=False))
            cache_len = len(compressed)
            ratio = (1 - cache_len / raw_len) * 100 if raw_len > 0 else 0
            logger.info(
                f"[cache] EI JSON 缓存已存储: log_id={log_id}, "
                f"压缩前={raw_len}B, 压缩后={cache_len}B, 节省={ratio:.1f}%"
            )
            return True
    except Exception as e:
        logger.error(f"[cache] 存储 EI JSON 缓存失败: log_id={log_id}, 错误: {e}")
    return False


def get_ei_json_from_cache(db: Session, log_id: int, ttl_hours: int = 720) -> Optional[Dict[str, Any]]:
    """通过日志 ID 获取缓存的 EI JSON（如果未过期）。"""
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log or not is_cache_valid(log, ttl_hours):
        return None
    return decompress_ei_json(log.ei_json_cache)


def get_ei_json_by_sha256(db: Session, file_sha256: str, ttl_hours: int = 720) -> Optional[Dict[str, Any]]:
    """通过文件 SHA256 查找任意日志的 EI JSON 缓存（用于上传时复用）。"""
    log = (
        db.query(Log)
        .filter(Log.file_sha256 == file_sha256, Log.ei_json_cache.isnot(None))
        .order_by(Log.ei_json_cached_at.desc())
        .first()
    )
    if not log or not is_cache_valid(log, ttl_hours):
        return None
    logger.info(f"[cache] SHA256 命中缓存: {file_sha256[:16]}..., log_id={log.id}")
    return decompress_ei_json(log.ei_json_cache)


def clear_ei_json_cache(db: Session, log_id: int) -> bool:
    """清除指定日志的 EI JSON 缓存。"""
    log = db.query(Log).filter(Log.id == log_id).first()
    if log:
        log.ei_json_cache = None
        log.ei_json_cached_at = None
        db.flush()
        logger.info(f"[cache] EI JSON 缓存已清除: log_id={log_id}")
        return True
    return False
