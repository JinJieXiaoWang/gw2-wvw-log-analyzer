import { aiService } from '@/services'
import type { AiReport } from '@/services/ai/aiService'
import { computed, ref } from 'vue'

export type { AiReport }

export interface SuggestionsData {
  suggestions: string[]
  high_priority?: string[]
}

export interface TrendTimePoint {
  date: string
  damage: number
  kills: number
  deaths: number
  duration: number
}

export interface TrendData {
  data_points?: number
  total_damage?: number
  total_kills?: number
  avg_duration?: number
  trend?: string
  insights?: string[]
  time_series?: TrendTimePoint[]
}

export interface FightOption {
  id: string
  name: string
  date: string
}

export interface PlayerOption {
  id: string
  name: string
  profession: string
}

export interface BuildOption {
  id: string
  name: string
  profession: string
}

export interface AiConfig {
  enabled: boolean
  provider: string
  has_api_key: boolean
  cache_enabled: boolean
  fallback_enabled: boolean
}

export interface PersonalGrowthData {
  overall_score: number
  percentiles: Record<string, number>
  dimension_scores: Record<string, { score: number }>
  trends: {
    overall: string
    dps_trend: string
    survival_trend: string
    confidence: number
  }
  suggestions: Array<{
    category: string
    message: string
    actions?: string[]
  }>
  llm_analysis?: {
    narrative: string
    growth_plan?: Array<{ phase: string; focus: string }>
  }
}

export interface DeathAttributionData {
  survival_score: number
  death_stats: {
    total_fights: number
    death_rate: number
    total_deaths: number
    avg_dodge_per_fight: number
  }
  attributions: Array<{
    primary_reason: string
    primary_label: string
    start_time: string
    confidence: number
    all_reasons: string[]
  }>
  suggestions: Array<{
    priority: string
    message: string
    actions?: string[]
  }>
  llm_analysis?: {
    narrative: string
  }
}

export interface SquadSynergyData {
  squads: Array<{
    group_id: number
    synergy_score: number
    member_count: number
    role_distribution: Record<string, number>
    suggestions: Array<{ priority: string; message: string }>
  }>
}

export interface BuildExecutionData {
  build_type: string
  execution_score: number
  execution_check?: {
    checks: Array<{ label: string; actual: string; status: string }>
  }
}

export interface CriticalMomentsData {
  moments: Array<{
    importance: string
    label: string
    description: string
    evaluations?: Array<{
      character_name: string
      profession: string
      performance?: { rating: string }
    }>
  }>
}

