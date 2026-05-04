#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据一致性检查脚本
检查 fight_stats 和 ei_player 表中 has_commander_tag 字段的一致性
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_commander_tag_consistency():
    """检查指挥官标记数据一致性"""
    engine = create_engine(settings.get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 60)
    print("检查 fight_stats 与 ei_player 的 has_commander_tag 一致性")
    print("=" * 60)
    
    # 查询不一致的记录
    query = text("""
        SELECT 
            fs.fight_id,
            fs.account,
            fs.character_name,
            fs.has_commander_tag AS fs_tag,
            ep.has_commander_tag AS ep_tag
        FROM fight_stats fs
        JOIN fights f ON fs.fight_id = f.id
        JOIN ei_player ep ON f.log_id = ep.log_id AND fs.account = ep.account
        WHERE fs.has_commander_tag != ep.has_commander_tag
        ORDER BY fs.fight_id
    """)
    
    result = session.execute(query).fetchall()
    
    if not result:
        print("✓ 所有记录的 has_commander_tag 字段一致")
        session.close()
        return True
    
    print(f"\n发现 {len(result)} 条不一致的记录:")
    print("-" * 80)
    print(f"{'战斗ID':<8} {'账户':<20} {'角色名':<20} {'fight_stats':<12} {'ei_player':<12}")
    print("-" * 80)
    
    for row in result[:10]:  # 只显示前10条
        print(f"{row[0]:<8} {row[1]:<20} {row[2]:<20} {row[3]:<12} {row[4]:<12}")
    
    if len(result) > 10:
        print(f"... 还有 {len(result) - 10} 条记录未显示")
    
    session.close()
    return False

def sync_commander_tags():
    """同步指挥官标记（以 ei_player 为准）"""
    engine = create_engine(settings.get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\n正在同步 has_commander_tag 字段...")
    
    update_query = text("""
        UPDATE fight_stats fs
        JOIN fights f ON fs.fight_id = f.id
        JOIN ei_player ep ON f.log_id = ep.log_id AND fs.account = ep.account
        SET fs.has_commander_tag = ep.has_commander_tag
        WHERE fs.has_commander_tag != ep.has_commander_tag
    """)
    
    result = session.execute(update_query)
    session.commit()
    
    print(f"已同步 {result.rowcount} 条记录")
    session.close()

if __name__ == "__main__":
    # 检查一致性
    is_consistent = check_commander_tag_consistency()
    
    if not is_consistent:
        # 询问是否同步
        response = input("\n是否同步数据？(y/n): ").strip().lower()
        if response == "y":
            sync_commander_tags()
            print("✓ 同步完成")
        else:
            print("已取消同步")