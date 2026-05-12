# 模块功能：系统用户数据模型
# 帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：SQLAlchemy

from app.config.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class SysUser(Base):
    # 功能：系统用户数据模型
    # 参数：无
    # 返回：无

    __tablename__ = "sys_user"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="自增主键"
    )
    username = Column(
        String(50), unique=True, index=True, nullable=False, comment="用户名"
    )
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(
        String(20),
        default="operator",
        nullable=False,
        comment="角色：super_admin/operator/user/guest",
    )
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_predefined = Column(Boolean, default=False, nullable=False, comment="是否预定义")
    email = Column(String(100), nullable=True, comment="邮箱")
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        comment="创建时间",
    )
    last_login = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    token_version = Column(
        Integer,
        default=0,
        nullable=False,
        comment="令牌版本（用于密码修改后使旧token失效?,默认0）",
    )
