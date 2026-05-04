# 模块功能：游戏数据管理
# 作者：系统
# 创建日期：2026-04-27
# 依赖说明：json, pathlib

import json
from pathlib import Path
from typing import Any, Dict, Optional

# 获取数据目录
DATA_DIR = Path(__file__).parent


def load_json_file(filename: str) -> Dict[str, Any]:
    # 功能：加载JSON数据文件
    # 参数：filename - 文件名
    # 返回：解析后的字典数据
    # 异常：FileNotFoundError, json.JSONDecodeError
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {filename}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_data_version() -> Dict[str, Any]:
    # 功能：获取数据版本信息
    # 参数：无
    # 返回：版本信息字典
    try:
        return load_json_file("version.json")
    except FileNotFoundError:
        return {
            "version": "1.0.0",
            "last_updated": "2026-04-27",
            "description": "GW2游戏数据",
        }
