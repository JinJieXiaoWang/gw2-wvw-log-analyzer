#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接解析 ZEVTC 文件并生成完整的结构化数据报告
对文件 20260426-220412.zevtc 进行完整解析
"""
import json
import os
import sys
import time
from datetime import datetime

# 设置 stdout 编码为 UTF-8
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.zevtc.parser import EnhancedZevtcParser


def parse_zevtc_direct(file_path):
    """直接使用 ZEVTC 解析器解析文件"""
    print("[1/5] 开始解析文件...")
    print(f"  文件: {file_path}")
    
    try:
        parser = EnhancedZevtcParser(file_path)
        result = parser.parse()
        print("  [OK] 文件解析成功")
        print(f"    玩家数: {len(parser.player_stats)}")
        if parser.meta:
            print(f"    战斗时长: {parser.meta.duration_s} 秒")
    except Exception as e:
        print(f"  [ERROR] 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return parser


def extract_structured_data(parser):
    """从解析结果中提取结构化数据"""
    print("\n[2/5] 提取结构化数据...")
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "file_name": os.path.basename(parser.path),
        "meta": {},
        "players": [],
        "commander_tags": [],
        "groups": {},
    }
    
    if parser.meta:
        data["meta"] = {
            "start_time": parser.meta.start_datetime,
            "end_time": parser.meta.end_datetime,
            "duration_sec": parser.meta.duration_s,
            "duration_ms": parser.meta.duration_ms,
            "map_id": parser.meta.map_id,
            "map_name": parser.meta.map_name if hasattr(parser.meta, 'map_name') else "",
            "total_damage": parser.meta.total_damage if hasattr(parser.meta, 'total_damage') else 0,
            "total_kills": parser.meta.total_kills if hasattr(parser.meta, 'total_kills') else 0,
            "total_deaths": parser.meta.total_deaths if hasattr(parser.meta, 'total_deaths') else 0,
        }
    
    for addr, player in parser.player_stats.items():
        player_data = {
            "address": addr,
            "account": player.account,
            "name": player.name,
            "profession": player.profession,
            "specialization": player.specialization if hasattr(player, 'specialization') else "",
            "group": player.group,
            "has_commander_tag": player.has_commander_tag,
            "total_damage": player.total_damage,
            "power_damage": player.power_damage,
            "condition_damage": player.condi_damage,
            "breakbar_damage": player.breakbar_damage,
            "dps": player.dps if hasattr(player, 'dps') else 0,
            "downs_inflicted": player.downs_inflicted,
            "kills_inflicted": player.kills_inflicted,
            "own_downs": player.own_downs,
            "own_deaths": player.own_deaths,
            "boon_strips": player.boon_strips,
            "condition_cleanses": player.condi_cleanses,
        }
        
        if player.has_commander_tag:
            data["commander_tags"].append({
                "account": player.account,
                "name": player.name,
                "group": player.group,
            })
        
        if player.group not in data["groups"]:
            data["groups"][player.group] = []
        data["groups"][player.group].append(player.account)
        
        data["players"].append(player_data)
    
    print("  [OK] 提取完成")
    print(f"    玩家数: {len(data['players'])}")
    print(f"    指挥官数: {len(data['commander_tags'])}")
    
    return data


def build_ei_json(parser):
    """构建类似 EI 的 JSON 输出"""
    print("\n[3/5] 构建 EI 格式数据...")
    
    ei_json = {
        "eliteInsightsVersion": "GW2WvWLogSystem 1.0",
        "recordedBy": parser.meta.recorded_by if hasattr(parser.meta, 'recorded_by') else "",
        "recordedAccount": parser.meta.recorded_account if hasattr(parser.meta, 'recorded_account') else "",
        "startTime": parser.meta.start_datetime if parser.meta else "",
        "endTime": parser.meta.end_datetime if parser.meta else "",
        "duration": parser.meta.duration_ms if parser.meta else 0,
        "durationSeconds": parser.meta.duration_s if parser.meta else 0,
        "mapId": parser.meta.map_id if parser.meta else 0,
        "mapName": parser.meta.map_name if hasattr(parser.meta, 'map_name') else "",
        "players": [],
        "targets": [],
        "skillMap": {},
        "phases": [],
    }
    
    # 构建玩家数据
    for addr, player in parser.player_stats.items():
        ei_player = {
            "name": player.name,
            "account": player.account,
            "profession": player.profession,
            "group": player.group,
            "hasCommanderTag": player.has_commander_tag,
            "totalDamage": player.total_damage,
            "powerDamage": player.power_damage,
            "conditionDamage": player.condi_damage,
            "breakbarDamage": player.breakbar_damage,
            "dps": player.dps if hasattr(player, 'dps') else 0,
            "kills": player.kills_inflicted,
            "downs": player.downs_inflicted,
            "ownKills": player.own_deaths,
            "ownDowns": player.own_downs,
        }
        ei_json["players"].append(ei_player)
    
    # 阶段数据
    if parser.meta:
        ei_json["phases"] = [
            {"phaseIndex": 0, "name": "Full Fight", "startTime": 0, "endTime": parser.meta.duration_ms}
        ]
    
    print("  [OK] EI 格式数据构建完成")
    
    return ei_json


def generate_comprehensive_report(parser, output_dir):
    """生成完整的报告"""
    print("\n[4/5] 生成完整报告...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 基本结构化数据
    structured_data = extract_structured_data(parser)
    structured_path = os.path.join(output_dir, "structured_data.json")
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 结构化数据已保存: {structured_path}")
    
    # EI 格式数据
    ei_json = build_ei_json(parser)
    ei_path = os.path.join(output_dir, "ei_format.json")
    with open(ei_path, "w", encoding="utf-8") as f:
        json.dump(ei_json, f, ensure_ascii=False, indent=2)
    print(f"  [OK] EI 格式数据已保存: {ei_path}")
    
    # 指挥官详细分析
    commander_analysis = analyze_commanders(structured_data)
    commander_path = os.path.join(output_dir, "commander_analysis.json")
    with open(commander_path, "w", encoding="utf-8") as f:
        json.dump(commander_analysis, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 指挥官分析已保存: {commander_path}")
    
    # 统计摘要
    summary = generate_summary_report(structured_data)
    summary_path = os.path.join(output_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"  [OK] 摘要已保存: {summary_path}")
    
    print("\n" + "=" * 60)
    print("[OK] 完整报告生成完成！")
    print("=" * 60)
    print(f"\n报告目录: {output_dir}")
    
    return {
        "structured_data": structured_data,
        "ei_json": ei_json,
        "commander_analysis": commander_analysis,
        "summary": summary,
    }


def analyze_commanders(structured_data):
    """分析指挥官相关的数据"""
    analysis = {
        "total_commanders": len(structured_data["commander_tags"]),
        "commanders": structured_data["commander_tags"],
        "group_distribution": {},
        "commander_performance": [],
    }
    
    for commander in structured_data["commander_tags"]:
        # 找出该指挥官的详细统计
        player_data = None
        for p in structured_data["players"]:
            if p["account"] == commander["account"]:
                player_data = p
                break
        
        if player_data:
            analysis["commander_performance"].append({
                "account": player_data["account"],
                "name": player_data["name"],
                "profession": player_data["profession"],
                "group": player_data["group"],
                "damage": player_data["total_damage"],
                "dps": player_data["dps"],
                "kills": player_data["kills_inflicted"],
                "downs": player_data["downs_inflicted"],
            })
        
        if commander["group"] not in analysis["group_distribution"]:
            analysis["group_distribution"][commander["group"]] = 0
        analysis["group_distribution"][commander["group"]] += 1
    
    return analysis


def generate_summary_report(structured_data):
    """生成文本摘要报告"""
    summary = []
    summary.append("=" * 60)
    summary.append("GW2 WvW 战斗报告摘要")
    summary.append("=" * 60)
    summary.append("")
    summary.append(f"战斗时间: {structured_data['meta']['start_time']} - {structured_data['meta']['end_time']}")
    summary.append(f"战斗时长: {structured_data['meta']['duration_sec']} 秒")
    summary.append(f"地图: {structured_data['meta']['map_name']}")
    summary.append("")
    summary.append(f"玩家总数: {len(structured_data['players'])}")
    summary.append(f"指挥官总数: {len(structured_data['commander_tags'])}")
    summary.append(f"团队数: {len(structured_data['groups'])}")
    summary.append("")
    summary.append("-" * 60)
    summary.append("指挥官列表:")
    summary.append("-" * 60)
    for comm in structured_data["commander_tags"]:
        summary.append(f"  - {comm['name']} ({comm['account']}) - 团队 {comm['group']}")
    
    summary.append("")
    summary.append("-" * 60)
    summary.append("团队分布:")
    summary.append("-" * 60)
    for group_num, players in sorted(structured_data["groups"].items()):
        summary.append(f"  团队 {group_num}: {len(players)} 人")
    
    summary.append("")
    summary.append("-" * 60)
    summary.append("伤害排行 Top 10:")
    summary.append("-" * 60)
    
    sorted_players = sorted(
        structured_data["players"],
        key=lambda x: x["total_damage"],
        reverse=True
    )
    for i, player in enumerate(sorted_players[:10], 1):
        summary.append(f"  {i}. {player['name']} - {player['total_damage']:,} 伤害 ({player['dps']} DPS)")
    
    return "\n".join(summary)


def main():
    test_file = r"d:\Code\backend\tests\fixtures\20260426-220412.zevtc"
    output_dir = r"d:\Code\backend\tests\fixtures\20260426-220412_report"
    
    print("=" * 60)
    print("GW2 WvW 战斗日志完整解析")
    print("=" * 60)
    print(f"文件: {test_file}")
    
    # 1. 解析
    parser = parse_zevtc_direct(test_file)
    if not parser:
        return 1
    
    # 2. 生成报告
    reports = generate_comprehensive_report(parser, output_dir)
    
    # 3. 打印一些关键信息
    print("\n=== 指挥官分析 ===")
    if reports["commander_analysis"]["commanders"]:
        print(f"指挥官数量: {reports['commander_analysis']['total_commanders']}")
        for comm in reports["commander_analysis"]["commanders"]:
            print(f"  - {comm['name']} ({comm['account']})")
    else:
        print("未发现指挥官标记")
    
    print("\n=== ժҪ ===")
    print(reports["summary"])
    
    return 0


if __name__ == "__main__":
    exit(main())
