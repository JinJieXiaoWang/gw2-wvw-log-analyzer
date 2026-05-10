# -*- coding: utf-8 -*-
"""直接测试数据提取和写入流程"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib

from app.config.database import SessionLocal, get_db
from app.core.zevtc.parser import EnhancedZevtcParser
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.log import Log
from app.models.member import Member
from app.services.zevtc.log_import_service import LogImportService


def get_file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def test_data_flow():
    filepath = "tests/20260503-222921.zevtc"
    file_hash = get_file_hash(filepath)

    db = SessionLocal()

    try:
        # 1. 检查日志是否已存在
        log = db.query(Log).filter(Log.file_sha256 == file_hash).first()

        if log:
            print(f"日志已存在: log_id={log.id}")
            print(f"parse_status: {log.parse_status}")
            print(f"dps_report_permalink: {log.dps_report_permalink}")
            print()

            # 删除旧数据，重新导入
            print("删除旧数据，准备重新导入...")
            fight = db.query(Fight).filter(Fight.log_id == log.id).first()
            if fight:
                db.query(FightStats).filter(FightStats.fight_id == fight.id).delete()
                db.delete(fight)
            db.commit()
            print()

        # 2. 创建新的 LogImportService 并导入
        print("=" * 80)
        print("开始新的导入流程")
        print("=" * 80)
        print()

        importer = LogImportService(db)

        # 3. 模拟解析流程，添加详细日志
        from app.core.zevtc.parser import EnhancedZevtcParser

        parser = EnhancedZevtcParser(filepath)
        ei_json = parser.parse()

        print("步骤1: 解析本地文件")
        print(f"  玩家数量: {len(ei_json.get('players', []))}")
        print()

        # 4. 检查 dps.report API
        print("步骤2: 检查 dps.report API")
        from app.services.system.dps_report_service import upload_and_parse

        try:
            dps_result = upload_and_parse(filepath)
            if dps_result and dps_result.get("ei_json"):
                print(f"  DPS Report 解析成功!")
                print(f"  Permalink: {dps_result.get('permalink')}")
                ei_json = dps_result["ei_json"]  # 使用 dps.report 的数据
            else:
                print(f"  DPS Report 解析失败，使用本地数据")
        except Exception as e:
            print(f"  DPS Report API 异常: {e}")
            print(f"  使用本地数据")
        print()

        # 5. 提取数据
        print("步骤3: 提取玩家数据")
        player_stats = importer._extract_player_stats(parser, ei_json)

        target = "Doubface.5319"
        for p in player_stats:
            if p["account"] == target:
                print(f"  目标玩家 {target}:")
                print(f"    damage: {p['damage']:,}")
                print(f"    dps: {p['dps']:,}")
                print(f"    power_damage: {p['power_damage']:,}")
                print(f"    condi_damage: {p['condi_damage']:,}")
                break
        print()

        # 6. 检查 EI JSON 中的数据
        print("步骤4: 检查 EI JSON 中的数据")
        for p in ei_json.get("players", []):
            if p.get("account") == target:
                dps_all = p.get("dpsAll", [{}])[0]
                print(f"  EI JSON 中 {target}:")
                print(f"    damage: {dps_all.get('damage', 0):,}")
                print(f"    dps: {dps_all.get('dps', 0):,}")
                print(f"    powerDamage: {dps_all.get('powerDamage', 0):,}")
                print(f"    condiDamage: {dps_all.get('condiDamage', 0):,}")
                break
        print()

        # 7. 写入数据库
        print("步骤5: 写入数据库")

        # 获取日志
        log = db.query(Log).filter(Log.file_sha256 == file_hash).first()
        log_id = log.id
        file_path = log.file_path

        # 插入 fight
        fight_data = importer._extract_fight_data(parser, ei_json)
        fight = importer._insert_fight(log_id, fight_data)
        print(f"  插入 fight: fight_id={fight.id}")

        # 插入 players
        importer._insert_players(fight.id, player_stats)
        print(f"  插入 player_stats: {len(player_stats)} 条记录")

        db.commit()
        print()

        # 8. 验证数据库
        print("步骤6: 验证数据库")
        stats = db.query(FightStats).filter(FightStats.fight_id == fight.id).all()

        for s in stats:
            if s.account == target:
                print(f"  数据库中 {target}:")
                print(f"    damage: {s.damage:,}")
                print(f"    dps: {s.dps:,}")
                print(f"    power_damage: {s.power_damage:,}")
                print(f"    condi_damage: {s.condi_damage:,}")
                break

    finally:
        db.close()


if __name__ == "__main__":
    test_data_flow()
