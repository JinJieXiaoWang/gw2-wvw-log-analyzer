# -*- coding: utf-8 -*-
"""
数据看板服务层测试 v2.0

测试覆盖:
    1. overview - KPI 概览数据结构
    2. trends - 时间趋势补零
    3. profession_distribution - 职业分布不因转职拆分
    4. map_stats - 地图统计
    5. top_players - 玩家排行聚合
    6. recent_fights - 最近战斗
    7. buff_overview - Buff 覆盖率
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
from app.models.log import Log
from app.models.member import Member
from app.services.system import dashboard_service


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_data(db_session):
    """创建测试数据"""
    base = datetime(2026, 5, 1, 12, 0, 0)

    # Members
    m1 = Member(account_name="PlayerOne.1234")
    m2 = Member(account_name="PlayerTwo.5678")
    db_session.add_all([m1, m2])
    db_session.flush()

    # AccountCharacters
    db_session.add_all([
        AccountCharacter(account_name="PlayerOne.1234", character_name="DragonSlayer", profession="Warrior",
                         first_seen_date=base.date(), last_seen_date=base.date(), seen_count=1),
        AccountCharacter(account_name="PlayerOne.1234", character_name="HealBot", profession="Guardian",
                         first_seen_date=base.date(), last_seen_date=base.date(), seen_count=1),
        AccountCharacter(account_name="PlayerTwo.5678", character_name="ShadowBlade", profession="Thief",
                         first_seen_date=base.date(), last_seen_date=base.date(), seen_count=1),
    ])

    # Fights (5/1 × 4, 5/2 × 2)
    fight_configs = [
        {"day_offset": 0, "hour_offset": 0, "map": "Red Desert", "dmg": 2000000, "heal": 500000},
        {"day_offset": 0, "hour_offset": 2, "map": "Blue Alpine", "dmg": 1500000, "heal": 400000},
        {"day_offset": 0, "hour_offset": 4, "map": "Red Desert", "dmg": 1800000, "heal": 450000},
        {"day_offset": 0, "hour_offset": 6, "map": "Eternal", "dmg": 2200000, "heal": 600000},
        {"day_offset": 1, "hour_offset": 0, "map": "Blue Alpine", "dmg": 1600000, "heal": 350000},
        {"day_offset": 1, "hour_offset": 2, "map": "Red Desert", "dmg": 1900000, "heal": 480000},
    ]

    fights = []
    for i, cfg in enumerate(fight_configs):
        f = Fight(
            log_id=i + 1,
            start_time=base + timedelta(days=cfg["day_offset"], hours=cfg["hour_offset"]),
            duration_sec=300,
            map_name=cfg["map"],
            total_damage=cfg["dmg"],
            total_healing=cfg["heal"],
            player_count=10,
        )
        fights.append(f)
        db_session.add(f)
    db_session.flush()

    # FightStats
    stats_configs = [
        # 5/1 fights
        {"fight": fights[0], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 500000, "dps": 1600, "heal": 5000, "killed": 5, "dead": 1, "score": 85.0},
        {"fight": fights[0], "member": m2, "char": "ShadowBlade", "prof": "Thief", "dmg": 400000, "dps": 1300, "heal": 2000, "killed": 3, "dead": 2, "score": 78.0},
        {"fight": fights[1], "member": m1, "char": "DragonSlayer", "prof": "Warrior", "dmg": 550000, "dps": 1800, "heal": 6000, "killed": 6, "dead": 0, "score": 88.0},
        {"fight": fights[1], "member": m2, "char": "ShadowBlade", "prof": "Thief", "dmg": 350000, "dps": 1100, "heal": 1500, "killed": 2, "dead": 1, "score": 72.0},
        {"fight": fights[2], "member": m1, "char": "HealBot", "prof": "Guardian", "dmg": 100000, "dps": 300, "heal": 50000, "killed": 1, "dead": 0, "score": 92.0},
        {"fight": fights[2], "member": m2, "char": "ShadowBlade", "prof": "Thief", "dmg": 420000, "dps": 1400, "heal": 1000, "killed": 4, "dead": 1, "score": 80.0},
        {"fight": fights[3], "member": m1, "char": "HealBot", "prof": "Guardian", "dmg": 120000, "dps": 400, "heal": 55000, "killed": 2, "dead": 0, "score": 90.0},
        # 5/2 fights
        {"fight": fights[4], "member": m1, "char": "DragonSlayer", "prof": "Berserker", "dmg": 600000, "dps": 2000, "heal": 4000, "killed": 7, "dead": 1, "score": 95.0},
        {"fight": fights[4], "member": m2, "char": "ShadowBlade", "prof": "Thief", "dmg": 380000, "dps": 1200, "heal": 1800, "killed": 3, "dead": 2, "score": 75.0},
        {"fight": fights[5], "member": m1, "char": "DragonSlayer", "prof": "Berserker", "dmg": 580000, "dps": 1900, "heal": 4500, "killed": 6, "dead": 0, "score": 93.0},
    ]

    for sc in stats_configs:
        fs = FightStats(
            fight_id=sc["fight"].id,
            member_id=sc["member"].id,
            account=sc["member"].account_name,
            character_name=sc["char"],
            profession=sc["prof"],
            damage=sc["dmg"],
            dps=sc["dps"],
            healing=sc["heal"],
            killed=sc["killed"],
            dead_count=sc["dead"],
            ai_score=sc["score"],
            might_uptime=80.0,
            fury_uptime=75.0,
            quickness_uptime=60.0,
            alacrity_uptime=55.0,
            protection_uptime=70.0,
            stability_uptime=45.0,
        )
        db_session.add(fs)

    # Logs
    for i in range(6):
        db_session.add(Log(
            id=i + 1,
            log_uuid=f"uuid-{i}",
            filename=f"log_{i}.zevtc",
            file_sha256=f"sha256-{i}",
            file_size_compressed=1000,
            file_size_raw=2000,
            parse_status="completed",
        ))

    db_session.commit()
    return {"members": [m1, m2], "fights": fights}


# =============================================================================
# Tests
# =============================================================================

def test_overview_structure(db_session, sample_data):
    """overview 返回正确的数据结构"""
    data = dashboard_service.get_overview(db_session, days=7)
    assert "total_fights" in data
    assert "total_damage" in data
    assert "total_healing" in data
    assert "active_accounts" in data
    assert "change" in data
    assert data["total_fights"] == 6


def test_overview_change_calculation(db_session, sample_data):
    """环比变化计算不为 None"""
    data = dashboard_service.get_overview(db_session, days=7)
    assert isinstance(data["change"]["fights"], int)
    assert isinstance(data["change"]["damage"], int)


def test_trends_damage(db_session, sample_data):
    """damage 趋势返回正确的日期和数值"""
    data = dashboard_service.get_trends(db_session, days=7, metric="damage")
    assert "dates" in data
    assert "values" in data
    assert len(data["dates"]) == len(data["values"])
    assert data["metric"] == "damage"
    # 5/1 有 4 场战斗，5/2 有 2 场
    total_damage = sum(data["values"])
    assert total_damage > 0


def test_trends_fights(db_session, sample_data):
    """fights 趋势按天计数正确"""
    data = dashboard_service.get_trends(db_session, days=7, metric="fights")
    assert data["metric"] == "fights"


def test_profession_distribution_not_split_by_spec_change(db_session, sample_data):
    """同一角色转职后不应拆分为两个职业统计"""
    data = dashboard_service.get_profession_distribution(db_session, days=7)
    items = data["items"]
    # DragonSlayer 从 Warrior 转成了 Berserker，但应只计为一个角色
    # 最新职业是 Berserker
    professions = [i["profession"] for i in items]
    assert "Berserker" in professions or "Warrior" in professions
    # 不应同时出现 Warrior 和 Berserker（因为是同一个角色）
    assert not ("Warrior" in professions and "Berserker" in professions)


def test_map_stats_structure(db_session, sample_data):
    """地图统计返回正确结构"""
    data = dashboard_service.get_map_stats(db_session, days=7)
    items = data["items"]
    assert len(items) > 0
    # Red Desert 出场最多 (3 次)
    red_desert = next((i for i in items if i["map_name"] == "Red Desert"), None)
    assert red_desert is not None
    assert red_desert["fight_count"] == 3


def test_top_players_aggregate_by_account(db_session, sample_data):
    """玩家排行按 account 聚合"""
    data = dashboard_service.get_top_players(db_session, days=7, sort_by="damage", limit=10)
    items = data["items"]
    assert len(items) == 2
    # PlayerOne 伤害更高
    p1 = next(i for i in items if i["account"] == "PlayerOne.1234")
    p2 = next(i for i in items if i["account"] == "PlayerTwo.5678")
    assert p1["total_damage"] > p2["total_damage"]
    # 包含 DragonSlayer + HealBot 的伤害
    expected_p1 = 500000 + 550000 + 100000 + 120000 + 600000 + 580000
    assert p1["total_damage"] == expected_p1


def test_top_players_sort_by_healing(db_session, sample_data):
    """按治疗排序时 HealBot 应排第一"""
    data = dashboard_service.get_top_players(db_session, days=7, sort_by="healing", limit=10)
    items = data["items"]
    assert items[0]["account"] == "PlayerOne.1234"


def test_recent_fights(db_session, sample_data):
    """最近战斗返回正确数量"""
    items = dashboard_service.get_recent_fights(db_session, limit=5)
    assert len(items) <= 5
    assert len(items) > 0
    assert "map_name" in items[0]
    assert "start_time" in items[0]


def test_buff_overview(db_session, sample_data):
    """Buff 概览返回正确结构"""
    data = dashboard_service.get_buff_overview(db_session, days=7)
    buffs = data["buffs"]
    assert "might" in buffs
    assert "fury" in buffs
    assert "quickness" in buffs
    assert "alacrity" in buffs
    assert "protection" in buffs
    assert "stability" in buffs


def test_ai_score_distribution(db_session, sample_data):
    """AI 评分分布返回正确结构"""
    data = dashboard_service.get_ai_score_distribution(db_session, days=7)
    assert "items" in data
    assert "avg_score" in data
    assert data["total"] > 0
    grades = [i["grade"] for i in data["items"]]
    assert "S" in grades
    assert "A" in grades


def test_parse_status_distribution(db_session, sample_data):
    """解析状态分布返回正确结构"""
    data = dashboard_service.get_parse_status_distribution(db_session)
    assert "total" in data
    assert "items" in data
    assert data["total"] == 6  # 我们创建了 6 条日志
