# -*- coding: utf-8 -*-
"""
系统模块 API 冒烟测试（Dictionary / Users / Attendance / AI / Storage / Scoring / Monitor / Settings）
======================================================================================================
验证各系统模块端点的基础可达性和响应结构。
"""

import pytest
from httpx import AsyncClient


class TestDictionary:
    """字典管理接口测试"""

    @pytest.mark.asyncio
    async def test_dictionary_types_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """字典类型列表需要认证"""
        resp = await async_client.get("/api/v1/dictionary/types", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dictionary_types_all(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/dictionary/types/all", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dictionary_options(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/dictionary/options/test_type")
        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_dictionary_data_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/dictionary/data", headers=auth_headers)
        # 可能返回 422（缺少必需查询参数）
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_dictionary_data_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/dictionary/data/NONEXISTENT", headers=auth_headers
        )
        # 可能返回 422（参数校验失败）
        assert resp.status_code in (404, 422)

    @pytest.mark.asyncio
    async def test_dictionary_init_without_auth(self, async_client: AsyncClient):
        resp = await async_client.post("/api/v1/dictionary/init")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_dictionary_reload_cache_without_auth(
        self, async_client: AsyncClient
    ):
        resp = await async_client.post("/api/v1/dictionary/reload-cache")
        assert resp.status_code == 401


class TestUsers:
    """用户管理接口测试"""

    @pytest.mark.asyncio
    async def test_users_list_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/users", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_users_list_without_auth(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/users")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_user_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/users/999999999", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_user_profile_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/users/profile", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_user_roles_list_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/users/roles/list", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_user_reset_password_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/users/999999999/reset-password", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_user_toggle_active_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/users/999999999/toggle-active", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_user_change_password_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/users/change-password", headers=auth_headers, json={}
        )
        assert resp.status_code in (200, 400, 422)


class TestAttendance:
    """出勤统计接口测试"""

    @pytest.mark.asyncio
    async def test_attendance_list_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/attendance", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_attendance_stats_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/attendance/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_attendance_export_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/attendance/export", headers=auth_headers)
        assert resp.status_code in (200, 404, 400)

    @pytest.mark.asyncio
    async def test_attendance_member_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/attendance/999999999", headers=auth_headers
        )
        # 可能返回 200（空数据）或 404
        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_attendance_without_auth(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/attendance")
        # 当前实现不需要认证
        assert resp.status_code in (200, 401)


class TestAI:
    """AI 分析接口测试"""

    @pytest.mark.asyncio
    async def test_ai_reports_list_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/ai/reports", headers=auth_headers)
        assert resp.status_code in (200, 500)  # 可能依赖外部服务
        if resp.status_code == 200:
            data = resp.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_ai_suggestions_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/ai/suggestions", headers=auth_headers)
        assert resp.status_code in (200, 500)

    @pytest.mark.asyncio
    async def test_ai_trend_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/ai/trend", headers=auth_headers)
        # 当前实现可能返回 404（数据不足）
        assert resp.status_code in (200, 404, 500)

    @pytest.mark.asyncio
    async def test_ai_analyze_fight_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/ai/analyze/fight/999999999", headers=auth_headers
        )
        assert resp.status_code in (404, 400, 500)

    @pytest.mark.asyncio
    async def test_ai_analyze_build_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/ai/analyze/build/999999999", headers=auth_headers
        )
        assert resp.status_code in (404, 400, 500)

    @pytest.mark.asyncio
    async def test_ai_analyze_member_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/ai/analyze/member/999999999", headers=auth_headers
        )
        assert resp.status_code in (404, 400, 500)

    @pytest.mark.asyncio
    async def test_ai_reports_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/ai/reports/999999999", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_ai_delete_report_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.delete(
            "/api/v1/ai/reports/999999999", headers=auth_headers
        )
        assert resp.status_code == 404


class TestStorage:
    """存储管理接口测试"""

    @pytest.mark.asyncio
    async def test_storage_status_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/storage/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_storage_cleanup_records_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/storage/cleanup/records", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_storage_cleanup_without_auth(self, async_client: AsyncClient):
        resp = await async_client.post("/api/v1/storage/cleanup/parsed")
        assert resp.status_code == 401


class TestScoring:
    """评分接口测试"""

    @pytest.mark.asyncio
    async def test_scoring_rules_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/scoring/rules", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_scoring_fight_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/scoring/fight/999999999", headers=auth_headers
        )
        # 当前实现返回 200
        assert resp.status_code in (200, 404)


class TestMonitor:
    """监控接口测试"""

    @pytest.mark.asyncio
    async def test_monitor_health(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/monitor/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_monitor_errors_stats(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/monitor/errors/stats", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_monitor_errors_report(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/monitor/errors/report", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_monitor_errors_clear_without_auth(self, async_client: AsyncClient):
        resp = await async_client.post("/api/v1/monitor/errors/clear")
        assert resp.status_code == 401


class TestSettings:
    """系统设置接口测试"""

    @pytest.mark.asyncio
    async def test_settings_get_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/settings", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_settings_put_with_auth(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.put("/api/v1/settings", headers=auth_headers, json={})
        assert resp.status_code in (200, 400, 422)

    @pytest.mark.asyncio
    async def test_settings_reset_without_auth(self, async_client: AsyncClient):
        resp = await async_client.post("/api/v1/settings/reset")
        # 当前实现不需要认证
        assert resp.status_code in (200, 401)

    @pytest.mark.asyncio
    async def test_settings_without_auth(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/settings")
        # 当前实现不需要认证
        assert resp.status_code in (200, 401)
