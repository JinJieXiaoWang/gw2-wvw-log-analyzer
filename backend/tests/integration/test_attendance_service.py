# -*- coding: utf-8 -*-
"""
出勤统计服务层测试 v2.0

测试覆盖的边界场景:
    1. 同一角色同一天多个日志 → 只计 1 次出勤
    2. 同一账号同一天多角色 → 账号维度只计 1 次
    3. 跨日期日志 → 按 fight.start_time 归属到对应日期
    4. 不同角色数据清晰分离
    5. 日期筛选严格使用 fight.start_time，与 upload_time 无关
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.account_character import AccountCharacter
from app.models.fight import Fight
from app.models.fight_stats import FightStats
from app.models.member import Member
from app.services.zevtc import attendance_service


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def db_session():
    """提供内存 SQLite 会话，每个测试独立"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_data(db_session):
    """创建测试数据：
    账号 A (PlayerOne.1234):
        - DragonSlayer (Warrior):
            5/1: 3 fights  → 角色计 1 次
            5/2: 2 fights  → 角色计 1 次
        - HealBot (Guardian):
            5/1: 2 fights  → 角色计 1 次
        账号维度: 5/1(两角色) → 1次, 5/2(单角色) → 1次, 共 2 次

    账号 B (PlayerTwo.5678):
        - ShadowBlade (Thief):
            5/1: 1 fight   → 角色计 1 次
        账号维度: 共 1 次
    """
    base = datetime(2026, 5, 1, 12, 0, 0)

    # Members（只存 account_name）
    m1 = Member(account_name="PlayerOne.1234")
    m2 = Member(account_name="PlayerTwo.5678")
    db_session.add_all([m1, m2])
    db_session.flush()

    # AccountCharacters
    ac1 = AccountCharacter(
        account_name="PlayerOne.1234",
        character_name="DragonSlayer",
        profession="Warrior",
        first_seen_date=base.date(),
        last_seen_date=base.date(),
        seen_count=1,
    )
    ac2 = AccountCharacter(
        account_name="PlayerOne.1234",
        character_name="HealBot",
        profession="Guardian",
        first_seen_date=base.date(),
        last_seen_date=base.date(),
        seen_count=1,
    )
    ac3 = AccountCharacter(
        account_name="PlayerTwo.5678",
        character_name="ShadowBlade",
        profession="Thief",
        first_seen_date=base.date(),
        last_seen_date=base.date(),
        seen_count=1,
    )
    db_session.add_all([ac1, ac2, ac3])

    # Fights（按日期分布）
    fight_configs = [
        # 5月1日 - DragonSlayer 第1个日志
        {"day_offset": 0, "hour_offset": 0, "map": "Red Desert", "server": "ServerA"},
        # 5月1日 - DragonSlayer 第2个日志（同角色同日）
        {"day_offset": 0, "hour_offset": 1, "map": "Red Desert", "server": "ServerA"},
        # 5月1日 - DragonSlayer 第3个日志（同角色同日）
        {"day_offset": 0, "hour_offset": 2, "map": "Blue Alpine", "server": "ServerA"},
        # 5月1日 - HealBot 第1个日志（同日不同角色）
        {"day_offset": 0, "hour_offset": 3, "map": "Eternal", "server": "ServerA"},
        # 5月1日 - HealBot 第2个日志（同日不同角色）
        {"day_offset": 0, "hour_offset": 4, "map": "Eternal", "server": "ServerA"},
        # 5月2日 - DragonSlayer 第1个日志
        {"day_offset": 1, "hour_offset": 0, "map": "Red Desert", "server": "ServerB"},
        # 5月2日 - DragonSlayer 第2个日志（同角色同日）
        {"day_offset": 1, "hour_offset": 1, "map": "Blue Alpine", "server": "ServerB"},
        # 5月1日 - ShadowBlade
        {"day_offset": 0, "hour_offset": 5, "map": "Red Desert", "server": "ServerA"},
    ]

    fights = []
    for i, cfg in enumerate(fight_configs):
        fight = Fight(
            log_id=i + 1,
            start_time=base + timedelta(days=cfg["day_offset"], hours=cfg["hour_offset"]),
            duration_sec=300,
            map_name=cfg["map"],
            server_name=cfg["server"],
            total_damage=1000000,
            player_count=10,
        )
        fights.append(fight)
        db_session.add(fight)
    db_session.flush()

    # FightStats（按上述 fights 分配）
    stats_configs = [
        # 5/1 DragonSlayer ×3
        {"fight": fights[0], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 500000},
        {"fight": fights[1], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 450000},
        {"fight": fights[2], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 600000},
        # 5/1 HealBot ×2
        {"fight": fights[3], "member": m1, "char": "HealBot", "prof": "Guardian", "dmg": 100000},
        {"fight": fights[4], "member": m1, "char": "HealBot", "prof": "Guardian", "dmg": 120000},
        # 5/2 DragonSlayer ×2
        {"fight": fights[5], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 550000},
        {"fight": fights[6], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 480000},
        # 5/1 ShadowBlade ×1
        {"fight": fights[7], "member": m2, "char": "ShadowBlade", "prof": "Thief", "dmg": 400000},
    ]

    for sc in stats_configs:
        fs = FightStats(
            fight_id=sc["fight"].id,
            member_id=sc["member"].id,
            account=sc["member"].account_name,
            character_name=sc["char"],
            profession=sc["prof"],
            damage=sc["dmg"],
            dps=sc["dmg"] // 300,
            healing=10000,
            killed=5,
            dead_count=1,
            ai_score=85.0,
        )
        db_session.add(fs)

    db_session.commit()
    return {"members": [m1, m2], "fights": fights}


