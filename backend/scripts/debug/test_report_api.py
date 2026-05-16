#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告 API 接口
对文件 20260426-220412.zevtc 进行完整解析，获取结构化数据
"""
import json
import os
import sys
import time

import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123456"
TEST_FILE_PATH = r"d:\Code\backend\tests\fixtures\20260426-220412.zevtc"
OUTPUT_JSON_PATH = r"d:\Code\backend\tests\fixtures\report_api_analysis.json"


def login(session):
    """登录获取 access token"""
    print("[1/8] 登录获取 access token...")
    login_url = f"{BASE_URL}{API_PREFIX}/auth/login"
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    }
    response = session.post(login_url, json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None
    result = response.json()
    if not result.get("success"):
        print(f"登录失败: {result.get('message')}")
        return None
    token = result.get("data", {}).get("access_token")
    print(f"  ✓ 登录成功，token 已获取")
    return token


def test_dps_report(session):
    """使用 test/dps-report 接口测试"""
    print("[2/8] 上传到 dps.report...")
    test_url = f"{BASE_URL}{API_PREFIX}/test/dps-report"
    if not os.path.exists(TEST_FILE_PATH):
        print(f"  ✗ 测试文件不存在: {TEST_FILE_PATH}")
        return None
    with open(TEST_FILE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_FILE_PATH), f, "application/octet-stream")}
        response = session.post(test_url, files=files, timeout=300)
    
    if response.status_code != 200:
        print(f"  ✗ 请求失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if not result.get("success"):
        print(f"  ✗ 上传失败: {result.get('message')}")
        return None
    
    print(f"  ✓ dps.report 解析成功")
    print(f"    permalink: {result.get('data', {}).get('permalink')}")
    print(f"    upload_time: {result.get('data', {}).get('upload_time_ms')}ms")
    print(f"    players: {result.get('data', {}).get('player_count')}")
    print(f"    targets: {result.get('data', {}).get('target_count')}")
    return result


def upload_log(session, token):
    """上传日志文件到系统"""
    print("[3/8] 上传日志到系统...")
    upload_url = f"{BASE_URL}{API_PREFIX}/logs"
    if not os.path.exists(TEST_FILE_PATH):
        print(f"  ✗ 测试文件不存在: {TEST_FILE_PATH}")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(TEST_FILE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_FILE_PATH), f, "application/octet-stream")}
        response = session.post(
            upload_url,
            files=files,
            headers=headers,
            params={"auto_parse": "false"},
            timeout=60
        )
    
    if response.status_code != 200:
        print(f"  ✗ 上传失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if not result.get("success"):
        print(f"  ✗ 上传失败: {result.get('message')}")
        return None
    
    log_data = result.get("data")
    log_id = log_data.get("id")
    print(f"  ✓ 上传成功，日志ID: {log_id}")
    print(f"    filename: {log_data.get('filename')}")
    return log_data


def parse_log(session, token, log_id):
    """解析日志"""
    print(f"[4/8] 解析日志 ID {log_id}...")
    parse_url = f"{BASE_URL}{API_PREFIX}/logs/{log_id}/parse"
    headers = {"Authorization": f"Bearer {token}"}
    response = session.post(parse_url, headers=headers, timeout=300)
    
    if response.status_code != 200:
        print(f"  ✗ 解析失败: {response.status_code} - {response.text}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"  ✗ 解析失败: {result.get('message')}")
        return False
    
    print(f"  ✓ 解析任务已提交")
    return True


def wait_for_parse(session, token, log_id):
    """等待解析完成"""
    print("[5/8] 等待解析完成...")
    max_wait = 120
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        log_url = f"{BASE_URL}{API_PREFIX}/logs/{log_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(log_url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                log_data = result.get("data")
                status = log_data.get("parse_status")
                print(f"    parse_status: {status}")
                if status == "completed":
                    print("  ✓ 解析完成")
                    return True
                elif status == "failed":
                    print("  ✗ 解析失败")
                    return False
        time.sleep(5)
    print("  ✗ 等待超时")
    return False


def get_complete_data(session, token, log_id):
    """获取完整的报告数据"""
    print("[6/8] 获取完整报告数据...")
    all_data = {
        "log_id": log_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": None,
        "players": None,
        "targets": None,
        "phases": None,
        "timeline": None,
        "skill_map": None,
        "ei_report": None,
        "fight_data": None,
        "fight_stats": None,
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取摘要
    summary_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/summary"
    print("  获取摘要...")
    try:
        response = session.get(summary_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["summary"] = result.get("data")
                print(f"    ✓ 摘要获取成功")
    except Exception as e:
        print(f"    ✗ 获取摘要失败: {e}")
    
    # 2. 获取玩家列表
    players_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/players"
    print("  获取玩家列表...")
    try:
        response = session.get(players_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["players"] = result.get("data")
                print(f"    ✓ 玩家列表获取成功: {result.get('data', {}).get('count', 0)}")
    except Exception as e:
        print(f"    ✗ 获取玩家列表失败: {e}")
    
    # 3. 获取目标列表
    targets_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/targets"
    print("  获取目标列表...")
    try:
        response = session.get(targets_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["targets"] = result.get("data")
                print(f"    ✓ 目标列表获取成功: {result.get('data', {}).get('count', 0)}")
    except Exception as e:
        print(f"    ✗ 获取目标列表失败: {e}")
    
    # 4. 获取阶段列表
    phases_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/phases"
    print("  获取阶段列表...")
    try:
        response = session.get(phases_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["phases"] = result.get("data")
                print(f"    ✓ 阶段列表获取成功: {result.get('data', {}).get('count', 0)}")
    except Exception as e:
        print(f"    ✗ 获取阶段列表失败: {e}")
    
    # 5. 获取战斗时间线
    timeline_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/timeline"
    print("  获取战斗时间线...")
    try:
        response = session.get(timeline_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["timeline"] = result.get("data")
                print(f"    ✓ 战斗时间线获取成功")
    except Exception as e:
        print(f"    ✗ 获取战斗时间线失败: {e}")
    
    # 6. 获取技能映射
    skill_map_url = f"{BASE_URL}{API_PREFIX}/wvw-report/logs/{log_id}/skill-map"
    print("  获取技能映射...")
    try:
        response = session.get(skill_map_url, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                all_data["skill_map"] = result.get("data")
                print(f"    ✓ 技能映射获取成功")
    except Exception as e:
        print(f"    ✗ 获取技能映射失败: {e}")
    
    # 7. 获取 EI 报告详细数据（从数据库）
    print("  获取 EI 详细数据...")
    all_data["ei_report"] = get_ei_report_raw_data(session, token, log_id)
    
    # 8. 获取战斗和战斗统计
    all_data["fight_data"] = get_fight_data(session, token, log_id)
    
    print("  ✓ 完整数据获取完成")
    return all_data


def get_ei_report_raw_data(session, token, log_id):
    """获取原始的 EI 报告数据（直接访问数据库）"""
    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        from app.config.database import SessionLocal
        from app.models.ei_report import EiReport
        
        # 注意：这里用 SQL 查询
        db = SessionLocal()
        reports = db.query(EiReport).filter(EiReport.log_id == log_id).first()
        result = {
            "ei_report": None
        }
        if reports:
            result["ei_report"] = {
                "id": reports.id,
                "log_id": reports.log_id,
                "version": reports.elite_insights_version,
                "player_count": reports.player_count,
                "target_count": reports.target_count,
                "parsed_at": str(reports.parsed_at),
            }
        db.close()
        print(f"    ✓ EI 元数据获取成功")
        return result
    except Exception as e:
        print(f"    ✗ 获取原始数据失败: {e}")
        return None


def get_fight_data(session, token, log_id):
    """获取战斗和战斗统计数据"""
    try:
        from app.config.database import SessionLocal
        from app.models.fight import Fight
        from app.models.fight_stats import FightStats
        
        db = SessionLocal()
        fight = db.query(Fight).filter(Fight.log_id == log_id).first()
        stats = db.query(FightStats).filter(FightStats.fight_id == fight.id).all()
        
        result = {
            "fight": None,
            "fight_stats": [],
        }
        if fight:
            result["fight"] = {
                "id": fight.id,
                "log_id": fight.log_id,
                "start_time": str(fight.start_time),
                "duration_sec": fight.duration_sec,
                "total_damage": fight.total_damage,
                "player_count": fight.player_count,
            }
            print(f"    ✓ 战斗数据获取成功")
        if stats:
            for s in stats:
                stat_data = {
                    "id": s.id,
                    "fight_id": s.fight_id,
                    "account": s.account,
                    "character_name": s.character_name,
                    "damage": s.damage,
                    "dps": s.dps,
                    "has_commander_tag": s.has_commander_tag,
                    "group_id": s.group_id,
                    "team_id": s.team_id,
                }
                result["fight_stats"].append(stat_data)
            print(f"    ✓ 战斗统计获取成功: {len(stats)}")
        
        db.close()
        return result
    except Exception as e:
        print(f"    ✗ 获取战斗数据失败: {e}")
        return None


def save_and_analyze(data):
    """保存和分析数据"""
    print("[7/8] 保存数据到 JSON 文件...")
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    
    # 保存
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 数据已保存到 {OUTPUT_JSON_PATH}")
    
    # 分析
    print("\n[8/8] 分析数据完整性...")
    analysis = {
        "total_data_size_bytes": os.path.getsize(OUTPUT_JSON_PATH),
        "summary_present": data.get("summary") is not None,
        "players_present": data.get("players") is not None,
        "targets_present": data.get("targets") is not None,
        "phases_present": data.get("phases") is not None,
        "timeline_present": data.get("timeline") is not None,
        "skill_map_present": data.get("skill_map") is not None,
        "player_count": 0,
        "target_count": 0,
        "phase_count": 0,
        "skill_count": 0,
        "commander_tags": [],
        "potential_issues": [],
    }
    
    if data.get("players"):
        analysis["player_count"] = data.get("players", {}).get("count", 0)
        players = data.get("players", {}).get("players", [])
        commanders = [p for p in players if p.get("has_commander_tag")]
        analysis["commander_tags"] = [
            {"name": c.get("name"), "account": c.get("account")} for c in commanders
        ]
    if data.get("targets"):
        analysis["target_count"] = data.get("targets", {}).get("count", 0)
    if data.get("phases"):
        analysis["phase_count"] = data.get("phases", {}).get("count", 0)
    if data.get("skill_map"):
        analysis["skill_count"] = data.get("skill_map", {}).get("count", 0)
    
    if data.get("fight_data") and data.get("fight_data").get("fight_stats"):
        analysis["fight_stat_count"] = len(data.get("fight_data", {}).get("fight_stats"))
        fight_stats = data.get("fight_data", {}).get("fight_stats", [])
        stat_commanders = [s for s in fight_stats if s.get("has_commander_tag")]
        analysis["stats_commanders"] = [
            {"name": s.get("character_name"), "account": s.get("account")} 
            for s in stat_commanders
        ]
        
        # 检查指挥官标记一致性
        if "commander_tags" in analysis and "stats_commanders" in analysis:
            commanders1 = set(c.get("account") for c in analysis["commander_tags"])
            commanders2 = set(c.get("account") for c in analysis["stats_commanders"])
            if commanders1 != commanders2:
                analysis["potential_issues"].append({
                    "type": "has_commander_tag_inconsistent",
                    "details": "fight_stats 与 players 标记的指挥官不一致",
                    "players_commanders": list(commanders1),
                    "fight_stats_commanders": list(commanders2),
                })
    
    # 保存分析结果
    analysis_path = OUTPUT_JSON_PATH.replace(".json", "_analysis.json")
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 分析结果已保存到 {analysis_path}")
    
    # 输出分析
    print("\n=== 数据完整性分析报告 ===")
    print(f"数据大小: {analysis['total_data_size_bytes']} bytes")
    print(f"摘要: {'✓ 存在' if analysis['summary_present'] else '✗ 缺失'}")
    print(f"玩家: {'✓ 存在' if analysis['players_present'] else '✗ 缺失'} ({analysis['player_count']} 人)")
    print(f"目标: {'✓ 存在' if analysis['targets_present'] else '✗ 缺失'} ({analysis['target_count']} 个)")
    print(f"阶段: {'✓ 存在' if analysis['phases_present'] else '✗ 缺失'} ({analysis['phase_count']} 个)")
    print(f"技能: {'✓ 存在' if analysis['skill_map_present'] else '✗ 缺失'} ({analysis['skill_count']} 个)")
    print(f"指挥官: {len(analysis['commander_tags'])} 人")
    print(f"潜在问题: {len(analysis['potential_issues'])} 个")
    
    if analysis['potential_issues']:
        print("\n⚠️ 发现的问题:")
        for issue in analysis['potential_issues']:
            print(f"  - {issue['type']}: {issue['details']}")
    
    return analysis


def main():
    print("=" * 60)
    print("开始 GW2 WvW 报告 API 完整测试")
    print("=" * 60)
    
    # 会话
    session = requests.Session()
    
    # 1. 登录
    token = login(session)
    if not token:
        return 1
    
    # 2. 测试 dps.report
    dps_report_result = test_dps_report(session)
    
    # 3. 上传文件
    log_data = upload_log(session, token)
    if not log_data:
        return 1
    log_id = log_data.get("id")
    
    # 4. 解析
    if parse_log(session, token, log_id):
        wait_for_parse(session, token, log_id)
    
    # 5. 获取完整数据
    all_data = get_complete_data(session, token, log_id)
    
    # 6. 保存和分析
    analysis = save_and_analyze(all_data)
    
    print("\n" + "=" * 60)
    print("✓ 测试完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
