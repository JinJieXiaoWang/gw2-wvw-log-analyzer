# -*- coding: utf-8 -*-
# 模块功能：出勤数据导出服务
# 作者：系统
# 创建日期：2026-05-12
# 依赖说明：pandas, openpyxl

import csv
from io import BytesIO, StringIO

import pandas as pd
from fastapi.responses import StreamingResponse

from app.utils.logger import logger


async def export_account_detail(
    detail_data: dict,
    account_name: str,
    export_format: str = "csv",
) -> StreamingResponse:
    """导出账号出勤详情Excel 或 CSV 格式

    Args:
        detail_data: 账号详情数据
        account_name: 账号名称
        export_format: 导出格式，csv ?excel

    Returns:
        StreamingResponse: 文件流响应
    """
    if export_format.lower() == "excel":
        return _export_excel(detail_data, account_name)
    else:
        return _export_csv(detail_data, account_name)


def _export_excel(detail_data: dict, account_name: str) -> StreamingResponse:
    """导出账号出勤详情Excel 格式"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")

    summary_df = pd.DataFrame([{
        "账号": detail_data.get("summary", {}).get("account_name", ""),
        "出勤天数": detail_data.get("summary", {}).get("attendance_count", 0),
        "参战次数": detail_data.get("summary", {}).get("fight_count", 0),
        "总时长": detail_data.get("summary", {}).get("total_duration_sec", 0),
        "总伤害": detail_data.get("summary", {}).get("total_damage", 0),
        "平均评分": detail_data.get("summary", {}).get("avg_score", 0),
    }])
    summary_df.to_excel(writer, sheet_name="摘要", index=False)

    characters = detail_data.get("characters", [])
    if characters:
        chars_df = pd.DataFrame(characters)
        chars_df.to_excel(writer, sheet_name="角色列表", index=False)

    recent_fights = detail_data.get("recent_fights", [])
    if recent_fights:
        fights_df = pd.DataFrame(recent_fights)
        fights_df.to_excel(writer, sheet_name="最近战斗记录", index=False)

    writer.close()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{account_name}_attendance_detail.xlsx"'
        },
    )


def _export_csv(detail_data: dict, account_name: str) -> StreamingResponse:
    """导出账号出勤详情CSV 格式"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["字段", "值"])
    writer.writerow(["账号", detail_data.get("summary", {}).get("account_name", "")])
    writer.writerow(["出勤天数", detail_data.get("summary", {}).get("attendance_count", 0)])
    writer.writerow(["参战次数", detail_data.get("summary", {}).get("fight_count", 0)])
    writer.writerow(["总时长", detail_data.get("summary", {}).get("total_duration_sec", 0)])
    writer.writerow(["总伤害", detail_data.get("summary", {}).get("total_damage", 0)])
    writer.writerow(["平均评分", detail_data.get("summary", {}).get("avg_score", 0)])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{account_name}_attendance_detail.csv"'
        },
    )
