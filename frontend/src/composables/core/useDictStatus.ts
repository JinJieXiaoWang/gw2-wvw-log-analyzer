/**
 * useDictStatus - 字典状态快捷 Hook
 * 功能：针对最常用的"启用/禁用"类状态，提供极简 API
 * 专门替代 `status === 0 ? '启用' : '禁用'` 这类硬编码三元判断
 *
 * 使用示例：
 *   const { isEnabled, label, severity } = useDictStatus('sys_normal_disable', data.status)
 *   // isEnabled -> true/false
 *   // label -> '启用' | '禁用'
 *   // severity -> 'success' | 'danger'
 */

import { computed, type ComputedRef } from 'vue'
import { useDictStore } from '@/store/system/dict'

export interface DictStatusResult {
  /** 是否启用状态（值为0时） */
  isEnabled: ComputedRef<boolean>
  /** 显示标签 */
  label: ComputedRef<string>
  /** PrimeVue severity */
  severity: ComputedRef<string>
  /** 原始字典项 */
  dictItem: ComputedRef<{ label: string; value: string; css_class?: string } | null>
}

/**
 * 获取字典状态信息
 * @param dictType 字典类型编码（如 'sys_normal_disable'）
 * @param value 当前值
 * @returns 状态信息对象
 */
export function useDictStatus(
  dictType: string,
  value: string | number | undefined | null
): DictStatusResult {
  const dictStore = useDictStore()

  const dictItem = computed(() => {
    if (value === undefined || value === null || value === '') return null
    return dictStore.getDictItem(dictType, value)
  })

  const label = computed(() => {
    if (value === undefined || value === null || value === '') return '-'
    return dictStore.getDictLabel(dictType, value)
  })

  const isEnabled = computed(() => {
    // 常用约定：0 表示启用/正常/是，1 表示禁用/异常/否
    const val = String(value)
    return val === '0' || val === 'true' || val === 'enabled' || val === 'normal'
  })

  const severity = computed(() => {
    const val = String(value).toLowerCase()
    if (val === '0' || val === 'completed' || val === 'success' || val === 'enabled' || val === 'normal') {
      return 'success'
    }
    if (val === '1' || val === 'failed' || val === 'error' || val === 'disabled' || val === 'abnormal') {
      return 'danger'
    }
    if (val === 'pending' || val === 'warning') {
      return 'warning'
    }
    if (val === 'parsing' || val === 'processing') {
      return 'info'
    }
    return 'secondary'
  })

  return {
    isEnabled,
    label,
    severity,
    dictItem,
  }
}

/**
 * useDictStatusSync - 同步版（不触发加载，仅从 Store 读取）
 * 适用于已知字典已预加载的场景
 */
export function useDictStatusSync(
  dictType: string,
  value: string | number | undefined | null
): Omit<DictStatusResult, 'dictItem'> & { color: ComputedRef<string> } {
  const dictStore = useDictStore()

  const label = computed(() => {
    if (value === undefined || value === null || value === '') return '-'
    return dictStore.getDictLabel(dictType, value)
  })

  const color = computed(() => {
    if (value === undefined || value === null) return '#6b7280'
    return dictStore.getDictColor(dictType, value)
  })

  const isEnabled = computed(() => {
    const val = String(value)
    return val === '0' || val === 'true' || val === 'enabled' || val === 'normal'
  })

  const severity = computed(() => {
    const val = String(value).toLowerCase()
    if (val === '0' || val === 'completed' || val === 'success' || val === 'enabled') return 'success'
    if (val === '1' || val === 'failed' || val === 'error' || val === 'disabled') return 'danger'
    if (val === 'pending' || val === 'warning') return 'warning'
    if (val === 'parsing' || val === 'processing') return 'info'
    return 'secondary'
  })

  return {
    isEnabled,
    label,
    severity,
    color,
  }
}
