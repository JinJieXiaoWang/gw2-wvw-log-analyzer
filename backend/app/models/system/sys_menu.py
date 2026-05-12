# 模块功能：系统菜单数据模型
# 作者：帅妹妹丶.8297
# 创建日期?2026-05-11
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
from sqlalchemy.orm import relationship

from app.config.database import Base


class SysMenu(Base):
    """
    系统菜单模型

    对应数据库表：sys_menu

    菜单类型说明?
    - M: 目录（Menu?
    - C: 菜单（Component?
    - F: 按钮（Function?
    """

    __tablename__ = "sys_menu"

    menu_id = Column(INTEGER, primary_key=True, autoincrement=True, comment="菜单ID")

    menu_name = Column(VARCHAR(50), nullable=False, comment="菜单名称")

    parent_id = Column(
        INTEGER, ForeignKey("sys_menu.menu_id"), default=0, comment="父菜单ID"
    )

    order_num = Column(INTEGER, default=0, comment="显示顺序")

    path = Column(VARCHAR(200), default="", comment="路由地址")

    component = Column(VARCHAR(255), nullable=True, comment="组件路径")

    query = Column(VARCHAR(255), nullable=True, comment="路由参数")

    route_name = Column(VARCHAR(50), default="", comment="路由名称")

    is_frame = Column(INTEGER, default=1, comment="是否为外链（0?1否）")

    is_cache = Column(INTEGER, default=0, comment="是否缓存?缓存 1不缓存）")

    menu_type = Column(CHAR(1), default="", comment="菜单类型（M目录 C菜单 F按钮?)

    visible = Column(CHAR(1), default="0", comment="菜单状态（0显示 1隐藏?)

    status = Column(CHAR(1), default="0", comment="菜单状态（0正常 1停用?)

    perms = Column(VARCHAR(100), nullable=True, comment="权限标识")

    icon = Column(VARCHAR(100), default="#", comment="菜单图标")

    create_by = Column(VARCHAR(64), default="", comment="创建?)

    create_time = Column(
        DATETIME, default=func.now(), server_default=func.now(), comment="创建时间"
    )

    update_by = Column(VARCHAR(64), default="", comment="更新?)

    update_time = Column(
        DATETIME,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    remark = Column(VARCHAR(500), default="", comment="备注")

    # 自引用关系（父菜单）
    parent = relationship(
        "SysMenu", remote_side=[menu_id], backref="children", uselist=False
    )

    def to_dict(self):
        """将模型转换为字典"""
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
            "children": [child.to_dict() for child in (self.children or [])],
        }