export function useAiAnalysis() {
  const aiEnabled = ref(true)
  const analyzing = ref(false)
  const analyzingTitle = ref('AI分析中')
  const analyzingMessage = ref('正在处理您的数据...')
  const analyzingProgress = ref(0)
  const currentProvider = ref('DeepSeek')
  const cacheHitRate = ref(78)
  const cacheEntries = ref(156)
  const suggestionsData = ref<SuggestionsData | null>(null)
  const trendData = ref<TrendData | null>(null)
  const loadingSuggestions = ref(false)
  const loadingTrend = ref(false)

  const isRuleBasedMode = computed(() => !aiEnabled.value)

  // === 新增AI战术复盘与成长顾问系统状态 ===
  const personalGrowthData = ref<PersonalGrowthData | null>(null)
  const deathAttributionData = ref<DeathAttributionData | null>(null)
  const squadSynergyData = ref<SquadSynergyData | null>(null)
  const buildExecutionData = ref<BuildExecutionData | null>(null)
  const criticalMomentsData = ref<CriticalMomentsData | null>(null)
  const loadingPersonalGrowth = ref(false)
  const loadingDeathAttribution = ref(false)
  const loadingSquadSynergy = ref(false)
  const loadingBuildExecution = ref(false)
  const loadingCriticalMoments = ref(false)

  const loadAiStatus = async () => {
    try {
      const response = await aiService.getStatus()
      if (response.success && response.data) {
        const config = response.data.config as AiConfig
        aiEnabled.value = config.enabled !== false
        currentProvider.value = config?.provider || 'DeepSeek'
        cacheHitRate.value = response.data.cache?.hit_rate || 78
        cacheEntries.value = response.data.cache?.total_entries || 156
        return config
      }
      return null
    } catch (error) {
      console.error('获取AI状态失败:', error)
      return null
    }
  }

  const loadSuggestions = async () => {
    loadingSuggestions.value = true
    try {
      const response = await aiService.getSuggestions()
      if (response.success && response.data) {
        suggestionsData.value = response.data as SuggestionsData
      }
    } catch (error) {
      console.error('加载AI优化建议失败:', error)
    } finally {
      loadingSuggestions.value = false
    }
  }

  const loadTrend = async (timeRange: string = '7d') => {
    loadingTrend.value = true
    try {
      const response = await aiService.getTrendAnalysis({ time_range: timeRange })
      if (response.success && response.data) {
        trendData.value = response.data as TrendData
      }
    } catch (error) {
      console.error('加载AI趋势分析失败:', error)
    } finally {
      loadingTrend.value = false
    }
  }

  const analyzeFight = async (fightId: number, scope: 'current' | 'full' = 'current') => {
    analyzing.value = true
    analyzingTitle.value = '战斗分析中'
    analyzingMessage.value = scope === 'current' 
      ? 'AI正在分析选定的战斗数据...' 
      : 'AI正在分析全部战斗数据...'
    analyzingProgress.value = 0
    
    const progressInterval = setInterval(() => {
      if (analyzingProgress.value < 95) {
        analyzingProgress.value += Math.random() * 15
      }
    }, 300)
    
    try {
      const response = await aiService.analyzeFight(fightId)
      analyzingProgress.value = 100
      
      setTimeout(() => {
        analyzing.value = false
        clearInterval(progressInterval)
      }, 500)
      
      return response
    } catch (error) {
      analyzing.value = false
      clearInterval(progressInterval)
      throw error
    }
  }

  const analyzeMember = async (memberId: number, scope: 'current' | 'full' = 'current') => {
    analyzing.value = true
    analyzingTitle.value = '玩家分析中'
    analyzingMessage.value = scope === 'current'
      ? 'AI正在分析该玩家的选定数据...'
      : 'AI正在分析该玩家的全部历史数据...'
    analyzingProgress.value = 0
    
    const progressInterval = setInterval(() => {
      if (analyzingProgress.value < 95) {
        analyzingProgress.value += Math.random() * 15
      }
    }, 300)
    
    try {
      const response = await aiService.analyzeMemberSkills(memberId)
      analyzingProgress.value = 100
      
      setTimeout(() => {
        analyzing.value = false
        clearInterval(progressInterval)
      }, 500)
      
      return response
    } catch (error) {
      analyzing.value = false
      clearInterval(progressInterval)
      throw error
    }
  }

  const analyzeBuild = async (buildId: number) => {
    analyzing.value = true
    analyzingTitle.value = 'Build分析中'
    analyzingMessage.value = 'AI正在评估Build配置...'
    analyzingProgress.value = 0
    
    const progressInterval = setInterval(() => {
      if (analyzingProgress.value < 95) {
        analyzingProgress.value += Math.random() * 15
      }
    }, 300)
    
    try {
      const response = await aiService.analyzeBuild(buildId)
      analyzingProgress.value = 100
      
      setTimeout(() => {
        analyzing.value = false
        clearInterval(progressInterval)
      }, 500)
      
      return response
    } catch (error) {
      analyzing.value = false
      clearInterval(progressInterval)
      throw error
    }
  }

  // === 新增AI战术复盘与成长顾问系统分析方法 ===

  const analyzePersonalGrowth = async (account: string, fightCount: number = 30) => {
    loadingPersonalGrowth.value = true
    try {
      const response = await aiService.analyzePersonalGrowth(account, fightCount)
      if (response.success && response.data) {
        personalGrowthData.value = response.data
      }
      return response
    } catch (error) {
      console.error('个人成长档案分析失败:', error)
      throw error
    } finally {
      loadingPersonalGrowth.value = false
    }
  }

  const analyzeDeathAttribution = async (account: string, fightId?: number) => {
    loadingDeathAttribution.value = true
    try {
      const response = await aiService.analyzeDeathAttribution(account, fightId)
      if (response.success && response.data) {
        deathAttributionData.value = response.data
      }
      return response
    } catch (error) {
      console.error('死亡归因分析失败:', error)
      throw error
    } finally {
      loadingDeathAttribution.value = false
    }
  }

  const analyzeSquadSynergy = async (fightId: number, groupId?: number) => {
    loadingSquadSynergy.value = true
    try {
      const response = await aiService.analyzeSquadSynergy(fightId, groupId)
      if (response.success && response.data) {
        squadSynergyData.value = response.data
      }
      return response
    } catch (error) {
      console.error('小队协同分析失败:', error)
      throw error
    } finally {
      loadingSquadSynergy.value = false
    }
  }

  const analyzeBuildExecution = async (account: string, buildId?: number) => {
    loadingBuildExecution.value = true
    try {
      const response = await aiService.analyzeBuildExecution(account, buildId)
      if (response.success && response.data) {
        buildExecutionData.value = response.data
      }
      return response
    } catch (error) {
      console.error('Build执行验证失败:', error)
      throw error
    } finally {
      loadingBuildExecution.value = false
    }
  }

  const analyzeCriticalMoments = async (fightId: number, account?: string) => {
    loadingCriticalMoments.value = true
    try {
      const response = await aiService.analyzeCriticalMoments(fightId, account)
      if (response.success && response.data) {
        criticalMomentsData.value = response.data
      }
      return response
    } catch (error) {
      console.error('关键片段分析失败:', error)
      throw error
    } finally {
      loadingCriticalMoments.value = false
    }
  }

  return {
    aiEnabled,
    analyzing,
    analyzingTitle,
    analyzingMessage,
    analyzingProgress,
    currentProvider,
    cacheHitRate,
    cacheEntries,
    suggestionsData,
    trendData,
    loadingSuggestions,
    loadingTrend,
    isRuleBasedMode,
    loadAiStatus,
    loadSuggestions,
    loadTrend,
    analyzeFight,
    analyzeMember,
    analyzeBuild,
    // 新增
    personalGrowthData,
    deathAttributionData,
    squadSynergyData,
    buildExecutionData,
    criticalMomentsData,
    loadingPersonalGrowth,
    loadingDeathAttribution,
    loadingSquadSynergy,
    loadingBuildExecution,
    loadingCriticalMoments,
    analyzePersonalGrowth,
    analyzeDeathAttribution,
    analyzeSquadSynergy,
    analyzeBuildExecution,
    analyzeCriticalMoments,
  }
}

