# -*- coding: utf-8 -*-
# 模块功能：AI模型客户端
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-01
# 依赖说明：httpx, openai

import asyncio
import json
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import httpx

from app.config.ai_config import ModelProvider, ai_config
from app.utils.logger import logger


class RequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"


class AIResponse:
    """AI响应包装类"""

    def __init__(
        self,
        content: str,
        provider: ModelProvider,
        model: str,
        status: RequestStatus,
        response_time: float,
        raw_response: Optional[Dict] = None,
        error: Optional[str] = None,
        cache_hit: bool = False,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.status = status
        self.response_time = response_time
        self.raw_response = raw_response
        self.error = error
        self.cache_hit = cache_hit
        self.quality_score: Optional[float] = None
        self.relevance_score: Optional[float] = None

    @property
    def is_success(self) -> bool:
        return (
            self.status == RequestStatus.SUCCESS or self.status == RequestStatus.CACHED
        )

    @property
    def is_fallback(self) -> bool:
        return getattr(self, "_is_fallback", False)

    @is_fallback.setter
    def is_fallback(self, value: bool):
        self._is_fallback = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "provider": self.provider.value,
            "model": self.model,
            "status": self.status.value,
            "response_time": self.response_time,
            "cache_hit": self.cache_hit,
            "is_fallback": getattr(self, "_is_fallback", False),
            "quality_score": self.quality_score,
            "relevance_score": self.relevance_score,
            "error": self.error,
        }


