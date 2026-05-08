/**
 * 字典状态管理（Pinia Store）
 * 功能：全局字典缓存，支持批量加载、标签翻译、颜色查询
 * 设计理念：借鉴若依(RuoYi)字典管理，登录后一次性加载常用字典，组件内直接读取
 * 作者：系统
 * 创建日期：2026-05-07
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dictionaryService } from '@/services/system/dictionaryService'

export interface DictItem {
  label: string
  value: string
  css_class?: string
  is_default: number
}

export const useDictStore = defineStore('dict', () => {
  // ============================================
  // 状态
  // ============================================
  /** 字典缓存 Map<dictType, DictItem[]> */
  const dictCache = ref<Map<string, DictItem[]>>(new Map())
  /** 正在加载的字典类型集合 */
  const loadingTypes = ref<Set<string>>(new Set())
  /** 加载失败的字典类型集合 */
  const failedTypes = ref<Set<string>>(new Set())

  // ============================================
  // Getters (Computed)
  // ============================================

  /**
   * 判断指定字典是否已缓存
   */
  const hasDict = computed(() => (dictType: string): boolean => {
    return dictCache.value.has(dictType) && (dictCache.value.get(dictType)?.length || 0) > 0
  })

  /**
   * 判断指定字典是否正在加载
   */
  const isLoading = computed(() => (dictType: string): boolean => {
    return loadingTypes.value.has(dictType)
  })

  // ============================================
  // Actions
  // ============================================

  /**
   * 获取字典数据（优先缓存）
   * @param dictType 字典类型编码
   * @returns DictItem[] 或 null
   */
  function getDict(dictType: string): DictItem[] | null {
    if (!dictType) return null
    return dictCache.value.get(dictType) || null
  }

  /**
   * 设置字典数据
   * @param dictType 字典类型编码
   * @param data 字典项数组
   */
  function setDict(dictType: string, data: DictItem[]): void {
    if (!dictType) return
    dictCache.value.set(dictType, data)
    failedTypes.value.delete(dictType)
  }

  /**
   * 通过字典值获取标签
   * @param dictType 字典类型编码
   * @param value 字典值
   * @returns 标签文本，找不到返回原值
   */
  function getDictLabel(dictType: string, value: string | number | undefined): string {
    if (value === undefined || value === null || value === '') return '-'
    const dictData = getDict(dictType)
    if (!dictData || dictData.length === 0) return String(value)
    const item = dictData.find((item) => String(item.value) === String(value))
    return item?.label || String(value)
  }

  /**
   * 批量获取字典标签
   * @param dictType 字典类型编码
   * @param values 字典值数组
   * @returns 标签数组
   */
  function getDictLabels(dictType: string, values: (string | number)[]): string[] {
    return values.map((value) => getDictLabel(dictType, value))
  }

  /**
   * 通过字典值获取完整字典项
   * @param dictType 字典类型编码
   * @param value 字典值
   * @returns DictItem 或 null
   */
  function getDictItem(dictType: string, value: string | number): DictItem | null {
    const dictData = getDict(dictType)
    if (!dictData || dictData.length === 0) return null
    const item = dictData.find((item) => String(item.value) === String(value))
    return item || null
  }

  /**
   * 通过字典标签获取值（反向查询）
   * @param dictType 字典类型编码
   * @param label 字典标签
   * @returns 字典值，找不到返回 null
   */
  function getDictValue(dictType: string, label: string): string | null {
    const dictData = getDict(dictType)
    if (!dictData || dictData.length === 0) return null
    const item = dictData.find((item) => item.label === label)
    return item?.value ?? null
  }

  /**
   * 通过字典值获取颜色
   * @param dictType 字典类型编码
   * @param value 字典值
   * @returns 颜色值（css_class），找不到返回 '#6b7280'
   */
  function getDictColor(dictType: string, value: string | number | undefined): string {
    if (value === undefined || value === null) return '#6b7280'
    const item = getDictItem(dictType, value)
    return item?.css_class || '#6b7280'
  }

  /**
   * 移除指定字典缓存
   * @param dictType 字典类型编码
   */
  function removeDict(dictType: string): void {
    dictCache.value.delete(dictType)
    loadingTypes.value.delete(dictType)
    failedTypes.value.delete(dictType)
  }

  /**
   * 清空所有字典缓存
   */
  function cleanDict(): void {
    dictCache.value.clear()
    loadingTypes.value.clear()
    failedTypes.value.clear()
  }

  /**
   * 加载单个字典（带缓存检查）
   * @param dictType 字典类型编码
   * @param forceRefresh 是否强制刷新
   * @returns Promise<DictItem[]>
   */
  async function loadDict(dictType: string, forceRefresh: boolean = false): Promise<DictItem[]> {
    if (!dictType) return []

    // 有缓存且不强制刷新，直接返回
    const cached = getDict(dictType)
    if (cached && !forceRefresh) {
      return cached
    }

    // 正在加载中，等待完成
    if (loadingTypes.value.has(dictType)) {
      // 简单轮询等待
      for (let i = 0; i < 50; i++) {
        await new Promise((r) => setTimeout(r, 100))
        const result = getDict(dictType)
        if (result) return result
      }
      return []
    }

    loadingTypes.value.add(dictType)
    failedTypes.value.delete(dictType)

    try {
      const options = await dictionaryService.getOptions(dictType)
      const items: DictItem[] = options.map((opt) => ({
        label: opt.label || '',
        value: opt.value || '',
        css_class: opt.css_class || '',
        is_default: opt.is_default || 0,
      }))
      setDict(dictType, items)
      return items
    } catch (e) {
      console.error(`[DictStore] 加载字典失败: ${dictType}`, e)
      failedTypes.value.add(dictType)
      return []
    } finally {
      loadingTypes.value.delete(dictType)
    }
  }

  /**
   * 批量加载多个字典（并行）
   * @param dictTypes 字典类型编码数组
   * @param forceRefresh 是否强制刷新
   * @returns Promise<Record<string, DictItem[]>>
   */
  async function loadDicts(dictTypes: string[], forceRefresh: boolean = false): Promise<Record<string, DictItem[]>> {
    const promises = dictTypes.map(async (type) => {
      const data = await loadDict(type, forceRefresh)
      return { type, data }
    })

    const results = await Promise.all(promises)
    const map: Record<string, DictItem[]> = {}
    for (const r of results) {
      map[r.type] = r.data
    }
    return map
  }

  /**
   * 登录后批量预加载常用字典
   * 建议在登录成功后调用，一次性加载系统常用字典到缓存
   */
  async function preloadCommonDicts(): Promise<void> {
    const commonTypes = [
      'profession',
      'specialization',
      'role',
      'scoring_dimension',
      'game_mode',
    ]
    await loadDicts(commonTypes)
    console.info('[DictStore] 常用字典预加载完成')
  }

  /**
   * 刷新指定字典（清除缓存后重新加载）
   * @param dictType 字典类型编码
   */
  async function refreshDict(dictType: string): Promise<DictItem[]> {
    removeDict(dictType)
    return loadDict(dictType, true)
  }

  /**
   * 刷新所有字典缓存
   */
  async function refreshAllDicts(): Promise<void> {
    const types = Array.from(dictCache.value.keys())
    for (const type of types) {
      await refreshDict(type)
    }
  }

  return {
    dictCache,
    loadingTypes,
    failedTypes,
    hasDict,
    isLoading,
    getDict,
    setDict,
    getDictLabel,
    getDictLabels,
    getDictItem,
    getDictValue,
    getDictColor,
    removeDict,
    cleanDict,
    loadDict,
    loadDicts,
    preloadCommonDicts,
    refreshDict,
    refreshAllDicts,
  }
})
