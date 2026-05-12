# -*- coding: utf-8 -*-
# 模块功能：系统角色常量
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12

ROLES = [
    {
        "id": 1,
        "name": "super_admin",
        "description": "超级管理员",
        "permissions": ["read", "write", "upload", "delete", "manage_users"],
    },
    {
        "id": 2,
        "name": "operator",
        "description": "操作员",
        "permissions": ["read", "write", "upload", "delete"],
    },
    {"id": 3, "name": "user", "description": "普通用户", "permissions": ["read"]},
    {"id": 4, "name": "guest", "description": "游客", "permissions": ["read"]},
]
