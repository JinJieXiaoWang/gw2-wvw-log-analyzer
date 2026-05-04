# -*- coding: utf-8 -*-
"""
EVTC 二进制格式常量定义

参考: ArcDPS EVTC 规范 Revision 1
所有结构大小与偏移量均基于官方文档与实测验证。
"""

# ============================================================================
# 文件结构常量
# ============================================================================

EVTC_MAGIC = b"EVTC"
HEADER_SIZE = 24  # 文件头固定 24 字节
AGENT_SIZE = 96  # 每个 Agent 记录 96 字节
SKILL_SIZE = 68  # 每个 Skill 记录 68 字节
EVENT_SIZE_REV0 = 60  # Revision 0 事件 60 字节
EVENT_SIZE_REV1 = 64  # Revision 1 事件 64 字节

# ============================================================================
# Header 字段偏移 (24 bytes)
# ============================================================================
# offset 0-3   : magic      (char[4])   = "EVTC"
# offset 4-11  : build_date (char[8])   = "YYYYMMDD"
# offset 12    : revision   (uint8)     = 格式版本
# offset 13    : auto_flag  (uint8)     = 1 表示本地玩家录制
# offset 14-15 : boss_id    (uint16)    = 触发器/Boss ID
# offset 16-19 : agent_count(uint32)   = Agent 数量
# offset 20-23 : skill_count(uint32)   = Skill 数量 (部分实现中在 Agent 表后单独读取)

HEADER_OFFSET_MAGIC = 0
HEADER_OFFSET_BUILD_DATE = 4
HEADER_OFFSET_REVISION = 12
HEADER_OFFSET_AUTO_FLAG = 13
HEADER_OFFSET_BOSS_ID = 14
HEADER_OFFSET_AGENT_COUNT = 16
HEADER_OFFSET_SKILL_COUNT = 20

# ============================================================================
# Agent 字段偏移 (96 bytes)
# ============================================================================
# offset 0-7   : address    (uint64)
# offset 8-11  : prof       (uint32)
# offset 12-15 : is_elite   (uint32)    = 0xFFFFFFFF 表示 NPC
# offset 16-17 : toughness  (int16)
# offset 18-19 : concentration (int16)
# offset 20-21 : healing    (int16)
# offset 22-23 : hitbox_width  (int16)
# offset 24-25 : condition  (int16)
# offset 26-27 : hitbox_height (int16)
# offset 28-95 : name_raw   (char[68])  = "member_name\0account_name\0..."

AGENT_OFFSET_ADDRESS = 0
AGENT_OFFSET_PROF = 8
AGENT_OFFSET_IS_ELITE = 12
AGENT_OFFSET_TOUGHNESS = 16
AGENT_OFFSET_CONCENTRATION = 18
AGENT_OFFSET_HEALING = 20
AGENT_OFFSET_HITBOX_WIDTH = 22
AGENT_OFFSET_CONDITION = 24
AGENT_OFFSET_HITBOX_HEIGHT = 26
AGENT_OFFSET_NAME_RAW = 28
AGENT_NAME_RAW_SIZE = 68

# ============================================================================
# Skill 字段偏移 (68 bytes)
# ============================================================================
# offset 0-3   : gw2_skill_id (int32)
# offset 4-67  : name_raw     (char[64])

SKILL_OFFSET_GW2_SKILL_ID = 0
SKILL_OFFSET_NAME_RAW = 4
SKILL_NAME_RAW_SIZE = 64

# ============================================================================
# Event 字段偏移 (64 bytes, Revision >= 1)
# ============================================================================
# 注意: 经实测验证，overstack_value 和 skill_id 在实际文件中按 4 字节读取，
#       以支持 skill_id > 65535 的场景。因此 Event 布局为:
#
# offset 0-7   : time              (uint64)
# offset 8-15  : src_agent         (uint64)
# offset 16-23 : dst_agent         (uint64)
# offset 24-27 : value             (int32)
# offset 28-31 : buff_dmg          (int32)
# offset 32-35 : overstack_value   (uint32)
# offset 36-39 : skill_id          (uint32)
# offset 40-41 : src_instid        (uint16)
# offset 42-43 : dst_instid        (uint16)
# offset 44-45 : src_master_instid (uint16)
# offset 46-47 : dst_master_instid (uint16)
# offset 48    : iff               (uint8)
# offset 49    : buff              (uint8)
# offset 50    : result            (uint8)
# offset 51    : is_activation     (uint8)
# offset 52    : is_buffremove     (uint8)
# offset 53    : is_ninety         (uint8)
# offset 54    : is_fifty          (uint8)
# offset 55    : is_moving         (uint8)
# offset 56    : is_statechange    (uint8)
# offset 57    : is_flanking       (uint8)
# offset 58    : is_shields        (uint8)
# offset 59    : is_offcycle       (uint8)
# offset 60-63 : pad64             (uint8[4])  # Rev1 填充

