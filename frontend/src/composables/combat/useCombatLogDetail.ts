/**
 * useCombatLogDetail - 战斗日志详情页业务逻辑 composable
 * 功能：集中管理 CombatLogDetailView 的所有状态、计算属性、数据请求
 * 规范：单一职责、函数式拆分、≤50行、幂等外部调用
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getSkillIconUrl } from '@/utils/profession/skillIcons'
import { configManager } from '@/services/core/configManager'
import { logsService } from '@/services/combat/logsService'
import { eiAnalysisService, type EiAnalysisResponse, type EiAnalysisPlayer, type EiAnalysisFight, type EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import type { PlayerRotationData } from '@/services/ei/eiAnalysisService'
import {
  type StatCategory,
  CATEGORY_SORT_KEY,
  CATEGORY_FIELDS,
  calcHitRate,
  getStatValue,
} from '@/utils/combat/combatStats'

/** KPI条目类型 */
export interface KpiItem {
  icon: string
  label: string
  value: string
  color: string
  bg: string
  barColor: string
  unit: string
  percent: number
}

/** Donut图数据 */
export interface DonutData {
  total: number
  p: number
  c: number
  b: number
  pd: string
  cd: string
  bd: string
  co: number
  bo: number
}

/** 统计平均值 */
export interface StatAverages {
  protection: number
  stability: number
  hitRate: number
  skillCastUptime: number
  stackDist: number
  distToCom: number
}

/** 小队数据 */
export interface GroupData {
  id: number
  players: EiAnalysisPlayer[]
}

/** Tab 配置常量 */
const TAB_ITEMS = [
  { label: '战斗概况', icon: 'pi pi-chart-bar' },
  { label: '玩家 & 小队', icon: 'pi pi-users' },
]

/** KPI 参考阈值常量 */
const KPI_THRESHOLDS = {
  maxDamage: 5_000_000,
  maxDowned: 100,
  maxDeaths: 50,
  maxDps: 50_000,
}

