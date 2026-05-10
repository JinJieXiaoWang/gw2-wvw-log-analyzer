import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { fightsApi } from '@/api'
import type { Fight, FightStats, FightQueryParams } from '@/api/combat/fights'
import { configManager } from '@/services/core/configManager'

export function useFightData() {
  const fights = ref<Fight[]>([])
  const selectedFight = ref<Fight | null>(null)
  const selectedFightStats = ref<FightStats | null>(null)
  const toast = useToast()
  const loading = ref(false)
  const hasMore = ref(true)
  const page = ref(1)
  const pageSize = ref(20)

  const filters = ref<FightQueryParams>({ mapName: '', serverName: '', result: undefined, page: 1, pageSize: pageSize.value })

  const loadFights = async () => {
    loading.value = true
    try {
      const response = await fightsApi.getFights({ ...filters.value, page: 1, pageSize: pageSize.value })
      if (response.success && response.data) {
        fights.value = response.data
        hasMore.value = response.data.length === pageSize.value
        page.value = 1
      }
    } catch (error: any) {
      toast.add({ severity: 'error', summary: '加载失败', detail: '战斗列表加载失败，请刷新重试', life: configManager.get('ui').toastErrorLife })
    } finally {
      loading.value = false
    }
  }

  const loadMoreFights = async () => {
    if (!hasMore.value || loading.value) return
    page.value++
    loading.value = true
    try {
      const response = await fightsApi.getFights({ ...filters.value, page: page.value, pageSize: pageSize.value })
      if (response.success && response.data) {
        fights.value = [...fights.value, ...response.data]
        hasMore.value = response.data.length === pageSize.value
      }
    } catch (error: any) {
      toast.add({ severity: 'error', summary: '加载失败', detail: '加载更多战斗失败，请刷新重试', life: configManager.get('ui').toastErrorLife })
    } finally {
      loading.value = false
    }
  }

  const viewFightDetail = async (fightId: string) => {
    try {
      const response = await fightsApi.getFightDetail(fightId)
      if (response.success && response.data) {
        selectedFight.value = response.data
        selectedFightStats.value = null
      }
    } catch (error) { console.error('加载战斗详情失败:', error) }
  }

  const viewFightStats = async (fightId: string) => {
    try {
      const response = await fightsApi.getFightStats(fightId)
      if (response.success && response.data) {
        selectedFightStats.value = response.data
        if (!selectedFight.value) {
          const fr = await fightsApi.getFightDetail(fightId)
          if (fr.success && fr.data) selectedFight.value = fr.data
        }
      }
    } catch (error) { console.error('加载战斗统计失败:', error) }
  }

  const formatDate = (dateString: string) => new Date(dateString).toLocaleString()
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  onMounted(() => loadFights())

  return { fights, selectedFight, selectedFightStats, loading, hasMore, filters, loadFights, loadMoreFights, viewFightDetail, viewFightStats, formatDate, formatDuration }
}
