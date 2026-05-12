# 模块功能：通用数据验证模式
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-28
# 依赖说明：pydantic v2

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    # 功能：统一API响应模型
    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="提示消息")
    data: Optional[Any] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(), description="时间?
    )
    code: Optional[int] = Field(None, description="HTTP状态码")

    @classmethod
    def success_response(
        cls, data: Any = None, message: str = "操作成功", code: int = None
    ):
        # 功能：创建成功响?        # 参数：data - 响应数据；message - 提示消息；code - HTTP状态码
        # 返回：ApiResponse实例
        return cls(
            success=True,
            message=message,
            data=data,
            code=code,
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def fail_response(
        cls,
        message: str,
        error_code: str = "OPERATION_FAILED",
        code: int = None,
        data: Any = None,
    ):
        # 功能：创建失败响应（操作未成功但不是系统错误?        # 参数：message - 错误消息；error_code - 错误代码；code - HTTP状态码；data - 附加数据
        # 返回：ApiResponse实例
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            code=code,
            data=data,
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def error_response(
        cls,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        code: int = None,
        data: Any = None,
    ):
        # 功能：创建错误响?        # 参数：message - 错误消息；error_code - 错误代码；code - HTTP状态码；data - 附加数据
        # 返回：ApiResponse实例
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            code=code,
            data=data,
            timestamp=datetime.now().isoformat(),
        )


class PaginatedResponse(BaseModel):
    # 功能：分页响应模型    model_config = ConfigDict(from_attributes=True)

    items: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(0, description="总页?)


class HTTPValidationError(BaseModel):
    # 功能：HTTP验证错误响应模型
    detail: List[dict] = Field(..., description="错误详情")


class ChangePasswordRequest(BaseModel):
    # 功能：修改密码请求模型    current_password: str = Field(
        ..., min_length=6, max_length=128, description="当前密码"
    )
    new_password: str = Field(..., min_length=6, max_length=128, description="新密?)
    confirm_password: str = Field(
        ..., min_length=6, max_length=128, description="确认新密?
    )


class LoginStatusResponse(BaseModel):
    # 功能：登录状态响应模型    is_logged_in: bool = Field(..., description="是否已登?)
    user: Optional[dict] = Field(None, description="用户信息（已登录时返回）")
    permissions: List[str] = Field(["read"], description="权限列表")
