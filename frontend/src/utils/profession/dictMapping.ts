/**
 * 字典值映射工具模块
 * 功能：提供字典值到标签和颜色的映射功能，支持职业和精英特长两种字典类型
 * 作者：帅姐姐
 * 创建日期：2026-05-01
 * 
 * 该模块实现了前端字典值映射功能：
 * 1. 优先从字典API获取数据
 * 2. 失败时使用本地硬编码数据作为回退
 * 3. 支持职业(profession)和精英特长(specialization)两种字典类型
 * 4. 提供缓存机制优化性能
 */

import { dictionaryService, type DictOption } from '@/services/system/dictionaryService'

/**
 * 字典映射缓存结构
 */
interface DictMappingCache {
  options: DictOption[]
  valueToLabel: Map<string, string>
  valueToColor: Map<string, string>
  timestamp: number
}

/**
 * 缓存有效期（毫秒）- 默认10分钟
 */
const CACHE_TTL = 10 * 60 * 1000

/**
 * 全局字典映射缓存
 */
const dictMappingCache = new Map<string, DictMappingCache>()

/**
 * 硬编码的职业字典数据（回退用）
 */
const HARDCODED_PROFESSIONS: DictOption[] = [
  { value: 'Guardian', label: '守护者', css_class: '#FBCF4B', is_default: 0 },
  { value: 'Dragonhunter', label: '猎龙者', css_class: '#E89F48', is_default: 0 },
  { value: 'Firebrand', label: '燃火者', css_class: '#F5AD1F', is_default: 0 },
  { value: 'Willbender', label: '破锋者', css_class: '#FFDF80', is_default: 0 },
  { value: 'Luminary', label: '圣辉者', css_class: '#FFD700', is_default: 0 },
  { value: 'Warrior', label: '战士', css_class: '#FFDA6B', is_default: 0 },
  { value: 'Berserker', label: '狂战士', css_class: '#FF9900', is_default: 0 },
  { value: 'Spellbreaker', label: '破法者', css_class: '#EFD97D', is_default: 0 },
  { value: 'Bladesworn', label: '誓剑士', css_class: '#D7AF69', is_default: 0 },
  { value: 'Paragon', label: '圣言士', css_class: '#FFC864', is_default: 0 },
  { value: 'Engineer', label: '工程师', css_class: '#B8742C', is_default: 0 },
  { value: 'Scrapper', label: '机械师', css_class: '#A08C50', is_default: 0 },
  { value: 'Holosmith', label: '全息师', css_class: '#FFD700', is_default: 0 },
  { value: 'Mechanist', label: '玉偃师', css_class: '#D09C59', is_default: 0 },
  { value: 'Amalgam', label: '流金师', css_class: '#C8B478', is_default: 0 },
  { value: 'Ranger', label: '游侠', css_class: '#77BA4F', is_default: 0 },
  { value: 'Druid', label: '德鲁伊', css_class: '#59A63B', is_default: 0 },
  { value: 'Soulbeast', label: '魂兽师', css_class: '#6DB045', is_default: 0 },
  { value: 'Untamed', label: '狂兽师', css_class: '#8BC463', is_default: 0 },
  { value: 'Galeshot', label: '风冲击', css_class: '#9BD473', is_default: 0 },
  { value: 'Thief', label: '潜行者', css_class: '#9B8AC9', is_default: 0 },
  { value: 'Daredevil', label: '独行侠', css_class: '#8A7BB9', is_default: 0 },
  { value: 'Deadeye', label: '神枪手', css_class: '#7A6AB9', is_default: 0 },
  { value: 'Specter', label: '缚影者', css_class: '#AA9AD9', is_default: 0 },
  { value: 'Antiquary', label: '彩戏师', css_class: '#BAABD9', is_default: 0 },
  { value: 'Elementalist', label: '元素使', css_class: '#E63757', is_default: 0 },
  { value: 'Tempest', label: '暴风使', css_class: '#D62747', is_default: 0 },
  { value: 'Weaver', label: '编织者', css_class: '#C61737', is_default: 0 },
  { value: 'Catalyst', label: '元晶师', css_class: '#F64767', is_default: 0 },
  { value: 'Evoker', label: '唤元师', css_class: '#FF5777', is_default: 0 },
  { value: 'Mesmer', label: '幻术师', css_class: '#B35FCF', is_default: 0 },
  { value: 'Chronomancer', label: '时空术士', css_class: '#A34FCF', is_default: 0 },
  { value: 'Mirage', label: '幻象术士', css_class: '#933FCF', is_default: 0 },
  { value: 'Virtuoso', label: '灵刃术士', css_class: '#C36FDF', is_default: 0 },
  { value: 'Troubadour', label: '吟游诗人', css_class: '#D37FEF', is_default: 0 },
  { value: 'Necromancer', label: '死灵法师', css_class: '#6C7A26', is_default: 0 },
  { value: 'Reaper', label: '夺魂者', css_class: '#5C6A16', is_default: 0 },
  { value: 'Scourge', label: '灾厄师', css_class: '#4C5A06', is_default: 0 },
  { value: 'Harbinger', label: '先驱者', css_class: '#7C8A36', is_default: 0 },
  { value: 'Ritualist', label: '祭祀者', css_class: '#8C9A46', is_default: 0 },
  { value: 'Revenant', label: '魂武者', css_class: '#00C896', is_default: 0 },
  { value: 'Herald', label: '预告者', css_class: '#00B886', is_default: 0 },
  { value: 'Renegade', label: '龙魂使', css_class: '#00A876', is_default: 0 },
  { value: 'Vindicator', label: '裁决者', css_class: '#00D8A6', is_default: 0 },
  { value: 'Conduit', label: '契灵使', css_class: '#00E8B6', is_default: 0 }
]

