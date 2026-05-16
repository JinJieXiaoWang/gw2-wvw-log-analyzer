# 模块功能：菜单树构建与权限过滤工具
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-12

from typing import Dict, List, Optional


def build_menu_tree(menus: List, parent_id: int = 0) -> List[Dict]:
    """
    将扁平菜单列表构建为树形结构

    参数据        menus - 菜单对象列表（需支持 menu_id, parent_id, to_dict() 方法）
        parent_id - 父菜单ID，默认为0

    返回?        树形结构菜单列表，已按 order_num 排序
    """
    # 过滤掉虚拟 ROOT 节点，防止其出现在菜单树中
    menus = [m for m in menus if m.menu_id != 0]
    menu_dict = {menu.menu_id: menu.to_dict() for menu in menus}
    tree = []

    for menu in menus:
        menu_dict[menu.menu_id]["children"] = []

    for menu in menus:
        if menu.parent_id == parent_id:
            tree.append(menu_dict[menu.menu_id])
        elif menu.parent_id in menu_dict:
            menu_dict[menu.parent_id]["children"].append(menu_dict[menu.menu_id])

    def _sort_children(node):
        if "children" in node and node["children"]:
            node["children"].sort(key=lambda x: x["order_num"])
            for child in node["children"]:
                _sort_children(child)

    for node in tree:
        _sort_children(node)

    return tree


def filter_accessible_menus(
    all_menus: List,
    user_role: Optional[str],
    user_permissions: Optional[List[str]],
    public_only: bool = False,
) -> List:
    """
    根据用户角色和权限过滤可访问的菜单
    参数据        all_menus - 所有菜单列表
        user_role - 用户角色
        user_permissions - 用户权限列表
        public_only - 是否只筛选公开菜单（无权限限制且可见）

    返回?        过滤后的菜单列表
    """
    accessible = []

    for menu in all_menus:
        # 跳过虚拟 ROOT 节点（menu_id=0），该节点仅用于解决外键约束，不应返回给前端
        if menu.menu_id == 0:
            continue
        # 只显示状态正常的菜单
        if menu.status != "0":
            continue

        if public_only:
            # 公开菜单：可见且无权限限制
            if menu.visible != "0" or menu.perms:
                continue
            accessible.append(menu)
            continue

        # 超级管理员拥有所有权限
        if user_role == "super_admin":
            accessible.append(menu)
            continue

        # 检查权限
        if menu.perms:
            required_perms = menu.perms.split(",")
            has_permission = any(perm in user_permissions for perm in required_perms)
            if has_permission:
                accessible.append(menu)
        else:
            # 无权限标识的菜单默认所有人可访问
            accessible.append(menu)

    return accessible
