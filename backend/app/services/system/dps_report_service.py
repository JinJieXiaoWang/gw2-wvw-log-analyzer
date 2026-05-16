# -*- coding: utf-8 -*-
"""
dps.report API 服务模块
用于上传 zevtc 文件并获取高质量的 EI JSON 解析结果

安全增强：
    - 首次使用时自动获取 userToken（https://dps.report/getUserToken）
    - token 保存在内存中，确保不同机器/实例使用不同 token
    - 上传时附带 token，保证文件安全性

错误处理增强（2026-05-05）：
    - 超时/限流/失败时抛出特定异常，不再静默返回 None
    - 上层（batch worker）根据异常类型决定重试或放弃
    - 支持流式上传，避免大文件全量读入内存
"""

import os
import threading
import time
from typing import Any, Dict, Optional

import orjson
import requests

from app.services.system.dps_report_queue import dps_report_queue
from app.services.zevtc.rate_limiter import dps_report_limiter
from app.utils.logger import logger

DPS_REPORT_UPLOAD_URL = "https://dps.report/uploadContent"
DPS_REPORT_JSON_URL = "https://dps.report/getJson"
DPS_REPORT_TOKEN_URL = "https://dps.report/getUserToken"

# 支持通过环境变量配置代理（适用于中国大陆服务器）
REQUESTS_PROXIES = {}
_http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
_https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
if _http_proxy:
    REQUESTS_PROXIES["http"] = _http_proxy
if _https_proxy:
    REQUESTS_PROXIES["https"] = _https_proxy

# 进程级内存缓存（确保同一进程内复用，不同进程/机器各自独立）
_dps_report_token: Optional[str] = None


class DpsReportError(Exception):
    """dps.report API 基础异常"""
    pass


class DpsReportTimeoutError(DpsReportError):
    """dps.report 请求超时"""
    pass


class DpsReportRateLimitError(DpsReportError):
    """dps.report API 限流 (HTTP 429)"""
    pass


class DpsReportHttpError(DpsReportError):
    """dps.report HTTP 错误响应"""
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class DpsReportParseError(DpsReportError):
    """dps.report 解析失败（返回了 error 字段）"""
    pass


