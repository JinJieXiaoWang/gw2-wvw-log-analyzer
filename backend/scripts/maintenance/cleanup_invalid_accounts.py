# -*- coding: utf-8 -*-
# 模块功能：清理数据库中无效账号数据的脚本
# 作者：系统
# 创建日期：2026-05-06
# 说明：
#   1. 识别并清理 member、account_character、fight_stats 表中的无效账号数据
#   2. 无效账号包括：空账号、黑名单账号、格式不符合规则的账号
#   3. 执行前会显示预估删除数量，用户确认后才执行
#   4. 建议先备份数据库再执行

import os
import sys
import re
from typing import List, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.zevtc.constants import (
    INVALID_ACCOUNT_PATTERNS,
    ACCOUNT_NAME_MIN_LENGTH,
    ACCOUNT_NAME_MAX_LENGTH,
    ACCOUNT_NAME_REGEX,
)

# 预编译正则表达式
INVALID_ACCOUNT_REGEXES = [re.compile(pattern, re.IGNORECASE) for pattern in INVALID_ACCOUNT_PATTERNS]
ACCOUNT_NAME_REGEX_OBJ = re.compile(ACCOUNT_NAME_REGEX)


def is_valid_account_name(account_name: str) -> bool:
    """验证账号名称是否有效。"""
    if not account_name or not isinstance(account_name, str):
        return False
    
    account_name = account_name.strip()
    
    if len(account_name) < ACCOUNT_NAME_MIN_LENGTH or len(account_name) > ACCOUNT_NAME_MAX_LENGTH:
        return False
    
    if not ACCOUNT_NAME_REGEX_OBJ.match(account_name):
        return False
    
    for regex in INVALID_ACCOUNT_REGEXES:
        if regex.match(account_name):
            return False
    
    return True


def get_invalid_accounts(db_session) -> List[str]:
    """获取所有无效账号名称列表。"""
    # 从 member 表获取所有账号
    result = db_session.execute(text("SELECT account_name FROM member"))
    all_accounts = [row[0] for row in result.fetchall()]
    
    # 筛选无效账号
    invalid_accounts = [acc for acc in all_accounts if not is_valid_account_name(acc)]
    
    return invalid_accounts


def get_affected_records(db_session, invalid_accounts: List[str]) -> dict:
    """获取受影响的记录数量。"""
    if not invalid_accounts:
        return {
            'members': 0,
            'account_characters': 0,
            'fight_stats': 0,
            'ei_players': 0,
        }
    
    placeholders = ','.join([':acc_%d' % i for i in range(len(invalid_accounts))])
    params = {'acc_%d' % i: acc for i, acc in enumerate(invalid_accounts)}
    
    # 统计 member 表
    result = db_session.execute(
        text(f"SELECT COUNT(*) FROM member WHERE account_name IN ({placeholders})"),
        params
    )
    members_count = result.scalar() or 0
    
    # 统计 account_character 表
    result = db_session.execute(
        text(f"SELECT COUNT(*) FROM account_character WHERE account_name IN ({placeholders})"),
        params
    )
    account_characters_count = result.scalar() or 0
    
    # 统计 fight_stats 表（通过 member 关联）
    result = db_session.execute(
        text(f"""
            SELECT COUNT(*) FROM fight_stats 
            JOIN member ON fight_stats.member_id = member.id 
            WHERE member.account_name IN ({placeholders})
        """),
        params
    )
    fight_stats_count = result.scalar() or 0
    
    # 统计 ei_player 表
    result = db_session.execute(
        text(f"SELECT COUNT(*) FROM ei_player WHERE account IN ({placeholders})"),
        params
    )
    ei_players_count = result.scalar() or 0
    
    return {
        'members': members_count,
        'account_characters': account_characters_count,
        'fight_stats': fight_stats_count,
        'ei_players': ei_players_count,
    }


