# 模块功能：自定义异常?# 作者：帅妹妹丶.8297
# 创建日期?2026-04-27
# 依赖说明：无

from fastapi import HTTPException, status


class AppException(HTTPException):
    # 功能：应用基础异常?    def __init__(
        self, status_code: int, detail: str, headers: dict[str, str] | None = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    # 功能：资源未找到异常
    def __init__(self, detail: str = "资源未找?):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(AppException):
    # 功能：请求参数错误异?    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(AppException):
    # 功能：未授权异常
    def __init__(self, detail: str = "未授?):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    # 功能：禁止访问异?    def __init__(self, detail: str = "禁止访问"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(AppException):
    # 功能：资源冲突异?    def __init__(self, detail: str = "资源冲突"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InternalServerErrorException(AppException):
    # 功能：服务器内部错误异常
    def __init__(self, detail: str = "服务器内部错?):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
