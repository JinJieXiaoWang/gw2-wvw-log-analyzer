# 模块功能：批量解析API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-11
# 依赖说明：FastAPI

from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import HTTP_200_OK
from app.models.auth.sys_user import SysUser
from app.routers.auth.auth import get_current_admin
from app.schemas.log.batch_parse import (
    BatchParseTaskCreate,
    BatchParseTaskDetailResponse,
    BatchParseTaskListResponse,
    BatchParseTaskResponse,
)
from app.schemas.auth.common import ApiResponse
from app.services.zevtc import batch_parse_service
from app.utils.error.exceptions import BadRequestException, NotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/batch-parse", tags=["批量解析"])


def _verify_task_permission(
    task,
    current_admin: SysUser,
    action: str = "访问",
    admin_role: str = "super_admin",
):
    """检查当前管理员是否有权限操作指定任务"""
    if task.created_by != current_admin.id and current_admin.role != admin_role:
        raise BadRequestException(f"无权{action}此任务")


@router.post("", response_model=ApiResponse, summary="创建批量解析任务")
async def create_batch_parse_task(
    task_data: BatchParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：创建批量解析任务并立即开始执行
    if not task_data.log_ids:
        raise BadRequestException("日志ID列表不能为空")

    try:
        # 创建任务
        task = batch_parse_service.BatchParseService.create_task(
            db=db,
            log_ids=task_data.log_ids,
            task_name=task_data.task_name,
            created_by=current_admin.id,
        )

        # 提交任务到后台队列（带overwrite参数）
        # db_url 参数已废弃，worker 内部直接使用 SessionLocal()
        from app.config.database.database_settings import db_settings

        background_tasks.add_task(
            batch_parse_service.submit_batch_task,
            task.id,
            db_settings.get_database_url(),
            task_data.overwrite,
        )

        return ApiResponse(
            success=True,
            message="批量解析任务创建成功",
            data=BatchParseTaskResponse.model_validate(task),
        )
    except ValueError as e:
        raise BadRequestException(str(e))


@router.get("", response_model=ApiResponse, summary="获取批量解析任务列表")
async def get_batch_parse_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：获取批量解析任务列表
    skip = (page - 1) * page_size
    tasks, total = batch_parse_service.BatchParseService.get_tasks(
        db=db, skip=skip, limit=page_size, status=status, created_by=current_admin.id
    )

    return ApiResponse(
        success=True,
        message="获取批量解析任务列表成功",
        data={
            "items": [BatchParseTaskResponse.model_validate(task) for task in tasks],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get(
    "/{task_id}", response_model=ApiResponse, summary="获取批量解析任务详情"
)
async def get_batch_parse_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：获取批量解析任务详情
    task = batch_parse_service.BatchParseService.get_task_by_id(db, task_id)
    if not task:
        raise NotFoundException(f"批量解析任务不存在: {task_id}")

    _verify_task_permission(task, current_admin)

    items = batch_parse_service.BatchParseService.get_task_items(db, task_id)

    return ApiResponse(
        success=True,
        message="获取批量解析任务详情成功",
        data=BatchParseTaskDetailResponse(
            **BatchParseTaskResponse.model_validate(task).model_dump(), items=items
        ),
    )


@router.get(
    "/{task_id}/result",
    response_model=ApiResponse,
    summary="获取批量解析任务结果",
)
async def get_batch_parse_result(
    task_id: int,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：获取批量解析任务结果
    task = batch_parse_service.BatchParseService.get_task_by_id(db, task_id)
    if not task:
        raise NotFoundException(f"批量解析任务不存在: {task_id}")

    _verify_task_permission(task, current_admin)

    try:
        result = batch_parse_service.BatchParseService.get_task_result(db, task_id)
        return ApiResponse(
            success=True, message="获取批量解析任务结果成功", data=result
        )
    except ValueError as e:
        raise BadRequestException(str(e))


@router.delete(
    "/{task_id}", response_model=ApiResponse, summary="删除批量解析任务"
)
async def delete_batch_parse_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：删除批量解析任务
    task = batch_parse_service.BatchParseService.get_task_by_id(db, task_id)
    if not task:
        raise NotFoundException(f"批量解析任务不存在: {task_id}")

    _verify_task_permission(task, current_admin, action="删除", admin_role="admin")

    success = batch_parse_service.BatchParseService.delete_task(db, task_id)
    if success:
        return ApiResponse(success=True, message="删除批量解析任务成功")
    else:
        return ApiResponse(success=False, message="删除批量解析任务失败")
