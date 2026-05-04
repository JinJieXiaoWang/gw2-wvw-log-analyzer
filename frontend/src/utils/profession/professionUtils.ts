/**
 * 职业信息工具模块
 * 功能：提供职业相关信息的获取，支持从字典API和本地映射两种数据源
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 *
 * 该模块解决了硬编码的职业映射与后端字典数据不同步的问题
 * 使用策略：优先从字典API获取，失败时使用本地硬编码作为回退
 */

import type { DictOption } from '@/services/system/dictionaryService'
import { dictionaryService } from '@/services/system/dictionaryService'

/**
 * 职业信息缓存
 */
interface ProfessionCache {
  names: Map<string, string>
  colors: Map<string, string>
  icons: Map<string, string>
  timestamp: number
}

const PROFESSION_CACHE_TTL = 5 * 60 * 1000 // 5分钟
let professionCache: ProfessionCache | null = null

/**
 * 从硬编码映射获取职业名称（回退用）
 */
const HARDCODED_PROFESSIONS: Record<string, string> = {
  Guardian: '守护者',
  Dragonhunter: '猎龙者',
  Firebrand: '燃火者',
  Willbender: '破锋者',
  Luminary: '圣辉者',
  Warrior: '战士',
  Berserker: '狂战士',
  Spellbreaker: '破法者',
  Bladesworn: '誓剑士',
  Paragon: '圣言士',
  Engineer: '工程师',
  Scrapper: '机械师',
  Holosmith: '全息师',
  Mechanist: '玉偃师',
  Amalgam: '流金师',
  Ranger: '游侠',
  Druid: '德鲁伊',
  Soulbeast: '魂兽师',
  Untamed: '狂兽师',
  Galeshot: '风冲击',
  Thief: '潜行者',
  Daredevil: '独行侠',
  Deadeye: '神枪手',
  Specter: '缚影者',
  Antiquary: '彩戏师',
  Elementalist: '元素使',
  Tempest: '暴风使',
  Weaver: '编织者',
  Catalyst: '元晶师',
  Evoker: '唤元师',
  Mesmer: '幻术师',
  Chronomancer: '时空术士',
  Mirage: '幻象术士',
  Virtuoso: '灵刃术士',
  Troubadour: '吟游诗人',
  Necromancer: '死灵法师',
  Reaper: '夺魂者',
  Scourge: '灾厄师',
  Harbinger: '先驱者',
  Ritualist: '祭祀者',
  Revenant: '魂武者',
  Herald: '预告者',
  Renegade: '龙魂使',
  Vindicator: '裁决者',
  Conduit: '契灵使'
}

/**
 * 硬编码的职业颜色（回退用）
 */
const HARDCODED_PROFESSION_COLORS: Record<string, string> = {
  Guardian: 'rgb(251,207,75)',
  Dragonhunter: 'rgb(232,159,72)',
  Firebrand: 'rgb(245,173,31)',
  Willbender: 'rgb(255,223,128)',
  Luminary: 'rgb(255,215,0)',
  Warrior: 'rgb(255,218,107)',
  Berserker: 'rgb(255,153,0)',
  Spellbreaker: 'rgb(239,217,125)',
  Bladesworn: 'rgb(215,175,105)',
  Paragon: 'rgb(255,200,100)',
  Engineer: 'rgb(184,116,44)',
  Scrapper: 'rgb(160,140,80)',
  Holosmith: 'rgb(255,215,0)',
  Mechanist: 'rgb(208,156,89)',
  Amalgam: 'rgb(200,180,120)',
  Ranger: 'rgb(119,186,79)',
  Druid: 'rgb(89,166,59)',
  Soulbeast: 'rgb(109,176,69)',
  Untamed: 'rgb(139,196,99)',
  Galeshot: 'rgb(150,200,100)',
  Thief: 'rgb(231,124,3)',
  Daredevil: 'rgb(232,127,12)',
  Deadeye: 'rgb(242,147,22)',
  Specter: 'rgb(180,100,30)',
  Antiquary: 'rgb(220,140,60)',
  Elementalist: 'rgb(238,105,105)',
  Tempest: 'rgb(100,180,220)',
  Weaver: 'rgb(200,120,120)',
  Catalyst: 'rgb(180,100,100)',
  Evoker: 'rgb(220,100,140)',
  Mesmer: 'rgb(153,102,204)',
  Chronomancer: 'rgb(170,151,217)',
  Mirage: 'rgb(180,122,224)',
  Virtuoso: 'rgb(160,140,210)',
  Troubadour: 'rgb(190,160,220)',
  Necromancer: 'rgb(68,138,92)',
  Reaper: 'rgb(88,158,112)',
  Scourge: 'rgb(100,140,100)',
  Harbinger: 'rgb(78,148,102)',
  Ritualist: 'rgb(90,160,120)',
  Revenant: 'rgb(141,194,244)',
  Herald: 'rgb(121,174,224)',
  Renegade: 'rgb(161,214,255)',
  Vindicator: 'rgb(129,182,228)',
  Conduit: 'rgb(130,190,230)'
}

