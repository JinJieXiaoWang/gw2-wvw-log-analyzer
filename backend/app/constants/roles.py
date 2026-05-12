# -*- coding: utf-8 -*-
# 模块功能：系统角色常?# 作者：系统
# 创建日期?2026-05-12

ROLES = [
    {
        "id": 1,
        "name": "super_admin",
        "description": "超级管理?,
        "permissions": ["read", "write", "upload", "delete", "manage_users"],
    },
    {
        "id": 2,
        "name": "operator",
        "description": "操作?,
        "permissions": ["read", "write", "upload", "delete"],
    },
    {"id": 3, "name": "user", "description": "普通用?, "permissions": ["read"]},
    {"id": 4, "name": "guest", "description": "游客", "permissions": ["read"]},
]
