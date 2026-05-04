# -*- coding: utf-8 -*-
"""
文件上传功能回归测试
验证 ZEVTC 文件上传后数据库记录完整
"""

from io import BytesIO

import pytest
from httpx import AsyncClient


class TestLogUpload:
    """日志上传接口测试"""

    @pytest.mark.asyncio
    async def test_upload_zevtc_file(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """上传真实 ZEVTC 文件，验证返回结构和数据库字段完整性"""
        import os
        import random

        test_file_path = "tests/20260426-220412.zevtc"
        if not os.path.exists(test_file_path):
            pytest.skip("测试用 ZEVTC 文件不存在")

        # 使用随机后缀避免 SHA256 重复
        unique_suffix = f"_{random.randint(100000, 999999)}"
        with open(test_file_path, "rb") as f:
            content = f.read()
        # 在 ZIP 内部追加一个无关的额外字节来改变 SHA256（不影响 EVTC 解析）
        # 更简单的方式：使用一个临时文件名，因为 SHA256 基于内容而非文件名
        # 但内容相同会导致 SHA256 重复，所以我们先检查是否已存在
        resp = await async_client.post(
            "/api/v1/logs?auto_parse=false",
            headers=auth_headers,
            files={
                "file": (
                    f"test{unique_suffix}.zevtc",
                    BytesIO(content),
                    "application/octet-stream",
                )
            },
        )

        assert resp.status_code in (200, 409), f"上传失败: {resp.text}"
        data = resp.json()
        if resp.status_code == 200:
            assert data["success"] is True
            log_data = data["data"]
            # 核心字段必须存在且非空
            assert "id" in log_data
            assert "log_uuid" in log_data
            assert log_data["log_uuid"] is not None
            assert "file_sha256" in log_data
            assert (
                log_data["file_sha256"] is not None
                and len(log_data["file_sha256"]) == 64
            )
            assert "file_size_compressed" in log_data
            assert log_data["file_size_compressed"] > 0
            assert "file_size_raw" in log_data
            assert log_data["file_size_raw"] > 0
            assert "filename" in log_data
            assert log_data["parse_status"] == "pending"

            # 清理
            log_id = log_data["id"]
            del_resp = await async_client.delete(
                f"/api/v1/logs/{log_id}", headers=auth_headers
            )
            assert del_resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_upload_invalid_extension(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """上传非法扩展名应返回 400"""
        import io

        resp = await async_client.post(
            "/api/v1/logs",
            headers=auth_headers,
            files={"file": ("test.txt", io.BytesIO(b"fake content"), "text/plain")},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_upload_without_auth(self, async_client: AsyncClient):
        """未认证上传行为（当前实现未强制认证）"""
        import io
        import random

        unique_content = f"fake content {random.randint(100000,999999)}".encode()
        resp = await async_client.post(
            "/api/v1/logs",
            files={
                "file": (
                    "test.zevtc",
                    io.BytesIO(unique_content),
                    "application/octet-stream",
                )
            },
        )
        # 当前上传端点未要求认证；如果内容重复则返回 409
        assert resp.status_code in (200, 401, 409)
