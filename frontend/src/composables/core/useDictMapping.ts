/**
 * 字典映射组合式函数
 * 功能：提供响应式的字典数据访问接口，支持缓存和自动刷新
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { ref, computed, watch, onMounted, type Ref } from 'vue'
import { dictionaryService, type DictOption, type DictData, type DictType } from '@/services/system/dictionaryService'
import { professionService } from '@/services/professionService'

/**
 * 缓存条目结构
 */
interface CacheEntry<T> {
  data: T
  timestamp: number
}

/**
 * 缓存有效期（毫秒）- 默认5分钟
 */
const DEFAULT_CACHE_TTL = 5 * 60 * 1000

/**
 * 全局字典缓存
 */
const globalCache = new Map<string, CacheEntry<any>>()

/**
 * 清理过期缓存
 */
function cleanExpiredCache(dictType?: string): void {
  const now = Date.now()
  if (dictType) {
    const entry = globalCache.get(dictType)
    if (entry && now - entry.timestamp > DEFAULT_CACHE_TTL) {
      globalCache.delete(dictType)
    }
  } else {
    for (const [key, entry] of globalCache.entries()) {
      if (now - entry.timestamp > DEFAULT_CACHE_TTL) {
        globalCache.delete(key)
      }
    }
  }
}

/**
 * 清除所有字典缓存
 */
export function clearDictCache(): void {
  globalCache.clear()
}

/**
 * 清除指定类型缓存
 */
export function clearDictCacheByType(dictType: string): void {
  globalCache.delete(dictType)
}

// =============================================
// useDictMapping - 通用字典映射Hook
// =============================================

/**
 * 字典映射组合式函数
 * @param dictType 字典类型编码
 * @param autoLoad 是否自动加载，默认true
 * @returns 字典数据和相关方法
 */
