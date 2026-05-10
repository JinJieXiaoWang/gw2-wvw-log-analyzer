# -*- coding: utf-8 -*-
"""
API 测试基础设施
提供 TestClient、认证 fixtures、以及公共测试工具
"""

import json
from typing import Any, Dict, Optional

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.log import Log
from main import app


@pytest.fixture(scope="session")
def openapi_schema() -> Dict[str, Any]:
    """加载 OpenAPI Schema（由外部脚本预生成）"""
    with open("docs/openapi_schema.json", encoding="utf-8") as f:
        return json.load(f)


@pytest_asyncio.fixture
async def async_client():
    """创建异步 HTTP 客户端（自动处理 lifespan）"""
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient) -> Dict[str, str]:
    """
    获取已认证请求头（Bearer Token）
    使用预置管理员账号登录
    """
    login_payload = {"username": "admin", "password": "123456"}
    resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 200, f"登录失败: {resp.text}"
    data = resp.json()
    assert data.get("success") is True, f"登录响应异常: {data}"
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db_session() -> Session:
    """获取数据库会话（供直接 ORM 操作使用）"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def existing_log_id(db_session: Session) -> Optional[int]:
    """
    返回数据库中已存在的日志 ID（优先返回已完成解析的日志）
    用于需要真实 log_id 的测试场景
    """
    log = (
        db_session.query(Log)
        .filter(Log.parse_status == "completed")
        .order_by(Log.id.desc())
        .first()
    )
    if log:
        return log.id
    log = db_session.query(Log).order_by(Log.id.desc()).first()
    if log:
        return log.id
    return None


class ApiTester:
    """
    封装常用 API 测试断言工具
    """

    @staticmethod
    def assert_success(response, expected_status: int = 200):
        assert (
            response.status_code == expected_status
        ), f"HTTP {response.status_code}: {response.text[:500]}"
        data = response.json()
        assert data.get("success") is True, f"业务失败: {data.get('message', data)}"
        return data

    @staticmethod
    def assert_error(
        response, expected_status: int, expected_msg_substring: Optional[str] = None
    ):
        assert (
            response.status_code == expected_status
        ), f"期望 HTTP {expected_status}，实际 {response.status_code}: {response.text[:500]}"
        data = response.json()
        # 可能返回 success=False 或者 detail 错误
        msg = data.get("message", data.get("detail", str(data)))
        if expected_msg_substring:
            assert (
                expected_msg_substring in msg
            ), f"错误消息不包含 '{expected_msg_substring}': {msg}"
        return data
