# -*- coding: utf-8 -*-
"""完整模拟数据提取和写入流程，定位问题"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib

from app.config.database import SessionLocal
from app.core.zevtc.parser import EnhancedZevtcParser
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.log import Log


def get_file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def simulate_data_flow():
    filepath = "tests/20260503-222921.zevtc"
    file_hash = get_file_hash(filepath)

    # 1. 解析源文件
    parser = EnhancedZevtcParser(filepath)
    ei_json = parser.parse()

    print("=" * 80)
    print("步骤1: 数据提取（模拟 _extract_player_stats）")
    print("=" * 80)

    duration_sec = max(1, int(parser.meta.duration_ms / 1000))

    # 建立映射
    ei_players_by_account = {}
    for p in ei_json.get("players", []):
        ei_players_by_account[p.get("account", "")] = p

    # 模拟提取
    extracted_players = []
    for addr, pstats in parser.player_stats.items():
        ei_p = ei_players_by_account.get(pstats.account, {})
        dps_all = ei_p.get("dpsAll", [{}])[0] if ei_p.get("dpsAll") else {}
        stats_all = ei_p.get("statsAll", [{}])[0] if ei_p.get("statsAll") else {}
        defenses = ei_p.get("defenses", [{}])[0] if ei_p.get("defenses") else {}

        # 关键：检查数据来源
        if dps_all and dps_all.get("damage"):
            dmg = dps_all.get("damage", 0)
            dps = dps_all.get("dps", 0)
            power_dmg = dps_all.get("powerDamage", 0)
            condi_dmg = dps_all.get("condiDamage", 0)
            data_source = "EI_JSON"
        else:
            dmg = pstats.total_damage
            dps = int(dmg / duration_sec) if duration_sec > 0 else 0
            power_dmg = pstats.power_damage
            condi_dmg = pstats.condi_damage
            data_source = "PARSER_FALLBACK"

        extracted_players.append(
            {
                "account": pstats.account,
                "character_name": pstats.name,
                "profession": pstats.profession,
                "damage": dmg,
                "dps": dps,
                "power_damage": power_dmg,
                "condi_damage": condi_dmg,
                "data_source": data_source,
            }
        )

    # 打印提取的数据
    target = "Doubface.5319"
    for p in extracted_players:
        if p["account"] == target:
            print(f"提取的数据 (Doubface.5319):")
            print(f"  data_source: {p['data_source']}")
            print(f"  damage: {p['damage']:,}")
            print(f"  dps: {p['dps']:,}")
            print(f"  power_damage: {p['power_damage']:,}")
            print(f"  condi_damage: {p['condi_damage']:,}")
            break

    print()

    # 2. 查询数据库
    print("=" * 80)
    print("步骤2: 查询数据库")
    print("=" * 80)

    db = SessionLocal()
    try:
        log = db.query(Log).filter(Log.file_sha256 == file_hash).first()
        if not log:
            print("数据库中未找到对应记录！")
            return

        fight = db.query(Fight).filter(Fight.log_id == log.id).first()
        if not fight:
            print("该日志尚未解析！")
            return

        stats = db.query(FightStats).filter(FightStats.fight_id == fight.id).all()

        for s in stats:
            if s.account == target:
                print(f"数据库存储的数据 (Doubface.5319):")
                print(f"  damage: {s.damage:,}")
                print(f"  dps: {s.dps:,}")
                print(f"  power_damage: {s.power_damage:,}")
                print(f"  condi_damage: {s.condi_damage:,}")
                break

    finally:
        db.close()

    print()
    print("=" * 80)
    print("步骤3: 对比分析")
    print("=" * 80)

    # 从上面的输出可以对比

    print("如果提取的数据 != 数据库存储的数据，说明问题在写入过程中")


if __name__ == "__main__":
    simulate_data_flow()
