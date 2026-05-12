<template>
  <div class="space-y-6">
    <!-- 页面头部 -->
    <PageHeader
      title="数据看板"
      subtitle="WvW 战斗数据总览"
      icon="pi pi-chart-line"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    >
      <template #actions>
        <Select
          v-model="timeRange"
          :options="timeRangeOptions"
          option-label="label"
          option-value="value"
          class="w-32"
        />
      </template>
    </PageHeader>

    <!-- 统计卡片 -->
    <StatCards
      :is-loading-stats="isLoadingOverview"
      :dashboard-stats="overviewData"
    />

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <DamageTrend
        v-model:metric="trendMetric"
        :chart-data="trendData"
        :is-loading="isLoadingTrends"
      />
      <ProfessionDistribution
        :items="professionItems"
        :is-loading="isLoadingProfessions"
      />
    </div>

    <!-- 地图 + Buff -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <MapHeatmap
          :items="mapItems"
          :is-loading="isLoadingMaps"
        />
      </div>
      <BuffOverview
        :buffs="buffData"
        :is-loading="isLoadingBuffs"
      />
    </div>

    <!-- 玩家排行 -->
    <TopPlayers
      v-model:sort-by="topPlayerSort"
      :items="topPlayerItems"
      :is-loading="isLoadingTopPlayers"
    />

    <!-- 最近战斗 -->
    <BattleHistory
      :items="recentFights"
      :is-loading="isLoadingRecentFights"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 数据看板视图 v2.0
 * 功能：基于真实 API 数据的多维数据可视化
 * 更新：2026-05-04
 */

import { ref, watch, onMounted } from 'vue'
import Select from 'primevue/select'
import PageHeader from '@/layout/components/PageHeader.vue'
import StatCards from '@/components/dashboard/StatCards.vue'
import DamageTrend from '@/components/dashboard/DamageTrend.vue'
import ProfessionDistribution from '@/components/dashboard/ProfessionDistribution.vue'
import MapHeatmap from '@/components/dashboard/MapHeatmap.vue'
import BuffOverview from '@/components/dashboard/BuffOverview.vue'
import TopPlayers from '@/components/dashboard/TopPlayers.vue'
import BattleHistory from '@/components/dashboard/BattleHistory.vue'

import { dashboardService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'

// ============================================
// 时间范围
// ============================================
const timeRange = ref('30d')
const timeRangeOptions = [
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' },
  { label: '最近90天', value: '90d' },
  { label: '全部', value: 'all' }
]

const daysFromRange = (range: string): number => {
  const map: Record<string, number> = { '7d': 7, '30d': 30, '90d': 90, 'all': 365 }
  return map[range] || 30
}

// ============================================
// 加载状态
// ============================================
const isLoadingOverview = ref(false)
const isLoadingTrends = ref(false)
const isLoadingProfessions = ref(false)
const isLoadingMaps = ref(false)
const isLoadingBuffs = ref(false)
const isLoadingTopPlayers = ref(false)
const isLoadingRecentFights = ref(false)

// ============================================
// 数据状态
// ============================================
const overviewData = ref<any>(null)
const trendMetric = ref('damage')
const trendData = ref<any>(null)
const professionItems = ref<any[]>([])
const mapItems = ref<any[]>([])
const buffData = ref<Record<string, number> | null>(null)
const topPlayerSort = ref('damage')
const topPlayerItems = ref<any[]>([])
const recentFights = ref<any[]>([])

// ============================================
// API 获取函数
// ============================================

const fetchOverview = async () => {
  isLoadingOverview.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getOverview(daysFromRange(timeRange.value)),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      overviewData.value = result.data
    }
  } catch (e) {
    console.error('获取概览失败', e)
  } finally {
    isLoadingOverview.value = false
  }
}

const fetchTrends = async () => {
  isLoadingTrends.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getTrends(daysFromRange(timeRange.value), trendMetric.value),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      trendData.value = result.data
    }
  } catch (e) {
    console.error('获取趋势失败', e)
  } finally {
    isLoadingTrends.value = false
  }
}

const fetchProfessions = async () => {
  isLoadingProfessions.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getProfessionDistribution(daysFromRange(timeRange.value)),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      professionItems.value = result.data.items || []
    }
  } catch (e) {
    console.error('获取职业分布失败', e)
  } finally {
    isLoadingProfessions.value = false
  }
}

const fetchMaps = async () => {
  isLoadingMaps.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getMapStatistics(daysFromRange(timeRange.value)),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      mapItems.value = result.data.items || []
    }
  } catch (e) {
    console.error('获取地图统计失败', e)
  } finally {
    isLoadingMaps.value = false
  }
}

const fetchBuffs = async () => {
  isLoadingBuffs.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getBuffOverview(daysFromRange(timeRange.value)),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      buffData.value = result.data.buffs || null
    }
  } catch (e) {
    console.error('获取Buff概览失败', e)
  } finally {
    isLoadingBuffs.value = false
  }
}

const fetchTopPlayers = async () => {
  isLoadingTopPlayers.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getTopPlayers(daysFromRange(timeRange.value), topPlayerSort.value, 20),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      topPlayerItems.value = result.data.items || []
    }
  } catch (e) {
    console.error('获取玩家排行失败', e)
  } finally {
    isLoadingTopPlayers.value = false
  }
}

const fetchRecentFights = async () => {
  isLoadingRecentFights.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      dashboardService.getRecentFights(10),
      { showErrorMessage: false }
    )
    if (result.success && result.data) {
      recentFights.value = result.data || []
    }
  } catch (e) {
    console.error('获取最近战斗失败', e)
  } finally {
    isLoadingRecentFights.value = false
  }
}

const fetchAll = async () => {
  await Promise.all([
    fetchOverview(),
    fetchTrends(),
    fetchProfessions(),
    fetchMaps(),
    fetchBuffs(),
    fetchTopPlayers(),
    fetchRecentFights(),
  ])
}

// ============================================
// 监听变化
// ============================================

watch(timeRange, () => {
  fetchAll()
})

watch(trendMetric, () => {
  fetchTrends()
})

watch(topPlayerSort, () => {
  fetchTopPlayers()
})

// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchAll()
})
</script>

<style scoped lang="css">
/* 动画样式已移至子组件 */
</style>
