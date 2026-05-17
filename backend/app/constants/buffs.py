# -*- coding: utf-8 -*-
"""
Buff 映射常量（已精简）
说明：Buff 名称和中文映射已统一由 gw_buff 表 / game_static_buffs 种子数据提供。
本文件仅保留 EI JSON 数据处理协议映射（与 dps.report API 返回结构绑定）。

【重要】以下为 EI JSON 中 buffMap / buffUptimes 实际使用的 buff ID 映射，
基于对 dps.report API 返回的真实 EI JSON 数据验证（log_id=1,5,6 等样本交叉确认）。
"""

# EI JSON Buff ID → 内部关键字映射（用于战斗数据提取）
# 此为协议级映射，与 dps.report API 返回的 EI JSON 结构绑定
BUFF_ID_MAP = {
    # 核心增益（Core Boons）
    740: "might",           # Might（威能）
    725: "fury",            # Fury（激怒）
    717: "protection",      # Protection（保护）
    726: "vigor",           # Vigor（活力）— EI 中 id=726 对应 Vigor
    743: "aegis",           # Aegis（圣盾）
    1122: "stability",      # Stability（稳固）
    1187: "quickness",      # Quickness（敏捷）
    30328: "alacrity",      # Alacrity（急速）
    26980: "resistance",    # Resistance（抗性）
    718: "regeneration",    # Regeneration（再生）
    9283: "reinforced_armor", # Reinforced Armor（强化护甲，WvW 中 Vigor 的替代形式）
    # 扩展增益
    11887: "resolution",    # Resolution（决心）
}

# EI Buff ID → 英文显示名称（回退用）
# 同样基于真实 EI JSON 数据验证
STATIC_BUFF_NAMES = {
    740: "Might",
    725: "Fury",
    717: "Protection",
    726: "Vigor",
    743: "Aegis",
    1122: "Stability",
    1187: "Quickness",
    30328: "Alacrity",
    26980: "Resistance",
    718: "Regeneration",
    9283: "Reinforced Armor",
    11887: "Resolution",
}
