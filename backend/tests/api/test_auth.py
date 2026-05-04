# -*- coding: utf-8 -*-
"""
认证模块 API 深度测试
=====================
覆盖场景：
- 正常登录 / 失败登录（密码错误、用户名不存在、参数缺失）
- 登出（已认证 / 未认证）
- 登录状态查询（有 token / 无 token / 无效 token）
- 用户信息获取（已认证 / 未认证）
- 修改密码（正常流程、旧密码错误、参数校验）
- Token 边界：过期 token、 malformed token、空 token
"""

import pytest
from httpx import AsyncClient


class TestAuthLogin:
    """登录接口测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """正常登录应返回 JWT token 和用户信息"""
        resp = await async_client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "123456"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
        assert "permissions" in data["data"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient):
        """密码错误应返回 400 业务错误"""
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong_password_123"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False
        assert "密码" in data.get("message", "") or "用户名" in data.get("message", "")

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """不存在的用户名应返回 400"""
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent_user_99999", "password": "any_password"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_login_missing_username(self, async_client: AsyncClient):
        """缺少用户名应返回 422 验证错误"""
        resp = await async_client.post(
            "/api/v1/auth/login", json={"password": "123456"}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_password(self, async_client: AsyncClient):
        """缺少密码应返回 422 验证错误"""
        resp = await async_client.post("/api/v1/auth/login", json={"username": "admin"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_empty_body(self, async_client: AsyncClient):
        """空请求体应返回 422"""
        resp = await async_client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422


class TestAuthLogout:
    """登出接口测试"""

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, auth_headers: dict):
        """已认证用户登出应返回成功"""
        resp = await async_client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, async_client: AsyncClient):
        """未认证用户登出应返回 401"""
        resp = await async_client.post("/api/v1/auth/logout")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, async_client: AsyncClient):
        """无效 token 登出应返回 401"""
        resp = await async_client.post(
            "/api/v1/auth/logout", headers={"Authorization": "Bearer invalid_token_123"}
        )
        assert resp.status_code == 401


class TestAuthStatus:
    """登录状态查询测试"""

    @pytest.mark.asyncio
    async def test_status_no_token(self, async_client: AsyncClient):
        """无 token 应返回未登录状态"""
        resp = await async_client.get("/api/v1/auth/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["is_logged_in"] is False
        assert data["data"]["permissions"] == ["read"]

    @pytest.mark.asyncio
    async def test_status_with_valid_token(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """有效 token 应返回已登录状态和用户信息"""
        resp = await async_client.get("/api/v1/auth/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["is_logged_in"] is True
        assert "user" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    @pytest.mark.asyncio
    async def test_status_with_malformed_token(self, async_client: AsyncClient):
        """格式错误的 token 应返回未登录状态（而非抛异常）"""
        resp = await async_client.get(
            "/api/v1/auth/status", headers={"Authorization": "InvalidFormat token"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["is_logged_in"] is False


class TestAuthProfile:
    """用户信息接口测试"""

    @pytest.mark.asyncio
    async def test_profile_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """已认证用户获取个人信息"""
        resp = await async_client.get("/api/v1/auth/profile", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "user" in data["data"]
        assert "permissions" in data["data"]

    @pytest.mark.asyncio
    async def test_profile_without_auth(self, async_client: AsyncClient):
        """未认证用户应返回 401"""
        resp = await async_client.get("/api/v1/auth/profile")
        assert resp.status_code == 401


class TestAuthChangePassword:
    """修改密码接口测试"""

    @pytest.mark.asyncio
    async def test_change_password_wrong_old(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """旧密码错误应返回 400"""
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrong_old_password",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False
        assert "密码" in data.get("message", "")

    @pytest.mark.asyncio
    async def test_change_password_missing_fields(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """缺少字段应返回 422 (Pydantic 验证错误)"""
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={"current_password": "123456"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_too_short(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """新密码太短应返回 422 (Pydantic 最小长度验证)"""
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "123456",
                "new_password": "123",
                "confirm_password": "123",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_mismatch_confirm(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """两次输入的密码不一致应返回 400"""
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "123456",
                "new_password": "newpass123",
                "confirm_password": "different123",
            },
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False
        assert "不一致" in data.get("message", "")

    @pytest.mark.asyncio
    async def test_change_password_without_auth(self, async_client: AsyncClient):
        """未认证修改密码应返回 401"""
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "123456",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password_invalidates_old_token(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """修改密码后，旧 token 应失效"""
        # 先用旧 token 获取 profile（应成功）
        resp = await async_client.get("/api/v1/auth/profile", headers=auth_headers)
        assert resp.status_code == 200

        try:
            # 修改密码
            resp = await async_client.post(
                "/api/v1/auth/change-password",
                headers=auth_headers,
                json={
                    "current_password": "123456",
                    "new_password": "newpass123",
                    "confirm_password": "newpass123",
                },
            )
            assert resp.status_code == 200

            # 再用旧 token 获取 profile（应失败）
            resp = await async_client.get("/api/v1/auth/profile", headers=auth_headers)
            assert resp.status_code == 401
            data = resp.json()
            assert "失效" in data.get("message", "") or "重新登录" in data.get("message", "")
        finally:
            # 恢复密码，避免影响其他测试（使用新密码登录后再改回）
            login_resp = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "admin", "password": "newpass123"},
            )
            if login_resp.status_code == 200:
                new_token = login_resp.json()["data"]["access_token"]
                new_headers = {"Authorization": f"Bearer {new_token}"}
                await async_client.post(
                    "/api/v1/auth/change-password",
                    headers=new_headers,
                    json={
                        "current_password": "newpass123",
                        "new_password": "123456",
                        "confirm_password": "123456",
                    },
                )


class TestAuthTokenEdgeCases:
    """Token 边界条件测试"""

    @pytest.mark.asyncio
    async def test_access_protected_with_expired_token_format(
        self, async_client: AsyncClient
    ):
        """使用明显过期/伪造的 JWT 访问受保护资源应返回 401"""
        # 构造一个结构像 JWT 但签名无效的 token
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxMDAwfQ.invalid_signature"
        resp = await async_client.get(
            "/api/v1/auth/profile", headers={"Authorization": f"Bearer {fake_token}"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_with_empty_token(self, async_client: AsyncClient):
        """空 Bearer token 应返回 401"""
        resp = await async_client.get(
            "/api/v1/auth/profile", headers={"Authorization": "Bearer "}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_no_bearer_prefix(self, async_client: AsyncClient):
        """缺少 Bearer 前缀应返回 401"""
        resp = await async_client.get(
            "/api/v1/auth/profile", headers={"Authorization": "some_token_value"}
        )
        assert resp.status_code == 401