export function useAiReports() {
  const reports = ref<AiReport[]>([])
  const selectedReport = ref<AiReport | null>(null)
  const loading = ref(false)
  const hasMore = ref(true)
  const page = ref(1)
  const pageSize = ref(10)
  const reportFilter = ref('all')

  const filteredReports = computed(() => {
    if (reportFilter.value === 'all') return reports.value
    return reports.value.filter(r => (r as any).report_type === reportFilter.value)
  })

  const loadReports = async () => {
    loading.value = true
    page.value = 1
    try {
      const response = await aiService.getReports({
        page: page.value,
        page_size: pageSize.value,
        report_type: reportFilter.value === 'all' ? undefined : reportFilter.value,
      })
      if (response.success && response.data) {
        const data = response.data as { items: AiReport[]; total: number }
        reports.value = data.items || []
        hasMore.value = (data.items || []).length === pageSize.value
      }
    } catch (error) {
      console.error('加载AI报告失败:', error)
    } finally {
      loading.value = false
    }
  }

  const loadMoreReports = async () => {
    if (!hasMore.value || loading.value) return
    page.value++
    loading.value = true
    try {
      const response = await aiService.getReports({
        page: page.value,
        page_size: pageSize.value,
        report_type: reportFilter.value === 'all' ? undefined : reportFilter.value,
      })
      if (response.success && response.data) {
        const data = response.data as { items: AiReport[]; total: number }
        reports.value = [...reports.value, ...(data.items || [])]
        hasMore.value = (data.items || []).length === pageSize.value
      }
    } catch (error) {
      console.error('加载更多报告失败:', error)
    } finally {
      loading.value = false
    }
  }

  const viewReport = async (reportId: string) => {
    try {
      const response = await aiService.getReport(Number(reportId))
      if (response.success && response.data) {
        selectedReport.value = response.data as AiReport
      }
    } catch (error) {
      console.error('获取报告详情失败:', error)
      throw error
    }
  }

  const deleteReport = async (reportId: string) => {
    try {
      const response = await aiService.deleteReport(Number(reportId))
      if (response.success) {
        reports.value = reports.value.filter(r => r.id !== reportId)
      }
      return response
    } catch (error) {
      console.error('删除报告失败:', error)
      throw error
    }
  }

  return {
    reports,
    selectedReport,
    loading,
    hasMore,
    page,
    pageSize,
    reportFilter,
    filteredReports,
    loadReports,
    loadMoreReports,
    viewReport,
    deleteReport,
  }
}
