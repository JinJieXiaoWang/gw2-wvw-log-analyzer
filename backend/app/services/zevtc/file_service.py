# -*- coding: utf-8 -*-
# 模块功能：文件上传存储服务
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12

import os
import uuid

from fastapi import UploadFile

from app.config.settings import settings


class FileService:
    @staticmethod
    def get_upload_dir() -> str:
        return settings.UPLOAD_DIR

    @staticmethod
    def ensure_upload_dir(upload_dir: str | None = None) -> str:
        dir_path = upload_dir or settings.UPLOAD_DIR
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    @staticmethod
    def exists(filepath: str) -> bool:
        return bool(filepath and os.path.exists(filepath))

    @staticmethod
    async def save_upload(
        file: UploadFile, upload_dir: str | None = None
    ) -> tuple[str, bytes]:
        dir_path = FileService.ensure_upload_dir(upload_dir)
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(dir_path, f"{file_id}{file_ext}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path, content

    @staticmethod
    def delete_file(filepath: str) -> bool:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError:
                return False
        return False
