# 模块功能：认证相关API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-28
# 依赖说明：FastAPI, Depends, HTTPException, status

from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.admin import AdminLogin, AdminResponse, LoginResponse
from app.schemas.common import ApiResponse
from app.schemas.user import PasswordChange
from app.services.auth_service import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    authenticate_admin,
    create_access_token,
    decode_access_token,
    get_admin_by_id,
    get_current_admin,
    get_password_hash,
    get_user_permissions,
    require_super_admin,
    verify_password,
)
from app.utils.exceptions import BadRequestException, UnauthorizedException
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/login",
    response_model=ApiResponse,
    summary="操作员登录",
    description="操作员登录接口，成功后返回JWT访问令牌",
)
async def login(
    login_data: AdminLogin,
    db: Session = Depends(get_db),
    x_forwarded_for: str = Header(None),
):
    """
    操作员登录接口

    请求方式：POST
    请求体：JSON格式 {"username": "...", "password": "..."}

    成功返回包含JWT令牌的响应，令牌有效期2小时。

    登录限制：5分钟内最多尝试5次，超过后锁定15分钟。
    """
    client_ip = x_forwarded_for or "127.0.0.1"

    admin = authenticate_admin(db, login_data.username, login_data.password, client_ip)

    if isinstance(admin, dict) and "locked" in admin:
        raise BadRequestException(detail=admin["locked"])

    if not admin:
        raise BadRequestException(detail="用户名或密码错误")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={
            "sub": str(admin.id),
            "username": admin.username,
            "role": admin.role,
            "tv": admin.token_version or 0,
        },
        expires_delta=access_token_expires,
    )

    user_response = AdminResponse(
        id=admin.id,
        username=admin.username,
        role=admin.role,
        is_active=admin.is_active,
        is_predefined=admin.is_predefined,
        created_at=admin.created_at,
        last_login=admin.last_login,
    )

    permissions = get_user_permissions(admin.role)

    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=user_response,
        permissions=permissions,
    )

    return ApiResponse.success_response(data=login_response.model_dump(), message="登录成功")


@router.post(
    "/logout",
    response_model=ApiResponse,
    summary="操作员登出",
    description="操作员登出接口",
)
async def logout(current_admin=Depends(get_current_admin)):
    """
    操作员登出接口

    请求方式：POST
    认证要求：需要有效的JWT令牌

    前端应在调用此接口后清除本地存储的token。
    """
    return ApiResponse.success_response(message="登出成功")


@router.get(
    "/status",
    response_model=ApiResponse,
    summary="获取登录状态",
    description="获取当前登录状态",
)
async def get_login_status(
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    """
    获取登录状态接口

    请求方式：GET

    检查当前用户是否已登录，返回用户信息和权限列表。
    """
    if not authorization or not authorization.startswith("Bearer "):
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"]},
            message="获取状态成功",
        )

    token = authorization[7:]
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"]},
            message="获取状态成功",
        )

    admin_id = int(payload.get("sub"))
    admin = get_admin_by_id(db, admin_id)

    if not admin or not admin.is_active:
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"]},
            message="获取状态成功",
        )

    # 验证 token_version
    token_version = payload.get("tv")
    if token_version is not None and token_version != (admin.token_version or 0):
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"]},
            message="获取状态成功",
        )

    role = payload.get("role", "operator")
    permissions = get_user_permissions(role)

    user_data = {
        "id": admin.id,
        "username": admin.username,
        "role": role,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
        "last_login": admin.last_login.isoformat() if admin.last_login else None,
        "is_active": admin.is_active,
    }

    return ApiResponse.success_response(
        data={"is_logged_in": True, "user": user_data, "permissions": permissions},
        message="获取状态成功",
    )


@router.get(
    "/profile",
    response_model=ApiResponse,
    summary="获取用户信息",
    description="获取当前登录操作员的详细信息",
)
async def get_profile(current_admin=Depends(get_current_admin)):
    """
    获取用户信息接口

    请求方式：GET
    认证要求：需要有效的JWT令牌

    返回当前登录操作员的详细信息和权限列表。
    """
    user_response = AdminResponse(
        id=current_admin.id,
        username=current_admin.username,
        role=current_admin.role,
        is_active=current_admin.is_active,
        is_predefined=current_admin.is_predefined,
        created_at=current_admin.created_at,
        last_login=current_admin.last_login,
    )

    permissions = get_user_permissions(current_admin.role)

    return ApiResponse.success_response(
        data={"user": user_response.model_dump(), "permissions": permissions},
        message="获取用户信息成功",
    )


@router.post(
    "/change-password",
    response_model=ApiResponse,
    summary="修改密码",
    description="修改当前登录用户的密码",
)
async def change_password(
    password_data: PasswordChange,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    修改密码接口

    请求方式：POST
    认证要求：需要有效的JWT令牌

    验证当前密码，更新为新密码。
    """
    # 兼容 old_password 字段名
    current_password = password_data.current_password or password_data.old_password
    if not current_password:
        raise BadRequestException(detail="请提供当前密码")

    # confirm_password 可选验证（前端若提供了才校验一致性）
    if password_data.confirm_password is not None and password_data.new_password != password_data.confirm_password:
        raise BadRequestException(detail="两次输入的密码不一致")

    if len(password_data.new_password) < 6:
        raise BadRequestException(detail="新密码长度至少6位")

    if not verify_password(current_password, current_admin.password_hash):
        raise BadRequestException(detail="当前密码错误")

    current_admin.password_hash = get_password_hash(password_data.new_password)
    current_admin.token_version = (current_admin.token_version or 0) + 1
    db.commit()

    logger.info(f"用户 {current_admin.username} 修改了密码")

    return ApiResponse.success_response(message="密码修改成功", data=None)



