# 模块功能：评分API接口
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-30
# 依赖说明：FastAPI, SQLAlchemy

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.services.wvw.scoring_service import ScoringService
from app.utils.logger import logger

router = APIRouter(prefix="/scoring", tags=["评分系统"])


@router.get("/rules", response_model=ApiResponse)
async def get_scoring_rules(db: Session = Depends(get_db)):
    """
    获取评分规则

    Returns:
        评分规则API响应
    """
    try:
        rules = ScoringService.get_scoring_rules(db)
        return ApiResponse.success_response(message="获取评分规则成功", data=rules)
    except Exception as e:
        logger.error(f"获取评分规则失败: {e}")
        return ApiResponse.error_response(message=f"获取评分规则失败: {e}")


@router.get("/fight/{fight_id}", response_model=ApiResponse)
async def calculate_fight_scores(fight_id: int, db: Session = Depends(get_db)):
    """
    计算一场战斗的所有玩家评分

    Args:
        fight_id: 战斗ID
        db: 数据库会话

    Returns:
        评分结果API响应
    """
    try:
        result = ScoringService.calculate_all_scores(fight_id, db)
        return ApiResponse.success_response(
            message=f"计算战斗 {fight_id} 评分成功", data=result
        )
    except Exception as e:
        logger.error(f"计算战斗评分失败: {e}")
        return ApiResponse.error_response(message=f"计算评分失败: {e}")
