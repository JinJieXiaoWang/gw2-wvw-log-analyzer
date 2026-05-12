# 模块功能：评?API 接口（实时计?+ 重算任务?
# 作者：帅妹妹丶.8297
# 创建日期?2026-04-30
# 更新日期?2026-05-12
# 依赖说明：FastAPI, SQLAlchemy, Pydantic, APScheduler
# 说明?
#   1. 本模块提供实时评分计算接口和后台重算任务接口?
#   2. 实时计算基于当前评分规则配置动态计算?
#   3. 重算任务支持全量或按条件筛选重算历史数据，通过 APScheduler 后台执行?
#   4. 若数据库中无规则配置，则自动回退到系统硬编码的默认规则?

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth.common import ApiResponse
from app.schemas.scoring.scoring import FightScoreResult, ScoringRulesResult
from app.schemas.scoring.scoring_recalculation import (
    RecalculateRequest,
    RecalculateResponse,
    RecalculateStatusResponse,
)
from app.services.scoring.score_query_service import PlayerScoreService
from app.services.scoring.score_recalculation_service import ScoreRecalculationService
from app.services.wvw.scoring_service import ScoringService
from app.utils.error.exceptions import BadRequestException
from app.utils.logger import logger

router = APIRouter(prefix="/scoring", tags=["评分系统 ?实时计算与重?])


@router.get(
    "/rules",
    response_model=ApiResponse,
    summary="获取当前评分规则配置",
    description=(
        "读取 scoring_rule 数据表中的规则权重配置?
        "若表为空或数据不足，自动回退到系统默认规则?
        "返回结果包含各维度权重（?damage_weight、healing_weight 等）"
        "以及阈值参数（min_score_threshold、max_score_cap）?
    ),
)
async def get_scoring_rules(db: Session = Depends(get_db)) -> ApiResponse:
    """
    获取当前生效的评分规则配置?

    **规则来源优先?*?
    1. 数据?`scoring_rule` 表中启用的规则
    2. 系统硬编码默认规则（兜底?

    **返回字段说明**?
    - `damage_weight`: 伤害维度权重（默?0.35?
    - `healing_weight`: 治疗维度权重（默?0.20?
    - `survival_weight`: 生存维度权重（默?0.10?
    - `min_score_threshold`: 最低分数阈值（默认 0.0?
    - `max_score_cap`: 最高分数上限（默认 100.0?
    """
    try:
        rules = ScoringService.get_scoring_rules(db)
        result = ScoringRulesResult(
            rules=rules,
            role_type="dps",
            is_default=len(rules) <= 2,
        )
        return ApiResponse.success_response(
            message="获取评分规则成功", data=result.model_dump()
        )
    except Exception as e:
        logger.error(f"获取评分规则失败: {e}")
        return ApiResponse.error_response(message=f"获取评分规则失败: {e}")


@router.get(
    "/fight/{fight_id}",
    response_model=ApiResponse,
    summary="计算一场战斗的所有玩家评?,
    description=(
        "根据指定的战?ID，查询该场战斗的所有玩家统计数据，"
        "结合当前评分规则配置，逐人计算综合评分与各维度评分明细?
        "计算结果包含总分、等级（S/A/B/C/D/F）、各维度得分及使用的规则配置?
    ),
)
async def calculate_fight_scores(
    fight_id: int = Path(..., ge=1, description="战斗记录唯一标识（关系fights.id?),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    计算一场战斗中所有玩家的综合评分?

    **评分规则关联**?
    - 本接口在计算过程中会调用 `ScoringService.get_scoring_rules()`?
      实时读取 `scoring_rule` 表中的权重配置作为计算依据?
    - 若数据库无规则，则使用系统默认规则（?`/rules` 接口说明）?

    **计算流程**?
    1. 查询 `fight_stats` 表中该战斗的所有玩家记?
    2. 计算各维度的最大值用于归一?
    3. 逐人调用 `calculate_player_score()` 计算评分
    4. 返回包含 `fight_id`、`total_players`、`scores[]`、`scoring_rules` 的完整结?

    **参数说明**?
    - `fight_id`: 战斗 ID，必须为正整?

    **返回值结?*?
    - `data.fight_id`: 战斗 ID
    - `data.total_players`: 参与评分的玩家数据
    - `data.scores[]`: 玩家评分列表，每项包含：
        - `member_id`: 成员 ID
        - `account`: 玩家账号
        - `total_score`: 综合评分?-100?
        - `grade`: 等级（S/A/B/C/D/F?
        - `breakdown`: 各维度评分明?
    - `data.scoring_rules`: 本次计算使用的规则权?
    """
    try:
        # 【v4.0】使?PlayerScoreService 查询时实时计算，规则更新立即生效
        result = PlayerScoreService.calculate_fight_scores(db, fight_id)
        fight_result = FightScoreResult(**result)
        return ApiResponse.success_response(
            message=f"计算战斗 {fight_id} 评分成功",
            data=fight_result.model_dump(),
        )
    except Exception as e:
        logger.error(f"计算战斗评分失败: {e}")
        return ApiResponse.error_response(message=f"计算评分失败: {e}")


# ==================== 评分重算任务接口 ====================

@router.post(
    "/recalculate",
    response_model=ApiResponse,
    summary="触发评分重算任务",
    description=(
        "根据筛选条件触发历史评分数据的后台重算任务?
        "任务在后台异步执行，通过返回?version_id 查询进度?
        "支持按时间范围、职业、账号、战斗ID等条件筛选?
    ),
)
async def trigger_recalculation(
    request: RecalculateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    触发评分重算任务?

    **执行流程**?
    1. 创建 `ScoringRuleVersion` 记录（status=pending?
    2. 通过 APScheduler 添加后台任务
    3. 返回 version_id 供前端轮询进?

    **筛选条?*（filters 字段）：
    - `fight_ids`: 指定战斗ID列表
    - `date_from` / `date_to`: 时间范围（YYYY-MM-DD?
    - `professions`: 指定职业列表
    - `account_names`: 指定账号列表
    - ?filters 表示全量重算

    **并发控制**?
    - 同一时刻只允许一个重算任务在执行?
    - 如果已有任务在执行，新请求将被拒?
    """
    try:
        # 并发控制检?
        if ScoreRecalculationService.is_task_running(db):
            raise BadRequestException("已有重算任务在执行中，请等待完成后再触发新任?)

        filters = request.filters.model_dump(exclude_none=True) if request.filters else {}

        # 创建重算任务
        version = ScoreRecalculationService.create_task(
            db, filters, description=request.description or ""
        )

        # 启动后台任务（使?APScheduler ?asyncio.create_task?
        ScoreRecalculationService.start_recalculation_task(version.id, filters)

        return ApiResponse.success_response(
            message="重算任务已创建，正在后台执行",
            data=RecalculateResponse(
                version_id=version.id,
                version=version.version,
                status=version.status,
                message="重算任务已创?,
            ).model_dump(),
        )
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"创建重算任务失败: {e}")
        return ApiResponse.error_response(message=f"创建重算任务失败: {e}")


@router.get(
    "/recalculate/{version_id}",
    response_model=ApiResponse,
    summary="查询重算任务进度",
    description="根据版本记录ID查询后台重算任务的执行进度和状态?,
)
async def get_recalculation_status(
    version_id: int = Path(..., ge=1, description="版本记录ID"),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    查询重算任务的执行进度?

    **返回字段说明**?
    - `status`: 任务状态（pending/processing/completed/failed?
    - `total_records`: 需更新的总记录数
    - `updated_records`: 已更新记录数
    - `progress_percent`: 进度百分?
    - `created_at`: 任务创建时间
    - `completed_at`: 任务完成时间
    """
    try:
        status = ScoreRecalculationService.get_task_status(db, version_id)
        if not status:
            raise BadRequestException(f"版本记录 ID={version_id} 不存?)

        return ApiResponse.success_response(
            message="获取重算进度成功",
            data=RecalculateStatusResponse(**status).model_dump(),
        )
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"获取重算进度失败: {e}")
        return ApiResponse.error_response(message=f"获取重算进度失败: {e}")