class AICache:
    """AI响应缓存管理器"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}

    def get(self, cache_key: str) -> Optional[AIResponse]:
        """获取缓存的响应"""
        if not ai_config.AI_CACHE_ENABLED:
            return None

        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - self._timestamps[cache_key] < ai_config.AI_CACHE_TTL:
                logger.debug(f"缓存命中: {cache_key[:50]}...")
                return entry["response"]
            else:
                self.delete(cache_key)
        return None

    def set(self, cache_key: str, response: AIResponse) -> None:
        """设置缓存"""
        if not ai_config.AI_CACHE_ENABLED:
            return

        self._cache[cache_key] = {"response": response}
        self._timestamps[cache_key] = time.time()
        logger.debug(f"缓存设置: {cache_key[:50]}...")

    def delete(self, cache_key: str) -> None:
        """删除缓存"""
        if cache_key in self._cache:
            del self._cache[cache_key]
            del self._timestamps[cache_key]

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
        logger.info("AI缓存已清空")

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {"total_entries": len(self._cache), "keys": list(self._cache.keys())}


_ai_cache = AICache()


def get_cache() -> AICache:
    """获取缓存实例"""
    return _ai_cache


def generate_cache_key(
    messages: List[Dict], provider: ModelProvider, model: str
) -> str:
    """生成缓存键"""
    import hashlib

    content = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    key = f"{provider.value}:{model}:{hashlib.md5(content.encode()).hexdigest()}"
    return key


class BaseModelClient:
    """模型客户端基类"""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self.client = httpx.AsyncClient(timeout=ai_config.AI_REQUEST_TIMEOUT)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        raise NotImplementedError

    async def _make_request(
        self, url: str, headers: Dict, payload: Dict, model: str
    ) -> AIResponse:
        """执行HTTP请求"""
        start_time = time.time()
        try:
            response = await self.client.post(
                url, headers=headers, json=payload, timeout=ai_config.AI_REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            content = self._extract_content(data)
            response_time = time.time() - start_time

            return AIResponse(
                content=content,
                provider=self.provider,
                model=model,
                status=RequestStatus.SUCCESS,
                response_time=response_time,
                raw_response=data,
            )
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"模型请求失败: {e}")
            return AIResponse(
                content="",
                provider=self.provider,
                model=model,
                status=RequestStatus.FAILED,
                response_time=response_time,
                error=str(e),
            )

    def _extract_content(self, data: Dict) -> str:
        """从响应中提取内容"""
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice:
                return choice["message"].get("content", "")
        return ""


class OpenAIClient(BaseModelClient):
    """OpenAI客户端"""

    def __init__(self):
        super().__init__(ModelProvider.OPENAI)

    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        config = ai_config.get_active_provider_config()

        url = f"{config['api_base']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature or config["temperature"],
            "max_tokens": max_tokens or config["max_tokens"],
        }

        return await self._make_request(url, headers, payload, config["model"])


class DeepSeekClient(BaseModelClient):
    """DeepSeek客户端"""

    def __init__(self):
        super().__init__(ModelProvider.DEEPSEEK)

    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        config = ai_config.get_active_provider_config()

        url = f"{config['api_base']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature or config["temperature"],
            "max_tokens": max_tokens or config["max_tokens"],
        }

        return await self._make_request(url, headers, payload, config["model"])


class QwenClient(BaseModelClient):
    """通义千问客户端"""

    def __init__(self):
        super().__init__(ModelProvider.QWEN)

    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        config = ai_config.get_active_provider_config()

        url = f"{config['api_base']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature or config["temperature"],
            "max_tokens": max_tokens or config["max_tokens"],
        }

        return await self._make_request(url, headers, payload, config["model"])


class ModelClientFactory:
    """模型客户端工厂"""

    _clients: Dict[ModelProvider, type] = {
        ModelProvider.OPENAI: OpenAIClient,
        ModelProvider.DEEPSEEK: DeepSeekClient,
        ModelProvider.QWEN: QwenClient,
    }

    @classmethod
    def create(cls, provider: Optional[ModelProvider] = None) -> BaseModelClient:
        """创建模型客户端"""
        provider = provider or ai_config.AI_MODEL_PROVIDER
        client_class = cls._clients.get(provider)
        if client_class is None:
            raise ValueError(f"不支持的模型提供商: {provider}")
        return client_class()

    @classmethod
    def get_all_providers(cls) -> List[ModelProvider]:
        """获取所有支持的提供商"""
        return list(cls._clients.keys())


class AIModelService:
    """AI模型服务核心类"""

    def __init__(self):
        self.cache = get_cache()

    async def chat(
        self,
        messages: List[Dict],
        use_cache: bool = True,
        provider: Optional[ModelProvider] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        enable_fallback: bool = True,
    ) -> AIResponse:
        """
        执行聊天完成请求

        参数:
            messages: 消息列表
            use_cache: 是否使用缓存
            provider: 指定提供商（不指定则使用默认）
            temperature: 温度参数
            max_tokens: 最大token数
            enable_fallback: 是否启用降级
        """
        # 检查缓存
        cache_key = generate_cache_key(
            messages,
            provider or ai_config.AI_MODEL_PROVIDER,
            ai_config.get_active_provider_config()["model"],
        )
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached.status = RequestStatus.CACHED
                cached.cache_hit = True
                return cached

        # 尝试主要提供商
        response = await self._try_provider(messages, provider, temperature, max_tokens)

        # 降级处理
        if (
            not response.is_success
            and enable_fallback
            and ai_config.AI_FALLBACK_ENABLED
        ):
            response = await self._try_fallback(messages, temperature, max_tokens)

        # 缓存成功响应
        if response.is_success and use_cache:
            self.cache.set(cache_key, response)

        return response

    async def _try_provider(
        self,
        messages: List[Dict],
        provider: Optional[ModelProvider],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> AIResponse:
        """尝试单个提供商"""
        client = ModelClientFactory.create(provider)

        # 重试机制
        for attempt in range(ai_config.AI_MAX_RETRIES):
            try:
                async with client:
                    response = await client.chat_completion(
                        messages, temperature, max_tokens
                    )
                    if response.is_success:
                        return response

                    if attempt < ai_config.AI_MAX_RETRIES - 1:
                        logger.warning(
                            f"请求失败，{ai_config.AI_RETRY_DELAY}秒后重试 (第{attempt+1}次)"
                        )
                        await asyncio.sleep(ai_config.AI_RETRY_DELAY)

            except Exception as e:
                logger.error(f"提供商调用异常: {e}")
                if attempt == ai_config.AI_MAX_RETRIES - 1:
                    return AIResponse(
                        content="",
                        provider=provider or ai_config.AI_MODEL_PROVIDER,
                        model="unknown",
                        status=RequestStatus.FAILED,
                        response_time=0,
                        error=str(e),
                    )

        return response

    async def _try_fallback(
        self,
        messages: List[Dict],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> AIResponse:
        """尝试降级提供商"""
        logger.info("开始降级策略...")

        current_provider = ai_config.AI_MODEL_PROVIDER
        fallback_order = [
            p for p in ai_config.AI_FALLBACK_PROVIDER_ORDER if p != current_provider
        ]

        for fallback_provider in fallback_order:
            logger.info(f"尝试降级提供商: {fallback_provider}")
            response = await self._try_provider(
                messages, fallback_provider, temperature, max_tokens
            )
            if response.is_success:
                response.is_fallback = True
                logger.info(f"降级成功: {fallback_provider}")
                return response

        logger.warning("所有降级提供商均失败")
        return response


_ai_service = AIModelService()


def get_ai_service() -> AIModelService:
    """获取AI模型服务实例"""
    return _ai_service
