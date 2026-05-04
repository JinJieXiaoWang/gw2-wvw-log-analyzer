# 模块功能：管理员认证服务模块
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-28
# 依赖说明：SQLAlchemy, bcrypt, jwt

from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.sys_user import SysUser
from app.utils.logger import logger

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2


login_attempts: Dict[str, dict] = {}
LOCKOUT_DURATION = timedelta(minutes=15)
MAX_ATTEMPTS = 5
ATTEMPT_WINDOW = timedelta(minutes=5)


def get_password_hash(password: str) -> str:
    # 功能：对密码进行哈希加密
    # 参数：password - 要加密的密码
    # 返回：加密后的密码字符串
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 功能：验证密码是否匹配哈希值
    # 参数：plain_password - 要验证的明文密码
    # hashed_password - 存储的哈希密码
    # 返回：如果密码匹配则返回True，否则返回False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"验证密码失败: {e}")
        return False


def get_admin_by_username(db: Session, username: str) -> Optional[SysUser]:
    # 功能：根据用户名获取管理员
    # 参数：db - 数据库会话；username - 要获取的管理员用户名
    # 返回：SysUser对象或None
    return db.query(SysUser).filter(SysUser.username == username).first()


def get_admin_by_id(db: Session, admin_id: int) -> Optional[SysUser]:
    # 功能：根据管理员ID获取管理员
    # 参数：db - 数据库会话；admin_id - 要获取的管理员ID
    # 返回：SysUser对象或None
    return db.query(SysUser).filter(SysUser.id == admin_id).first()


