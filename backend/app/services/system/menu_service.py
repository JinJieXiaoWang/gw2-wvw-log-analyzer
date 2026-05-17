# 模块功能：菜单管理服务
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-11
# 依赖说明：SQLAlchemy, Pydantic, Cache

from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.constants.default_menus import DEFAULT_MENUS
from app.constants.dict_values import MenuStatus, MenuType, MenuVisible, MenuYesNo
from app.models.system.sys_menu import SysMenu
from app.utils.logger import logger
from app.utils.menu_tree_builder import build_menu_tree, filter_accessible_menus


class MenuService:
    """菜单管理服务（无缓存，直接查询SQLite）"""

    def __init__(self, db: Session):
        self.db = db

    def create_menu(self, menu_create: dict, create_by: str = "") -> SysMenu:
        """创建菜单（含名称重复、父菜单存在性校验）"""
        menu_name = menu_create.get("menu_name")
        parent_id = menu_create.get("parent_id", 0)

        existing = self.db.query(SysMenu).filter(
            SysMenu.menu_name == menu_name,
            SysMenu.parent_id == parent_id
        ).first()
        if existing:
            raise ValueError(f"菜单名称 '{menu_name}' 已存在")

        if parent_id != 0 and not self.get_menu_by_id(parent_id):
            raise ValueError(f"父菜单ID {parent_id} 不存在")

        menu = SysMenu(
            menu_name=menu_name,
            parent_id=parent_id,
            order_num=menu_create.get("order_num", 0),
            path=menu_create.get("path", ""),
            component=menu_create.get("component"),
            query=menu_create.get("query", ""),
            route_name=menu_create.get("route_name", ""),
            is_frame=menu_create.get("is_frame", MenuYesNo.YES),
            is_cache=menu_create.get("is_cache", MenuYesNo.NO),
            menu_type=menu_create.get("menu_type", MenuType.MENU),
            visible=menu_create.get("visible", MenuVisible.SHOW),
            status=menu_create.get("status", MenuStatus.NORMAL),
            perms=menu_create.get("perms"),
            icon=menu_create.get("icon", "#"),
            create_by=create_by,
            remark=menu_create.get("remark", "")
        )
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        logger.info(f"创建菜单成功: {menu.menu_id} - {menu.menu_name}")
        return menu

    def get_menu_by_id(self, menu_id: int) -> Optional[SysMenu]:
        """根据ID获取菜单"""
        return self.db.query(SysMenu).filter(SysMenu.menu_id == menu_id).first()

    def get_menu_by_name(self, menu_name: str) -> Optional[SysMenu]:
        """根据名称获取菜单"""
        return self.db.query(SysMenu).filter(SysMenu.menu_name == menu_name).first()

    def update_menu(self, menu_id: int, menu_update: dict, update_by: str = "") -> Optional[SysMenu]:
        """更新菜单（含名称重复、父菜单存在性校验）"""
        menu = self.get_menu_by_id(menu_id)
        if not menu:
            return None

        new_name = menu_update.get("menu_name")
        if new_name and new_name != menu.menu_name:
            existing = self.db.query(SysMenu).filter(
                SysMenu.menu_name == new_name,
                SysMenu.parent_id == menu.parent_id,
                SysMenu.menu_id != menu_id
            ).first()
            if existing:
                raise ValueError(f"菜单名称 '{new_name}' 已存在")

        new_parent_id = menu_update.get("parent_id")
        if new_parent_id is not None and new_parent_id != menu.parent_id:
            if new_parent_id != 0 and not self.get_menu_by_id(new_parent_id):
                raise ValueError(f"父菜单ID {new_parent_id} 不存在")

        fields = [
            "menu_name", "parent_id", "order_num", "path", "component",
            "query", "route_name", "is_frame", "is_cache", "menu_type",
            "visible", "status", "perms", "icon", "remark",
        ]
        for field in fields:
            if field in menu_update:
                setattr(menu, field, menu_update[field])
        if update_by:
            menu.update_by = update_by

        self.db.commit()
        self.db.refresh(menu)
        logger.info(f"更新菜单成功: {menu_id} - {menu.menu_name}")
        return menu

    def delete_menu(self, menu_id: int) -> bool:
        """删除菜单（级联删除子菜单）"""
        menu = self.get_menu_by_id(menu_id)
        if not menu:
            return False

        for child in self.db.query(SysMenu).filter(SysMenu.parent_id == menu_id).all():
            self.delete_menu(child.menu_id)

        self.db.delete(menu)
        self.db.commit()
        logger.info(f"删除菜单成功: {menu_id} - {menu.menu_name}")
        return True

    def list_menus(
        self,
        menu_name: Optional[str] = None,
        menu_type: Optional[str] = None,
        status: Optional[str] = None,
        visible: Optional[str] = None,
        parent_id: Optional[int] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[int, List[SysMenu]]:
        """分页查询菜单列表"""
        query = self.db.query(SysMenu)
        if menu_name:
            query = query.filter(SysMenu.menu_name.like(f"%{menu_name}%"))
        if menu_type:
            query = query.filter(SysMenu.menu_type == menu_type)
        if status is not None:
            query = query.filter(SysMenu.status == status)
        if visible is not None:
            query = query.filter(SysMenu.visible == visible)
        if parent_id is not None:
            query = query.filter(SysMenu.parent_id == parent_id)
        query = query.order_by(SysMenu.parent_id, SysMenu.order_num)
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return total, items

    def get_all_menus(self) -> List[SysMenu]:
        """获取所有菜单（按父ID和排序号排序，直接查库）"""
        return self.db.query(SysMenu).order_by(SysMenu.parent_id, SysMenu.order_num).all()

    def get_menu_tree(self, parent_id: int = 0) -> List[Dict]:
        """获取菜单树形结构"""
        return build_menu_tree(self.get_all_menus(), parent_id)

    def get_user_menus(self, user_role: str, user_permissions: List[str]) -> List[Dict]:
        """获取用户有权限访问的菜单"""
        accessible = filter_accessible_menus(self.get_all_menus(), user_role, user_permissions)
        return build_menu_tree(accessible, 0)

    def get_public_menus(self) -> List[Dict]:
        """获取游客可访问的公开菜单"""
        public = filter_accessible_menus(self.get_all_menus(), None, None, public_only=True)
        logger.debug("获取公开菜单成功")
        return build_menu_tree(public, 0)

    def check_menu_permission(self, menu_id: int, user_permissions: List[str]) -> bool:
        """检查用户是否有权限访问指定菜单"""
        menu = self.get_menu_by_id(menu_id)
        if not menu:
            return False
        if "manage_users" in user_permissions:
            return True
        if menu.status == MenuStatus.DISABLED or menu.visible == MenuVisible.HIDDEN:
            return False
        if not menu.perms:
            return True
        required_perms = menu.perms.split(",")
        return any(perm in user_permissions for perm in required_perms)

    def get_all_permissions(self) -> List[str]:
        """获取所有权限标识"""
        permissions = set()
        for menu in self.get_all_menus():
            if menu.perms:
                for perm in menu.perms.split(","):
                    permissions.add(perm.strip())
        return sorted(list(permissions))

    def sync_permissions(self, role: str) -> List[str]:
        """同步用户角色的权限列表（从菜单表获取）"""
        if role == "super_admin":
            return self.get_all_permissions()
        permissions = set()
        for menu in self.get_all_menus():
            if menu.perms and menu.status == MenuStatus.NORMAL and menu.visible == MenuVisible.SHOW:
                permissions.update(menu.perms.split(","))
        return sorted(list(permissions))

    def batch_update_menus(self, menus_data: List[dict], update_by: str = "") -> int:
        """批量更新菜单"""
        updated_count = 0
        for menu_data in menus_data:
            if "menu_id" not in menu_data:
                continue
            menu = self.get_menu_by_id(menu_data["menu_id"])
            if not menu:
                continue
            for field in ["menu_name", "parent_id", "order_num", "visible", "status"]:
                if field in menu_data:
                    setattr(menu, field, menu_data[field])
            if update_by:
                menu.update_by = update_by
            updated_count += 1
        if updated_count > 0:
            self.db.commit()
            logger.info(f"批量更新菜单成功: {updated_count} 条")
        return updated_count

    def _upsert_menu_def(self, menu_def: dict, parent_id: int, init_by: str) -> Tuple[int, bool]:
        """创建或复用菜单定义，返回 (menu_id, 是否新建)"""
        existing = self.db.query(SysMenu).filter(
            SysMenu.menu_name == menu_def["menu_name"],
            SysMenu.parent_id == parent_id
        ).first()
        if existing:
            return existing.menu_id, False
        menu = SysMenu(
            menu_name=menu_def["menu_name"],
            parent_id=parent_id,
            order_num=menu_def["order_num"],
            path=menu_def["path"],
            component=menu_def["component"],
            route_name=menu_def.get("route_name", ""),
            is_frame=menu_def.get("is_frame", MenuYesNo.YES),
            is_cache=menu_def.get("is_cache", MenuYesNo.NO),
            menu_type=menu_def["menu_type"],
            visible=menu_def["visible"],
            status=menu_def["status"],
            perms=menu_def.get("perms"),
            icon=menu_def.get("icon", "#"),
            create_by=init_by,
            remark=menu_def.get("remark", "")
        )
        self.db.add(menu)
        self.db.flush()
        return menu.menu_id, True

    def init_default_menus(self, init_by: str = "system") -> int:
        """初始化默认菜单数据"""
        key_to_id = {}
        created_count = 0

        for menu_def in DEFAULT_MENUS:
            if menu_def["parent_key"] is not None:
                continue
            menu_id, created = self._upsert_menu_def(menu_def, 0, init_by)
            key_to_id[menu_def["key"]] = menu_id
            if created:
                created_count += 1

        for menu_def in DEFAULT_MENUS:
            if menu_def["parent_key"] is None:
                continue
            parent_id = key_to_id.get(menu_def["parent_key"])
            if not parent_id:
                logger.warning(f"父菜?{menu_def['parent_key']} 不存在，跳过创建 {menu_def['menu_name']}")
                continue
            menu_id, created = self._upsert_menu_def(menu_def, parent_id, init_by)
            key_to_id[menu_def["key"]] = menu_id
            if created:
                created_count += 1

        self.db.commit()
        logger.info(f"初始化默认菜单完成，共创建 {created_count} 条菜单")
        return created_count
