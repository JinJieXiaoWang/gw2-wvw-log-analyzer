# 模块功能：认证相关API路由
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-28
# 依赖说明：FastAPI, Depends, HTTPException, status

from datetime import timedelta

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.admin import AdminLogin, AdminResponse, LoginResponse
from app.schemas.auth.common import ApiResponse
from app.schemas.auth.user import PasswordChange
from app.services import auth_service
from app.services.auth.auth_service import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    authenticate_admin,
    create_access_token,
    decode_access_token,
    get_admin_by_id,
    get_current_admin,
    get_user_permissions,
    require_super_admin,
)
from app.services.system.menu_service import MenuService
from app.utils.error.exceptions import BadRequestException, UnauthorizedException
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/login",
    response_model=ApiResponse,
    summary="操作员登?,
    description="操作员登录接口，成功后返回JWT访问令牌",
)
async def login(
    login_data: AdminLogin,
    db: Session = Depends(get_db),
    x_forwarded_for: str = Header(None),
):
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
    menu_service = MenuService(db)
    menus = menu_service.get_user_menus(admin.role, permissions)
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=user_response,
        permissions=permissions,
        menus=menus,
    )
    return ApiResponse.success_response(data=login_response.model_dump(), message="登录成功")


@router.post(
    "/logout",
    response_model=ApiResponse,
    summary="操作员登?,
    description="操作员登出接?,
)
async def logout(current_admin=Depends(get_current_admin)):
    return ApiResponse.success_response(message="登出成功")


@router.get(
    "/status",
    response_model=ApiResponse,
    summary="获取登录状?,
    description="获取当前登录状?,
)
async def get_login_status(
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    menu_service = MenuService(db)
    
    if not authorization or not authorization.startswith("Bearer "):
        # 未登录，返回公开菜单
        public_menus = menu_service.get_public_menus()
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"], "menus": public_menus},
            message="获取状态成?,
        )
    token = authorization[7:]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        # token 无效，返回公开菜单
        public_menus = menu_service.get_public_menus()
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"], "menus": public_menus},
            message="获取状态成?,
        )
    admin_id = int(payload.get("sub"))
    admin = get_admin_by_id(db, admin_id)
    if not admin or not admin.is_active:
        # 用户无效，返回公开菜单
        public_menus = menu_service.get_public_menus()
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"], "menus": public_menus},
            message="获取状态成?,
        )
    token_version = payload.get("tv")
    if token_version is not None and token_version != (admin.token_version or 0):
        # token 版本不匹配，返回公开菜单
        public_menus = menu_service.get_public_menus()
        return ApiResponse.success_response(
            data={"is_logged_in": False, "user": None, "permissions": ["read"], "menus": public_menus},
            message="获取状态成?,
        )
    role = payload.get("role", "operator")
    permissions = get_user_permissions(role)
    menus = menu_service.get_user_menus(role, permissions)
    user_data = {
        "id": admin.id,
        "username": admin.username,
        "role": role,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
        "last_login": admin.last_login.isoformat() if admin.last_login else None,
        "is_active": admin.is_active,
    }
    return ApiResponse.success_response(
        data={"is_logged_in": True, "user": user_data, "permissions": permissions, "menus": menus},
        message="获取状态成?,
    )


@router.get(
    "/profile",
    response_model=ApiResponse,
    summary="获取用户信息",
    description="获取当前登录操作员的详细信息",
)
async def get_profile(current_admin=Depends(get_current_admin)):
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
    description="修改当前登录用户的密?,
)
async def change_password(
    password_data: PasswordChange,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    current_password = password_data.current_password or password_data.old_password
    auth_service.change_admin_password_with_validation(
        db=db,
        admin=current_admin,
        current_password=current_password,
        new_password=password_data.new_password,
        confirm_password=password_data.confirm_password,
    )
    return ApiResponse.success_response(message="密码修改成功", data=None)
