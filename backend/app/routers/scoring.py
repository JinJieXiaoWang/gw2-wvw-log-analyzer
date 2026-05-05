# 模块功能：评分 API 接口（实时计算）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-30
# 更新日期：2026-05-05
# 依赖说明：FastAPI, SQLAlchemy, Pydantic
# 说明：
#   1. 本模块提供实时评分计算接口，基于当前评分规则配置动态计算。
#   2. 接口与评分规则系统深度关联：计算时自动读取 scoring_rule 表中的权重配置。
#   3. 若数据库中无规则配置，则自动回退到系统硬编码的默认规则。
#   4. 日志导入时（log_import_service.py）的评分由 calculate_player_score 独立计算，
#      不经过本接口，但两者使用同一套规则逻辑。

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.scoring import FightScoreResult, ScoringRulesResult
from app.services.wvw.scoring_service import ScoringService
from app.utils.logger import logger

router = APIRouter(prefix="/scoring", tags=["评分系统 — 实时计算"])


@router.get(
    "/rules",
    response_model=ApiResponse,
    summary="获取当前评分规则配置",
    description=(
        "读取 scoring_rule 数据表中的规则权重配置。"
        "若表为空或数据不足，自动回退到系统默认规则。"
        "返回结果包含各维度权重（如 damage_weight、healing_weight 等）"
        "以及阈值参数（min_score_threshold、max_score_cap）。"
    ),
)
async def get_scoring_rules(db: Session = Depends(get_db)) -> ApiResponse:
    """
    获取当前生效的评分规则配置。

    **规则来源优先级**：
    1. 数据库 `scoring_rule` 表中启用的规则
    2. 系统硬编码默认规则（兜底）

    **返回字段说明**：
    - `damage_weight`: 伤害维度权重（默认 0.35）
    - `healing_weight`: 治疗维度权重（默认 0.20）
    - `survival_weight`: 生存维度权重（默认 0.10）
    - `min_score_threshold`: 最低分数阈值（默认 0.0）
    - `max_score_cap`: 最高分数上限（默认 100.0）
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
    summary="计算一场战斗的所有玩家评分",
    description=(
        "根据指定的战斗 ID，查询该场战斗的所有玩家统计数据，"
        "结合当前评分规则配置，逐人计算综合评分与各维度评分明细。"
        "计算结果包含总分、等级（S/A/B/C/D/F）、各维度得分及使用的规则配置。"
    ),
)
async def calculate_fight_scores(
    fight_id: int = Path(..., ge=1, description="战斗记录唯一标识（关联 fights.id）"),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    计算一场战斗中所有玩家的综合评分。

    **评分规则关联**：
    - 本接口在计算过程中会调用 `ScoringService.get_scoring_rules()`，
      实时读取 `scoring_rule` 表中的权重配置作为计算依据。
    - 若数据库无规则，则使用系统默认规则（见 `/rules` 接口说明）。

    **计算流程**：
    1. 查询 `fight_stats` 表中该战斗的所有玩家记录
    2. 计算各维度的最大值用于归一化
    3. 逐人调用 `calculate_player_score()` 计算评分
    4. 返回包含 `fight_id`、`total_players`、`scores[]`、`scoring_rules` 的完整结果

    **参数说明**：
    - `fight_id`: 战斗 ID，必须为正整数

    **返回值结构**：
    - `data.fight_id`: 战斗 ID
    - `data.total_players`: 参与评分的玩家数量
    - `data.scores[]`: 玩家评分列表，每项包含：
        - `member_id`: 成员 ID
        - `account`: 玩家账号
        - `total_score`: 综合评分（0-100）
        - `grade`: 等级（S/A/B/C/D/F）
        - `breakdown`: 各维度评分明细
    - `data.scoring_rules`: 本次计算使用的规则权重
    """
    try:
        result = ScoringService.calculate_all_scores(fight_id, db)
        fight_result = FightScoreResult(**result)
        return ApiResponse.success_response(
            message=f"计算战斗 {fight_id} 评分成功",
            data=fight_result.model_dump(),
        )
    except Exception as e:
        logger.error(f"计算战斗评分失败: {e}")
        return ApiResponse.error_response(message=f"计算评分失败: {e}")
