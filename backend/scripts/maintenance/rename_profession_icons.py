# -*- coding: utf-8 -*-
# 模块功能：重命名职业图标文件为英?# 作者：System
# 创建日期?2026-05-11
# 依赖说明：os, shutil

import os
import shutil
from pathlib import Path


def main():
    # 图片文件路径
    prof_dir = Path(r"d:\Code\Gw2-wvw-log-analyzer\frontend\src\assets\images\prof")
    
    if not prof_dir.exists():
        print(f"目录不存? {prof_dir}")
        return
    
    # 中文到英文的映射
    mapping = {
        "守护?png": "Guardian.png",
        "猎龙?png": "Dragonhunter.png",
        "燃火?png": "Firebrand.png",
        "破锋?png": "Willbender.png",
        "圣辉?png": "Luminary.png",
        "战士.png": "Warrior.png",
        "狂战?png": "Berserker.png",
        "破法?png": "Spellbreaker.png",
        "誓剑?png": "Bladesworn.png",
        "圣言?png": "Paragon.png",
        "工程?png": "Engineer.png",
        "机械?png": "Scrapper.png",
        "全息?png": "Holosmith.png",
        "玉偃?png": "Mechanist.png",
        "流金?png": "Amalgam.png",
        "游侠.png": "Ranger.png",
        "德鲁?png": "Druid.png",
        "魂兽?png": "Soulbeast.png",
        "狂兽?png": "Untamed.png",
        "风羽?png": "Galeshot.png",
        "潜行?png": "Thief.png",
        "独行?png": "Daredevil.png",
        "神枪?png": "Deadeye.png",
        "缚影?png": "Specter.png",
        "彩戏?png": "Antiquary.png",
        "元素?png": "Elementalist.png",
        "暴风?png": "Tempest.png",
        "编织?png": "Weaver.png",
        "元晶?png": "Catalyst.png",
        "唤元?png": "Evoker.png",
        "幻术?png": "Mesmer.png",
        "时空术士.png": "Chronomancer.png",
        "幻象术士.png": "Mirage.png",
        "灵刃术士.png": "Virtuoso.png",
        "吟游诗人.png": "Troubadour.png",
        "唤灵?png": "Necromancer.png",
        "夺魂?png": "Reaper.png",
        "灾厄?png": "Scourge.png",
        "先驱?png": "Harbinger.png",
        "祭祀?png": "Ritualist.png",
        "魂武?png": "Revenant.png",
        "预告?png": "Herald.png",
        "龙魂?png": "Renegade.png",
        "裁决?png": "Vindicator.png",
        "契灵?png": "Conduit.png"
    }
    
    print(f"开始重命名 {prof_dir} 目录下的图片文件...\n")
    
    renamed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(prof_dir):
        if filename in mapping:
            old_path = prof_dir / filename
            new_path = prof_dir / mapping[filename]
            
            # 如果新文件已存在，备份或跳过
            if new_path.exists():
                print(f"跳过: {filename} -> {mapping[filename]} (目标文件已存?")
                skipped_count += 1
                continue
            
            shutil.move(old_path, new_path)
            print(f"重命? {filename} -> {mapping[filename]}")
            renamed_count += 1
        else:
            print(f"跳过: {filename} (未在映射表中)")
            skipped_count += 1
    
    print(f"\n重命名完成 共重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文?)


if __name__ == "__main__":
    main()
