# -*- coding: utf-8 -*-
"""
通知系统 API 测试
================
覆盖场景：
- 游客访问（返回空数据，不 401）
- 已认证用户完整业务流程
- 未认证写操作（标记已读）→ 401
"""

import pytest
from httpx import AsyncClient

from app.config.database import get_db_context
from app.models.sys_notice import SysNotice, SysNoticeRead
from app.services.system.notice_service import NoticeService


class TestNoticeGuestAccess:
    """游客访问测试 — 通知查询接口应允许游客访问"""

    @pytest.mark.asyncio
    async def test_guest_unread_count(self, async_client: AsyncClient):
        """游客获取未读计数应返回 0"""
        resp = await async_client.get("/api/v1/notices/unread-count")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["count"] == 0

    @pytest.mark.asyncio
    async def test_guest_list(self, async_client: AsyncClient):
        """游客获取通知列表应返回空数组"""
        resp = await async_client.get("/api/v1/notices")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_guest_mark_read(self, async_client: AsyncClient):
        """游客标记已读应返回 401"""
        resp = await async_client.post("/api/v1/notices/1/read")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_guest_mark_all_read(self, async_client: AsyncClient):
        """游客全部已读应返回 401"""
        resp = await async_client.post("/api/v1/notices/read-all")
        assert resp.status_code == 401


class TestNoticeWithAuth:
    """已认证通知功能测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """每个测试前后清理测试数据"""
        yield
        with get_db_context() as db:
            db.query(SysNoticeRead).filter(SysNoticeRead.user_id == 1).delete()
            db.query(SysNotice).filter(SysNotice.create_by == 'api_test').delete()
            db.commit()

    @pytest.mark.asyncio
    async def test_unread_count_empty(self, async_client: AsyncClient, auth_headers):
        """无通知时未读计数为 0"""
        resp = await async_client.get(
            "/api/v1/notices/unread-count", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["count"] == 0

    @pytest.mark.asyncio
    async def test_list_empty(self, async_client: AsyncClient, auth_headers):
        """无通知时列表为空"""
        resp = await async_client.get("/api/v1/notices", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_full_flow(self, async_client: AsyncClient, auth_headers):
        """完整业务流程：创建 → 查询 → 标记已读 → 全部已读"""
        # 1. 创建测试通知
        with get_db_context() as db:
            NoticeService.create_notice(db, "API测试通知1", "内容1", "1", create_by="api_test")
            NoticeService.create_notice(db, "API测试通知2", "内容2", "1", create_by="api_test")
            NoticeService.create_notice(db, "API测试公告", "公告内容", "2", create_by="api_test")
            db.commit()

        # 2. 获取未读计数
        resp = await async_client.get(
            "/api/v1/notices/unread-count", headers=auth_headers
        )
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["count"] == 3

        # 3. 获取列表
        resp = await async_client.get("/api/v1/notices", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert len(data["data"]["items"]) == 3
        # 第一条未读
        assert data["data"]["items"][0]["is_read"] is False
        notice_id = data["data"]["items"][0]["notice_id"]

        # 4. 标记单条已读
        resp = await async_client.post(
            f"/api/v1/notices/{notice_id}/read", headers=auth_headers
        )
        data = resp.json()
        assert data["success"] is True

        # 5. 未读计数应为 2
        resp = await async_client.get(
            "/api/v1/notices/unread-count", headers=auth_headers
        )
        data = resp.json()
        assert data["data"]["count"] == 2

        # 6. 列表中该条应为已读
        resp = await async_client.get("/api/v1/notices", headers=auth_headers)
        data = resp.json()
        item = next(i for i in data["data"]["items"] if i["notice_id"] == notice_id)
        assert item["is_read"] is True

        # 7. 仅查询未读
        resp = await async_client.get(
            "/api/v1/notices?unread_only=true", headers=auth_headers
        )
        data = resp.json()
        assert data["data"]["total"] == 2

        # 8. 标记全部已读
        resp = await async_client.post(
            "/api/v1/notices/read-all", headers=auth_headers
        )
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["count"] == 2

        # 9. 未读计数应为 0
        resp = await async_client.get(
            "/api/v1/notices/unread-count", headers=auth_headers
        )
        data = resp.json()
        assert data["data"]["count"] == 0

        # 10. 重复标记不报错
        resp = await async_client.post(
            f"/api/v1/notices/{notice_id}/read", headers=auth_headers
        )
        assert resp.status_code == 200

        # 11. 重复全部标记不报错
        resp = await async_client.post(
            "/api/v1/notices/read-all", headers=auth_headers
        )
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["count"] == 0

    @pytest.mark.asyncio
    async def test_pagination(self, async_client: AsyncClient, auth_headers):
        """分页测试"""
        with get_db_context() as db:
            for i in range(25):
                NoticeService.create_notice(
                    db, f"分页通知{i}", f"内容{i}", "1", create_by="api_test"
                )
            db.commit()

        # 第1页
        resp = await async_client.get(
            "/api/v1/notices?page=1&page_size=10", headers=auth_headers
        )
        data = resp.json()
        assert data["data"]["total"] == 25
        assert len(data["data"]["items"]) == 10
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10

        # 第3页
        resp = await async_client.get(
            "/api/v1/notices?page=3&page_size=10", headers=auth_headers
        )
        data = resp.json()
        assert len(data["data"]["items"]) == 5

    @pytest.mark.asyncio
    async def test_invalid_page_params(self, async_client: AsyncClient, auth_headers):
        """无效分页参数应返回 422"""
        resp = await async_client.get(
            "/api/v1/notices?page=0", headers=auth_headers
        )
        assert resp.status_code == 422

        resp = await async_client.get(
            "/api/v1/notices?page_size=200", headers=auth_headers
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_mark_read_invalid_id(self, async_client: AsyncClient, auth_headers):
        """标记不存在的通知应正常处理（不报错）"""
        resp = await async_client.post(
            "/api/v1/notices/99999/read", headers=auth_headers
        )
        # 即使 notice_id 不存在，也应返回成功（因为只是标记已读）
        assert resp.status_code == 200