def check_login_attempts(username: str, client_ip: str) -> Optional[str]:
    # 功能：检查登录尝试次数限制
    # 参数：username - 用户名；client_ip - 客户端IP
    # 返回：None表示可尝试登录，否则返回错误消息
    now = datetime.now(UTC)
    key = f"{username}:{client_ip}"

    if key in login_attempts:
        attempt_data = login_attempts[key]

        if attempt_data["locked_until"] and now < attempt_data["locked_until"]:
            remaining = int((attempt_data["locked_until"] - now).total_seconds() // 60)
            return f"账户已锁定，请{remaining}分钟后重试"

        if attempt_data["attempts"] >= MAX_ATTEMPTS:
            login_attempts[key]["locked_until"] = now + LOCKOUT_DURATION
            login_attempts[key]["attempts"] = 0
            return f"登录失败次数过多，账户已锁定15分钟"

        time_since_first = now - attempt_data["first_attempt"]
        if time_since_first > ATTEMPT_WINDOW:
            login_attempts[key] = {
                "attempts": 1,
                "first_attempt": now,
                "locked_until": None,
            }
        else:
            login_attempts[key]["attempts"] += 1
    else:
        login_attempts[key] = {
            "attempts": 1,
            "first_attempt": now,
            "locked_until": None,
        }

    return None


def reset_login_attempts(username: str, client_ip: str):
    # 功能：重置登录尝试次数
    # 参数：username - 用户名；client_ip - 客户端IP
    key = f"{username}:{client_ip}"
    if key in login_attempts:
        del login_attempts[key]


def authenticate_admin(
    db: Session, username: str, password: str, client_ip: str = "127.0.0.1"
) -> Optional[SysUser]:
    # 功能：认证管理员
    # 参数：db - 数据库会话；username - 要认证的管理员用户名；password - 要认证的管理员密码；client_ip - 客户端IP
    # 返回：认证成功的SysUser对象或None
    admin = get_admin_by_username(db, username)

    if admin and not admin.is_active:
        logger.warning(f"登录失败：账号已禁用 - {username}")
        return None

    lockout_msg = check_login_attempts(username, client_ip)
    if lockout_msg:
        logger.warning(f"登录失败：{lockout_msg} - {username}")
        return {"locked": lockout_msg}

    if not admin:
        logger.warning(f"登录失败：用户名不存在 - {username}")
        return None

    if not verify_password(password, admin.password_hash):
        logger.warning(f"登录失败：密码错误 - {username}")
        return None

    reset_login_attempts(username, client_ip)
    admin.last_login = datetime.now(UTC)
    db.commit()
    logger.info(f"管理员登录成功: {username}")
    return admin


def create_admin(db: Session, username: str, password: str) -> SysUser:
    # 功能：创建新的管理员
    # 参数：db - 数据库会话；username - 要创建的管理员用户名；password - 要创建的管理员密码
    # 返回：创建的SysUser对象
    admin = SysUser(
        username=username, password_hash=get_password_hash(password), is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"管理员创建成功: {username}")
    return admin


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # 功能：创建JWT访问令牌
    # 参数：data - 要加密到token中的数据；expires_delta - 过期时间间隔
    # 返回：JWT令牌字符串
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    # 功能：解码JWT访问令牌
    # 参数：token - JWT令牌字符串
    # 返回：解码后的payload字典或None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token已过期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("JWT token无效")
        return None


def change_admin_password(
    db: Session, admin_id: int, current_password: str, new_password: str
) -> bool:
    # 功能：修改管理员密码
    # 参数：db - 数据库会话；admin_id - 管理员ID；current_password - 当前密码；new_password - 新密码
    # 返回：修改成功返回True，否则返回False
    admin = get_admin_by_id(db, admin_id)
    if not admin:
        return False
    if not verify_password(current_password, admin.password_hash):
        return False
    admin.password_hash = get_password_hash(new_password)
    admin.token_version = (admin.token_version or 0) + 1
    db.commit()
    logger.info(f"管理员密码修改成功: {admin.username}")
    return True


def get_user_permissions(role: str = "operator") -> List[str]:
    # 功能：获取用户权限列表
    # 参数：role - 用户角色
    # 返回：权限列表
    if role == "super_admin":
        return ["read", "write", "upload", "delete", "manage_users"]
    if role == "operator" or role == "admin":
        return ["read", "write", "upload", "delete"]
    return ["read"]


def init_predefined_admin(db: Session) -> SysUser:
    # 功能：初始化预置管理员账号
    # 参数：db - 数据库会话
    # 返回：预置管理员SysUser对象

    PREDEFINED_USERNAME = "admin"
    # 从 Settings 读取预置管理员密码，若未设置则生成随机强密码
    import secrets

    from app.config.settings import settings

    PREDEFINED_PASSWORD = settings.ADMIN_INITIAL_PASSWORD
    password_source = "配置"
    if not PREDEFINED_PASSWORD:
        PREDEFINED_PASSWORD = secrets.token_urlsafe(16)
        password_source = "随机生成"
        # 使用醒目的日志格式输出随机密码，确保管理员能够发现
        logger.warning("=" * 60)
        logger.warning("【安全提示】ADMIN_INITIAL_PASSWORD 未在 .env 中配置")
        logger.warning("系统已自动生成随机强密码，请妥善保存：")
        logger.warning(f"  用户名 : {PREDEFINED_USERNAME}")
        logger.warning(f"  密码   : {PREDEFINED_PASSWORD}")
        logger.warning("=" * 60)
    else:
        logger.info(f"使用 .env 中配置的 ADMIN_INITIAL_PASSWORD 初始化管理员账号")

    existing_admin = get_admin_by_username(db, PREDEFINED_USERNAME)
    if existing_admin:
        # 如果账号之前不是预置的，标记为预置并赋予超级管理员权限
        updated = False
        if not existing_admin.is_predefined:
            existing_admin.is_predefined = True
            existing_admin.role = "super_admin"
            updated = True

        # 关键修复：当 ADMIN_PASSWORD_SYNC=true 且密码来源为配置（非随机生成）时，
        # 若现有密码与配置密码不匹配，则同步更新密码。
        # 这解决了 Docker 重新部署后密码不一致导致的登录失败问题。
        if settings.ADMIN_PASSWORD_SYNC and password_source == "配置":
            if not verify_password(PREDEFINED_PASSWORD, existing_admin.password_hash):
                existing_admin.password_hash = get_password_hash(PREDEFINED_PASSWORD)
                existing_admin.token_version = (existing_admin.token_version or 0) + 1
                updated = True
                logger.warning("=" * 60)
                logger.warning("【密码同步】ADMIN_PASSWORD_SYNC 已启用")
                logger.warning(f"预置管理员 {PREDEFINED_USERNAME} 的密码已更新为配置值")
                logger.warning("所有现有登录令牌已失效，请使用新密码重新登录")
                logger.warning("=" * 60)

        if updated:
            db.commit()
            db.refresh(existing_admin)
        return existing_admin

    admin = SysUser(
        username=PREDEFINED_USERNAME,
        password_hash=get_password_hash(PREDEFINED_PASSWORD),
        role="super_admin",
        is_active=True,
        is_predefined=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"预置管理员账号已创建: {admin.username}")
    return admin


def delete_admin(db: Session, admin_id: int) -> bool:
    # 功能：删除管理员账号（预置管理员禁止删除）
    # 参数：db - 数据库会话；admin_id - 要删除的管理员ID
    # 返回：删除成功返回True，否则返回False

    admin = get_admin_by_id(db, admin_id)
    if not admin:
        return False

    if admin.is_predefined:
        logger.warning(f"尝试删除预置管理员账号被拒绝: {admin.username}")
        return False

    db.delete(admin)
    db.commit()
    logger.info(f"管理员账号已删除: {admin.username}")
    return True


def get_admins(db: Session, skip: int = 0, limit: int = 100) -> List[SysUser]:
    # 功能：获取管理员列表
    # 参数：db - 数据库会话；skip - 跳过数量；limit - 限制数量
    # 返回：管理员列表
    return db.query(SysUser).offset(skip).limit(limit).all()


# =============================================================================
# 依赖注入（提取到 service 层供所有路由共享）
# =============================================================================

from fastapi import Depends, Header

from app.config.database import get_db
from app.utils.exceptions import ForbiddenException, UnauthorizedException


async def get_current_admin(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> SysUser:
    """获取当前登录的管理员（用于依赖注入）"""
    if not authorization:
        raise UnauthorizedException(detail="未提供认证令牌")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(detail="无效的认证令牌格式")

    token = authorization[7:]
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise UnauthorizedException(detail="无效的认证令牌")

    admin_id = int(payload.get("sub"))
    admin = get_admin_by_id(db, admin_id)

    if not admin or not admin.is_active:
        raise UnauthorizedException(detail="用户不存在或已禁用")

    # 验证 token_version，防止密码修改后旧token仍然有效
    token_version = payload.get("tv")
    if token_version is not None and token_version != (admin.token_version or 0):
        raise UnauthorizedException(detail="认证令牌已失效，请重新登录")

    return admin


def require_super_admin(admin: SysUser = Depends(get_current_admin)) -> SysUser:
    """要求超级管理员权限"""
    if admin.role != "super_admin":
        raise ForbiddenException(detail="需要超级管理员权限")
    return admin


def require_permission(permission: str):
    """要求指定权限的依赖工厂"""
    def checker(admin: SysUser = Depends(get_current_admin)) -> SysUser:
        permissions = get_user_permissions(admin.role)
        if permission not in permissions:
            raise ForbiddenException(detail=f"需要{permission}权限")
        return admin
    return checker
