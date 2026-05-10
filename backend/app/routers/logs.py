# 模块功能：日志管理API路由
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 依赖说明：FastAPI

import asyncio
import hashlib
import json
import os
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

# 全局解析并发限制：最多同时解析 3 个日志，防止线程池被占满导致服务器卡死
MAX_CONCURRENT_PARSE = 3
_parse_semaphore = threading.Semaphore(MAX_CONCURRENT_PARSE)

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Query,
    Request,
    UploadFile,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.models.log import Log
from app.models.sys_user import SysUser
from app.routers.auth import get_current_admin
from app.schemas.batch_parse import (
    BatchParseProgressResponse,
    BatchParseResultResponse,
    BatchParseTaskCreate,
    BatchParseTaskDetailResponse,
    BatchParseTaskListResponse,
    BatchParseTaskResponse,
    BatchParseTaskUpdate,
)
from app.schemas.common import ApiResponse
from app.schemas.log import (
    LogListResponse,
    LogResponse,
    LogUpdate,
    ParseProgressResponse,
    ParseResultResponse,
    ValidationReportResponse,
)
from app.services.zevtc import batch_parse_service, log_service, parser_service
from app.utils.cache import Cache
from app.utils.exceptions import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
)
from app.utils.logger import logger

router = APIRouter(prefix="/logs", tags=["日志管理"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_upload_semaphore = asyncio.Semaphore(2)


class _ProgressStore:
    """解析进度存储包装器，基于TTL Cache防止无界增长
    
    原实现使用普通 dict，解析崩溃或重启后条目永久残留，导致内存泄漏。
    改用 Cache（LRU + TTL）后，条目会在 24 小时后自动过期，
    且最大保留 1000 条，超出时淘汰最早的条目。
    """
    def __init__(self):
        self._cache = Cache(max_size=1000, default_ttl=86400)

    def _key(self, log_id: int) -> str:
        return f"parse_progress:{log_id}"

    def __setitem__(self, log_id: int, value: Dict[str, Any]) -> None:
        self._cache.set(self._key(log_id), value, ttl=86400)

    def __getitem__(self, log_id: int) -> Dict[str, Any]:
        val = self._cache.get(self._key(log_id))
        if val is None:
            # 自动创建默认条目，避免 KeyError 导致解析任务崩溃
            val = {
                "stage": "未开始",
                "progress": 0,
                "current_file": "",
                "players_found": 0,
                "events_processed": 0,
                "errors": [],
                "warnings": [],
            }
            self._cache.set(self._key(log_id), val, ttl=86400)
        return val

    def __contains__(self, log_id: int) -> bool:
        return self._cache.get(self._key(log_id)) is not None

    def __delitem__(self, log_id: int) -> None:
        self._cache.delete(self._key(log_id))

    def get(self, log_id: int, default: Any = None) -> Any:
        val = self._cache.get(self._key(log_id))
        return val if val is not None else default


parse_progress_store = _ProgressStore()


@router.get("", response_model=ApiResponse, summary="获取日志列表")
async def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    parse_status: Optional[str] = Query(None, description="解析状态"),
    search: Optional[str] = Query(None, description="文件名搜索"),
    db: Session = Depends(get_db),
):
    # 功能：获取日志列表
    skip = (page - 1) * page_size
    logs, total = log_service.get_logs(
        db, skip=skip, limit=page_size, parse_status=parse_status, search=search
    )

    return ApiResponse.success_response(
        data={
            "items": [LogResponse.model_validate(log) for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取日志列表成功",
        code=HTTP_200_OK,
    )


# ==================== 批量解析相关接口 ====================


@router.post("/batch-parse", response_model=ApiResponse, summary="创建批量解析任务")
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
        from app.config.database_settings import db_settings

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


@router.get("/batch-parse", response_model=ApiResponse, summary="获取批量解析任务列表")
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
    "/batch-parse/{task_id}", response_model=ApiResponse, summary="获取批量解析任务详情"
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

    # 检查权限
    if task.created_by != current_admin.id and current_admin.role != "super_admin":
        raise BadRequestException("无权访问此任务")

    # 获取任务项
    from app.models.batch_parse import BatchParseTaskItem

    items = (
        db.query(BatchParseTaskItem).filter(BatchParseTaskItem.task_id == task_id).all()
    )

    return ApiResponse(
        success=True,
        message="获取批量解析任务详情成功",
        data=BatchParseTaskDetailResponse(
            **BatchParseTaskResponse.model_validate(task).model_dump(), items=items
        ),
    )


@router.get(
    "/batch-parse/{task_id}/result",
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

    # 检查权限
    if task.created_by != current_admin.id and current_admin.role != "super_admin":
        raise BadRequestException("无权访问此任务")

    try:
        result = batch_parse_service.BatchParseService.get_task_result(db, task_id)
        return ApiResponse(
            success=True, message="获取批量解析任务结果成功", data=result
        )
    except ValueError as e:
        raise BadRequestException(str(e))


@router.delete(
    "/batch-parse/{task_id}", response_model=ApiResponse, summary="删除批量解析任务"
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

    # 检查权限
    if task.created_by != current_admin.id and current_admin.role != "admin":
        raise BadRequestException("无权删除此任务")

    success = batch_parse_service.BatchParseService.delete_task(db, task_id)
    if success:
        return ApiResponse(success=True, message="删除批量解析任务成功")
    else:
        return ApiResponse(success=False, message="删除批量解析任务失败")


@router.get("/{log_id}", response_model=ApiResponse, summary="获取日志详情")
async def get_log(log_id: int, db: Session = Depends(get_db)):
    # 功能：获取日志详情
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    return ApiResponse(
        success=True, message="获取日志成功", data=LogResponse.model_validate(log)
    )


@router.post("", response_model=ApiResponse, summary="上传日志文件")
async def upload_log(
    file: UploadFile = File(...),
    auto_parse: bool = Query(False, description="是否自动解析"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request: Request = None,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：上传日志文件
    if not file.filename.endswith(".zevtc"):
        raise BadRequestException("只支持 .zevtc 格式的文件")

    async with _upload_semaphore:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

    # 计算 SHA256 指纹
    file_sha256 = hashlib.sha256(content).hexdigest()

    # 重复文件检测
    existing_log = db.query(Log).filter(Log.file_sha256 == file_sha256).first()
    if existing_log:
        # 删除本次保存的重复文件
        try:
            os.remove(file_path)
        except OSError:
            pass
        logger.info(
            f"文件重复上传: {file.filename} (sha256={file_sha256[:16]}...), 已有日志ID: {existing_log.id}"
        )
        return ApiResponse(
            success=True,
            message="文件已存在，无需重复上传",
            data=LogResponse.model_validate(existing_log),
        )

    # 使用传输大小作为文件大小（不解析 ZIP 内部结构）
    file_size_raw = len(content)

    # 获取客户端 IP
    upload_ip = None
    if request:
        upload_ip = request.headers.get(
            "x-forwarded-for", request.client.host if request.client else None
        )

    log = log_service.create_log(
        db=db,
        log_data={
            "log_uuid": str(uuid.uuid4()),
            "filename": file.filename,
            "file_sha256": file_sha256,
            "file_size_compressed": len(content),
            "file_size_raw": file_size_raw,
            "file_path": file_path,
            "upload_ip": upload_ip,
        },
    )

    # 自动解析
    if auto_parse:
        background_tasks.add_task(parse_log_background, log.id, db.bind.url, True)
        logger.info(f"上传日志成功并自动触发解析，日志ID: {log.id}")
        return ApiResponse(
            success=True,
            message="上传日志成功，已自动开始解析",
            data=LogResponse.model_validate(log),
        )

    logger.info(f"上传日志成功，日志ID: {log.id}")

    return ApiResponse(
        success=True, message="上传日志成功", data=LogResponse.model_validate(log)
    )


@router.delete("/{log_id}", response_model=ApiResponse, summary="删除日志")
async def delete_log(
    log_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)
):
    # 功能：删除日志
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        logger.warning(f"删除失败：日志ID {log_id} 不存在")
        raise NotFoundException(f"日志ID {log_id} 不存在")

    logger.info(f"用户 {current_admin.username} 请求删除日志: {log.filename}")

    try:
        # 删除文件
        file_deleted = False
        if log.file_path and os.path.exists(log.file_path):
            try:
                os.remove(log.file_path)
                file_deleted = True
                logger.info(f"删除日志文件成功: {log.file_path}")
            except Exception as e:
                logger.warning(f"删除日志文件失败: {str(e)}")

        # 删除数据库记录
        success = log_service.delete_log(db, log_id)

        # 清理进度存储
        if log_id in parse_progress_store:
            del parse_progress_store[log_id]

        logger.info(f"日志删除成功: {log.filename}")
        return ApiResponse(success=True, message="删除日志成功")

    except Exception as e:
        logger.error(f"删除日志异常: {str(e)}", exc_info=True)
        raise InternalServerErrorException(f"删除日志失败: {str(e)}")


@router.put("/{log_id}", response_model=ApiResponse, summary="更新日志")
async def update_log(
    log_id: int,
    log_update: LogUpdate,
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：更新日志
    log = log_service.update_log(db, log_id, log_update)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    return ApiResponse(
        success=True, message="更新日志成功", data=LogResponse.model_validate(log)
    )


@router.post("/{log_id}/parse", response_model=ApiResponse, summary="解析日志文件")
async def parse_log(
    log_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    overwrite: bool = Query(True, description="是否覆盖已有的解析数据"),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：解析日志文件（后台任务）
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status == "parsing":
        raise BadRequestException("日志正在解析中")

    if not os.path.exists(log.file_path):
        raise NotFoundException(f"日志文件不存在: {log.file_path}")

    # 更新状态为解析中
    log_service.update_parse_status(db, log_id, "parsing")

    # 初始化进度存储
    parse_progress_store[log_id] = {
        "stage": "初始化",
        "progress": 0,
        "current_file": os.path.basename(log.file_path),
        "players_found": 0,
        "events_processed": 0,
        "errors": [],
        "warnings": [],
        "start_time": datetime.now().isoformat(),
    }

    # 启动后台解析任务（带overwrite参数和当前用户ID）
    background_tasks.add_task(parse_log_background, log_id, db.bind.url, overwrite, current_admin.id)

    return ApiResponse(success=True, message="开始解析日志", data={"log_id": log_id})


def _do_parse_log(log_id: int, db_url: str, overwrite: bool = True, user_id: int = 0):
    """实际执行解析（供信号量包装调用）"""
    from app.config.database import SessionLocal
    from app.services.system.notice_service import NoticeService

    db = SessionLocal()

    try:
        log = log_service.get_log_by_id(db, log_id)
        if not log:
            return

        # 更新进度
        parse_progress_store[log_id]["stage"] = "解析文件"
        parse_progress_store[log_id]["progress"] = 10

        # v2.0: 使用 LogImportService 提取标量数据写入 fights/fight_stats/members
        from app.services.zevtc.log_import_service import LogImportService

        importer = LogImportService(db)
        import_result = importer.import_log(log_id, log.file_path)

        if import_result["success"]:
            parse_progress_store[log_id]["stage"] = "完成"
            parse_progress_store[log_id]["progress"] = 100
            parse_progress_store[log_id]["end_time"] = datetime.now().isoformat()
            parse_progress_store[log_id]["players_found"] = import_result[
                "players_count"
            ]
            db.commit()
            logger.info(
                f"日志解析完成，日志ID: {log_id}, fight_id={import_result['fight_id']}, players={import_result['players_count']}"
            )
        else:
            parse_progress_store[log_id]["stage"] = "错误"
            parse_progress_store[log_id]["errors"].append(import_result["error"])
            log_service.update_parse_status(
                db, log_id, "failed", import_result["error"]
            )
            db.commit()
            logger.error(
                f"日志解析失败，日志ID: {log_id}, 原因: {import_result['error']}"
            )
            # 解析失败时创建全局通知（所有人可见）
            NoticeService.create_notice(
                db=db,
                title=f"日志解析失败: {log.filename}",
                content=f"文件 {log.filename} (ID: {log_id}) 解析失败，原因: {import_result['error']}，请尝试重新解析。",
                notice_type="1",
                source_type="parse_failed",
                source_id=str(log_id),
                create_by=str(user_id) if user_id else "system",
            )
            db.commit()

    except Exception as e:
        logger.error(f"解析异常: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        log_service.update_parse_status(db, log_id, "failed", str(e))
        if log_id in parse_progress_store:
            parse_progress_store[log_id]["errors"].append(str(e))
            parse_progress_store[log_id]["stage"] = "错误"
        # 异常时也创建通知
        try:
            log = log_service.get_log_by_id(db, log_id)
            if log:
                NoticeService.create_notice(
                    db=db,
                    title=f"日志解析异常: {log.filename}",
                    content=f"文件 {log.filename} (ID: {log_id}) 解析过程中发生异常: {str(e)}，请尝试重新解析。",
                    notice_type="1",
                    source_type="parse_failed",
                    source_id=str(log_id),
                    create_by=str(user_id) if user_id else "system",
                )
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


async def parse_log_background(log_id: int, db_url: str, overwrite: bool = True, user_id: int = 0):
    """后台解析任务（带全局并发限制，防止服务器卡死）"""
    # 使用信号量限制全局并发数，超过限制则排队等待
    with _parse_semaphore:
        _do_parse_log(log_id, db_url, overwrite, user_id)


@router.get(
    "/{log_id}/parse/progress", response_model=ApiResponse, summary="获取日志解析进度"
)
async def get_parse_progress(log_id: int, db: Session = Depends(get_db)):
    # 功能：获取解析进度
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    progress = parse_progress_store.get(
        log_id,
        {
            "stage": "未开始",
            "progress": 0,
            "current_file": "",
            "players_found": 0,
            "events_processed": 0,
            "errors": [],
            "warnings": [],
        },
    )

    return ApiResponse(success=True, message="获取解析进度成功", data=progress)


@router.get(
    "/{log_id}/parse/result", response_model=ApiResponse, summary="获取解析结果"
)
async def get_parse_result(log_id: int, db: Session = Depends(get_db)):
    # 功能：获取解析结果
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status == "pending":
        raise BadRequestException("当前文件尚未解析，请解析后再进行查看")

    if log.parse_status == "parsing":
        raise BadRequestException("日志正在解析中，请等待解析完成")

    if log.parse_status == "failed":
        raise BadRequestException(f"日志解析失败: {log.error_message or '未知错误'}")

    if log.parse_status != "completed":
        raise BadRequestException(f"日志状态异常，当前状态: {log.parse_status}")

    # 从新体系获取统计
    from app.models.fight import Fight
    from app.models.fight_stats import FightStats

    fight = db.query(Fight).filter(Fight.log_id == log_id).first()
    fight_id = fight.id if fight else None
    stats_count = (
        db.query(FightStats).filter(FightStats.fight_id == fight_id).count()
        if fight_id
        else 0
    )

    return ApiResponse(
        success=True,
        message="获取解析结果成功",
        data={
            "log_id": log_id,
            "parse_status": log.parse_status,
            "parse_time": log.parsed_at.isoformat() if log.parsed_at else None,
            "fight_id": fight_id,
            "player_count": stats_count,
            "map_name": fight.map_name if fight else None,
            "duration_sec": fight.duration_sec if fight else None,
        },
    )


@router.post("/{log_id}/validate", response_model=ApiResponse, summary="验证解析数据")
async def validate_parsed_data(log_id: int, db: Session = Depends(get_db)):
    # 功能：验证解析数据
    log = log_service.get_log_by_id(db, log_id)
    if not log:
        raise NotFoundException(f"日志ID {log_id} 不存在")

    if log.parse_status != "completed":
        raise BadRequestException(f"日志未完成解析，当前状态: {log.parse_status}")

    parser = parser_service.LogParser()
    if os.path.exists(log.file_path):
        try:
            parser.parse_file(log.file_path)
            validation = parser.validate_data()

            return ApiResponse(
                success=validation.get("passed", False),
                message="数据验证完成",
                data=validation,
            )
        except Exception as e:
            logger.error(f"数据验证失败: {e}")

    return ApiResponse(success=False, message="无法验证数据", data=None)


@router.post("/batch-delete", response_model=ApiResponse, summary="批量删除日志")
async def batch_delete_logs(
    log_ids: list[int],
    db: Session = Depends(get_db),
    current_admin: SysUser = Depends(get_current_admin),
):
    # 功能：批量删除日志
    deleted_count = 0
    failed_ids = []

    try:
        for log_id in log_ids:
            log = log_service.get_log_by_id(db, log_id)
            if not log:
                failed_ids.append(log_id)
                continue

            # 删除文件
            if log.file_path and os.path.exists(log.file_path):
                try:
                    os.remove(log.file_path)
                except Exception as e:
                    logger.error(f"删除日志文件失败 {log_id}: {e}")

            # 删除数据库记录
            if log_service.delete_log(db, log_id):
                deleted_count += 1
                # 清理进度存储
                if log_id in parse_progress_store:
                    del parse_progress_store[log_id]
            else:
                failed_ids.append(log_id)
    except Exception as e:
        db.rollback()
        logger.error(f"批量删除日志异常: {e}", exc_info=True)
        raise InternalServerErrorException(f"批量删除失败: {str(e)}")

    return ApiResponse(
        success=True,
        message=f"批量删除完成: 删除 {deleted_count} 个，失败 {len(failed_ids)} 个",
        data={"deleted_count": deleted_count, "failed_ids": failed_ids},
    )


@router.get("/export", summary="导出日志数据")
async def export_logs(
    log_ids: Optional[list[int]] = Query(
        None, description="要导出的日志ID列表，不填则导出所有"
    ),
    format: str = Query("json", description="导出格式: json/csv"),
    db: Session = Depends(get_db),
):
    # 功能：导出日志数据
    if log_ids:
        logs = [
            log_service.get_log_by_id(db, log_id)
            for log_id in log_ids
            if log_service.get_log_by_id(db, log_id)
        ]
    else:
        logs, _ = log_service.get_logs(db, skip=0, limit=1000)

    export_data = []
    for log in logs:
        export_data.append(
            {
                "id": log.id,
                "log_uuid": log.log_uuid,
                "filename": log.filename,
                "file_sha256": log.file_sha256,
                "file_size_compressed": log.file_size_compressed,
                "file_size_raw": log.file_size_raw,
                "file_path": log.file_path,
                "parse_status": log.parse_status,
                "parse_time_ms": log.parse_time_ms,
                "parsed_at": log.parsed_at.isoformat() if log.parsed_at else None,
                "error_message": log.error_message,
                "upload_time": log.upload_time.isoformat() if log.upload_time else None,
                "upload_ip": log.upload_ip,
                "uploaded_by": log.uploaded_by,
            }
        )

    if format == "csv":
        import csv
        from io import StringIO

        output = StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        content = output.getvalue()
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(
            content=content,
            headers={"Content-Disposition": "attachment; filename=logs.csv"},
            media_type="text/csv",
        )
    else:
        return ApiResponse(success=True, message="导出成功", data=export_data)
