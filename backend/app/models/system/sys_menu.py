# 模块功能：系统菜单数据模型
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-11
# 依赖说明：SQLAlchemy

from sqlalchemy import (
    BIGINT,
    CHAR,
    DATETIME,
    INTEGER,
    VARCHAR,
    Column,
    ForeignKey,
    func,
)
from sqlalchemy.orm import foreign, relationship, remote

from app.config.database import Base


class SysMenu(Base):
    """
    系统菜单模型

    对应数据库表：sys_menu

    菜单类型说明?
    - M: 目录（Menu)
    - C: 菜单（Component)
    - F: 按钮（Function)
    """

    __tablename__ = "sys_menu"

    menu_id = Column(INTEGER, primary_key=True, autoincrement=True, comment="菜单ID")

    menu_name = Column(VARCHAR(50), nullable=False, comment="菜单名称")

    # 注意：已移除 ForeignKey 约束，因为虚拟 ROOT 节点（menu_id=0, parent_id=0）
    # 会形成自引用，在 MySQL 等严格外键检查的数据库中导致约束失败。
    # 应用层通过 menu_service 的校验确保 parent_id 有效性。
    parent_id = Column(
        INTEGER, default=0, comment="父菜单ID"
    )

    order_num = Column(INTEGER, default=0, comment="显示顺序")

    path = Column(VARCHAR(200), default="", comment="路由地址")

    component = Column(VARCHAR(255), nullable=True, comment="组件路径")

    query = Column(VARCHAR(255), nullable=True, comment="路由参数")

    route_name = Column(VARCHAR(50), default="", comment="路由名称")

    is_frame = Column(INTEGER, default=1, comment="是否为外链（0否 1是）")

    is_cache = Column(INTEGER, default=0, comment="是否缓存（0不缓存 1缓存）")

    menu_type = Column(CHAR(1), default="", comment="菜单类型（M目录, C菜单, F按钮）")

    visible = Column(CHAR(1), default="0", comment="菜单状态（0显示 1隐藏）")

    status = Column(CHAR(1), default="0", comment="菜单状态（0正常 1停用）")

    perms = Column(VARCHAR(100), nullable=True, comment="权限标识")

    icon = Column(VARCHAR(100), default="#", comment="菜单图标")

    create_by = Column(VARCHAR(64), default="", comment="创建人")

    create_time = Column(
        DATETIME, default=func.now(), server_default=func.now(), comment="创建时间"
    )

    update_by = Column(VARCHAR(64), default="", comment="更新人")

    update_time = Column(
        DATETIME,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    remark = Column(VARCHAR(500), default="", comment="备注")

    # 自引用关系（父菜单）
    # 显式指定 primaryjoin 并使用 foreign() 注解，因为已移除 ForeignKey 约束
    # 以避免 ROOT 节点（menu_id=0, parent_id=0）自引用导致的外键约束失败
    parent = relationship(
        "SysMenu",
        primaryjoin="foreign(SysMenu.parent_id) == remote(SysMenu.menu_id)",
        backref="children",
        uselist=False,
    )

    def to_dict(self):
        """将模型转换为字典

        安全说明：children 递归中过滤 menu_id=0 的虚拟 ROOT 节点，
        防止自引用导致的无限递归（ROOT 节点的 parent_id=0 引用自身）。
        同时 build_menu_tree() 和 filter_accessible_menus() 也在外层做了过滤保护。
        """
        return {
            "menu_id": self.menu_id,
            "menu_name": self.menu_name,
            "parent_id": self.parent_id,
            "order_num": self.order_num,
            "path": self.path,
            "component": self.component,
            "query": self.query,
            "route_name": self.route_name,
            "is_frame": self.is_frame,
            "is_cache": self.is_cache,
            "menu_type": self.menu_type,
            "visible": self.visible,
            "status": self.status,
            "perms": self.perms,
            "icon": self.icon,
            "create_by": self.create_by,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_by": self.update_by,
            "update_time": self.update_time.isoformat() if self.update_time else None,
            "remark": self.remark,
            # 防御性过滤：排除虚拟 ROOT 节点，防止无限递归
            "children": [child.to_dict() for child in (self.children or []) if child.menu_id != 0],
        }