/**
 * 硬编码的精英特长字典数据（回退用）
 */
const HARDCODED_SPECIALIZATIONS: DictOption[] = [
  { value: 'Dragonhunter', label: '猎龙者', css_class: '#E89F48', is_default: 0 },
  { value: 'Firebrand', label: '燃火者', css_class: '#F5AD1F', is_default: 0 },
  { value: 'Willbender', label: '破锋者', css_class: '#FFDF80', is_default: 0 },
  { value: 'Luminary', label: '圣辉者', css_class: '#FFD700', is_default: 0 },
  { value: 'Berserker', label: '狂战士', css_class: '#FF9900', is_default: 0 },
  { value: 'Spellbreaker', label: '破法者', css_class: '#EFD97D', is_default: 0 },
  { value: 'Bladesworn', label: '誓剑士', css_class: '#D7AF69', is_default: 0 },
  { value: 'Paragon', label: '圣言士', css_class: '#FFC864', is_default: 0 },
  { value: 'Scrapper', label: '机械师', css_class: '#A08C50', is_default: 0 },
  { value: 'Holosmith', label: '全息师', css_class: '#FFD700', is_default: 0 },
  { value: 'Mechanist', label: '玉偃师', css_class: '#D09C59', is_default: 0 },
  { value: 'Amalgam', label: '流金师', css_class: '#C8B478', is_default: 0 },
  { value: 'Druid', label: '德鲁伊', css_class: '#59A63B', is_default: 0 },
  { value: 'Soulbeast', label: '魂兽师', css_class: '#6DB045', is_default: 0 },
  { value: 'Untamed', label: '狂兽师', css_class: '#8BC463', is_default: 0 },
  { value: 'Galeshot', label: '风冲击', css_class: '#9BD473', is_default: 0 },
  { value: 'Daredevil', label: '独行侠', css_class: '#8A7BB9', is_default: 0 },
  { value: 'Deadeye', label: '神枪手', css_class: '#7A6AB9', is_default: 0 },
  { value: 'Specter', label: '缚影者', css_class: '#AA9AD9', is_default: 0 },
  { value: 'Antiquary', label: '彩戏师', css_class: '#BAABD9', is_default: 0 },
  { value: 'Tempest', label: '暴风使', css_class: '#D62747', is_default: 0 },
  { value: 'Weaver', label: '编织者', css_class: '#C61737', is_default: 0 },
  { value: 'Catalyst', label: '元晶师', css_class: '#F64767', is_default: 0 },
  { value: 'Evoker', label: '唤元师', css_class: '#FF5777', is_default: 0 },
  { value: 'Chronomancer', label: '时空术士', css_class: '#A34FCF', is_default: 0 },
  { value: 'Mirage', label: '幻象术士', css_class: '#933FCF', is_default: 0 },
  { value: 'Virtuoso', label: '灵刃术士', css_class: '#C36FDF', is_default: 0 },
  { value: 'Troubadour', label: '吟游诗人', css_class: '#D37FEF', is_default: 0 },
  { value: 'Reaper', label: '夺魂者', css_class: '#5C6A16', is_default: 0 },
  { value: 'Scourge', label: '灾厄师', css_class: '#4C5A06', is_default: 0 },
  { value: 'Harbinger', label: '先驱者', css_class: '#7C8A36', is_default: 0 },
  { value: 'Ritualist', label: '祭祀者', css_class: '#8C9A46', is_default: 0 },
  { value: 'Herald', label: '预告者', css_class: '#00B886', is_default: 0 },
  { value: 'Renegade', label: '龙魂使', css_class: '#00A876', is_default: 0 },
  { value: 'Vindicator', label: '裁决者', css_class: '#00D8A6', is_default: 0 },
  { value: 'Conduit', label: '契灵使', css_class: '#00E8B6', is_default: 0 }
]

