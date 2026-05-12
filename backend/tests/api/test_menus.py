# -*- coding: utf-8 -*-
"""
菜单管理 API 集成测试
=====================
覆盖场景
- 创建菜单（正常流程、参数校验）
- 查询菜单（列表、详情、树形结构）
- 更新菜单
- 删除菜单（含子菜单级联删除）
- 获取用户可用菜单（权限控制）
- 批量操作菜单
- 初始化默认菜单
- 刷新缓存
"""

import pytest
from httpx import AsyncClient


class TestMenuCreate:
    """菜单创建接口测试"""

    @pytest.mark.asyncio
    async def test_create_menu_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """创建菜单成功"""
        import uuid
        unique_name = f"测试菜单_{uuid.uuid4().hex[:8]}"
        resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": unique_name,
                "parent_id": 0,
                "order_num": 999,
                "path": "/test",
                "component": "test/index",
                "route_name": "test",
                "menu_type": "C",
                "visible": "0",
                "status": "0",
                "icon": "home",
                "perms": "read",
                "remark": "测试菜单",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["menu_name"] == unique_name

    @pytest.mark.asyncio
    async def test_create_menu_without_auth(self, async_client: AsyncClient):
        """未认证创建菜单应返回 401"""
        resp = await async_client.post(
            "/api/v1/menus",
            json={
                "menu_name": "测试菜单",
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_menu_missing_required(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """缺少必填字段应返回 422"""
        resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={"parent_id": 0, "order_num": 1},
        )
        assert resp.status_code == 422


class TestMenuQuery:
    """菜单查询接口测试"""

    @pytest.mark.asyncio
    async def test_list_menus_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """分页查询菜单列表"""
        resp = await async_client.get(
            "/api/v1/menus?page=1&size=10", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "total" in data["data"]
        assert "items" in data["data"]

    @pytest.mark.asyncio
    async def test_get_menu_tree_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """获取菜单树形结构"""
        resp = await async_client.get("/api/v1/menus/tree", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_user_menus_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """获取用户可用菜单"""
        resp = await async_client.get("/api/v1/menus/user", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_get_permissions_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """获取所有权限标识"""
        resp = await async_client.get("/api/v1/menus/permissions/all", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    @pytest.fixture(scope="class")
    async def test_menu_id(self, async_client: AsyncClient, auth_headers: dict):
        """获取一个测试菜单的ID"""
        resp = await async_client.get("/api/v1/menus?page=1&size=1", headers=auth_headers)
        data = resp.json()
        if data["data"]["items"]:
            return data["data"]["items"][0]["menu_id"]
        # 创建测试菜单
        resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "查询测试菜单",
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            },
        )
        return resp.json()["data"]["menu_id"]

    @pytest.mark.asyncio
    async def test_get_menu_detail_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """获取菜单详情"""
        # 先获取一个菜单ID
        list_resp = await async_client.get("/api/v1/menus?page=1&size=1", headers=auth_headers)
        list_data = list_resp.json()
        if not list_data["data"]["items"]:
            # 创建测试菜单
            create_resp = await async_client.post(
                "/api/v1/menus",
                headers=auth_headers,
                json={
                    "menu_name": "详情测试菜单",
                    "parent_id": 0,
                    "order_num": 1,
                    "menu_type": "C",
                    "visible": "0",
                    "status": "0",
                },
            )
            menu_id = create_resp.json()["data"]["menu_id"]
        else:
            menu_id = list_data["data"]["items"][0]["menu_id"]

        resp = await async_client.get(f"/api/v1/menus/{menu_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["menu_id"] == menu_id


class TestMenuUpdate:
    """菜单更新接口测试"""

    @pytest.fixture(scope="class")
    async def test_update_menu_id(self, async_client: AsyncClient, auth_headers: dict):
        """创建一个用于更新测试的菜单"""
        resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "待更新菜单",
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            },
        )
        return resp.json()["data"]["menu_id"]

    @pytest.mark.asyncio
    async def test_update_menu_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """更新菜单成功"""
        import uuid
        unique_name = f"待更新菜单_{uuid.uuid4().hex[:8]}"
        update_name = f"已更新菜单_{uuid.uuid4().hex[:8]}"
        
        # 创建测试菜单
        create_resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": unique_name,
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            },
        )
        menu_id = create_resp.json()["data"]["menu_id"]

        resp = await async_client.put(
            f"/api/v1/menus/{menu_id}",
            headers=auth_headers,
            json={"menu_name": update_name, "order_num": 2},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["menu_name"] == update_name

    @pytest.mark.asyncio
    async def test_update_nonexistent_menu(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """更新不存在的菜单应返回 404"""
        resp = await async_client.put(
            "/api/v1/menus/99999",
            headers=auth_headers,
            json={"menu_name": "不存在的菜单"},
        )
        assert resp.status_code == 404


class TestMenuDelete:
    """菜单删除接口测试"""

    @pytest.fixture(scope="class")
    async def test_delete_menu_id(self, async_client: AsyncClient, auth_headers: dict):
        """创建一个用于删除测试的菜单"""
        resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "待删除菜单",
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            },
        )
        return resp.json()["data"]["menu_id"]

    @pytest.mark.asyncio
    async def test_delete_menu_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """正常删除菜单"""
        # 创建测试菜单
        create_resp = await async_client.post(
            "/api/v1/menus",
            headers=auth_headers,
            json={
                "menu_name": "待删除菜单",
                "parent_id": 0,
                "order_num": 1,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            },
        )
        menu_id = create_resp.json()["data"]["menu_id"]

        # 删除菜单
        resp = await async_client.delete(f"/api/v1/menus/{menu_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_menu(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """删除不存在的菜单应返回 404"""
        resp = await async_client.delete("/api/v1/menus/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestMenuBatch:
    """菜单批量操作测试"""

    @pytest.mark.asyncio
    async def test_batch_update_menus_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """批量更新菜单"""
        import uuid
        unique_suffix = uuid.uuid4().hex[:8]
        
        # 先创建几个测试菜单
        menu_ids = []
        for i in range(2):
            resp = await async_client.post(
                "/api/v1/menus",
                headers=auth_headers,
                json={
                    "menu_name": f"批量菜单{i}_{unique_suffix}",
                    "parent_id": 0,
                    "order_num": i,
                    "menu_type": "C",
                    "visible": "0",
                    "status": "0",
                },
            )
            menu_ids.append(resp.json()["data"]["menu_id"])

        # 批量更新
        resp = await async_client.post(
            "/api/v1/menus/batch",
            headers=auth_headers,
            json=[{"menu_id": mid, "visible": "1"} for mid in menu_ids],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestMenuInit:
    """默认菜单初始化测试"""

    @pytest.mark.asyncio
    async def test_init_default_menus_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """初始化默认菜单"""
        resp = await async_client.post("/api/v1/menus/init", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestMenuCache:
    """菜单缓存测试"""

    @pytest.mark.asyncio
    async def test_refresh_cache_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """刷新菜单缓存"""
        resp = await async_client.post("/api/v1/menus/refresh-cache", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestMenuAuthIntegration:
    """菜单与认证集成测试"""

    @pytest.mark.asyncio
    async def test_login_returns_menus(self, async_client: AsyncClient):
        """登录接口应返回用户可用菜单"""
        # 重置登录尝试次数
        from app.services.auth.auth_service import reset_all_login_attempts
        reset_all_login_attempts()
        
        resp = await async_client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "123456"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "menus" in data["data"]
        assert isinstance(data["data"]["menus"], list)

    @pytest.mark.asyncio
    async def test_status_returns_menus(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """获取登录状态接口应返回用户可用菜单"""
        resp = await async_client.get("/api/v1/auth/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "menus" in data["data"]
        assert isinstance(data["data"]["menus"], list)
