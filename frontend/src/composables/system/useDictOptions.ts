/**
 * useDictOptions - 字典选项动态获取组合式函数
 * 功能：从字典表动态获取选项列表，替代前端硬编码选项
 * 说明：与 useDictMapping 互补，专注于获取选项列表（下拉框、单选等）
 *       底层缓存统一使用 useDictMapping 的 globalCache + TTL 机制
 */

import { ref, computed, onMounted } from 'vue'
import { dictionaryService } from '@/services'
import type { DictOption } from '@/services'
import { globalCache, cleanExpiredCache } from '@/composables/core/useDictMapping'

// 本地 reactive 镜像，用于向消费端提供响应式接口
// 真正的缓存源为 useDictMapping 中的 globalCache（Map + TTL）
const optionsCache = ref<Record<string, DictOption[]>>({})
const optionsLoading = ref<Record<string, boolean>>({})
const optionsError = ref<Record<string, Error | null>>({})

/**
 * 获取单个字典类型的选项列表
 * @param dictType 字典类型编码
 * @param immediate 是否立即加载
 * @param fallbackOptions API失败时的回退选项
 */
export function useDictOptions(
  dictType: string,
  immediate: boolean = true,
  fallbackOptions: DictOption[] = []
) {
  const options = computed<DictOption[]>(() => {
    // 优先同步 globalCache（含 TTL），再回退到本地镜像和 fallback
    cleanExpiredCache(dictType)
    const cached = globalCache.get(dictType)
    if (cached && cached.data.length > 0) {
      return cached.data
    }
    const local = optionsCache.value[dictType]
    if (local && local.length > 0) return local
    return fallbackOptions
  })
  const loading = computed(() => optionsLoading.value[dictType] || false)
  const error = computed(() => optionsError.value[dictType] || null)

  const loadOptions = async (force: boolean = false): Promise<DictOption[]> => {
    if (!force) {
      cleanExpiredCache(dictType)
      const cached = globalCache.get(dictType)
      if (cached) {
        optionsCache.value[dictType] = cached.data
        return cached.data
      }
    } else {
      // 强制刷新时同时清理全局缓存
      globalCache.delete(dictType)
    }

    optionsLoading.value[dictType] = true
    optionsError.value[dictType] = null
    try {
      const data = await dictionaryService.getOptions(dictType)
      optionsCache.value[dictType] = data
      globalCache.set(dictType, { data, timestamp: Date.now() })
      return data
    } catch (err) {
      const e = err instanceof Error ? err : new Error(`加载字典 ${dictType} 失败`)
      optionsError.value[dictType] = e
      console.error(`[useDictOptions] ${dictType}:`, e)
      return fallbackOptions
    } finally {
      optionsLoading.value[dictType] = false
    }
  }

  const getLabel = (value: string): string => {
    const opt = options.value.find(o => o.value === value)
    return opt?.label || value
  }

  const getDefaultValue = (): string => {
    const opt = options.value.find(o => o.is_default === 1)
    return opt?.value || options.value[0]?.value || ''
  }

  if (immediate) {
    onMounted(() => {
      loadOptions()
    })
  }

  return {
    options,
    loading,
    error,
    loadOptions,
    getLabel,
    getDefaultValue,
  }
}

/**
 * 批量获取多个字典类型的选项
 * @param dictTypes 字典类型编码数组
 */
export function useMultiDictOptions(dictTypes: string[]) {
  const allLoading = computed(() =>
    dictTypes.some(t => optionsLoading.value[t])
  )
  const allLoaded = computed(() =>
    dictTypes.every(t => {
      cleanExpiredCache(t)
      return globalCache.has(t) || optionsCache.value[t] !== undefined
    })
  )

  const loadAll = async (): Promise<Record<string, DictOption[]>> => {
    const results: Record<string, DictOption[]> = {}
    await Promise.all(
      dictTypes.map(async (type) => {
        cleanExpiredCache(type)
        const cached = globalCache.get(type)
        if (cached) {
          optionsCache.value[type] = cached.data
          results[type] = cached.data
          return
        }
        optionsLoading.value[type] = true
        try {
          const data = await dictionaryService.getOptions(type)
          optionsCache.value[type] = data
          globalCache.set(type, { data, timestamp: Date.now() })
          results[type] = data
        } catch (err) {
          console.error(`[useMultiDictOptions] ${type}:`, err)
          results[type] = []
        } finally {
          optionsLoading.value[type] = false
        }
      })
    )
    return results
  }

  const getOptions = (dictType: string): DictOption[] => {
    cleanExpiredCache(dictType)
    const cached = globalCache.get(dictType)
    return cached?.data || optionsCache.value[dictType] || []
  }

  const getLabel = (dictType: string, value: string): string => {
    const opts = getOptions(dictType)
    const opt = opts.find(o => o.value === value)
    return opt?.label || value
  }

  return {
    allLoading,
    allLoaded,
    loadAll,
    getOptions,
    getLabel,
  }
}