export function useDictMapping(dictType: Ref<string> | string, autoLoad: boolean = true) {
  const data = ref<DictOption[]>([]) as Ref<DictOption[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const lastUpdated = ref<number>(0)

  const type = typeof dictType === 'string' ? ref(dictType) : dictType

  /**
   * 加载字典数据
   */
  async function loadDictData(): Promise<void> {
    if (!type.value) return

    // 检查缓存
    cleanExpiredCache(type.value)
    const cached = globalCache.get(type.value)
    if (cached && Date.now() - cached.timestamp < DEFAULT_CACHE_TTL) {
      data.value = cached.data
      lastUpdated.value = cached.timestamp
      return
    }

    loading.value = true
    error.value = null

    try {
      const result = await dictionaryService.getOptions(type.value)
      data.value = result
      lastUpdated.value = Date.now()
      globalCache.set(type.value, { data: result, timestamp: Date.now() })
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载字典数据失败')
      console.error(`[useDictMapping] 加载字典失败: ${type.value}`, err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 值转标签
   */
  function getLabel(value: string): string {
    const option = data.value.find(opt => opt.value === value)
    return option ? option.label : value
  }

  /**
   * 获取颜色
   */
  function getColor(value: string): string {
    const option = data.value.find(opt => opt.value === value)
    return option?.css_class || '#6b7280'
  }

  /**
   * 获取选项
   */
  function getOption(value: string): DictOption | undefined {
    return data.value.find(opt => opt.value === value)
  }

  /**
   * 刷新数据
   */
  async function refresh(): Promise<void> {
    clearDictCacheByType(type.value)
    await loadDictData()
  }

  // 自动加载
  if (autoLoad) {
    onMounted(() => {
      if (type.value) {
        loadDictData()
      }
    })

    // 监听类型变化
    watch(type, async (newType, oldType) => {
      if (newType !== oldType && newType) {
        await loadDictData()
      }
    })
  }

  return {
    data,
    loading,
    error,
    lastUpdated,
    loadDictData,
    getLabel,
    getColor,
    getOption,
    refresh
  }
}

// =============================================
// useDictLabel - 快速获取标签值
// =============================================

/**
 * 快速字典标签获取
 * @param dictType 字典类型
 * @param value 字典值
 * @returns ComputedRef<string>
 */
export function useDictLabel(dictType: string, value: Ref<string> | string) {
  const typeRef = ref(dictType)
  const { data, loadDictData } = useDictMapping(typeRef, true)

  const val = typeof value === 'string' ? ref(value) : value

  const label = computed(() => {
    if (!val.value) return ''
    const option = data.value.find(opt => opt.value === val.value)
    return option ? option.label : val.value
  })

  return {
    label,
    loading: ref(false),
    error: ref(null),
    refresh: loadDictData
  }
}

// =============================================
// useProfessions - 职业数据专用Hook
// 说明：职业数据由专用 professionService 管理，不从字典表获取
// =============================================

/**
 * 职业数据组合式函数
 * @param autoLoad 是否自动加载
 * @returns 职业数据和方法
 */
export function useProfessions(autoLoad: boolean = true) {
  const PROFESSION_CACHE_KEY = 'profession_api'

  const data = ref<DictOption[]>([]) as Ref<DictOption[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * 加载职业数据（从 professionService API，不从字典表）
   */
  async function loadProfessions(): Promise<void> {
    cleanExpiredCache(PROFESSION_CACHE_KEY)
    const cached = globalCache.get(PROFESSION_CACHE_KEY)
    if (cached) {
      data.value = cached.data
      return
    }

    loading.value = true
    error.value = null

    try {
      const professions = await professionService.getProfessions(false)
      const result: DictOption[] = professions.map(p => ({
        value: p.profession_key,
        label: p.profession_name,
        css_class: p.color,
        is_default: 0
      }))
      data.value = result
      globalCache.set(PROFESSION_CACHE_KEY, { data: result, timestamp: Date.now() })
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载职业数据失败')
      console.error('[useProfessions] 加载职业数据失败', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取职业中文名
   */
  function getProfessionName(profession: string): string {
    if (!profession) return ''
    const option = data.value.find(opt => opt.value === profession)
    return option ? option.label : profession
  }

  /**
   * 获取职业颜色
   */
  function getProfessionColor(profession: string): string {
    if (!profession) return '#6b7280'
    const option = data.value.find(opt => opt.value === profession)
    return option?.css_class || '#6b7280'
  }

  /**
   * 获取职业图标URL
   */
  function getProfessionIcon(profession: string): string {
    if (!profession) return ''
    const option = data.value.find(opt => opt.value === profession)
    return option?.css_class || ''
  }

  /**
   * 获取职业选项
   */
  function getProfessionOption(profession: string): DictOption | undefined {
    return data.value.find(opt => opt.value === profession)
  }

  /**
   * 刷新职业数据
   */
  async function refresh(): Promise<void> {
    clearDictCacheByType(PROFESSION_CACHE_KEY)
    await loadProfessions()
  }

  if (autoLoad) {
    onMounted(loadProfessions)
  }

  return {
    data,
    loading,
    error,
    loadProfessions,
    getProfessionName,
    getProfessionColor,
    getProfessionIcon,
    getProfessionOption,
    refresh
  }
}

// =============================================
// useRoles - 角色定位字典专用Hook
// =============================================

/**
 * 角色定位字典组合式函数
 */
export function useRoles(autoLoad: boolean = true) {
  const ROLE_CACHE_KEY = 'role'

  const data = ref<DictOption[]>([]) as Ref<DictOption[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * 加载角色字典
   */
  async function loadRoles(): Promise<void> {
    cleanExpiredCache(ROLE_CACHE_KEY)
    const cached = globalCache.get(ROLE_CACHE_KEY)
    if (cached) {
      data.value = cached.data
      return
    }

    loading.value = true
    error.value = null

    try {
      const result = await dictionaryService.getOptions('role')
      data.value = result
      globalCache.set(ROLE_CACHE_KEY, { data: result, timestamp: Date.now() })
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载角色字典失败')
      console.error('[useRoles] 加载角色字典失败', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取角色中文名
   */
  function getRoleName(role: string): string {
    if (!role) return ''
    const option = data.value.find(opt => opt.value === role)
    return option ? option.label : role
  }

  /**
   * 获取角色颜色
   */
  function getRoleColor(role: string): string {
    if (!role) return '#6b7280'
    const option = data.value.find(opt => opt.value === role)
    return option?.css_class || '#6b7280'
  }

  /**
   * 刷新角色数据
   */
  async function refresh(): Promise<void> {
    clearDictCacheByType(ROLE_CACHE_KEY)
    await loadRoles()
  }

  if (autoLoad) {
    onMounted(loadRoles)
  }

  return {
    data,
    loading,
    error,
    loadRoles,
    getRoleName,
    getRoleColor,
    refresh
  }
}

// =============================================
// useSpecializations - 精英特长数据专用Hook
// 说明：精英特长数据由专用 professionService 管理，不从字典表获取
// =============================================

/**
 * 精英特长数据组合式函数
 */
export function useSpecializations(autoLoad: boolean = true) {
  const SPEC_CACHE_KEY = 'specialization_api'

  const data = ref<DictOption[]>([]) as Ref<DictOption[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * 加载精英特长数据（从 professionService API，不从字典表）
   */
  async function loadSpecializations(): Promise<void> {
    cleanExpiredCache(SPEC_CACHE_KEY)
    const cached = globalCache.get(SPEC_CACHE_KEY)
    if (cached) {
      data.value = cached.data
      return
    }

    loading.value = true
    error.value = null

    try {
      const specs = await professionService.getEliteSpecs()
      const result: DictOption[] = specs.map(s => ({
        value: s.spec_key,
        label: s.spec_name,
        css_class: s.color,
        is_default: 0
      }))
      data.value = result
      globalCache.set(SPEC_CACHE_KEY, { data: result, timestamp: Date.now() })
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载精英特长数据失败')
      console.error('[useSpecializations] 加载精英特长数据失败', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取特长中文名
   */
  function getSpecializationName(spec: string): string {
    if (!spec) return ''
    const option = data.value.find(opt => opt.value === spec)
    return option ? option.label : spec
  }

  /**
   * 刷新数据
   */
  async function refresh(): Promise<void> {
    clearDictCacheByType(SPEC_CACHE_KEY)
    await loadSpecializations()
  }

  if (autoLoad) {
    onMounted(loadSpecializations)
  }

  return {
    data,
    loading,
    error,
    loadSpecializations,
    getSpecializationName,
    refresh
  }
}

// =============================================
// useGameModes - 游戏模式字典专用Hook
// =============================================

/**
 * 游戏模式字典组合式函数
 */
export function useGameModes(autoLoad: boolean = true) {
  const MODE_CACHE_KEY = 'game_mode'

  const data = ref<DictOption[]>([]) as Ref<DictOption[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * 加载游戏模式字典
   */
  async function loadGameModes(): Promise<void> {
    cleanExpiredCache(MODE_CACHE_KEY)
    const cached = globalCache.get(MODE_CACHE_KEY)
    if (cached) {
      data.value = cached.data
      return
    }

    loading.value = true
    error.value = null

    try {
      const result = await dictionaryService.getOptions('game_mode')
      data.value = result
      globalCache.set(MODE_CACHE_KEY, { data: result, timestamp: Date.now() })
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载游戏模式字典失败')
      console.error('[useGameModes] 加载游戏模式字典失败', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取模式名称
   */
  function getModeName(mode: string): string {
    if (!mode) return ''
    const option = data.value.find(opt => opt.value === mode)
    return option ? option.label : mode
  }

  /**
   * 刷新数据
   */
  async function refresh(): Promise<void> {
    clearDictCacheByType(MODE_CACHE_KEY)
    await loadGameModes()
  }

  if (autoLoad) {
    onMounted(loadGameModes)
  }

  return {
    data,
    loading,
    error,
    loadGameModes,
    getModeName,
    refresh
  }
}

// =============================================
// useDictTypes - 字典类型管理Hook
// =============================================

/**
 * 字典类型管理组合式函数
 */
export function useDictTypes(autoLoad: boolean = true) {
  const data = ref<DictType[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * 加载字典类型列表
   */
  async function loadDictTypes(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const result = await dictionaryService.getAllTypes()
      data.value = result
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载字典类型失败')
      console.error('[useDictTypes] 加载字典类型失败', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新数据
   */
  async function refresh(): Promise<void> {
    await loadDictTypes()
  }

  if (autoLoad) {
    onMounted(loadDictTypes)
  }

  return {
    data,
    loading,
    error,
    loadDictTypes,
    refresh
  }
}

// =============================================
// useDictData - 字典数据管理Hook
// =============================================

/**
 * 字典数据管理组合式函数
 */
export function useDictData(dictType: Ref<string> | string, autoLoad: boolean = true) {
  const data = ref<DictData[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(50)

  const type = typeof dictType === 'string' ? ref(dictType) : dictType

  /**
   * 加载字典数据（分页）
   */
  async function loadDictData(): Promise<void> {
    if (!type.value) return

    loading.value = true
    error.value = null

    try {
      const result = await dictionaryService.getData(type.value, page.value, pageSize.value)
      if (result) {
        data.value = result.items
        total.value = result.total
      }
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('加载字典数据失败')
      console.error(`[useDictData] 加载字典数据失败: ${type.value}`, err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新数据
   */
  async function refresh(): Promise<void> {
    await loadDictData()
  }

  /**
   * 设置页码
   */
  function setPage(newPage: number): void {
    page.value = newPage
    loadDictData()
  }

  /**
   * 设置每页数量
   */
  function setPageSize(newSize: number): void {
    pageSize.value = newSize
    page.value = 1
    loadDictData()
  }

  if (autoLoad) {
    onMounted(() => {
      if (type.value) {
        loadDictData()
      }
    })

    watch(type, async (newType, oldType) => {
      if (newType !== oldType && newType) {
        page.value = 1
        await loadDictData()
      }
    })
  }

  return {
    data,
    loading,
    error,
    total,
    page,
    pageSize,
    loadDictData,
    refresh,
    setPage,
    setPageSize
  }
}