import { ref, watch, onMounted, computed, type Ref } from 'vue'
import type { ApiResponse } from '@/models'
import { useToast } from 'primevue/usetoast'
import { debounce } from '@/utils/core/helpers'
import { dashboardService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { configManager } from '@/services/core/configManager'
import { useDictMapping } from '@/composables/core/useDictMapping'

export function useDataDashboard() {
  const toast = useToast()
  const timeRange = ref('30d')
  const { data: timeRangeDictData, loadDictData: loadTimeRangeDict } = useDictMapping('dashboard_time_range', false)
  const timeRangeOptions = computed(() => timeRangeDictData.value.length > 0
    ? timeRangeDictData.value.map((item) => ({ label: item.label, value: item.value }))
    : [{ label: '最近7天', value: '7d' }, { label: '最近30天', value: '30d' }, { label: '最近90天', value: '90d' }, { label: '全部', value: 'all' }])
  const daysFromRange = (r: string) => ({ '7d': 7, '30d': 30, '90d': 90, 'all': 365 }[r] || 30)

  // 启动时加载时间范围字典
  onMounted(() => {
    loadTimeRangeDict()
  })

  const loadings = {
    overview: ref(false), trends: ref(false), professions: ref(false),
    maps: ref(false), buffs: ref(false), topPlayers: ref(false), recentFights: ref(false)
  }

  const overviewData = ref<any>(null)
  const trendMetric = ref('damage')
  const trendData = ref<any>(null)
  const professionItems = ref<any[]>([])
  const mapItems = ref<any[]>([])
  const buffData = ref<Record<string, number> | null>(null)
  const buffConfig = ref<any[]>([])
  const topPlayerSort = ref('damage')
  const topPlayerItems = ref<Record<string, unknown>[]>([])
  const recentFights = ref<Record<string, unknown>[]>([])

  const fetchData = async (fn: () => Promise<ApiResponse<unknown>>, loading: Ref<boolean>, detail: string, setter?: (data: unknown) => void) => {
    loading.value = true
    try {
      const res = await ApiResponseWrapper.wrap(fn(), { showErrorMessage: true })
      if (res.success && res.data && setter) setter(res.data)
    } catch { toast.add({ severity: 'error', summary: '加载失败', detail, life: configManager.get('ui').toastErrorLife }) }
    finally { loading.value = false }
  }

  const fetchOverview = () => fetchData(() => dashboardService.getOverview(daysFromRange(timeRange.value)), loadings.overview, '数据概览加载失败', d => overviewData.value = d)
  const fetchTrends = () => fetchData(() => dashboardService.getTrends(daysFromRange(timeRange.value), trendMetric.value), loadings.trends, '趋势数据加载失败', d => trendData.value = d)
  const fetchProfessions = () => fetchData(() => dashboardService.getProfessionDistribution(daysFromRange(timeRange.value)), loadings.professions, '职业分布加载失败', d => professionItems.value = (d as Record<string, unknown>).items as Record<string, unknown>[] || [])
  const fetchMaps = () => fetchData(() => dashboardService.getMapStatistics(daysFromRange(timeRange.value)), loadings.maps, '地图统计加载失败', d => mapItems.value = (d as Record<string, unknown>).items as Record<string, unknown>[] || [])
  const fetchBuffs = () => fetchData(() => dashboardService.getBuffOverview(daysFromRange(timeRange.value)), loadings.buffs, 'Buff概览加载失败', d => {
    buffData.value = (d as Record<string, unknown>).buffs as Record<string, number> | null || null
    buffConfig.value = (d as Record<string, unknown>).config as any[] || []
  })
  const fetchTopPlayers = () => fetchData(() => dashboardService.getTopPlayers(daysFromRange(timeRange.value), topPlayerSort.value, 20), loadings.topPlayers, '玩家排行加载失败', d => topPlayerItems.value = (d as Record<string, unknown>).items as Record<string, unknown>[] || [])
  const fetchRecentFights = () => fetchData(() => dashboardService.getRecentFights(10), loadings.recentFights, '最近战斗加载失败', d => recentFights.value = (d as Record<string, unknown>).items as Record<string, unknown>[] || [])

  const fetchAll = async () => {
    await Promise.all([fetchOverview(), fetchTrends()])
    await Promise.all([fetchProfessions(), fetchMaps(), fetchBuffs()])
    await Promise.all([fetchTopPlayers(), fetchRecentFights()])
  }

  watch(timeRange, debounce(fetchAll, 300))
  watch(trendMetric, fetchTrends)
  watch(topPlayerSort, fetchTopPlayers)
  onMounted(fetchAll)

  return {
    timeRange, timeRangeOptions,
    isLoadingOverview: loadings.overview, isLoadingTrends: loadings.trends,
    isLoadingProfessions: loadings.professions, isLoadingMaps: loadings.maps,
    isLoadingBuffs: loadings.buffs, isLoadingTopPlayers: loadings.topPlayers,
    isLoadingRecentFights: loadings.recentFights,
    overviewData, trendMetric, trendData, professionItems, mapItems, buffData, buffConfig,
    topPlayerSort, topPlayerItems, recentFights
  }
}