/**
 * 获取硬编码的字典数据
 * @param dictType 字典类型
 * @returns DictOption[]
 */
function getHardcodedOptions(dictType: string): DictOption[] {
  switch (dictType) {
    case 'profession':
    case 'occupation':
      return HARDCODED_PROFESSIONS
    case 'specialization':
    case 'elite_specialty':
      return HARDCODED_SPECIALIZATIONS
    default:
      return []
  }
}

/**
 * 构建映射缓存
 * @param options 字典选项数组
 * @returns DictMappingCache
 */
function buildCache(options: DictOption[]): DictMappingCache {
  const valueToLabel = new Map<string, string>()
  const valueToColor = new Map<string, string>()
  
  for (const option of options) {
    valueToLabel.set(option.value, option.label)
    if (option.css_class) {
      valueToColor.set(option.value, option.css_class)
    }
  }
  
  return {
    options,
    valueToLabel,
    valueToColor,
    timestamp: Date.now()
  }
}

/**
 * 检查缓存是否有效
 * @param cache 缓存条目
 * @returns boolean
 */
function isCacheValid(cache: DictMappingCache | undefined): boolean {
  if (!cache) return false
  return Date.now() - cache.timestamp < CACHE_TTL
}

/**
 * 加载字典映射数据
 * @param dictType 字典类型（支持 profession/occupation, specialization/elite_specialty）
 * @param useCache 是否使用缓存（默认true）
 * @returns Promise<DictMappingCache>
 */
export async function loadDictMapping(
  dictType: string,
  useCache: boolean = true
): Promise<DictMappingCache> {
  // 标准化字典类型
  const normalizedType = dictType.toLowerCase().trim()
  
  // 检查缓存
  if (useCache) {
    const cached = dictMappingCache.get(normalizedType)
    if (cached && isCacheValid(cached)) {
      return cached
    }
  }
  
  // 尝试从API获取数据
  let options: DictOption[] = []
  try {
    options = await dictionaryService.getOptions(normalizedType)
  } catch (error) {
    console.warn(`[DictMapping] 从API获取字典数据失败，使用回退数据: ${normalizedType}`, error)
  }
  
  // 如果API返回为空，使用硬编码数据
  if (!options || options.length === 0) {
    options = getHardcodedOptions(normalizedType)
    console.log(`[DictMapping] 使用硬编码字典数据: ${normalizedType}`)
  }
  
  // 构建并缓存
  const cache = buildCache(options)
  dictMappingCache.set(normalizedType, cache)
  
  return cache
}

/**
 * 获取字典标签（同步方法，使用缓存）
 * @param dictType 字典类型
 * @param value 字典值
 * @param defaultValue 默认值
 * @returns string
 */
export function getDictLabel(
  dictType: string,
  value: string | null | undefined,
  defaultValue: string = '-'
): string {
  if (!value) return defaultValue
  
  const normalizedType = dictType.toLowerCase().trim()
  const cached = dictMappingCache.get(normalizedType)
  
  if (cached && isCacheValid(cached)) {
    return cached.valueToLabel.get(value) || defaultValue
  }
  
  // 如果缓存不存在，尝试从硬编码数据获取
  const options = getHardcodedOptions(normalizedType)
  const option = options.find(opt => opt.value === value)
  return option?.label || defaultValue
}

