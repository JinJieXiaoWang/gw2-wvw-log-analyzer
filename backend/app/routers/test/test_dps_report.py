# -*- coding: utf-8 -*-
"""
dps.report API 测试接口
用于验证 EI 解析能力和响应速度
"""

import time
from typing import Optional

import orjson
import requests
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import get_settings
from app.schemas.auth.common import ApiResponse
from app.utils.logger import logger

router = APIRouter(prefix="/test", tags=["测试工具"])
settings = get_settings()


class DpsReportTestResponse(BaseModel):
    permalink: str
    upload_time_ms: int
    parse_time_ms: int
    json_fetch_time_ms: int
    total_time_ms: int
    ei_version: Optional[str] = None
    player_count: int = 0
    target_count: int = 0
    skill_map_count: int = 0
    has_rotation: bool = False
    has_weapons: bool = False
    has_death_recap: bool = False
    sample_rotation_length: int = 0
    sample_weapons: list = []
    sample_death_recap: list = []
    raw_json: Optional[dict] = None


@router.post("/dps-report", response_model=ApiResponse, summary="测试 dps.report 解析")
async def test_dps_report(file: UploadFile = File(...)):
    """
    上传 zevtc 文件?dps.report，测?EI 解析速度和数据完整性?
    返回关键字段：rotation、weapons、deathRecap、skillMap 等?
    """
    total_start = time.time()

    if not file.filename or not file.filename.endswith(
        (".zevtc", ".evtc", ".evtc.zip")
    ):
        return ApiResponse(
            success=False,
            message="仅支?.zevtc / .evtc / .evtc.zip 文件",
            code=400,
            data=None,
        )

    try:
        content = await file.read()
        logger.info(
            f"[dps.report测试] 文件大小: {len(content)} bytes, 文件? {file.filename}"
        )

        # Step 1: 上传?dps.report
        upload_start = time.time()
        files = {"file": (file.filename, content, "application/octet-stream")}
        upload_resp = requests.post(
            f"{settings.DPS_REPORT_UPLOAD_URL}?json=1&generator=ei&detailedwvw=true",
            files=files,
            timeout=300,  # dps.report 可能排队很久
        )
        upload_time_ms = int((time.time() - upload_start) * 1000)

        if upload_resp.status_code != 200:
            logger.error(
                f"[dps.report测试] 上传失败: {upload_resp.status_code} - {upload_resp.text[:500]}"
            )
            return ApiResponse(
                success=False,
                message=f"dps.report 上传失败: HTTP {upload_resp.status_code}",
                code=502,
                data=None,
            )

        upload_data = orjson.loads(upload_resp.content)
        if upload_data.get("error"):
            logger.error(f"[dps.report测试] 解析错误: {upload_data['error']}")
            return ApiResponse(
                success=False,
                message=f"dps.report 返回错误: {upload_data['error']}",
                code=502,
                data=None,
            )

        permalink = upload_data.get("permalink")
        report_id = upload_data.get("id")
        logger.info(f"[dps.report测试] 上传成功: {permalink}, 耗时 {upload_time_ms}ms")

        # Step 2: 获取完整 EI JSON
        json_start = time.time()
        json_resp = requests.get(
            f"{settings.DPS_REPORT_JSON_URL}?permalink={permalink}",
            timeout=60,
        )
        json_fetch_time_ms = int((time.time() - json_start) * 1000)

        if json_resp.status_code != 200:
            logger.error(f"[dps.report测试] JSON获取失败: {json_resp.status_code}")
            return ApiResponse(
                success=False,
                message=f"dps.report JSON 获取失败: HTTP {json_resp.status_code}",
                code=502,
                data=None,
            )

        ei_json = orjson.loads(json_resp.content)
        parse_time_ms = upload_data.get("encounter", {}).get("duration", 0) * 1000

        # Step 3: 提取关键字段
        players = ei_json.get("players", [])
        targets = ei_json.get("targets", [])
        skill_map = ei_json.get("skillMap", {})

        sample_rotation = []
        sample_weapons = []
        sample_death_recap = []

        for p in players[:3]:
            rotation = p.get("rotation", [])
            if rotation and not sample_rotation:
                sample_rotation = (
                    rotation[:3] if isinstance(rotation[0], list) else rotation[:3]
                )
            weapons = p.get("weapons", [])
            if weapons and not sample_weapons:
                sample_weapons = weapons[:4]
            death_recap = p.get("deathRecap", [])
            if death_recap and not sample_death_recap:
                sample_death_recap = death_recap[:1]

        total_time_ms = int((time.time() - total_start) * 1000)

        result = DpsReportTestResponse(
            permalink=permalink,
            upload_time_ms=upload_time_ms,
            parse_time_ms=parse_time_ms,
            json_fetch_time_ms=json_fetch_time_ms,
            total_time_ms=total_time_ms,
            ei_version=ei_json.get("eliteInsightsVersion"),
            player_count=len(players),
            target_count=len(targets),
            skill_map_count=len(skill_map),
            has_rotation=any(p.get("rotation") for p in players),
            has_weapons=any(p.get("weapons") for p in players),
            has_death_recap=any(p.get("deathRecap") for p in players),
            sample_rotation_length=len(sample_rotation),
            sample_weapons=sample_weapons,
            sample_death_recap=sample_death_recap,
            raw_json=(
                {
                    "first_player_name": players[0].get("name") if players else None,
                    "first_player_profession": (
                        players[0].get("profession") if players else None
                    ),
                    "first_player_rotation_preview": sample_rotation,
                    "first_player_weapons_preview": sample_weapons,
                    "first_player_death_recap_preview": sample_death_recap,
                    "skill_map_keys": list(skill_map.keys())[:10],
                }
                if players
                else {}
            ),
        )

        logger.info(
            f"[dps.report测试] 完成: total={total_time_ms}ms, "
            f"upload={upload_time_ms}ms, json={json_fetch_time_ms}ms, "
            f"players={len(players)}, targets={len(targets)}, skills={len(skill_map)}, "
            f"has_rotation={result.has_rotation}, has_weapons={result.has_weapons}"
        )

        return ApiResponse.success_response(
            data=result.model_dump(), message="dps.report 解析成功"
        )

    except requests.exceptions.Timeout:
        logger.error("[dps.report测试] 请求超时")
        return ApiResponse(
            success=False,
            message="dps.report 请求超时（可能排队中?,
            code=504,
            data=None,
        )
    except Exception as e:
        logger.error(f"[dps.report测试] 异常: {e}", exc_info=True)
        return ApiResponse(
            success=False, message=f"内部错误: {str(e)}", code=500, data=None
        )