EVENT_OFFSET_TIME = 0
EVENT_OFFSET_SRC_AGENT = 8
EVENT_OFFSET_DST_AGENT = 16
EVENT_OFFSET_VALUE = 24
EVENT_OFFSET_BUFF_DMG = 28
EVENT_OFFSET_OVERSTACK = 32
EVENT_OFFSET_SKILL_ID = 36
EVENT_OFFSET_SRC_INSTID = 40
EVENT_OFFSET_DST_INSTID = 42
EVENT_OFFSET_SRC_MASTER_INSTID = 44
EVENT_OFFSET_DST_MASTER_INSTID = 46
EVENT_OFFSET_IFF = 48
EVENT_OFFSET_BUFF = 49
EVENT_OFFSET_RESULT = 50
EVENT_OFFSET_IS_ACTIVATION = 51
EVENT_OFFSET_IS_BUFFREMOVE = 52
EVENT_OFFSET_IS_NINETY = 53
EVENT_OFFSET_IS_FIFTY = 54
EVENT_OFFSET_IS_MOVING = 55
EVENT_OFFSET_IS_STATECHANGE = 56
EVENT_OFFSET_IS_FLANKING = 57
EVENT_OFFSET_IS_SHIELDS = 58
EVENT_OFFSET_IS_OFFCYCLE = 59
EVENT_OFFSET_PAD = 60


# ============================================================================
# StateChange 枚举
# ============================================================================
class StateChange:
    NONE = 0
    ENTER_COMBAT = 1
    EXIT_COMBAT = 2
    CHANGE_UP = 3
    CHANGE_DEAD = 4
    CHANGE_DOWN = 5
    SPAWN = 6
    DESPAWN = 7
    HEALTH_UPDATE = 8
    LOG_START = 9
    LOG_END = 10
    WEAPON_SWAP = 11
    MAX_HEALTH_UPDATE = 12
    POINT_OF_VIEW = 13
    LANGUAGE = 14
    GW2_BUILD = 15
    SHARD_ID = 16
    REWARD = 17
    BUFF_INITIAL = 18
    POSITION = 19
    VELOCITY = 20
    ROTATION = 21
    TEAM_CHANGE = 22
    ATTACK_TARGET = 23
    TARGETABLE = 24
    MAP_ID = 25
    REPL_INFO = 26
    STACK_ACTIVE = 27
    STACK_RESET = 28
    GUILD = 29
    BUFF_INFO = 30
    BUFF_FORMULA = 31
    SKILL_INFO = 32
    SKILL_TIMING = 33
    BREAKBAR_STATE = 34
    BREAKBAR_PERCENT = 35
    ERROR = 36
    TAG = 37
    BARRIER_UPDATE = 38
    STAT_RESET = 39
    EXTENSION = 40
    API_DELAYED = 41
    INSTANCE_START = 42
    TICK_RATE = 43
    LAST_90_BEFORE_DOWN = 44
    EFFECT = 45
    STABLE_ID = 46
    LOG_NPC_UPDATE = 47
    IDLE_EVENT = 48
    EXTENSION_COMBAT = 49
    FRACTAL_SCALE = 50
    EFFECT2 = 51
    RULESET = 52
    SQUAD_MARKER = 53
    ARC_BUILD = 54
    GLIDER = 55
    STUN_BREAK = 56
    CUSTOM = 80

    _NAMES = {
        0: "None",
        1: "EnterCombat",
        2: "ExitCombat",
        3: "ChangeUp",
        4: "ChangeDead",
        5: "ChangeDown",
        6: "Spawn",
        7: "Despawn",
        8: "HealthUpdate",
        9: "LogStart",
        10: "LogEnd",
        11: "WeapSwap",
        12: "MaxHealthUpdate",
        13: "PointOfView",
        14: "Language",
        15: "GWBuild",
        16: "ShardId",
        17: "Reward",
        18: "BuffInitial",
        19: "Position",
        20: "Velocity",
        21: "Rotation",
        22: "TeamChange",
        23: "AttackTarget",
        24: "Targetable",
        25: "MapID",
        26: "ReplInfo",
        27: "StackActive",
        28: "StackReset",
        29: "Guild",
        30: "BuffInfo",
        31: "BuffFormula",
        32: "SkillInfo",
        33: "SkillTiming",
        34: "BreakbarState",
        35: "BreakbarPercent",
        36: "Error",
        37: "Tag",
        38: "BarrierUpdate",
        39: "StatReset",
        40: "Extension",
        41: "APIDelayed",
        42: "InstanceStart",
        43: "TickRate",
        44: "Last90BeforeDown",
        45: "Effect",
        46: "StableId",
        47: "LogNPCUpdate",
        48: "IdleEvent",
        49: "ExtensionCombat",
        50: "FractalScale",
        51: "Effect2",
        52: "Ruleset",
        53: "SquadMarker",
        54: "ArcBuild",
        55: "Glider",
        56: "StunBreak",
        80: "Custom",
    }

    @classmethod
    def name(cls, code: int) -> str:
        return cls._NAMES.get(code, f"Unknown({code})")


