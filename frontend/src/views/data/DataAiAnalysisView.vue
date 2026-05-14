<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-bg via-slate-950 to-neutral-bg relative overflow-hidden">
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/8 rounded-full blur-3xl animate-pulse-slow" />
      <div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/8 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1.5s" />
      <div class="absolute inset-0 opacity-[0.02]" style="background-image: linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px); background-size: 50px 50px;" />
    </div>
    <div class="relative z-10 p-4 md:p-6 lg:p-8">
      <header class="mb-8">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div class="flex items-center gap-4">
            <div class="p-4 bg-gradient-to-br from-primary via-purple-600 to-indigo-700 rounded-2xl shadow-lg shadow-primary/20">
              <SvgIcon icon="brain" :size="32" class="text-white" />
            </div>
            <div>
              <h1 class="text-3xl lg:text-4xl font-bold text-white tracking-tight">AI 战斗分析中心</h1>
              <p class="text-neutral-text-secondary mt-1.5">智能分析战斗数据，发现隐藏的优化机会</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <button @click="handleRefresh" :disabled="isRefreshing" class="flex items-center gap-2 px-5 py-2.5 bg-neutral-card hover:bg-neutral-card-hover border border-neutral-border rounded-xl transition-all">
              <SvgIcon v-if="!isRefreshing" icon="refresh-cw" :size="18" class="text-neutral-text-secondary" />
              <span v-else class="animate-spin"><SvgIcon icon="loader" :size="18" /></span>
              <span class="text-neutral-text-secondary">{{ isRefreshing ? '刷新中...' : '刷新数据' }}</span>
            </button>
            <button @click="showConfig = !showConfig" class="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-light hover:to-indigo-500 text-white rounded-xl transition-all font-medium">
              <SvgIcon icon="settings" :size="18" />
              <span>配置管理</span>
            </button>
          </div>
        </div>
        <AiStatusBar :config="aiConfig" :stats="aiStats" @test-connection="testConnection" />
      </header>

      <!-- 配置面板 -->
      <div v-if="showConfig" class="bg-neutral-card/50 backdrop-blur-sm rounded-2xl border border-neutral-border p-6 lg:p-8 mb-6">
        <AiConfigPanel @config-updated="handleConfigUpdated" />
      </div>

      <!-- 分析类型标签页 -->
      <div class="flex items-center gap-1 mb-6 overflow-x-auto pb-1 scrollbar-hide">
        <button v-for="tab in analysisTabs" :key="tab.key"
          @click="activeAnalysisTab = tab.key"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all"
          :class="activeAnalysisTab === tab.key ? 'bg-primary/20 text-primary border border-primary/30' : 'text-neutral-text-secondary hover:text-white hover:bg-neutral-card-active'"
        >
          <SvgIcon :icon="tab.icon" :size="16" />
          {{ tab.label }}
        </button>
      </div>

      <!-- 概览页 -->
      <div v-if="activeAnalysisTab === 'overview'">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
          <div class="lg:col-span-8 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiQuickActions :recent-fights="recentFights" :recent-players="recentPlayers" :disabled="!aiEnabled || analyzing" @analyze-fight="handleQuickAnalyzeFight" @analyze-player="handleQuickAnalyzePlayer" @analyze-team="handleQuickAnalyzeTeam" />
          </div>
          <div class="lg:col-span-4 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiSystemStatus :config="aiConfig" :stats="aiStats" :testing-connection="testingConnection" @test-connection="testConnection" />
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiSuggestionsPanel :data="suggestionsData" :loading="loadingSuggestions" @refresh="loadSuggestions" />
          </div>
          <div class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiTrendPanel :data="trendData" :loading="loadingTrend" :time-range="trendTimeRange" @refresh="loadTrend" @time-range-change="handleTrendTimeRangeChange" />
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div class="lg:col-span-4 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiAnalysisToolsPanel :recent-fights="recentFights" :recent-players="recentPlayers" :recent-builds="recentBuilds" :disabled="!aiEnabled" @analyze="handleAnalyze" />
          </div>
          <div class="lg:col-span-8 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
            <AiReportPanel :reports="filteredReports" :loading="loading" :has-more="hasMore" :filter="reportFilter" @refresh="loadReports" @load-more="loadMoreReports" @view="handleViewReport" @delete="handleDeleteReport" @filter-change="handleFilterChange" />
          </div>
        </div>
      </div>

      <!-- 成长档案页 -->
      <div v-else-if="activeAnalysisTab === 'growth'" class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-sm text-neutral-text-secondary mb-1.5">选择玩家</label>
            <select v-model="selectedPlayerAccount" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option value="">请选择玩家</option>
              <option v-for="p in recentPlayers" :key="p.id" :value="p.name">{{ p.name }} ({{ p.profession }})</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-neutral-text-secondary mb-1.5">历史场次</label>
            <select v-model="growthFightCount" class="bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option :value="10">最近10场</option>
              <option :value="30">最近30场</option>
              <option :value="50">最近50场</option>
            </select>
          </div>
          <button @click="runPersonalGrowth" :disabled="!selectedPlayerAccount || loadingPersonalGrowth" class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
            {{ loadingPersonalGrowth ? '分析中...' : '生成档案' }}
          </button>
        </div>
        <AiPersonalGrowthPanel :data="personalGrowthData" :loading="loadingPersonalGrowth" />
      </div>

      <!-- 死亡归因页 -->
      <div v-else-if="activeAnalysisTab === 'death'" class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-sm text-neutral-text-secondary mb-1.5">选择玩家</label>
            <select v-model="selectedPlayerAccount" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option value="">请选择玩家</option>
              <option v-for="p in recentPlayers" :key="p.id" :value="p.name">{{ p.name }} ({{ p.profession }})</option>
            </select>
          </div>
          <button @click="runDeathAttribution" :disabled="!selectedPlayerAccount || loadingDeathAttribution" class="px-6 py-2.5 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-400 hover:to-orange-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
            {{ loadingDeathAttribution ? '分析中...' : '死亡归因分析' }}
          </button>
        </div>
        <AiDeathAttributionPanel :data="deathAttributionData" :loading="loadingDeathAttribution" />
      </div>

      <!-- 小队协同页 -->
      <div v-else-if="activeAnalysisTab === 'squad'" class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-sm text-neutral-text-secondary mb-1.5">选择战斗</label>
            <select v-model="selectedFightId" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option value="">请选择战斗</option>
              <option v-for="f in recentFights" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
          </div>
          <button @click="runSquadSynergy" :disabled="!selectedFightId || loadingSquadSynergy" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-400 hover:to-indigo-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
            {{ loadingSquadSynergy ? '分析中...' : '小队协同诊断' }}
          </button>
        </div>
        <div v-if="squadSynergyData" class="space-y-4">
          <div v-for="sq in squadSynergyData.squads || []" :key="sq.group_id" class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-semibold text-white">小队 {{ sq.group_id }}</h3>
              <span class="text-lg font-bold" :class="getScoreClass(sq.synergy_score)">{{ sq.synergy_score }}</span>
            </div>
            <div class="text-sm text-neutral-text-secondary mb-2">{{ sq.member_count }} 人 · 角色: {{ Object.entries(sq.role_distribution || {}).map(([k,v]) => `${k} ${v}`).join(', ') }}</div>
            <div v-if="sq.suggestions?.length" class="space-y-1.5 mt-3">
              <div v-for="(s, i) in sq.suggestions" :key="i" class="text-xs p-2 rounded" :class="s.priority === 'high' ? 'bg-error/10 text-error' : 'bg-warning/10 text-warning'">
                {{ s.message }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-neutral-text-tertiary">选择战斗并点击分析</div>
      </div>

      <!-- Build验证页 -->
      <div v-else-if="activeAnalysisTab === 'build'" class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-sm text-neutral-text-secondary mb-1.5">选择玩家</label>
            <select v-model="selectedPlayerAccount" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option value="">请选择玩家</option>
              <option v-for="p in recentPlayers" :key="p.id" :value="p.name">{{ p.name }} ({{ p.profession }})</option>
            </select>
          </div>
          <button @click="runBuildExecution" :disabled="!selectedPlayerAccount || loadingBuildExecution" class="px-6 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
            {{ loadingBuildExecution ? '验证中...' : 'Build执行验证' }}
          </button>
        </div>
        <div v-if="buildExecutionData">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
              <div class="text-xs text-neutral-text-secondary mb-1">Build类型</div>
              <div class="text-lg font-semibold text-white">{{ buildExecutionData.build_type }}</div>
            </div>
            <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
              <div class="text-xs text-neutral-text-secondary mb-1">执行评分</div>
              <div class="text-lg font-semibold" :class="getScoreClass(buildExecutionData.execution_score)">{{ buildExecutionData.execution_score }}</div>
            </div>
          </div>
          <div v-if="buildExecutionData.execution_check?.checks?.length" class="space-y-2">
            <div v-for="(check, i) in buildExecutionData.execution_check.checks" :key="i" class="flex items-center justify-between p-3 bg-neutral-card-active/30 rounded-lg">
              <span class="text-sm text-white">{{ check.label }}</span>
              <div class="flex items-center gap-3">
                <span class="text-xs text-neutral-text-secondary">实际: {{ check.actual }}</span>
                <span class="text-xs px-2 py-0.5 rounded font-medium" :class="check.status === 'pass' ? 'bg-status-success/20 text-status-success' : check.status === 'fail' ? 'bg-error/20 text-error' : 'bg-neutral-card-active text-neutral-text-secondary'">{{ check.status.toUpperCase() }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-neutral-text-tertiary">选择玩家并点击验证</div>
      </div>

      <!-- 关键片段页 -->
      <div v-else-if="activeAnalysisTab === 'moments'" class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-sm text-neutral-text-secondary mb-1.5">选择战斗</label>
            <select v-model="selectedFightId" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
              <option value="">请选择战斗</option>
              <option v-for="f in recentFights" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
          </div>
          <button @click="runCriticalMoments" :disabled="!selectedFightId || loadingCriticalMoments" class="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
            {{ loadingCriticalMoments ? '分析中...' : '关键片段复盘' }}
          </button>
        </div>
        <div v-if="criticalMomentsData?.moments?.length" class="space-y-4">
          <div v-for="(m, i) in criticalMomentsData.moments" :key="i" class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
            <div class="flex items-center gap-3 mb-2">
              <span class="text-xs px-2 py-0.5 rounded font-medium" :class="m.importance === 'critical' ? 'bg-error/20 text-error' : 'bg-warning/20 text-warning'">{{ m.importance }}</span>
              <span class="font-semibold text-white">{{ m.label }}</span>
            </div>
            <p class="text-sm text-neutral-text-secondary mb-3">{{ m.description }}</p>
            <div v-if="m.evaluations?.length" class="space-y-2">
              <div v-for="(evalItem, j) in m.evaluations" :key="j" class="flex items-center justify-between p-2 bg-black/20 rounded-lg">
                <span class="text-sm text-white">{{ evalItem.character_name }} ({{ evalItem.profession }})</span>
                <span class="text-xs px-2 py-0.5 rounded" :class="evalItem.performance?.rating === 'excellent' ? 'bg-status-success/20 text-status-success' : evalItem.performance?.rating === 'good' ? 'bg-warning/20 text-warning' : 'bg-error/20 text-error'">{{ evalItem.performance?.rating }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-neutral-text-tertiary">选择战斗并点击分析</div>
      </div>
    </div>

    <AiReportDetailModal v-if="selectedReport" :report="selectedReport" @close="selectedReport = null" />
    <AiAnalyzingModal v-if="analyzing" :title="analyzingTitle" :message="analyzingMessage" :progress="analyzingProgress" />
    <Transition name="slide-up">
      <div v-if="notification.show" :class="notificationClass" class="fixed bottom-8 right-8 px-6 py-4 rounded-2xl shadow-2xl z-50 flex items-center gap-4 min-w-[280px]">
        <SvgIcon :icon="notificationIcon" :size="24" class="text-white flex-shrink-0" />
        <div>
          <p class="text-white font-medium">{{ notification.title }}</p>
          <p class="text-white/80 text-sm">{{ notification.message }}</p>
        </div>
        <button @click="notification.show = false" class="ml-auto"><SvgIcon icon="x" :size="18" class="text-white/80 hover:text-white" /></button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import AiAnalysisToolsPanel from '@/components/ai/AiAnalysisToolsPanel.vue'
import AiAnalyzingModal from '@/components/ai/AiAnalyzingModal.vue'
import AiConfigPanel from '@/components/ai/AiConfigPanel.vue'
import AiDeathAttributionPanel from '@/components/ai/AiDeathAttributionPanel.vue'
import AiPersonalGrowthPanel from '@/components/ai/AiPersonalGrowthPanel.vue'
import AiQuickActions from '@/components/ai/AiQuickActions.vue'
import AiReportDetailModal from '@/components/ai/AiReportDetailModal.vue'
import AiReportPanel from '@/components/ai/AiReportPanel.vue'
import AiStatusBar from '@/components/ai/AiStatusBar.vue'
import AiSuggestionsPanel from '@/components/ai/AiSuggestionsPanel.vue'
import AiSystemStatus from '@/components/ai/AiSystemStatus.vue'
import AiTrendPanel from '@/components/ai/AiTrendPanel.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { useAiAnalysis, useAiReports } from '@/composables/useAiAnalysis'
import { aiService, attendanceService, fightsService } from '@/services'
import { computed, onMounted, reactive, ref } from 'vue'

const analysisTabs = [
  { key: 'overview', label: '概览', icon: 'layout-dashboard' },
  { key: 'growth', label: '成长档案', icon: 'trending-up' },
  { key: 'death', label: '死亡归因', icon: 'shield-alert' },
  { key: 'squad', label: '小队协同', icon: 'users' },
  { key: 'build', label: 'Build验证', icon: 'check-circle' },
  { key: 'moments', label: '关键片段', icon: 'clock' },
]

const {
  aiEnabled, analyzing, analyzingTitle, analyzingMessage, analyzingProgress,
  suggestionsData, loadingSuggestions, trendData, loadingTrend,
  loadAiStatus, loadSuggestions, loadTrend, analyzeFight, analyzeMember, analyzeBuild,
  personalGrowthData, deathAttributionData, squadSynergyData, buildExecutionData, criticalMomentsData,
  loadingPersonalGrowth, loadingDeathAttribution, loadingSquadSynergy, loadingBuildExecution, loadingCriticalMoments,
  analyzePersonalGrowth, analyzeDeathAttribution, analyzeSquadSynergy, analyzeBuildExecution, analyzeCriticalMoments,
} = useAiAnalysis()

const { reports, selectedReport, loading, hasMore, reportFilter, filteredReports, loadReports, loadMoreReports, viewReport, deleteReport } = useAiReports()

const showConfig = ref(false)
const activeAnalysisTab = ref('overview')
const isRefreshing = ref(false)
const testingConnection = ref(false)
const trendTimeRange = ref('7d')
const aiConfig = reactive({ enabled: true, provider: 'DeepSeek', has_api_key: false, cache_enabled: true, fallback_enabled: true })
const aiStats = reactive({ cache_hit_rate: 78, cache_entries: 156, today_count: 23, response_time: 125 })
const recentFights = ref<FightOption[]>([])
const recentPlayers = ref<PlayerOption[]>([])
const recentBuilds = ref<BuildOption[]>([])
const selectedPlayerAccount = ref('')
const selectedFightId = ref('')
const growthFightCount = ref(30)
const notification = reactive({ show: false, title: '', message: '', type: 'success' as 'success' | 'error' | 'warning' })

interface FightOption { id: string; name: string; date: string }
interface PlayerOption { id: string; name: string; profession: string }
interface BuildOption { id: string; name: string; profession: string }

const notificationClass = computed(() => {
  if (notification.type === 'success') return 'bg-gradient-to-r from-status-success to-emerald-600'
  if (notification.type === 'warning') return 'bg-gradient-to-r from-warning to-secondary'
  return 'bg-gradient-to-r from-error to-red-600'
})
const notificationIcon = computed(() => notification.type === 'success' ? 'check-circle' : notification.type === 'warning' ? 'alert-circle' : 'x-circle')
const getScoreClass = (score: number) => score >= 80 ? 'text-status-success' : score >= 60 ? 'text-warning' : 'text-error'

const showNotification = (message: string, type: 'success' | 'error' | 'warning' = 'success', title?: string) => {
  notification.title = title || (type === 'success' ? '操作成功' : type === 'warning' ? '提示' : '操作失败')
  notification.message = message
  notification.type = type
  notification.show = true
  setTimeout(() => { notification.show = false }, 4000)
}

const handleRefresh = async () => {
  isRefreshing.value = true
  try {
    const [config] = await Promise.all([loadAiStatus(), loadReports(), loadSuggestions(), loadTrend(trendTimeRange.value), loadRecentFights(), loadRecentPlayers()])
    if (config) {
      aiConfig.enabled = config.enabled
      aiConfig.provider = config.provider
      aiConfig.has_api_key = config.has_api_key
      aiConfig.cache_enabled = config.cache_enabled
      aiConfig.fallback_enabled = config.fallback_enabled
    }
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    isRefreshing.value = false
    showNotification('数据刷新完成', 'success')
  }
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    const response = await aiService.testConfiguration()
    if (response.success && response.data?.valid) {
      showNotification('连接测试成功！AI服务正常运行', 'success', '测试成功')
    } else {
      showNotification('连接测试失败，请检查配置', 'error', '测试失败')
    }
  } catch (error) {
    showNotification('连接测试失败', 'error', '测试失败')
  } finally {
    testingConnection.value = false
  }
}

const loadRecentFights = async () => {
  try {
    const response = await fightsService.getFights({ page: 1, pageSize: 20 })
    if (response.success && response.data) {
      const data = response.data as { items: Array<{ id: number; map_name?: string; duration_sec?: number; player_count?: number }> }
      recentFights.value = data.items?.map(f => ({
        id: f.id.toString(),
        name: f.map_name ? `${f.map_name} (${f.duration_sec}s, ${f.player_count}人)` : `战斗 ${f.id}`,
        date: ''
      })) || []
    }
  } catch (error) { console.error('加载最近战斗失败:', error) }
}

const loadRecentPlayers = async () => {
  try {
    const response = await attendanceService.getAccounts({ page: 1, page_size: 100 })
    if (response.success && response.data) {
      const data = response.data as { items?: Array<{ account: string; professions?: string[] }> }
      recentPlayers.value = (data.items || []).map(p => ({
        id: p.account,
        name: p.account,
        profession: p.professions?.[0] || 'Unknown'
      }))
    }
  } catch (error) { console.error('加载最近玩家失败:', error) }
}

const handleQuickAnalyzeFight = async () => {
  if (!recentFights.value.length) { showNotification('暂无最近战斗数据', 'error'); return }
  try {
    await analyzeFight(parseInt(recentFights.value[0].id))
    showNotification('战斗分析完成！报告已生成', 'success', '分析完成')
    loadReports()
  } catch { showNotification('分析失败', 'error') }
}

const handleQuickAnalyzePlayer = () => showNotification('玩家分析功能开发中', 'warning', '提示')
const handleQuickAnalyzeTeam = () => showNotification('团队分析功能开发中', 'warning', '提示')

const handleAnalyze = async (type: string, id: string) => {
  try {
    if (type === 'fight') { await analyzeFight(parseInt(id)); loadReports() }
    else if (type === 'member') { await analyzeMember(parseInt(id)); loadReports() }
    else if (type === 'build') { await analyzeBuild(parseInt(id)); loadReports() }
    showNotification(`${type}分析完成`, 'success', '分析完成')
  } catch { showNotification('分析失败', 'error') }
}

const runPersonalGrowth = async () => {
  try {
    await analyzePersonalGrowth(selectedPlayerAccount.value, growthFightCount.value)
    showNotification('个人成长档案生成完成', 'success', '分析完成')
  } catch { showNotification('分析失败', 'error') }
}

const runDeathAttribution = async () => {
  try {
    await analyzeDeathAttribution(selectedPlayerAccount.value)
    showNotification('死亡归因分析完成', 'success', '分析完成')
  } catch { showNotification('分析失败', 'error') }
}

const runSquadSynergy = async () => {
  try {
    await analyzeSquadSynergy(parseInt(selectedFightId.value))
    showNotification('小队协同诊断完成', 'success', '分析完成')
  } catch { showNotification('分析失败', 'error') }
}

const runBuildExecution = async () => {
  try {
    await analyzeBuildExecution(selectedPlayerAccount.value)
    showNotification('Build执行验证完成', 'success', '分析完成')
  } catch { showNotification('验证失败', 'error') }
}

const runCriticalMoments = async () => {
  try {
    await analyzeCriticalMoments(parseInt(selectedFightId.value))
    showNotification('关键片段复盘完成', 'success', '分析完成')
  } catch { showNotification('分析失败', 'error') }
}

const handleViewReport = async (id: string) => { try { await viewReport(id) } catch { showNotification('获取报告详情失败', 'error') } }
const handleDeleteReport = async (id: string) => { try { await deleteReport(id); showNotification('报告删除成功', 'success') } catch { showNotification('删除失败', 'error') } }
const handleFilterChange = (filter: string) => { reportFilter.value = filter; loadReports() }
const handleTrendTimeRangeChange = (range: string) => { trendTimeRange.value = range; loadTrend(range) }
const handleConfigUpdated = () => { loadAiStatus(); showNotification('配置已更新', 'success') }

onMounted(() => { handleRefresh() })
</script>

<script lang="ts">
export default { name: 'DataAiAnalysisView' }
</script>

<style scoped>
.animate-pulse-slow { animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 0.6; } }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px); }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