/**
 * 职业图标文件名映射
 */
const PROFESSION_ICON_PATHS: Record<string, string> = {
  Guardian: '守护者.png',
  Dragonhunter: '猎龙者.png',
  Firebrand: '燃火者.png',
  Willbender: '破锋者.png',
  Luminary: '圣辉者.png',
  Warrior: '战士.png',
  Berserker: '狂战士.png',
  Spellbreaker: '破法者.png',
  Bladesworn: '誓剑士.png',
  Paragon: '圣言者.png',
  Engineer: '工程师.png',
  Scrapper: '机械师.png',
  Holosmith: '全息师.png',
  Mechanist: '玉偃师.png',
  Amalgam: '流金师.png',
  Ranger: '游侠.png',
  Druid: '德鲁伊.png',
  Soulbeast: '魂兽师.png',
  Untamed: '狂兽师.png',
  Galeshot: '风羽者.png',
  Thief: '潜行者.png',
  Daredevil: '独行侠.png',
  Deadeye: '神枪手.png',
  Specter: '缚影者.png',
  Antiquary: '彩戏师.png',
  Elementalist: '元素师.png',
  Tempest: '暴风使.png',
  Weaver: '编织者.png',
  Catalyst: '元晶师.png',
  Evoker: '唤元师.png',
  Mesmer: '幻术师.png',
  Chronomancer: '时空术士.png',
  Mirage: '幻象术士.png',
  Virtuoso: '灵刃术士.png',
  Troubadour: '吟游诗人.png',
  Necromancer: '唤灵师.png',
  Reaper: '夺魂者.png',
  Scourge: '灾厄师.png',
  Harbinger: '先驱者.png',
  Ritualist: '祭祀者.png',
  Revenant: '魂武者.png',
  Herald: '预告者.png',
  Renegade: '龙魂使.png',
  Vindicator: '裁决者.png',
  Conduit: '契灵使.png'
}

/**
 * 初始化职业缓存
 */
function initCache(): void {
  if (!professionCache) {
    professionCache = {
      names: new Map(),
      colors: new Map(),
      icons: new Map(),
      timestamp: 0
    }
  }
}

/**
 * 检查缓存是否过期
 */
function isCacheExpired(): boolean {
  if (!professionCache) return true
  return Date.now() - professionCache.timestamp > PROFESSION_CACHE_TTL
}

/**
 * 加载职业字典数据
 */
async function loadProfessionData(): Promise<void> {
  initCache()

  if (!isCacheExpired()) return

  try {
    const options = await dictionaryService.getOptions('profession')
    if (options && options.length > 0) {
      professionCache!.names.clear()
      professionCache!.colors.clear()
      professionCache!.icons.clear()

      for (const opt of options) {
        professionCache!.names.set(opt.value, opt.label)
        if (opt.css_class) {
          professionCache!.colors.set(opt.value, opt.css_class)
        }
        const iconPath = PROFESSION_ICON_PATHS[opt.value]
        if (iconPath) {
          professionCache!.icons.set(opt.value, iconPath)
        }
      }
    } else {
      loadHardcodedData()
    }
  } catch (error) {
    console.warn('[professionUtils] 从API加载职业数据失败，使用硬编码数据', error)
    loadHardcodedData()
  } finally {
    professionCache!.timestamp = Date.now()
  }
}

