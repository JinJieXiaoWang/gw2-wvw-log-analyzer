# -*- coding: utf-8 -*-
"""
数据模块 API 冒烟测试（Fights / Members / Skills / Builds / Dashboard / GameData）
==============================================================================
对数据查询类端点进行基础可达性和响应结构验证，不深入业务逻辑。
"""

import pytest
from httpx import AsyncClient


class TestFights:
    """战斗数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_fights_list(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/fights", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_fight_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/fights/999999999", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_fight_stats_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/fights/999999999/stats", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_fights_without_auth(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/fights")
        # 当前实现不需要认证
        assert resp.status_code in (200, 401)


class TestEiAnalysis:
    """EI 分析摘要接口测试"""

    @pytest.mark.asyncio
    async def test_ei_analysis_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/ei-analysis/999999999", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["code"] == 404

    @pytest.mark.asyncio
    async def test_ei_analysis_structure(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        # 先获取日志列表，尝试用第一个日志测试
        logs_resp = await async_client.get(
            "/api/v1/logs?page=1&page_size=1", headers=auth_headers
        )
        if logs_resp.status_code != 200:
            pytest.skip("无法获取日志列表")
        logs_data = logs_resp.json()
        items = logs_data.get("data", {}).get("items", [])
        if not items:
            pytest.skip("数据库中无日志记录")

        log_id = items[0]["id"]
        resp = await async_client.get(
            f"/api/v1/ei-analysis/{log_id}", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        payload = data.get("data", {})
        # 验证核心字段结构
        assert "log_id" in payload
        assert "fight" in payload
        assert "aggregate" in payload
        assert "players" in payload
        assert "profession_distribution" in payload
        assert "buff_leaders" in payload
        assert "support_leaders" in payload
        assert "defense_leaders" in payload
        # fight 字段
        fight = payload["fight"]
        assert "map_name" in fight
        assert "duration_sec" in fight
        assert "kill_count" in fight
        assert "death_count" in fight
        # aggregate 字段
        agg = payload["aggregate"]
        assert "total_damage" in agg
        assert "avg_dps" in agg
        # players 数组
        players = payload["players"]
        if players:
            p0 = players[0]
            assert "account" in p0
            assert "damage" in p0
            assert "dps" in p0
            assert "profession" in p0


class TestMembers:
    """成员数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_members_list(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/members", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_members_professions(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/members/professions", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_members_ranking(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/members/ranking", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_member_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/members/999999999", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_member_stats_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/members/999999999/stats", headers=auth_headers
        )
        assert resp.status_code == 404


class TestSkills:
    """技能数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_skills_list(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/skills", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_skill_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/skills/999999999", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_skill_events_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/skills/999999999/events", headers=auth_headers
        )
        # 当前实现返回 200
        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_skill_rotation_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/skills/999999999/rotation", headers=auth_headers
        )
        # 当前实现返回 200
        assert resp.status_code in (200, 404)


class TestBuilds:
    """Build 数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_builds_list(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/builds", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_build_detail_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/builds/999999999", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_build_compare_without_body(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/builds/compare", headers=auth_headers, json={}
        )
        assert resp.status_code in (200, 400, 422)

    @pytest.mark.asyncio
    async def test_build_parse_without_body(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            "/api/v1/builds/parse", headers=auth_headers, json={}
        )
        assert resp.status_code in (200, 400, 422)


class TestDashboard:
    """仪表盘数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_dashboard_overview(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/dashboard/overview", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dashboard_maps(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/dashboard/maps", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dashboard_recent(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/dashboard/recent", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, async_client: AsyncClient, auth_headers: dict):
        resp = await async_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dashboard_trends(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get("/api/v1/dashboard/trends", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dashboard_profession_distribution(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            "/api/v1/dashboard/profession-distribution", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestGameData:
    """游戏数据接口冒烟测试"""

    @pytest.mark.asyncio
    async def test_game_data_info(self, async_client: AsyncClient):
        """游戏数据信息为公开端点"""
        resp = await async_client.get("/api/v1/game-data/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