# =============================================================================
# 测试：账号出勤列表 - 核心去重规则
# =============================================================================

def test_attendance_count_by_day_not_by_fight(db_session, sample_data):
    """核心规则：同一角色同一天多个日志，账号出勤只计 1 次"""
    items, total = attendance_service.get_account_attendance_list(db_session)

    assert total == 2
    p1 = next(i for i in items if i["account"] == "PlayerOne.1234")
    p2 = next(i for i in items if i["account"] == "PlayerTwo.5678")

    # PlayerOne: 5/1(两角色共5个日志) + 5/2(单角色共2个日志) = 2 个自然日
    assert p1["attendance_count"] == 2, (
        f"PlayerOne 应在 5/1 和 5/2 各计 1 次，"
        f"实际计 {p1['attendance_count']} 次"
    )

    # PlayerTwo: 5/1(1个日志) = 1 个自然日
    assert p2["attendance_count"] == 1


def test_total_damage_not_deduplicated(db_session, sample_data):
    """伤害等总量统计不应去重，应累加所有日志"""
    items, _ = attendance_service.get_account_attendance_list(db_session)
    p1 = next(i for i in items if i["account"] == "PlayerOne.1234")

    # PlayerOne 所有伤害累加: 500k+450k+600k+100k+120k+550k+480k = 2,800,000
    expected_damage = 500000 + 450000 + 600000 + 100000 + 120000 + 550000 + 480000
    assert p1["total_damage"] == expected_damage


def test_pagination_and_sort(db_session, sample_data):
    """测试分页和排序"""
    items, total = attendance_service.get_account_attendance_list(
        db_session, page=1, page_size=1, sort_by="total_damage", sort_order="desc"
    )
    assert total == 2
    assert len(items) == 1
    assert items[0]["account"] == "PlayerOne.1234"


# =============================================================================
# 测试：日期筛选（严格使用 fight.start_time）
# =============================================================================

def test_date_filter_uses_fight_start_time(db_session, sample_data):
    """日期筛选必须基于 fight.start_time，而非 upload_time"""
    base = datetime(2026, 5, 1, 12, 0, 0)

    # 筛选 5月1日
    items, total = attendance_service.get_account_attendance_list(
        db_session, start_date=base, end_date=base + timedelta(days=1)
    )
    assert total == 2
    p1 = next(i for i in items if i["account"] == "PlayerOne.1234")
    # 5/1 只有 1 个自然日
    assert p1["attendance_count"] == 1
    # 但伤害应只包含 5/1 的日志（5个）
    expected_5_1 = 500000 + 450000 + 600000 + 100000 + 120000
    assert p1["total_damage"] == expected_5_1

    # 筛选 5月2日
    items2, total2 = attendance_service.get_account_attendance_list(
        db_session,
        start_date=base + timedelta(days=1),
        end_date=base + timedelta(days=2),
    )
    assert total2 == 1
    p1_2 = next(i for i in items2 if i["account"] == "PlayerOne.1234")
    assert p1_2["attendance_count"] == 1
    expected_5_2 = 550000 + 480000
    assert p1_2["total_damage"] == expected_5_2


def test_date_filter_cross_day_logs(db_session, sample_data):
    """跨日期日志应正确归属到各自日期"""
    base = datetime(2026, 5, 1, 12, 0, 0)

    # 筛选 5/1 - 5/2 两天
    items, total = attendance_service.get_account_attendance_list(
        db_session, start_date=base, end_date=base + timedelta(days=2)
    )
    p1 = next(i for i in items if i["account"] == "PlayerOne.1234")
    # 两天各计 1 次
    assert p1["attendance_count"] == 2


# =============================================================================
# 测试：服务器/地图/职业筛选
# =============================================================================

def test_filter_by_server(db_session, sample_data):
    """按服务器筛选"""
    items, total = attendance_service.get_account_attendance_list(
        db_session, server_name="ServerB"
    )
    # 只有 5/2 的 DragonSlayer 在 ServerB
    assert total == 1
    assert items[0]["account"] == "PlayerOne.1234"
    assert items[0]["attendance_count"] == 1


def test_filter_by_map(db_session, sample_data):
    """按地图筛选"""
    items, total = attendance_service.get_account_attendance_list(
        db_session, map_name="Blue Alpine"
    )
    # Blue Alpine 出现在 5/1(fight[2]) 和 5/2(fight[6])
    assert total == 1
    assert items[0]["attendance_count"] == 2  # 跨两天


