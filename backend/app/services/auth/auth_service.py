# 模块功能：管理员认证服务模块
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-28
# 依赖说明：SQLAlchemy, bcrypt, jwt

from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.auth.sys_user import SysUser
from app.utils.logger import logger

from app.constants.auth import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    ATTEMPT_WINDOW,
    JWT_ALGORITHM,
    LOCKOUT_DURATION,
    MAX_LOGIN_ATTEMPTS,
)

SECRET_KEY = settings.SECRET_KEY

login_attempts: Dict[str, dict] = {}


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"验证密码失败: {e}")
        return False


def get_admin_by_username(db: Session, username: str) -> Optional[SysUser]:
    return db.query(SysUser).filter(SysUser.username == username).first()


def get_admin_by_id(db: Session, admin_id: int) -> Optional[SysUser]:
    return db.query(SysUser).filter(SysUser.id == admin_id).first()


def check_login_attempts(username: str, client_ip: str) -> Optional[str]:
    now = datetime.now(UTC)
    key = f"{username}:{client_ip}"
    if key in login_attempts:
        attempt_data = login_attempts[key]
        if attempt_data["locked_until"] and now < attempt_data["locked_until"]:
            remaining = int((attempt_data["locked_until"] - now).total_seconds() // 60)
            return f"账户已锁定，请{remaining}分钟后重试"
        if attempt_data["attempts"] >= MAX_LOGIN_ATTEMPTS:
            login_attempts[key]["locked_until"] = now + LOCKOUT_DURATION
            login_attempts[key]["attempts"] = 0
            return "登录失败次数过多，账户已锁定15分钟"
        time_since_first = now - attempt_data["first_attempt"]
        if time_since_first > ATTEMPT_WINDOW:
            login_attempts[key] = {"attempts": 1, "first_attempt": now, "locked_until": None}
        else:
            login_attempts[key]["attempts"] += 1
    else:
        login_attempts[key] = {"attempts": 1, "first_attempt": now, "locked_until": None}
    return None


def reset_login_attempts(username: str, client_ip: str):
    key = f"{username}:{client_ip}"
    if key in login_attempts:
        del login_attempts[key]


def reset_all_login_attempts():
    login_attempts.clear()


def authenticate_admin(db: Session, username: str, password: str, client_ip: str = "127.0.0.1"):
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
    admin = SysUser(username=username, password_hash=get_password_hash(password), is_active=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"管理员创建成功: {username}")
    return admin


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire, "aud": "gw2-log-analyzer", "iss": "gw2-log-analyzer-backend"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            audience="gw2-log-analyzer",
            issuer="gw2-log-analyzer-backend",
            options={"require": ["exp", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token已过期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("JWT token无效")
        return None


def change_admin_password(db: Session, admin_id: int, current_password: str, new_password: str) -> bool:
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
    if role == "super_admin":
        return ["read", "write", "upload", "delete", "manage_users"]
    if role == "operator" or role == "admin":
        return ["read", "write", "upload", "delete"]
    return ["read"]


def init_predefined_admin(db: Session) -> SysUser:
    PREDEFINED_USERNAME = "admin"
    import secrets
    from app.config.settings import settings
    PREDEFINED_PASSWORD = settings.ADMIN_INITIAL_PASSWORD
    password_source = "配置"
    if not PREDEFINED_PASSWORD:
        PREDEFINED_PASSWORD = secrets.token_urlsafe(16)
        password_source = "随机生成"
        logger.warning("=" * 60)
        logger.warning("【安全提示】ADMIN_INITIAL_PASSWORD 未在 .env 中配置")
        logger.warning("系统已自动生成随机强密码，请妥善保存")
        logger.warning(f"  用户名: {PREDEFINED_USERNAME}")
        logger.warning(f"  密码   : {PREDEFINED_PASSWORD}")
        logger.warning("=" * 60)
    else:
        logger.info(f"使用 .env 中配置的 ADMIN_INITIAL_PASSWORD 初始化管理员账号")
    existing_admin = get_admin_by_username(db, PREDEFINED_USERNAME)
    if existing_admin:
        updated = False
        if not existing_admin.is_predefined:
            existing_admin.is_predefined = True
            existing_admin.role = "super_admin"
            updated = True
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
    logger.info(f"预置管理员账号已创建: {admin.username}")
    return admin


def delete_admin(db: Session, admin_id: int) -> bool:
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
    return db.query(SysUser).offset(skip).limit(limit).all()


from fastapi import Depends, Header
from app.config.database import get_db
from app.utils.error.exceptions import BadRequestException, ForbiddenException, UnauthorizedException


async def get_current_admin(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> SysUser:
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
    token_version = payload.get("tv")
    if token_version is not None and token_version != (admin.token_version or 0):
        raise UnauthorizedException(detail="认证令牌已失效，请重新登录")
    return admin


async def get_current_user_optional(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> Optional[SysUser]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        admin_id = int(payload.get("sub"))
        admin = get_admin_by_id(db, admin_id)
        if not admin or not admin.is_active:
            return None
        token_version = payload.get("tv")
        if token_version is not None and token_version != (admin.token_version or 0):
            return None
        return admin
    except Exception:
        return None


def require_super_admin(admin: SysUser = Depends(get_current_admin)) -> SysUser:
    if admin.role != "super_admin":
        raise ForbiddenException(detail="需要超级管理员权限")
    return admin


def change_admin_password_with_validation(
    db: Session,
    admin: SysUser,
    current_password: str,
    new_password: str,
    confirm_password: Optional[str] = None,
) -> None:
    """修改管理员密码（包含完整校验逻辑）

    Args:
        db: 数据库会话
        admin: 当前管理员对象
        current_password: 当前密码
        new_password: 新密码
        confirm_password: 确认密码（可选）

    Raises:
        BadRequestException: 校验失败时抛出
    """
    if not current_password:
        raise BadRequestException(detail="请提供当前密码")
    if confirm_password is not None and new_password != confirm_password:
        raise BadRequestException(detail="两次输入的密码不一致")
    if len(new_password) < 6:
        raise BadRequestException(detail="新密码长度至少6位")
    if not verify_password(current_password, admin.password_hash):
        raise BadRequestException(detail="当前密码错误")
    admin.password_hash = get_password_hash(new_password)
    admin.token_version = (admin.token_version or 0) + 1
    db.commit()
    logger.info(f"用户 {admin.username} 修改了密码")


def require_permission(permission: str):
    def checker(admin: SysUser = Depends(get_current_admin)) -> SysUser:
        permissions = get_user_permissions(admin.role)
        if permission not in permissions:
            raise ForbiddenException(detail=f"需要{permission}权限")
        return admin
    return checker
