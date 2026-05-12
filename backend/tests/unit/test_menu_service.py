#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：测试菜单管理服?
# 作者：系统
# 创建日期?2026-05-11
# 依赖说明：pytest, SQLAlchemy

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.system.sys_menu import SysMenu
from app.services.system.menu_service import MenuService


@pytest.fixture
def db_session():
    """提供内存 SQLite 数据库会话，每个测试独立"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def menu_service(db_session):
    """提供菜单服务实例"""
    return MenuService(db_session)


def test_create_menu(menu_service):
    """测试创建菜单"""
    # 创建顶级菜单（使用字典格式）
    menu_data = {
        "menu_name": "测试菜单",
        "parent_id": 0,
        "order_num": 1,
        "path": "/test",
        "component": "test/index",
        "route_name": "test",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "home",
        "perms": "read",
        "remark": "测试菜单",
    }

    menu = menu_service.create_menu(menu_data, create_by="test")
    assert menu.menu_id is not None
    assert menu.menu_name == "测试菜单"
    assert menu.parent_id == 0
    assert menu.perms == "read"


def test_create_menu_with_parent(menu_service):
    """测试创建带父菜单的菜单项"""
    # 创建父菜单（使用字典格式?
    parent_data = {
        "menu_name": "父菜?,
        "parent_id": 0,
        "order_num": 1,
        "path": "",
        "menu_type": "M",
        "visible": "0",
        "status": "0",
        "icon": "folder",
    }
    parent = menu_service.create_menu(parent_data, create_by="test")

    # 创建子菜单（使用字典格式?
    child_data = {
        "menu_name": "子菜?,
        "parent_id": parent.menu_id,
        "order_num": 1,
        "path": "/child",
        "component": "child/index",
        "route_name": "child",
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "icon": "file",
        "perms": "read",
    }
    child = menu_service.create_menu(child_data, create_by="test")

    assert child.parent_id == parent.menu_id


def test_get_menu_by_id(menu_service):
    """测试通过ID获取菜单"""
    # 创建菜单（使用字典格式）
    menu_data = {
        "menu_name": "获取菜单",
        "parent_id": 0,
        "order_num": 1,
        "menu_type": "C",
        "visible": "0",
        "status": "0",
    }
    created = menu_service.create_menu(menu_data, create_by="test")

    # 获取菜单
    found = menu_service.get_menu_by_id(created.menu_id)
    assert found is not None
    assert found.menu_name == "获取菜单"

    # 获取不存在的菜单
    not_found = menu_service.get_menu_by_id(9999)
    assert not_found is None


def test_update_menu(menu_service):
    """测试更新菜单"""
    # 创建菜单（使用字典格式）
    menu_data = {
        "menu_name": "旧名?,
        "parent_id": 0,
        "order_num": 1,
        "menu_type": "C",
        "visible": "0",
        "status": "0",
    }
    created = menu_service.create_menu(menu_data, create_by="test")

    # 更新菜单（使用字典格式）
    update_data = {"menu_name": "新名?, "order_num": 2}
    updated = menu_service.update_menu(
        created.menu_id, update_data, update_by="test"
    )

    assert updated.menu_name == "新名?
    assert updated.order_num == 2


def test_delete_menu(menu_service):
    """测试删除菜单"""
    # 创建菜单（使用字典格式）
    menu_data = {
        "menu_name": "要删除的菜单",
        "parent_id": 0,
        "order_num": 1,
        "menu_type": "C",
        "visible": "0",
        "status": "0",
    }
    created = menu_service.create_menu(menu_data, create_by="test")

    # 删除菜单
    success = menu_service.delete_menu(created.menu_id)
    assert success is True

    # 验证菜单已删?
    found = menu_service.get_menu_by_id(created.menu_id)
    assert found is None


def test_delete_menu_with_children(menu_service):
    """测试删除包含子菜单的菜单（级联删除）"""
    # 创建父菜单（使用字典格式?
    parent_data = {
        "menu_name": "父菜?,
        "parent_id": 0,
        "order_num": 1,
        "menu_type": "M",
        "visible": "0",
        "status": "0",
    }
    parent = menu_service.create_menu(parent_data, create_by="test")

    # 创建子菜单（使用字典格式?
    child_data = {
        "menu_name": "子菜?,
        "parent_id": parent.menu_id,
        "order_num": 1,
        "menu_type": "C",
        "visible": "0",
        "status": "0",
    }
    menu_service.create_menu(child_data, create_by="test")

    # 删除父菜单（应级联删除子菜单?
    success = menu_service.delete_menu(parent.menu_id)
    assert success is True

    # 验证子菜单也被删?
    children = menu_service.db.query(SysMenu).filter(
        SysMenu.parent_id == parent.menu_id
    ).all()
    assert len(children) == 0


def test_get_menu_tree(menu_service):
    """测试获取菜单树形结构"""
    # 创建多级菜单（使用字典格式）
    for i in range(3):
        parent_data = {
            "menu_name": f"父菜单{i}",
            "parent_id": 0,
            "order_num": i,
            "menu_type": "M",
            "visible": "0",
            "status": "0",
        }
        parent = menu_service.create_menu(parent_data, create_by="test")

        for j in range(2):
            child_data = {
                "menu_name": f"子菜单{i}-{j}",
                "parent_id": parent.menu_id,
                "order_num": j,
                "menu_type": "C",
                "visible": "0",
                "status": "0",
            }
            menu_service.create_menu(child_data, create_by="test")

    # 获取树形结构
    tree = menu_service.get_menu_tree()
    assert isinstance(tree, list)
    assert len(tree) == 3

    # 验证树形结构
    for parent_node in tree:
        assert "children" in parent_node
        assert len(parent_node["children"]) == 2


def test_get_user_menus(menu_service):
    """测试获取用户权限菜单"""
    # 创建带权限的菜单（使用字典格式）
    menu_data = {
        "menu_name": "权限测试菜单",
        "parent_id": 0,
        "order_num": 1,
        "menu_type": "C",
        "visible": "0",
        "status": "0",
        "perms": "admin:read",
    }
    menu_service.create_menu(menu_data, create_by="test")

    # 测试有权限的情况
    user_menus = menu_service.get_user_menus("admin", ["admin:read"])
    assert isinstance(user_menus, list)
    assert len(user_menus) > 0

    # 测试无权限的情况
    user_menus_no_perm = menu_service.get_user_menus("user", ["user:read"])
    # 用户菜单应只包含无权限限制的菜单?


def test_list_menus(menu_service):
    """测试分页查询菜单列表"""
    # 创建多个菜单（使用字典格式）
    for i in range(5):
        menu_data = {
            "menu_name": f"列表测试菜单{i}",
            "parent_id": 0,
            "order_num": i,
            "menu_type": "C",
            "visible": "0",
            "status": "0",
        }
        menu_service.create_menu(menu_data, create_by="test")

    # 分页查询（返回的是元组：(total, items)?
    total, items = menu_service.list_menus(page=1, size=3)
    assert total == 5
    assert len(items) == 3

    # 第二?
    total2, items2 = menu_service.list_menus(page=2, size=3)
    assert len(items2) == 2