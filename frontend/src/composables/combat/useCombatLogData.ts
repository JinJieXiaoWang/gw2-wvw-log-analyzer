import { fmtDate, fmtDuration } from '@/composables/combat/useCombatHelpers'
import { logsService } from '@/services/combat/logsService'
import type { PlayerRotationData } from '@/services/ei/eiAnalysisService'
import { eiAnalysisService, type EiAnalysisAggregate, type EiAnalysisFight, type EiAnalysisPlayer, type EiAnalysisResponse } from '@/services/ei/eiAnalysisService'
import { professionService } from '@/services/professionService'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export function useCombatLogData() {
  const route = useRoute()
  const toast = useToast()
  const confirm = useConfirm()

  const loading = ref(true)
  const parsing = ref(false)
  const error = ref('')
  const logDetail = ref<Record<string, any>>({})
  const summary = ref<EiAnalysisResponse | null>(null)
  const selectedPlayer = ref<EiAnalysisPlayer | null>(null)
  const playerRotation = ref<PlayerRotationData | null>(null)
  const rotationLoading = ref(false)
  const dialogVisible = ref(false)

  const fightSummary = computed<EiAnalysisFight>(() => summary.value?.fight || ({} as EiAnalysisFight))

  const agg = computed<EiAnalysisAggregate>(() => summary.value?.aggregate || {
    duration_sec: 0, player_count: 0, total_damage: 0, total_power_damage: 0, total_condi_damage: 0,
    total_breakbar_damage: 0, total_damage_taken: 0, total_kills: 0, total_deaths: 0,
    total_downs: 0, total_downed: 0, total_boon_strips: 0, total_condition_cleanses: 0, total_resurrects: 0, avg_dps: 0, avg_critical_rate: 0
  })

  const players = computed(() => summary.value?.players || [])
  const topDpsPlayers = computed(() => summary.value?.top_dps_players || [])
  const commanders = computed(() => summary.value?.commanders || [])
  const groups = computed(() => summary.value?.groups || [])
  const ungroupedPlayers = computed(() => summary.value?.ungrouped_players || [])
  const sortedPlayerList = computed(() => summary.value?.sorted_players || [])

  const quickInfoItems = computed(() => [
    { label: '战斗时长', value: fmtDuration(fightSummary.value.duration_sec || 0), iconClass: 'pi pi-clock text-primary', iconBg: 'bg-primary/10 group-hover:bg-primary/20' },
    { label: '参战人数', value: `${summary.value?.total_players || 0} 人`, iconClass: 'pi pi-users text-success', iconBg: 'bg-success/10 group-hover:bg-success/20' },
    { label: '地图', value: fightSummary.value.map_name || '-', iconClass: 'pi pi-map text-info', iconBg: 'bg-info/10 group-hover:bg-info/20' },
    { label: '上传时间', value: fmtDate(logDetail.value.upload_time), iconClass: 'pi pi-calendar text-secondary', iconBg: 'bg-secondary/10 group-hover:bg-secondary/20' },
  ])

  const loadData = async (sortBy?: string) => {
    const logId = Number(route.params.id)
    if (!logId) { error.value = '无效的日志ID'; loading.value = false; return }
    loading.value = true; error.value = ''
    try {
      const [, logRes, sumRes] = await Promise.all([
        professionService.loadAllData(),
        logsService.getLog(logId),
        eiAnalysisService.getSummary(logId, sortBy || 'damage'),
      ])
      if (logRes.success) logDetail.value = logRes.data || {}
      if (sumRes.success && sumRes.data) {
        summary.value = sumRes.data
      } else {
        toast.add({ severity: 'warn', summary: '暂无解析数据', detail: '该日志尚未解析或解析失败', life: 3000 })
      }
    } catch (e: any) {
      error.value = e.message || '加载数据失败'
      toast.add({ severity: 'error', summary: '加载失败', detail: error.value, life: 3000 })
    } finally {
      loading.value = false
    }
  }

  const reparseLog = async () => {
    confirm.require({
      message: '重新解析将覆盖现有数据，是否继续？',
      header: '确认重新解析',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: '确认',
      rejectLabel: '取消',
      accept: async () => {
        const logId = Number(route.params.id)
        parsing.value = true
        try {
          const res = await logsService.parseLog(logId)
          if (res.success) {
            toast.add({ severity: 'info', summary: '重新解析', detail: '正在解析，请稍后刷新', life: 3000 })
            pollParseProgress(logId)
          } else throw new Error(res.message)
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '解析失败', detail: e.message || '重新解析失败', life: 3000 })
        } finally {
          parsing.value = false
        }
      }
    })
  }

  const pollParseProgress = (logId: number) => {
    const iv = setInterval(async () => {
      try {
        const res = await logsService.getParseProgress(logId)
        if (res.data?.progress === 100) {
          clearInterval(iv); await loadData()
          toast.add({ severity: 'success', summary: '解析完成', detail: '数据已更新', life: 3000 })
        } else if (res.data?.stage === '错误') {
          clearInterval(iv)
          toast.add({ severity: 'error', summary: '解析失败', detail: res.data?.errors?.[0] || '解析错误', life: 3000 })
        }
      } catch { clearInterval(iv) }
    }, 2000)
  }

  const openPlayerDialog = async (player: EiAnalysisPlayer) => {
    selectedPlayer.value = player
    dialogVisible.value = true
    rotationLoading.value = true
    playerRotation.value = null
    try {
      const logId = Number(route.params.id)
      const res = await eiAnalysisService.getPlayerRotation(logId, player.account)
      if (res.success && res.data) {
        playerRotation.value = res.data
      } else {
        toast.add({ severity: 'warn', summary: '暂无数据', detail: res.message || '该玩家没有技能循环数据', life: 3000 })
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '加载失败', detail: e.message || '获取技能数据失败', life: 3000 })
    } finally {
      rotationLoading.value = false
    }
  }

  watch(() => route.params.id, () => {
    loadData()
  })

  onMounted(() => { loadData() })

  return {
    loading,
    parsing,
    error,
    logDetail,
    summary,
    selectedPlayer,
    playerRotation,
    rotationLoading,
    dialogVisible,
    fightSummary,
    agg,
    players,
    topDpsPlayers,
    commanders,
    groups,
    ungroupedPlayers,
    sortedPlayerList,
    quickInfoItems,
    loadData,
    reparseLog,
    openPlayerDialog
  }
}
