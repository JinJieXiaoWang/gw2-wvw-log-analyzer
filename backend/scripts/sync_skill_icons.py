# -*- coding: utf-8 -*-
"""技能图标同步脚本

从 bdcode_skills.json 读取所有技能的 GW2 CDN icon URL，
检查 frontend/src/assets/images/skills/ 中是否已有对应 PNG，
缺失的通过 HTTP 增量下载。

用法:
    cd backend
    python scripts/sync_skill_icons.py
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# 项目根目录（backend 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_JSON = PROJECT_ROOT / "backend" / "app" / "data" / "bdcode_skills.json"
SKILLS_DIR = PROJECT_ROOT / "frontend" / "src" / "assets" / "images" / "skills"
CONCURRENT_LIMIT = 10
MIN_FILE_SIZE = 100  # bytes


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符（Windows 限制）。"""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip(" .")
    return name


def download_icon(name: str, url: str, dest: Path) -> dict:
    """下载单个图标，返回结果字典。"""
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 404:
            return {"name": name, "status": "not_found", "url": url}
        if resp.status_code != 200:
            return {
                "name": name,
                "status": f"http_{resp.status_code}",
                "url": url,
            }
        data = resp.content
        if len(data) < MIN_FILE_SIZE:
            return {
                "name": name,
                "status": "too_small",
                "url": url,
                "size": len(data),
            }
        dest.write_bytes(data)
        return {"name": name, "status": "success", "size": len(data)}
    except Exception as e:
        return {"name": name, "status": "error", "url": url, "error": str(e)}


def sync_skill_icons():
    """主同步逻辑。"""
    if not SKILLS_JSON.exists():
        print(f"[ERROR] 技能数据文件不存在: {SKILLS_JSON}")
        sys.exit(1)

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    with open(SKILLS_JSON, "r", encoding="utf-8") as f:
        skills = json.load(f)

    print(f"[INFO] bdcode_skills.json 共 {len(skills)} 个技能")

    # 收集缺失的图标
    pending = []
    skipped = 0
    for sk in skills:
        name = sk.get("name", "")
        icon_url = sk.get("icon", "")
        if not name or not icon_url:
            skipped += 1
            continue

        safe_name = sanitize_filename(name)
        dest = SKILLS_DIR / f"{safe_name}.png"

        if dest.exists() and dest.stat().st_size >= MIN_FILE_SIZE:
            skipped += 1
            continue

        pending.append((name, icon_url, dest))

    print(f"[INFO] 需要下载 {len(pending)} 个图标，已有/跳过 {skipped} 个")

    results = {"success": 0, "not_found": 0, "http_error": 0, "too_small": 0, "error": 0}

    if pending:
        with ThreadPoolExecutor(max_workers=CONCURRENT_LIMIT) as executor:
            future_map = {
                executor.submit(download_icon, name, url, dest): name
                for name, url, dest in pending
            }
            for future in as_completed(future_map):
                r = future.result()
                status = r["status"]
                if status == "success":
                    results["success"] += 1
                elif status == "not_found":
                    results["not_found"] += 1
                elif status.startswith("http_"):
                    results["http_error"] += 1
                elif status == "too_small":
                    results["too_small"] += 1
                else:
                    results["error"] += 1
                    print(f"[ERROR] {r['name']}: {r.get('error', status)}")

    # 输出报告
    print("\n========== 同步报告 ==========")
    print(f"  成功下载:   {results['success']}")
    print(f"  已有/跳过:  {skipped}")
    print(f"  404 缺失:   {results['not_found']}")
    print(f"  HTTP 错误:  {results['http_error']}")
    print(f"  文件过小:   {results['too_small']}")
    print(f"  异常失败:   {results['error']}")
    print("==============================")


if __name__ == "__main__":
    sync_skill_icons()
