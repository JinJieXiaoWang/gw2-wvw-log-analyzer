/**
 * 数据获取组合式函数
 * 功能：提供统一的数据获取接口，支持Mock和真实API切换
 * 作者：System
 * 创建日期：2024-01-15
 */

import { ref, computed, type Ref } from 'vue'
import { mockDataService } from '@/services/core/mockData'
import type { LogFile, PlayerStats, BuildCode, DashboardStats, AttendanceRecord } from '@/types'

interface UseDataListOptions<T> {
  fetchData: () => Promise<T[]>
  initialData?: T[]
  loadingDelay?: number
}

interface UseDataListReturn<T> {
  data: Ref<T[]>
  loading: Ref<boolean>
  error: Ref<Error | null>
  refresh: () => Promise<void>
  isEmpty: (data: Ref<T[]>) => boolean
}

function isEmpty<T>(data: Ref<T[]>): boolean {
  return data.value.length === 0
}

export function useDataList<T>(options: UseDataListOptions<T>): UseDataListReturn<T> {
  const { fetchData, initialData = [], loadingDelay = 0 } = options

  const data = ref<T[]>(initialData) as Ref<T[]>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const refresh = async () => {
    loading.value = true
    error.value = null

    try {
      if (loadingDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, loadingDelay))
      }
      data.value = await fetchData()
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('数据加载失败')
      console.error('数据加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    refresh,
    isEmpty
  }
}

export function useLogs() {
  return useDataList<LogFile>({
    fetchData: () => mockDataService.fetchLogs(),
    loadingDelay: 300
  })
}

export function usePlayers() {
  return useDataList<PlayerStats>({
    fetchData: () => mockDataService.fetchPlayers(),
    loadingDelay: 250
  })
}

export function useBuildCodes() {
  return useDataList<BuildCode>({
    fetchData: () => mockDataService.fetchBuildCodes(),
    loadingDelay: 200
  })
}

export function useDashboardStats() {
  const data = ref<DashboardStats | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const refresh = async () => {
    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 300))
      data.value = await mockDataService.fetchDashboardStats()
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('统计数据加载失败')
      console.error('统计数据加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    data: computed(() => data.value),
    loading,
    error,
    refresh
  }
}

export function useAttendance() {
  return useDataList<AttendanceRecord>({
    fetchData: () => mockDataService.fetchAttendanceRecords(),
    loadingDelay: 250
  })
}

export function useLogById(id: string | Ref<string>) {
  const logId = typeof id === 'string' ? ref(id) : id
  const data = ref<LogFile | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const refresh = async () => {
    if (!logId.value) return

    loading.value = true
    error.value = null

    try {
      const result = await mockDataService.fetchLogById(logId.value)
      data.value = result || null
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('日志详情加载失败')
      console.error('日志详情加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    data: computed(() => data.value),
    loading,
    error,
    refresh
  }
}