export function useCombatLogDetail() {
  const route = useRoute()
  const toast = useToast()
  const confirm = useConfirm()

  // ========== State ==========
  const activeTab = ref(0)
  const loading = ref(true)
  const parsing = ref(false)
  const error = ref('')
  const showDetailStats = ref(false)
  const showDamageDetailDialog = ref(false)
  const showStatDetailDialog = ref(false)
  const currentStatType = ref<StatCategory>('protection')
  const currentStatCategory = ref<string[]>([])
  const statDetailTitle = ref('')
  const dialogVisible = ref(false)
  const selectedPlayer = ref<EiAnalysisPlayer | null>(null)
  const playerRotation = ref<PlayerRotationData | null>(null)
  const rotationLoading = ref(false)
  const selectedTeamId = ref<number | null>(null)
  const logDetail = ref<Record<string, any>>({})
  const summary = ref<EiAnalysisResponse | null>(null)

  // 解析进度轮询定时器
  let parseProgressInterval: ReturnType<typeof setInterval> | null = null
  let loadDataRequestId = 0

  // ========== Computed ==========
  const fightSummary = computed<EiAnalysisFight>(() => summary.value?.fight || ({} as EiAnalysisFight))

  const agg = computed<EiAnalysisAggregate>(() => summary.value?.aggregate || {
    duration_sec: 0, player_count: 0, total_damage: 0, total_power_damage: 0, total_condi_damage: 0,
    total_breakbar_damage: 0, total_damage_taken: 0, total_kills: 0, total_deaths: 0,
    total_downs: 0, total_downed: 0, total_boon_strips: 0, total_condition_cleanses: 0,
    total_resurrects: 0, avg_dps: 0, avg_critical_rate: 0
  })

  const players = computed(() => summary.value?.players || [])
  const enemyPlayers = computed(() => summary.value?.enemy_players || [])

  const kpiList = computed(() => {
    const { maxDamage, maxDowned, maxDeaths, maxDps } = KPI_THRESHOLDS
    const a = agg.value
    return [
      { icon: 'pi pi-bolt', label: '总伤害', value: fmtCompact(a.total_damage), color: 'text-primary', bg: 'from-primary/20 to-primary/5', barColor: 'bg-primary', unit: '', percent: Math.min((a.total_damage / maxDamage) * 100, 100) },
      { icon: 'pi pi-shield', label: '总承伤', value: fmtCompact(a.total_damage_taken), color: 'text-secondary', bg: 'from-secondary/20 to-secondary/5', barColor: 'bg-secondary', unit: '', percent: Math.min((a.total_damage_taken / maxDamage) * 100, 100) },
      { icon: 'pi pi-star', label: '击杀', value: String(a.total_kills || 0), color: 'text-success', bg: 'from-success/20 to-success/5', barColor: 'bg-success', unit: '次', percent: Math.min((a.total_kills / maxDeaths) * 100, 100) },
      { icon: 'pi pi-times-circle', label: '死亡', value: String(a.total_deaths || 0), color: 'text-error', bg: 'from-error/20 to-error/5', barColor: 'bg-error', unit: '次', percent: Math.min((a.total_deaths / maxDeaths) * 100, 100) },
      { icon: 'pi pi-arrow-down', label: '倒地', value: String(a.total_downed || 0), color: 'text-warning', bg: 'from-warning/20 to-warning/5', barColor: 'bg-warning', unit: '次', percent: Math.min((a.total_downed / maxDowned) * 100, 100) },
      { icon: 'pi pi-chart-line', label: '平均DPS', value: fmtCompact(a.avg_dps), color: 'text-primary', bg: 'from-primary/20 to-primary/5', barColor: 'bg-primary', unit: '', percent: Math.min((a.avg_dps / maxDps) * 100, 100) },
    ]
  })

  const donut = computed(() => {
    const total = Math.max(agg.value.total_damage, 1)
    const p = Math.round((agg.value.total_power_damage / total) * 100)
    const c = Math.round((agg.value.total_condi_damage / total) * 100)
    const b = Math.round((agg.value.total_breakbar_damage / total) * 100)
    const circ = 2 * Math.PI * 40
    return {
      total: agg.value.total_damage,
      p, c, b,
      pd: `${(p / 100) * circ} ${circ}`,
      cd: `${(c / 100) * circ} ${circ}`,
      bd: `${(b / 100) * circ} ${circ}`,
      co: -((p / 100) * circ),
      bo: -(((p + c) / 100) * circ),
    }
  })

  const topDpsPlayers = computed(() => [...players.value].sort((a, b) => b.dps - a.dps).slice(0, 10))
  const commanders = computed(() => players.value.filter((p: EiAnalysisPlayer) => p.has_commander_tag))

  const groups = computed(() => {
    const result: { id: number; players: EiAnalysisPlayer[] }[] = []
    for (let i = 1; i <= 15; i++) {
      const g = players.value.filter((p: EiAnalysisPlayer) => p.group_id === i)
      if (g.length) result.push({ id: i, players: g })
    }
    return result
  })

  const ungroupedPlayers = computed(() => players.value.filter((p: EiAnalysisPlayer) => !p.group_id))

  const statAverages = computed(() => {
    const list = players.value
    if (!list.length) return { protection: 0, stability: 0, hitRate: 100, skillCastUptime: 0, stackDist: 0, distToCom: 0 }
    const avg = (key: keyof EiAnalysisPlayer) => {
      const filtered = list.filter(p => Number(p[key]) > 0)
      return filtered.length ? filtered.reduce((s, p) => s + Number(p[key]), 0) / filtered.length : 0
    }
    const hitRate = list.length ? list.reduce((s, p) => s + calcHitRate(p), 0) / list.length : 100
    return {
      protection: avg('protection_uptime'),
      stability: avg('stability_uptime'),
      hitRate: Math.min(Math.max(hitRate, 0), 100),
      skillCastUptime: avg('skill_cast_uptime'),
      stackDist: avg('stack_dist'),
      distToCom: avg('dist_to_com'),
    }
  })

  const statDetailList = computed(() => {
    const list = [...players.value]
    const type = currentStatType.value
    if (type === 'hitRate') {
      return list.sort((a, b) => calcHitRate(b) - calcHitRate(a))
    }
    const sortKey = CATEGORY_SORT_KEY[type] || 'damage'
    return list.sort((a: any, b: any) => (b[sortKey] || 0) - (a[sortKey] || 0))
  })

  const statDetailAverage = computed(() => {
    const fields = currentStatCategory.value
    const list = statDetailList.value
    if (!list.length || !fields.length) return 0
    let total = 0
    let count = 0
    for (const p of list) {
      for (const f of fields) {
        const val = getStatValue(p, f)
        const num = parseFloat(String(val).replace('%', '').replace(/,/g, ''))
        if (!isNaN(num) && isFinite(num)) {
          total += num
          count++
        }
      }
    }
    return count > 0 ? total / count : 0
  })

  const sortedPlayerList = computed(() => {
    return [...players.value].sort((a: any, b: any) => (b.damage || 0) - (a.damage || 0))
  })

  const powerPct = computed(() => {
    const t = agg.value.total_damage
    return t ? Math.round((agg.value.total_power_damage / t) * 100) : 0
  })
  const condiPct = computed(() => {
    const t = agg.value.total_damage
    return t ? Math.round((agg.value.total_condi_damage / t) * 100) : 0
  })
  const breakbarPct = computed(() => {
    const t = agg.value.total_damage
    return t ? Math.round((agg.value.total_breakbar_damage / t) * 100) : 0
  })

  const rotationEvents = computed(() => {
    if (!playerRotation.value?.rotation) return []
    const map = playerRotation.value.skill_map || {}
    const events: any[] = []
    for (const rot of playerRotation.value.rotation) {
      if (!rot || typeof rot !== 'object') continue
      const rawSkillId = rot.id ?? 0
      const lookupId = rawSkillId === -2 ? 0 : rawSkillId
      const skillInfo = map[String(lookupId)] || {}
      const name = skillInfo.name || `技能#${rawSkillId}`
      const iconUrl = skillInfo.icon || ''
      const icon = getSkillIconUrl(name, iconUrl)
      for (const cast of rot.skills || []) {
        events.push({
          castTime: cast.castTime ?? 0,
          skillId: rawSkillId,
          duration: cast.duration ?? 0,
          timeGained: cast.timeGained ?? 0,
          quickness: cast.quickness ?? 0,
          name,
          icon,
          autoAttack: skillInfo.auto_attack || false,
          isSwap: skillInfo.is_swap || false,
          isInstant: skillInfo.is_instant_cast || false,
          isTraitProc: skillInfo.is_trait_proc || false,
          gw2Id: skillInfo.gw2_id || rawSkillId,
        })
      }
    }
    return events
  })

  // ========== Methods ==========

  /** 加载日志详情与解析数据 */
  const loadData = async () => {
    const logId = Number(route.params.id)
    if (!logId) { error.value = '无效的日志ID'; loading.value = false; return }

    const reqId = ++loadDataRequestId
    loading.value = true
    error.value = ''

    try {
      const logRes = await logsService.getLog(logId)
      if (reqId !== loadDataRequestId) return
      if (logRes.success) {
        logDetail.value = logRes.data || {}
      } else {
        error.value = logRes.message || '获取日志信息失败'
        toast.add({ severity: 'error', summary: '加载失败', detail: error.value, life: configManager.get('ui').toastLife })
      }

      const sumRes = await eiAnalysisService.getSummary(logId)
      if (reqId !== loadDataRequestId) return
      if (sumRes.success && sumRes.data) {
        summary.value = sumRes.data
      } else {
        toast.add({ severity: 'warn', summary: '暂无解析数据', detail: '该日志尚未解析或解析失败', life: configManager.get('ui').toastLife })
      }
    } catch (e: any) {
      if (reqId !== loadDataRequestId) return
      error.value = e.message || '获取数据失败'
      toast.add({ severity: 'error', summary: '加载失败', detail: error.value, life: configManager.get('ui').toastLife })
    } finally {
      if (reqId === loadDataRequestId) loading.value = false
    }
  }

  /** 重新解析日志 */
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
            toast.add({ severity: 'info', summary: '重新解析', detail: '正在解析，请稍后刷新', life: configManager.get('ui').toastLife })
            startPollProgress(logId)
          } else throw new Error(res.message)
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '解析失败', detail: e.message || '重新解析失败', life: configManager.get('ui').toastLife })
        } finally {
          parsing.value = false
        }
      }
    })
  }

  /** 启动解析进度轮询 */
  const startPollProgress = (logId: number) => {
    clearPoll()
    let attempts = 0
    const maxAttempts = 30

    parseProgressInterval = setInterval(async () => {
      attempts++
      try {
        const res = await logsService.getParseProgress(logId)
        if (res.data?.progress === 100) {
          clearPoll()
          await loadData()
          toast.add({ severity: 'success', summary: '解析完成', detail: '数据已更新', life: configManager.get('ui').toastLife })
        } else if (res.data?.stage === '错误') {
          clearPoll()
          toast.add({ severity: 'error', summary: '解析失败', detail: res.data?.errors?.[0] || '解析错误', life: configManager.get('ui').toastLife })
        } else if (attempts >= maxAttempts) {
          clearPoll()
          toast.add({ severity: 'warn', summary: '解析超时', detail: '解析时间过长，请稍后手动刷新页面', life: configManager.get('ui').toastErrorLife })
        }
      } catch {
        if (attempts >= maxAttempts) {
          clearPoll()
          toast.add({ severity: 'error', summary: '连接失败', detail: '无法获取解析进度，请手动刷新', life: configManager.get('ui').toastErrorLife })
        }
      }
    }, 2000)
  }

  /** 清理轮询定时器 */
  const clearPoll = () => {
    if (parseProgressInterval) {
      clearInterval(parseProgressInterval)
      parseProgressInterval = null
    }
  }

  /** 打开统计详情弹窗 */
  const openStatDetailDialog = (type: StatCategory, title: string) => {
    currentStatType.value = type
    statDetailTitle.value = title
    const cfg = CATEGORY_FIELDS[type]
    currentStatCategory.value = cfg ? cfg.fields : [type]
    showStatDetailDialog.value = true
  }

  /** 打开玩家详情弹窗 */
  const openPlayerDialog = async (player: EiAnalysisPlayer) => {
    selectedPlayer.value = player
    dialogVisible.value = true
    await loadPlayerRotation(player)
  }

  /** 加载玩家技能循环数据 */
  const loadPlayerRotation = async (player?: EiAnalysisPlayer) => {
    const target = player || selectedPlayer.value
    if (!target) return
    rotationLoading.value = true
    playerRotation.value = null
    try {
      const logId = Number(route.params.id)
      const res = await eiAnalysisService.getPlayerRotation(logId, target.account)
      if (res.success && res.data) {
        playerRotation.value = res.data
      } else {
        toast.add({ severity: 'warn', summary: '暂无数据', detail: res.message || '该玩家没有技能循环数据', life: configManager.get('ui').toastLife })
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '加载失败', detail: e.message || '获取技能数据失败', life: configManager.get('ui').toastLife })
    } finally {
      rotationLoading.value = false
    }
  }

  /** DataTable 行点击 */
  const onRowClick = (event: any) => {
    const player = event.data as EiAnalysisPlayer
    if (player) openPlayerDialog(player)
  }

  // ========== Lifecycle ==========
  onMounted(() => { loadData() })
  onUnmounted(() => { clearPoll() })
  watch(() => route.params.id, () => { loadData() })

  // ========== Return ==========
  return {
    // State
    activeTab,
    loading,
    error,
    parsing,
    showDetailStats,
    showDamageDetailDialog,
    showStatDetailDialog,
    currentStatType,
    currentStatCategory,
    statDetailTitle,
    dialogVisible,
    selectedPlayer,
    playerRotation,
    rotationLoading,
    rotationEvents,
    selectedTeamId,
    logDetail,
    summary,

    // Computed
    fightSummary,
    agg,
    players,
    enemyPlayers,
    kpiList,
    donut,
    topDpsPlayers,
    commanders,
    groups,
    ungroupedPlayers,
    statAverages,
    statDetailList,
    statDetailAverage,
    sortedPlayerList,
    powerPct,
    condiPct,
    breakbarPct,

    // Constants
    tabItems: TAB_ITEMS,

    // Actions
    loadData,
    reparseLog,
    openStatDetailDialog,
    openPlayerDialog,
    loadPlayerRotation,
    onRowClick,
  }
}