def test_filter_by_profession(db_session, sample_data):
    """按职业筛选"""
    items, total = attendance_service.get_account_attendance_list(
        db_session, profession="Guardian"
    )
    # 只有 HealBot 是 Guardian，只在 5/1 出现
    assert total == 1
    assert items[0]["account"] == "PlayerOne.1234"
    assert items[0]["attendance_count"] == 1


def test_search_by_character_name(db_session, sample_data):
    """按角色名搜索"""
    items, total = attendance_service.get_account_attendance_list(
        db_session, search="HealBot"
    )
    assert total == 1
    assert items[0]["account"] == "PlayerOne.1234"


# =============================================================================
# 测试：账号详情 - 角色数据分离
# =============================================================================

def test_account_detail_character_separation(db_session, sample_data):
    """账号详情中不同角色的数据应清晰分离"""
    data = attendance_service.get_account_detail(db_session, "PlayerOne.1234")

    assert data is not None
    assert data["character_count"] == 2

    # 汇总统计（账号维度按自然日去重）
    assert data["summary"]["attendance_count"] == 2  # 5/1 和 5/2

    # 角色列表
    chars = data["characters"]
    assert len(chars) == 2

    dragon = next(c for c in chars if c["character_name"] == "DragonSlayer")
    heal = next(c for c in chars if c["character_name"] == "HealBot")

    # DragonSlayer: 5/1(3日志) + 5/2(2日志) = 2 个自然日
    assert dragon["attendance_count"] == 2
    assert dragon["profession"] == "Warrior"

    # HealBot: 5/1(2日志) = 1 个自然日
    assert heal["attendance_count"] == 1
    assert heal["profession"] == "Guardian"


def test_account_detail_recent_fights_include_all_characters(db_session, sample_data):
    """最近战斗记录应包含该账号下所有角色的记录"""
    data = attendance_service.get_account_detail(db_session, "PlayerOne.1234")
    recent = data["recent_fights"]

    # 最近 20 条应包含 DragonSlayer 和 HealBot 的记录
    char_names = {r["character_name"] for r in recent}
    assert "DragonSlayer" in char_names
    assert "HealBot" in char_names


def test_account_detail_date_filter(db_session, sample_data):
    """账号详情日期筛选"""
    base = datetime(2026, 5, 1, 12, 0, 0)

    # 只看 5/1
    data = attendance_service.get_account_detail(
        db_session, "PlayerOne.1234", start_date=base, end_date=base + timedelta(days=1)
    )
    assert data["summary"]["attendance_count"] == 1
    # 角色统计也应只包含 5/1
    dragon = next(c for c in data["characters"] if c["character_name"] == "DragonSlayer")
    assert dragon["attendance_count"] == 1
    # HealBot 也在 5/1
    heal = next(c for c in data["characters"] if c["character_name"] == "HealBot")
    assert heal["attendance_count"] == 1


def test_account_detail_not_found(db_session):
    """查询不存在的账号"""
    data = attendance_service.get_account_detail(db_session, "NotExist.9999")
    assert data is None


# =============================================================================
# 测试：角色战斗记录
# =============================================================================

def test_character_detail_attendance_by_day(db_session, sample_data):
    """角色详情中 attendance_count 应按自然日去重"""
    items, total, summary = attendance_service.get_character_detail(
        db_session, "PlayerOne.1234", "DragonSlayer"
    )

    # DragonSlayer 在 5/1(3日志) + 5/2(2日志) = 2 个自然日
    assert summary["attendance_count"] == 2
    # 但总条数是 5
    assert total == 5


def test_character_detail_day_filter(db_session, sample_data):
    """角色详情日期筛选"""
    base = datetime(2026, 5, 1, 12, 0, 0)

    # 只看 5/1
    items, total, summary = attendance_service.get_character_detail(
        db_session,
        "PlayerOne.1234",
        "DragonSlayer",
        start_date=base,
        end_date=base + timedelta(days=1),
    )
    assert summary["attendance_count"] == 1
    assert total == 3  # 3 个日志


def test_character_detail_pagination(db_session, sample_data):
    """角色战斗记录分页"""
    items, total, _ = attendance_service.get_character_detail(
        db_session, "PlayerOne.1234", "DragonSlayer", page=1, page_size=2
    )
    assert total == 5
    assert len(items) == 2


# =============================================================================
# 测试：筛选选项
# =============================================================================

def test_get_distinct_servers(db_session, sample_data):
    """获取服务器列表"""
    servers = attendance_service.get_distinct_servers(db_session)
    assert "ServerA" in servers
    assert "ServerB" in servers


def test_get_distinct_maps(db_session, sample_data):
    """获取地图列表"""
    maps = attendance_service.get_distinct_maps(db_session)
    assert "Red Desert" in maps
    assert "Blue Alpine" in maps
    assert "Eternal" in maps


def test_get_distinct_professions(db_session, sample_data):
    """获取职业列表"""
    professions = attendance_service.get_distinct_professions(db_session)
    assert "Warrior" in professions
    assert "Guardian" in professions
    assert "Thief" in professions
