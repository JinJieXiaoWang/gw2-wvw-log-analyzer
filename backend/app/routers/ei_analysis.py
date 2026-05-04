# -*- coding: utf-8 -*-
# 模块功能：EI分析结果查询（精简版）
# 作者：帅妹妹丶.8297
# 创建日期：2026-04-27
# 更新日期：2026-05-01
# 说明：v2.0 改造——不再返回 40MB 完整 EI JSON，仅返回 ~9KB 战斗摘要。
#       v2.1 增强——增加聚合统计、Buff 排行、支援排行等多维数据。

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.log import Log
from app.schemas.common import ApiResponse
from app.services.zevtc import fight_service as fight_svc
from app.utils.logger import logger


# Pydantic 响应模型（用于 rotation 接口文档）
class SkillMapItem(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    gw2_id: int
    skill_key: str


class PlayerRotationResponse(BaseModel):
    account: str
    character_name: Optional[str] = None
    profession: Optional[str] = None
    rotation: List[Any]
    skill_casts: Dict[str, int]
    skill_map: Dict[str, SkillMapItem]


router = APIRouter(prefix="/ei-analysis", tags=["EI分析"])


@router.get("/{log_id}", response_model=ApiResponse, summary="获取日志战斗摘要")
async def get_ei_summary(
    log_id: int,
    sort_by: Optional[str] = Query("damage", description="排序字段"),
    db: Session = Depends(get_db),
):
    """
    获取日志的战斗摘要数据。
    返回精简版数据（~9KB），替代原先 40MB 完整 EI JSON。
    v2.1 增加聚合统计、Buff 排行、支援数据。
    """
    try:
        fight = fight_svc.get_fights_by_log_id(db, log_id)
        if not fight:
            return ApiResponse(
                success=False, message="该日志暂无解析结果", code=404, data=None
            )

        fight = fight[0]
        players = fight_svc.get_log_player_stats(db, log_id, sort_by)
        aggregate = fight_svc.get_fight_aggregate_stats(db, log_id)

        # 查询 dps.report permalink
        log_record = db.query(Log).filter(Log.id == log_id).first()
        dps_report_permalink = log_record.dps_report_permalink if log_record else None

        # 职业分布
        prof_dist = {}
        for p in players:
            prof = p.get("profession", "Unknown")
            prof_dist[prof] = prof_dist.get(prof, 0) + 1

        # Buff 排行（按 Might  uptime 排序取 TOP5）
        buff_leaders = {
            "might": sorted(
                players, key=lambda x: x.get("might_uptime", 0), reverse=True
            )[:5],
            "quickness": sorted(
                players, key=lambda x: x.get("quickness_uptime", 0), reverse=True
            )[:5],
            "alacrity": sorted(
                players, key=lambda x: x.get("alacrity_uptime", 0), reverse=True
            )[:5],
            "fury": sorted(
                players, key=lambda x: x.get("fury_uptime", 0), reverse=True
            )[:5],
            "stability": sorted(
                players, key=lambda x: x.get("stability_uptime", 0), reverse=True
            )[:5],
        }

        # 支援排行
        support_leaders = {
            "boon_strips": sorted(
                players, key=lambda x: x.get("boon_strips", 0), reverse=True
            )[:5],
            "condition_cleanses": sorted(
                players, key=lambda x: x.get("condition_cleanses", 0), reverse=True
            )[:5],
            "resurrects": sorted(
                players, key=lambda x: x.get("resurrects", 0), reverse=True
            )[:5],
        }

        # 防御排行
        defense_leaders = {
            "damage_taken": sorted(
                players, key=lambda x: x.get("damage_taken", 0), reverse=True
            )[:5],
            "dodge_count": sorted(
                players, key=lambda x: x.get("dodge_count", 0), reverse=True
            )[:5],
        }

        summary = {
            "log_id": log_id,
            "fight": {
                "id": fight.id,
                "map_name": fight.map_name,
                "start_time": (
                    fight.start_time.isoformat() if fight.start_time else None
                ),
                "duration_sec": fight.duration_sec,
                "duration_ms": fight.duration_ms,
                "server_name": fight.server_name,
                "recorded_by": fight.recorded_by,
                "recorded_account": fight.recorded_account,
                "total_damage": fight.total_damage,
                "total_healing": fight.total_healing,
                "kill_count": fight.kill_count,
                "death_count": fight.death_count,
                "player_count": fight.player_count,
                "is_wvw": True,
            },
            "aggregate": aggregate,
            "players": players,
            "total_players": len(players),
            "enemy_players": fight_svc.get_enemy_players(db, log_id),
            "dps_report_permalink": dps_report_permalink,
            "profession_distribution": prof_dist,
            "buff_leaders": buff_leaders,
            "support_leaders": support_leaders,
            "defense_leaders": defense_leaders,
        }

        return ApiResponse.success_response(
            data=summary,
            message="获取分析摘要成功",
            code=200,
        )

    except Exception as e:
        logger.error(f"获取 EI 摘要失败: {e}", exc_info=True)
        return ApiResponse(
            success=False, message=f"查询失败: {str(e)}", code=500, data=None
        )


@router.get(
    "/{log_id}/player/{account}/rotation",
    response_model=ApiResponse,
    summary="获取玩家技能循环",
)
async def get_player_rotation(log_id: int, account: str, db: Session = Depends(get_db)):
    """
    获取指定玩家在指定日志中的技能循环(rotation)和技能释放次数。
    返回 EiPlayer.rotation_json + stats_all_json 中的 skill_casts + EiSkillMap 技能映射。
    """
    try:
        result = fight_svc.get_player_rotation(db, log_id, account)
        if not result:
            return ApiResponse(
                success=False,
                message="该玩家在此日志中没有技能数据",
                code=404,
                data=None,
            )

        return ApiResponse.success_response(data=result, message="获取成功", code=200)

    except Exception as e:
        logger.error(f"获取玩家技能循环失败: {e}", exc_info=True)
        return ApiResponse(
            success=False, message=f"查询失败: {str(e)}", code=500, data=None
        )


@router.get(
    "/{log_id}/player/{account}",
    response_model=ApiResponse,
    summary="获取玩家在某日志中的详细数据",
)
async def get_player_detail(log_id: int, account: str, db: Session = Depends(get_db)):
    """
    获取指定玩家在指定日志中的详细统计数据。
    """
    try:
        players = fight_svc.get_log_player_stats(db, log_id)
        player = next((p for p in players if p.get("account") == account), None)

        if not player:
            return ApiResponse(
                success=False, message="该玩家在此日志中不存在", code=404, data=None
            )

        return ApiResponse.success_response(data=player, message="获取成功", code=200)

    except Exception as e:
        logger.error(f"获取玩家详情失败: {e}", exc_info=True)
        return ApiResponse(
            success=False, message=f"查询失败: {str(e)}", code=500, data=None
        )
