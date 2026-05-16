/**
 * 武器名称中英文映射
 * 功能：WvW 战斗相关常量定义
 * 更新：2026-05-11
 */

// 武器名称中英文映射
export const WEAPON_NAME_MAP: Record<string, string> = {
  'Sword': '剑',
  'Axe': '斧',
  'Mace': '锤',
  'Shield': '盾',
  'Greatsword': '大剑',
  'Hammer': '巨锤',
  'Staff': '法杖',
  'Scepter': '权杖',
  'Focus': '聚能器',
  'Dagger': '匕首',
  'Pistol': '手枪',
  'Rifle': '步枪',
  'Shortbow': '短弓',
  'Longbow': '长弓',
  'Torch': '火炬',
  'Warhorn': '战号',
  'Spear': '矛',
  'Trident': '三叉戟',
  '2Hand': '双手',
  'MainHand': '主手',
  'OffHand': '副手',
}

// WvW 地图名称
export const WVW_MAP_NAMES: Record<string, string> = {
  'bluehome': '蓝家门口',
  'greenhome': '绿家门口',
  'redhome': '红家门口',
  'center': '中场',
  'far': '远点',
  ' SMC': '圣徒殿',
  ' Garrison': '要塞',
  ' Tower': '塔',
  ' Keep': '城堡',
  ' Camp': '营地',
}

// 战斗统计指标
export const COMBAT_STATS = {
  DAMAGE: 'damage',
  HEALING: 'healing',
  DPS: 'dps',
  HPS: 'hps',
  CONDITION_DAMAGE: 'conditionDamage',
  CRIT_CHANCE: 'criticalChance',
  CRIT_DAMAGE: 'criticalDamage',
} as const

// 伤害类型
export const DAMAGE_TYPES = {
  STRIKE: 'strike',
  CONDITION: 'condition',
  HEALING: 'healing',
  BARRIER: 'barrier',
} as const

// Buff/DeBuff 类型
export const BUFF_TYPES = {
  MIGHT: 'Might',
  FURY: 'Fury',
  PROTECTION: 'Protection',
  REGENERATION: 'Regeneration',
  VIGOR: 'Vigor',
  QUICKNESS: 'Quickness',
  ALACRITY: 'Alacrity',
  STABILITY: 'Stability',
  RESISTANCE: 'Resistance',
  AEGIS: 'Aegis',
  REFLECT: 'Reflect',
  SHIELD: 'Shield',
} as const

// 排序类型
export const SORT_TYPES = {
  DAMAGE: 'damage',
  DPS: 'dps',
  HEALING: 'healing',
  HPS: 'hps',
  KILLS: 'kills',
  DEATHS: 'deaths',
  KD: 'kd',
  DOWNSTACKS: 'downstacks',
} as const