def cleanup_invalid_accounts(db_session, invalid_accounts: List[str]) -> dict:
    """执行清理操作。"""
    if not invalid_accounts:
        return {'deleted': 0, 'details': {}}
    
    placeholders = ','.join([':acc_%d' % i for i in range(len(invalid_accounts))])
    params = {'acc_%d' % i: acc for i, acc in enumerate(invalid_accounts)}
    
    deleted = {
        'members': 0,
        'account_characters': 0,
        'fight_stats': 0,
        'ei_players': 0,
    }
    
    try:
        # 删除 ei_player 表中无效账号记录
        result = db_session.execute(
            text(f"DELETE FROM ei_player WHERE account IN ({placeholders})"),
            params
        )
        deleted['ei_players'] = result.rowcount
        
        # 删除 account_character 表中无效账号记录
        result = db_session.execute(
            text(f"DELETE FROM account_character WHERE account_name IN ({placeholders})"),
            params
        )
        deleted['account_characters'] = result.rowcount
        
        # 获取无效账号对应的 member_id
        result = db_session.execute(
            text(f"SELECT id FROM member WHERE account_name IN ({placeholders})"),
            params
        )
        member_ids = [row[0] for row in result.fetchall()]
        
        if member_ids:
            member_placeholders = ','.join([':mid_%d' % i for i in range(len(member_ids))])
            member_params = {'mid_%d' % i: mid for i, mid in enumerate(member_ids)}
            
            # 删除 fight_stats 表中关联记录
            result = db_session.execute(
                text(f"DELETE FROM fight_stats WHERE member_id IN ({member_placeholders})"),
                member_params
            )
            deleted['fight_stats'] = result.rowcount
            
            # 删除 member 表中无效账号记录
            result = db_session.execute(
                text(f"DELETE FROM member WHERE id IN ({member_placeholders})"),
                member_params
            )
            deleted['members'] = result.rowcount
        
        db_session.commit()
        
        return {
            'deleted': sum(deleted.values()),
            'details': deleted,
        }
    
    except Exception as e:
        db_session.rollback()
        raise e


def main():
    print("=" * 70)
    print("GW2 WVW Log Analyzer - 无效账号数据清理脚本")
    print("=" * 70)
    print()
    
    # 获取数据库连接信息
    from app.core.config import settings
    db_url = settings.DATABASE_URL
    
    print(f"数据库连接: {db_url}")
    print()
    
    # 创建数据库连接
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    try:
        # 步骤1: 获取无效账号列表
        print("[步骤1/4] 正在扫描无效账号...")
        invalid_accounts = get_invalid_accounts(db_session)
        print(f"  发现 {len(invalid_accounts)} 个无效账号")
        
        if invalid_accounts:
            print("  无效账号示例（最多显示20个）:")
            for acc in invalid_accounts[:20]:
                print(f"    - '{acc}'")
            if len(invalid_accounts) > 20:
                print(f"    ... 还有 {len(invalid_accounts) - 20} 个")
        
        print()
        
        # 步骤2: 统计受影响的记录
        print("[步骤2/4] 正在统计受影响的记录...")
        affected = get_affected_records(db_session, invalid_accounts)
        print(f"  member 表: {affected['members']} 条")
        print(f"  account_character 表: {affected['account_characters']} 条")
        print(f"  fight_stats 表: {affected['fight_stats']} 条")
        print(f"  ei_player 表: {affected['ei_players']} 条")
        print()
        
        total_affected = sum(affected.values())
        
        if total_affected == 0:
            print("没有需要清理的无效账号数据。")
            return
        
        # 步骤3: 确认操作
        print("[步骤3/4] 确认清理操作")
        print(f"即将删除 {total_affected} 条记录，包括 {len(invalid_accounts)} 个无效账号。")
        print()
        confirm = input("确认继续执行吗？(yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("操作已取消。")
            return
        
        # 步骤4: 执行清理
        print()
        print("[步骤4/4] 正在执行清理...")
        result = cleanup_invalid_accounts(db_session, invalid_accounts)
        
        print()
        print("清理完成！")
        print(f"  共删除 {result['deleted']} 条记录")
        print(f"    - member: {result['details']['members']} 条")
        print(f"    - account_character: {result['details']['account_characters']} 条")
        print(f"    - fight_stats: {result['details']['fight_stats']} 条")
        print(f"    - ei_player: {result['details']['ei_players']} 条")
        
    except Exception as e:
        print(f"\n执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()


if __name__ == '__main__':
    main()