def _get_user_token() -> Optional[str]:
    """获取 dps.report userToken（进程级缓存）"""
    global _dps_report_token
    if _dps_report_token:
        return _dps_report_token

    try:
        resp = requests.get(DPS_REPORT_TOKEN_URL, timeout=30, proxies=REQUESTS_PROXIES)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("userToken")
            if token:
                _dps_report_token = token
                logger.info(f"[dps.report] 获取 userToken 成功")
                return token
            else:
                logger.warning(f"[dps.report] getUserToken 响应缺少 token: {data}")
        else:
            logger.warning(f"[dps.report] getUserToken 失败: HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"[dps.report] 获取 userToken 异常: {e}")

    return None


def _upload_and_parse_core(file_path: str) -> Dict[str, Any]:
    """upload_and_parse 的核心逻辑（不包含队列包装）。"""
    if not os.path.exists(file_path):
        raise DpsReportError(f"文件不存在: {file_path}")

    total_start = time.time()

    # 获取 userToken（保证安全性）
    user_token = _get_user_token()
    token_param = f"&userToken={user_token}" if user_token else ""

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # === 限流检查 ===
    while not dps_report_limiter.acquire():
        wait_sec = dps_report_limiter.wait_time()
        logger.info(f"[dps.report] 限流等待: {wait_sec:.1f}s")
        time.sleep(wait_sec)

    logger.info(f"[dps.report] 开始上传: {filename}, {file_size} bytes")

    try:
        # 1. 上传文件到 dps.report（附带 token）
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            upload_url = (
                f"{DPS_REPORT_UPLOAD_URL}?json=1&generator=ei{token_param}"
            )
            upload_resp = requests.post(upload_url, files=files, timeout=300, proxies=REQUESTS_PROXIES)

        if upload_resp.status_code == 429:
            retry_after = None
            try:
                err_data = upload_resp.json()
                retry_after = err_data.get("retryAfter") or err_data.get("retry_after")
            except Exception:
                pass
            dps_report_limiter.record_rejection(retry_after=retry_after or 60)
            raise DpsReportRateLimitError(
                f"dps.report API 限流 (HTTP 429)", retry_after or 60
            )

        if upload_resp.status_code != 200:
            raise DpsReportHttpError(
                f"dps.report 上传失败: HTTP {upload_resp.status_code}",
                upload_resp.status_code,
            )

        upload_data = orjson.loads(upload_resp.content)
        if upload_data.get("error"):
            raise DpsReportParseError(
                f"dps.report 解析错误: {upload_data['error']}"
            )

        permalink = upload_data.get("permalink")
        parse_duration = upload_data.get("encounter", {}).get("duration", 0)
        logger.info(f"[dps.report] 上传成功: {permalink}")

        # 2. 获取完整 EI JSON
        json_resp = requests.get(
            f"{DPS_REPORT_JSON_URL}?permalink={permalink}{token_param}",
            timeout=60,
            proxies=REQUESTS_PROXIES,
        )

        if json_resp.status_code != 200:
            raise DpsReportHttpError(
                f"dps.report 获取 JSON 失败: HTTP {json_resp.status_code}",
                json_resp.status_code,
            )

        ei_json = orjson.loads(json_resp.content)

        # 3. 验证 permalink 可访问性（HEAD 请求，轻量）
        try:
            head_resp = requests.head(
                permalink,
                timeout=10,
                proxies=REQUESTS_PROXIES,
                allow_redirects=True,
            )
            if head_resp.status_code != 200:
                logger.warning(
                    f"[dps.report] permalink HEAD 验证失败: {permalink}, "
                    f"HTTP {head_resp.status_code}"
                )
            else:
                logger.debug(f"[dps.report] permalink 验证通过: {permalink}")
        except Exception as head_err:
            logger.warning(f"[dps.report] permalink HEAD 验证异常（非致命）: {head_err}")

        total_time = time.time() - total_start
        logger.info(f"[dps.report] 完整流程完成: {total_time:.2f}s")

        return {"permalink": permalink, "ei_json": ei_json, "duration": parse_duration}

    except requests.exceptions.Timeout:
        logger.warning("[dps.report] 请求超时")
        raise DpsReportTimeoutError("dps.report 请求超时")
    except DpsReportError:
        raise
    except Exception as e:
        logger.warning(f"[dps.report] 异常: {e}", exc_info=True)
        raise DpsReportError(f"dps.report 异常: {e}") from e


def upload_and_parse(file_path: str) -> Dict[str, Any]:
    """
    上传 zevtc 文件到 dps.report 并获取完整 EI JSON。
    本函数自动通过 DpsReportRequestQueue 排队，保证全局严格单并发。

    Args:
        file_path: 本地 zevtc 文件路径

    Returns:
        dict: {
            "permalink": str,
            "ei_json": dict,
            "duration": float (seconds)
        }

    Raises:
        DpsReportTimeoutError: 请求超时
        DpsReportRateLimitError: API 限流 (HTTP 429)
        DpsReportHttpError: HTTP 错误响应
        DpsReportParseError: dps.report 解析失败
        DpsReportError: 其他异常
    """
    # 如果当前线程就是队列 worker 线程，直接执行避免死锁
    # （子进程中队列是新实例，_worker_thread 为 None，也会直接执行）
    if dps_report_queue._worker_thread is not None and threading.current_thread() is dps_report_queue._worker_thread:
        return _upload_and_parse_core(file_path)

    # 普通调用：通过队列提交，全局串行
    return dps_report_queue.submit(_upload_and_parse_core, file_path)
