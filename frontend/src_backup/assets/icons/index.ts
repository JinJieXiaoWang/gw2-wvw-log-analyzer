/**
 * SVG 图标导出文件
 * 功能：统一管理所有图标资源，提供类型安全的图标名称
 * 作者：System
 * 创建日期：2026-05-10
 * 
 * 图标分类：
 * - ui: 通用UI图标（按钮、导航、操作等）
 * - combat: 战斗相关图标（武器、技能等）
 * - status: 状态图标（在线、离线、成功、错误等）
 * - profession: 职业图标（战士、守护者、盗贼等）
 * - buff: Buff图标（力量、狂怒、保护等）
 * - decor: 装饰元素（星星、火花等）
 */

export type IconCategory = 'ui' | 'combat' | 'status' | 'profession' | 'buff' | 'decor'

export interface IconInfo {
  name: string
  category: IconCategory
  path: string
}

export const UI_ICONS = [
  'home',
  'log',
  'dashboard',
  'analytics',
  'bar-chart',
  'pie-chart',
  'line-chart',
  'users',
  'user',
  'upload',
  'download',
  'search',
  'settings',
  'trash',
  'edit',
  'eye',
  'eye-off',
  'plus',
  'minus',
  'x',
  'check',
  'chevron-left',
  'chevron-right',
  'chevron-up',
  'chevron-down',
  'refresh',
  'external-link',
  'file',
  'folder',
  'clock',
  'calendar',
  'bell',
  'mail',
  'lock',
  'unlock',
  'wifi',
  'signal',
  'cloud',
  'hard-drive',
  'cpu',
  'database',
  'server',
  'shield',
  'alert-circle',
  'info',
  'help-circle',
  'lightbulb',
  'link',
  'tag',
  'bookmark',
  'star',
  'heart',
  'image',
  'video',
  'music',
  'volume-2',
  'volume-x',
  'map',
  'navigation',
  'compass'
] as const

export const COMBAT_ICONS = [
  'sword',
  'shield',
  'bow',
  'axe',
  'hammer',
  'dagger',
  'staff',
  'warhorn',
  'torch',
  'pistol',
  'rifle',
  'spear',
  'greatsword',
  'mace',
  'focus',
  'relic',
  'scepter',
  'harpoon'
] as const

export const STATUS_ICONS = [
  'online',
  'offline',
  'warning',
  'error',
  'success',
  'pending',
  'loading',
  'idle',
  'busy',
  'away'
] as const

export const PROFESSION_ICONS = [
  'warrior',
  'guardian',
  'thief',
  'engineer',
  'ranger',
  'mesmer',
  'necromancer',
  'elementalist',
  'revenant',
  'chronomancer',
  'druid',
  'scrapper',
  'holosmith',
  'dragonhunter',
  'herald',
  'renegade',
  'deadeye',
  'soulbeast',
  'specter',
  'weaver',
  'firebrand',
  'brandbreaker',
  'bladesworn',
  'virtuoso',
  'catalyst',
  'harbinger',
  'willbender',
  'mechanist'
] as const

export const BUFF_ICONS = [
  'might',
  'fury',
  'protection',
  'quickness',
  'alacrity',
  'regeneration',
  'resistance',
  'stability',
  'swiftness',
  'vigor',
  'resilience',
  'precision'
] as const

export const DECOR_ICONS = [
  'spark',
  'star',
  'circle',
  'hexagon'
] as const

export type UiIconName = typeof UI_ICONS[number]
export type CombatIconName = typeof COMBAT_ICONS[number]
export type StatusIconName = typeof STATUS_ICONS[number]
export type ProfessionIconName = typeof PROFESSION_ICONS[number]
export type BuffIconName = typeof BUFF_ICONS[number]
export type DecorIconName = typeof DECOR_ICONS[number]

export type IconName = 
  | UiIconName 
  | CombatIconName 
  | StatusIconName 
  | ProfessionIconName 
  | BuffIconName 
  | DecorIconName

export function getIconPath(category: IconCategory, name: string): string {
  return `/src/assets/icons/${category}/${name}.svg`
}

export function getIconUrl(category: IconCategory, name: string): string {
  return new URL(`../assets/icons/${category}/${name}.svg`, import.meta.url).href
}

export const ALL_ICONS: IconInfo[] = [
  ...UI_ICONS.map(name => ({ name, category: 'ui' as IconCategory, path: getIconPath('ui', name) })),
  ...COMBAT_ICONS.map(name => ({ name, category: 'combat' as IconCategory, path: getIconPath('combat', name) })),
  ...STATUS_ICONS.map(name => ({ name, category: 'status' as IconCategory, path: getIconPath('status', name) })),
  ...PROFESSION_ICONS.map(name => ({ name, category: 'profession' as IconCategory, path: getIconPath('profession', name) })),
  ...BUFF_ICONS.map(name => ({ name, category: 'buff' as IconCategory, path: getIconPath('buff', name) })),
  ...DECOR_ICONS.map(name => ({ name, category: 'decor' as IconCategory, path: getIconPath('decor', name) }))
]
