// 模块功能: 技能循环分析状态管理
// 作者: 帅姐姐
// 创建日期: 2026-05-14

import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'
import {
  RotationAnalysis,
  FilterOptions,
  ViewMode,
  CompareMode,
  TimeRange,
  createEmptyRotationAnalysis,
  createDefaultFilters,
  computeFilteredEvents,
  cropEventsByTimeRange
} from '@/models/skillRotation'
import { skillRotationService } from '@/services/build/skillRotationService'

export const useSkillRotationStore = defineStore('skillRotation', () => {
  // ==================== 选中状态 ====================
  const selectedLogId = ref<string | null>(null)
  const selectedMemberId = ref<string | null>(null)
  const viewMode = ref<ViewMode>('cycle')
  const compareMode = ref<CompareMode>('time')
  const timeRange = ref<TimeRange>('full')
  const filters = ref<FilterOptions>(createDefaultFilters())

  // ==================== 数据状态 ====================
  const analysisResult = shallowRef<RotationAnalysis | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ==================== 计算属性 ====================

  /**
   * 经过过滤的技能事件
   */
  const filteredEvents = computed(() => {
    if (!analysisResult.value) return []
    let events = computeFilteredEvents(analysisResult.value.events, filters.value)
    events = cropEventsByTimeRange(events, timeRange.value, analysisResult.value.fight_duration)
    return events
  })

  /**
   * 是否准备好分析（已选择日志和玩家）
   */
  const isReady = computed(() => selectedLogId.value && selectedMemberId.value)

  /**
   * 是否有分析结果
   */
  const hasResult = computed(() => !!analysisResult.value)

  /**
   * 是否有错误
   */
  const hasError = computed(() => !!error.value)

  // ==================== 操作方法 ====================

  /**
   * 执行技能循环分析
   */
  async function performAnalysis(): Promise<void> {
    if (!selectedLogId.value || !selectedMemberId.value) return

    isLoading.value = true
    error.value = null

    try {
      const response = await skillRotationService.analyzeSkillRotationByIds(
        selectedLogId.value,
        selectedMemberId.value
      )

      if (response.success && response.data) {
        analysisResult.value = response.data
      } else {
        analysisResult.value = createEmptyRotationAnalysis()
        error.value = '未返回有效的分析数据'
      }
    } catch (err) {
      console.error('技能循环分析失败:', err)
      error.value = err instanceof Error ? err.message : '分析过程出错'
      analysisResult.value = null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新过滤器选项
   */
  function setFilters(newFilters: Partial<FilterOptions>): void {
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * 设置视图模式
   */
  function setViewMode(mode: ViewMode): void {
    viewMode.value = mode
  }

  /**
   * 设置对比模式
   */
  function setCompareMode(mode: CompareMode): void {
    compareMode.value = mode
  }

  /**
   * 设置时间范围
   */
  function setTimeRange(range: TimeRange): void {
    timeRange.value = range
  }

  /**
   * 选择日志
   */
  function selectLog(logId: string | null): void {
    selectedLogId.value = logId
    // 选择新日志后，清空玩家选择和结果
    selectedMemberId.value = null
    analysisResult.value = null
    error.value = null
  }

  /**
   * 选择玩家
   */
  function selectMember(memberId: string | null): void {
    selectedMemberId.value = memberId
  }

  /**
   * 重置状态
   */
  function reset(): void {
    selectedLogId.value = null
    selectedMemberId.value = null
    analysisResult.value = null
    error.value = null
    isLoading.value = false
    filters.value = createDefaultFilters()
    viewMode.value = 'cycle'
    compareMode.value = 'time'
    timeRange.value = 'full'
  }

  return {
    selectedLogId,
    selectedMemberId,
    viewMode,
    compareMode,
    timeRange,
    filters,
    analysisResult,
    isLoading,
    error,
    filteredEvents,
    isReady,
    hasResult,
    hasError,
    performAnalysis,
    setFilters,
    setViewMode,
    setCompareMode,
    setTimeRange,
    selectLog,
    selectMember,
    reset
  }
})
