# -*- coding: utf-8 -*-
"""
Buff 映射常量（已精简）
说明：STATIC_BUFF_NAMES 已迁移至字典表 buff 类型
本文件仅保留 EI JSON 数据处理协议映射和核心回退映射
"""

# EI JSON Buff ID → 内部关键字映射（用于战斗数据提取）
# 此为协议级映射，与 dps.report API 返回的 EI JSON 结构绑定
BUFF_ID_MAP = {
    725: "might",
    726: "fury",
    740: "quickness",
    743: "alacrity",
    717: "protection",
    1122: "stability",
}

# 核心 Buff 名称回退映射（当字典表不可用时使用）
# 完整映射请维护在字典表 buff 类型中
STATIC_BUFF_NAMES = {
    717: "Regeneration",
    718: "Swiftness",
    719: "Fury",
    725: "Might",
    726: "Vigor",
    728: "Protection",
    740: "Aegis",
    743: "Stability",
    1122: "Quickness",
    1187: "Resistance",
    26980: "Alacrity",
    26981: "Resolution",
}