/**
 * 加载硬编码数据到缓存
 */
function loadHardcodedData(): void {
  initCache()
  professionCache!.names.clear()
  professionCache!.colors.clear()
  professionCache!.icons.clear()

  for (const [key, value] of Object.entries(HARDCODED_PROFESSIONS)) {
    professionCache!.names.set(key, value)
  }
  for (const [key, value] of Object.entries(HARDCODED_PROFESSION_COLORS)) {
    professionCache!.colors.set(key, value)
  }
  for (const [key, value] of Object.entries(PROFESSION_ICON_PATHS)) {
    professionCache!.icons.set(key, value)
  }
}

/**
 * 获取职业中文名称
 * @param profession 职业英文名称
 * @returns 职业中文名称
 */
export function getProfessionName(profession: string): string {
  initCache()
  if (!profession) return ''

  if (professionCache && professionCache.names.has(profession)) {
    return professionCache.names.get(profession)!
  }

  return HARDCODED_PROFESSIONS[profession] || profession
}

/**
 * 获取职业颜色
 * @param profession 职业英文名称
 * @returns CSS颜色值
 */
export function getProfessionColor(profession: string): string {
  initCache()
  if (!profession) return '#6b7280'

  if (professionCache && professionCache.colors.has(profession)) {
    return professionCache.colors.get(profession)!
  }

  return HARDCODED_PROFESSION_COLORS[profession] || '#6b7280'
}

/**
 * 获取职业图标路径
 * @param profession 职业英文名称
 * @returns 图标文件名
 */
export function getProfessionIconPath(profession: string): string {
  if (!profession) return ''

  initCache()
  if (professionCache && professionCache.icons.has(profession)) {
    return professionCache.icons.get(profession)!
  }

  return PROFESSION_ICON_PATHS[profession] || ''
}

/**
 * 获取职业图标URL
 * @param profession 职业英文名称
 * @returns 图标资源的完整URL
 */
export function getProfessionIconUrl(profession: string): string {
  const fileName = getProfessionIconPath(profession)
  if (!fileName) {
    console.warn(`[professionUtils] 职业图标未找到: ${profession}`)
    return ''
  }
  try {
    return new URL(`/src/assets/images/prof/${fileName}`, import.meta.url).href
  } catch (error) {
    console.error(`[professionUtils] 加载职业图标失败: ${profession}`, error)
    return ''
  }
}

/**
 * 初始化职业数据（预加载）
 * 调用此函数可以提前加载职业数据到缓存
 */
export async function initProfessionData(): Promise<void> {
  await loadProfessionData()
}

/**
 * 刷新职业缓存
 */
export async function refreshProfessionCache(): Promise<void> {
  if (professionCache) {
    professionCache.timestamp = 0
  }
  await loadProfessionData()
}

/**
 * 获取所有职业选项
 * @returns 职业选项列表
 */
export async function getAllProfessionOptions(): Promise<DictOption[]> {
  try {
    return await dictionaryService.getOptions('profession')
  } catch (error) {
    console.error('[professionUtils] 获取职业选项失败', error)
    return []
  }
}

/**
 * 检查职业是否有效
 * @param profession 职业英文名称
 * @returns 是否有效
 */
export function isValidProfession(profession: string): boolean {
  if (!profession) return false
  initCache()
  return professionCache!.names.has(profession) || profession in HARDCODED_PROFESSIONS
}

/**
 * 获取所有职业列表
 * @returns 职业英文名称数组
 */
export function getAllProfessions(): string[] {
  return Object.keys(HARDCODED_PROFESSIONS)
}

/**
 * 获取职业信息对象
 * @param profession 职业英文名称
 * @returns 包含名称、颜色、图标路径的对象
 */
export function getProfessionInfo(profession: string): {
  name: string
  color: string
  iconPath: string
  iconUrl: string
} {
  return {
    name: getProfessionName(profession),
    color: getProfessionColor(profession),
    iconPath: getProfessionIconPath(profession),
    iconUrl: getProfessionIconUrl(profession)
  }
}