# ============================================================================
# Result 枚举
# ============================================================================
class Result:
    NORMAL = 0
    CRIT = 1
    GLANCE = 2
    BLOCK = 3
    EVADE = 4
    INTERRUPT = 5
    ABSORB = 6
    BLIND = 7
    KILLING_BLOW = 8
    DOWNED = 9

    _NAMES = {
        0: "Normal",
        1: "Crit",
        2: "Glance",
        3: "Block",
        4: "Evade",
        5: "Interrupt",
        6: "Absorb",
        7: "Blind",
        8: "KillingBlow",
        9: "Downed",
    }

    @classmethod
    def name(cls, code: int) -> str:
        return cls._NAMES.get(code, f"Unknown({code})")


# ============================================================================
# IFF 枚举
# ============================================================================
class IFF:
    FRIEND = 0
    FOE = 1
    UNKNOWN = 2
    TARGET = 3
    TARGET2 = 4

    _NAMES = {
        0: "Friend",
        1: "Foe",
        2: "Unknown",
        3: "Target",
        4: "Target2",
    }

    @classmethod
    def name(cls, code: int) -> str:
        return cls._NAMES.get(code, f"Unknown({code})")


# ============================================================================
# Activation 枚举
# ============================================================================
class Activation:
    NONE = 0
    NORMAL = 1
    QUICKNESS = 2
    CANCEL_FIRE = 3
    CANCEL_CANCEL = 4
    RESET = 5
    UNKNOWN6 = 6
    UNKNOWN7 = 7

    _NAMES = {
        0: "None",
        1: "Normal",
        2: "Quickness",
        3: "CancelFire",
        4: "CancelCancel",
        5: "Reset",
        6: "Unknown6",
        7: "Unknown7",
    }

    @classmethod
    def name(cls, code: int) -> str:
        return cls._NAMES.get(code, f"Unknown({code})")


# ============================================================================
# BuffRemove 枚举
# ============================================================================
class BuffRemove:
    NONE = 0
    ALL = 1
    SINGLE = 2
    MANUAL = 3

    _NAMES = {
        0: "None",
        1: "All",
        2: "Single",
        3: "Manual",
    }

    @classmethod
    def name(cls, code: int) -> str:
        return cls._NAMES.get(code, f"Unknown({code})")


# ============================================================================
# 特殊值常量
# ============================================================================
UINT32_MAX = 0xFFFFFFFF  # NPC/Gadget 的 prof/is_elite 标记
UINT16_MAX = 0xFFFF
INT32_MAX = 2147483647

# Agent 类型推断
AGENT_TYPE_PLAYER = "player"
AGENT_TYPE_NPC = "npc"
AGENT_TYPE_GADGET = "gadget"
AGENT_TYPE_UNKNOWN = "unknown"

# 职业 ID 映射（基础职业）
# 职业 ID 映射（EVTC prof 字段，1-9 为基础职业）
# 精英特长通过 is_elite 字段（specialization ID）单独映射
PROFESSION_MAP = {
    1: "Guardian",
    2: "Warrior",
    3: "Engineer",
    4: "Ranger",
    5: "Thief",
    6: "Elementalist",
    7: "Mesmer",
    8: "Necromancer",
    9: "Revenant",
}

# 精英特长 ID 映射（GW2 Specialization ID → 精英特长名称）
# 来源: https://api.guildwars2.com/v2/specializations?ids=all
# 共 36 个精英特长（9 职业 × 4 资料片）
ELITE_SPEC_MAP = {
    # Guardian
    27: "Dragonhunter",
    62: "Firebrand",
    65: "Willbender",
    81: "Luminary",
    # Warrior
    18: "Berserker",
    61: "Spellbreaker",
    68: "Bladesworn",
    74: "Paragon",
    # Engineer
    43: "Scrapper",
    57: "Holosmith",
    70: "Mechanist",
    75: "Amalgam",
    # Ranger
    5: "Druid",
    55: "Soulbeast",
    72: "Untamed",
    78: "Galeshot",
    # Thief
    7: "Daredevil",
    58: "Deadeye",
    71: "Specter",
    77: "Antiquary",
    # Elementalist
    48: "Tempest",
    56: "Weaver",
    67: "Catalyst",
    80: "Evoker",
    # Mesmer
    40: "Chronomancer",
    59: "Mirage",
    66: "Virtuoso",
    73: "Troubadour",
    # Necromancer
    34: "Reaper",
    60: "Scourge",
    64: "Harbinger",
    76: "Ritualist",
    # Revenant
    52: "Herald",
    63: "Renegade",
    69: "Vindicator",
    79: "Conduit",
}

# 批量插入大小（调优参数）
BATCH_SIZE_AGENTS = 500
BATCH_SIZE_SKILLS = 500
BATCH_SIZE_EVENTS = 5000

# 数据库连接池默认配置
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600