/**
 * 获取字典颜色（同步方法，使用缓存）
 * @param dictType 字典类型
 * @param value 字典值
 * @param defaultColor 默认颜色
 * @returns string
 */
export function getDictColor(
  dictType: string,
  value: string | null | undefined,
  defaultColor: string = '#6b7280'
): string {
  if (!value) return defaultColor
  
  const normalizedType = dictType.toLowerCase().trim()
  const cached = dictMappingCache.get(normalizedType)
  
  if (cached && isCacheValid(cached)) {
    return cached.valueToColor.get(value) || defaultColor
  }
  
  // 如果缓存不存在，尝试从硬编码数据获取
  const options = getHardcodedOptions(normalizedType)
  const option = options.find(opt => opt.value === value)
  return option?.css_class || defaultColor
}

/**
 * 获取字典选项列表（同步方法，使用缓存）
 * @param dictType 字典类型
 * @returns DictOption[]
 */
export function getDictOptions(dictType: string): DictOption[] {
  const normalizedType = dictType.toLowerCase().trim()
  const cached = dictMappingCache.get(normalizedType)
  
  if (cached && isCacheValid(cached)) {
    return cached.options
  }
  
  // 如果缓存不存在，返回硬编码数据
  return getHardcodedOptions(normalizedType)
}

/**
 * 异步获取字典标签
 * @param dictType 字典类型
 * @param value 字典值
 * @param defaultValue 默认值
 * @returns Promise<string>
 */
export async function getDictLabelAsync(
  dictType: string,
  value: string | null | undefined,
  defaultValue: string = '-'
): Promise<string> {
  if (!value) return defaultValue
  
  await loadDictMapping(dictType)
  return getDictLabel(dictType, value, defaultValue)
}

/**
 * 异步获取字典颜色
 * @param dictType 字典类型
 * @param value 字典值
 * @param defaultColor 默认颜色
 * @returns Promise<string>
 */
export async function getDictColorAsync(
  dictType: string,
  value: string | null | undefined,
  defaultColor: string = '#6b7280'
): Promise<string> {
  if (!value) return defaultColor
  
  await loadDictMapping(dictType)
  return getDictColor(dictType, value, defaultColor)
}

/**
 * 预加载字典数据
 * @param dictTypes 字典类型数组
 * @returns Promise<void>
 */
export async function preloadDictMappings(dictTypes: string[]): Promise<void> {
  const promises = dictTypes.map(type => loadDictMapping(type))
  await Promise.all(promises)
}

/**
 * 清除指定类型的字典缓存
 * @param dictType 字典类型
 */
export function clearDictMappingCache(dictType?: string): void {
  if (dictType) {
    const normalizedType = dictType.toLowerCase().trim()
    dictMappingCache.delete(normalizedType)
  } else {
    dictMappingCache.clear()
  }
}

/**
 * 获取所有已缓存的字典类型
 * @returns string[]
 */
export function getCachedDictTypes(): string[] {
  const now = Date.now()
  const validTypes: string[] = []
  
  for (const [type, cache] of dictMappingCache.entries()) {
    if (now - cache.timestamp < CACHE_TTL) {
      validTypes.push(type)
    }
  }
  
  return validTypes
}

/**
 * 字典映射结果接口
 */
export interface DictMappingResult {
  label: string
  color: string
  found: boolean
}

/**
 * 获取完整的字典映射结果
 * @param dictType 字典类型
 * @param value 字典值
 * @returns DictMappingResult
 */
export function getDictMapping(
  dictType: string,
  value: string | null | undefined
): DictMappingResult {
  if (!value) {
    return {
      label: '-',
      color: '#6b7280',
      found: false
    }
  }
  
  const normalizedType = dictType.toLowerCase().trim()
  const cached = dictMappingCache.get(normalizedType)
  
  let label: string
  let color: string
  let found: boolean
  
  if (cached && isCacheValid(cached)) {
    label = cached.valueToLabel.get(value) || '-'
    color = cached.valueToColor.get(value) || '#6b7280'
    found = cached.valueToLabel.has(value)
  } else {
    // 从硬编码数据获取
    const options = getHardcodedOptions(normalizedType)
    const option = options.find(opt => opt.value === value)
    
    if (option) {
      label = option.label
      color = option.css_class || '#6b7280'
      found = true
    } else {
      label = value
      color = '#6b7280'
      found = false
    }
  }
  
  return { label, color, found }
}
