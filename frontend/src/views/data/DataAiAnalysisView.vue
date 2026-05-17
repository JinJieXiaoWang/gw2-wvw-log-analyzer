<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-bg via-slate-950 to-neutral-bg relative overflow-hidden">
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <!-- 动态值，无法使用 Tailwind 静态类 -->
      <div
        class="absolute top-0 left-1/4 bg-primary/8 rounded-full blur-3xl animate-pulse-slow"
        :style="decoStyle"
      />
      <!-- 动态值，无法使用 Tailwind 静态类 -->
      <div
        class="absolute bottom-0 right-1/4 bg-purple-600/8 rounded-full blur-3xl animate-pulse-slow"
        :style="decoStyleDelayed"
      />
      <div class="absolute inset-0 opacity-[0.02] bg-[linear-gradient(rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[length:50px_50px]" />
    </div>
    <div class="relative z-10 p-4 md:p-6 lg:p-8">
      <AiAnalysisPageHeader
        :page-title="PAGE_TITLE"
        :page-subtitle="PAGE_SUBTITLE"
        :is-refreshing="isRefreshing"
        :btn-refresh="BTN_REFRESH"
        :btn-refreshing="BTN_REFRESHING"
        :btn-config-manage="BTN_CONFIG_MANAGE"
        :ai-config="aiConfig"
        :ai-stats="aiStats"
        @refresh="handleRefresh"
        @toggle-config="showConfig = !showConfig"
        @test-connection="testConnection"
      />

      <div
        v-if="showConfig"
        class="bg-neutral-card/50 backdrop-blur-sm rounded-2xl border border-neutral-border p-6 lg:p-8 mb-6"
      >
        <AiConfigPanel @config-updated="handleConfigUpdated" />
      </div>

      <div class="flex items-center gap-1 mb-6 overflow-x-auto pb-1 scrollbar-hide">
        <button
          v-for="tab in ANALYSIS_TABS"
          :key="tab.key"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all"
          :class="activeAnalysisTab === tab.key ? 'bg-primary/20 text-primary border border-primary/30' : 'text-neutral-text-secondary hover:text-white hover:bg-neutral-card-active'"
          @click="activeAnalysisTab = tab.key"
        >
          <SvgIcon
            :icon="tab.icon"
            :size="16"
          />
          {{ tab.label }}
        </button>
      </div>

      <AiAnalysisOverviewTab
        v-if="activeAnalysisTab === 'overview'"
        :ai-enabled="aiEnabled"
        :analyzing="analyzing"
        :testing-connection="testingConnection"
        :recent-fights="recentFights"
        :recent-players="recentPlayers"
        :recent-builds="recentBuilds"
        :ai-config="aiConfig"
        :ai-stats="aiStats"
        :suggestions-data="suggestionsData"
        :loading-suggestions="loadingSuggestions"
        :trend-data="trendData"
        :loading-trend="loadingTrend"
        :trend-time-range="trendTimeRange"
        :filtered-reports="filteredReports"
        :loading="loading"
        :has-more="hasMore"
        :report-filter="reportFilter"
        @quick-analyze-fight="handleQuickAnalyzeFight"
        @quick-analyze-player="handleQuickAnalyzePlayer"
        @quick-analyze-team="handleQuickAnalyzeTeam"
        @analyze="handleAnalyze"
        @refresh-suggestions="loadSuggestions"
        @refresh-trend="loadTrend"
        @time-range-change="handleTrendTimeRangeChange"
        @refresh-reports="loadReports"
        @load-more-reports="loadMoreReports"
        @view-report="handleViewReport"
        @delete-report="handleDeleteReport"
        @filter-change="handleFilterChange"
        @test-connection="testConnection"
      />

      <AiAnalysisGrowthTab
        v-else-if="activeAnalysisTab === 'growth'"
        v-model:selected-player-account="selectedPlayerAccount"
        v-model:growth-fight-count="growthFightCount"
        class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border"
        :recent-players="recentPlayers"
        :personal-growth-data="personalGrowthData"
        :loading-personal-growth="loadingPersonalGrowth"
        @run="runPersonalGrowth"
      />

      <AiAnalysisDeathTab
        v-else-if="activeAnalysisTab === 'death'"
        v-model:selected-player-account="selectedPlayerAccount"
        class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border"
        :recent-players="recentPlayers"
        :death-attribution-data="deathAttributionData"
        :loading-death-attribution="loadingDeathAttribution"
        @run="runDeathAttribution"
      />

      <AiAnalysisSquadTab
        v-else-if="activeAnalysisTab === 'squad'"
        v-model:selected-fight-id="selectedFightId"
        class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border"
        :recent-fights="recentFights"
        :squad-synergy-data="squadSynergyData"
        :loading-squad-synergy="loadingSquadSynergy"
        @run="runSquadSynergy"
      />

      <AiAnalysisBuildVerifyTab
        v-else-if="activeAnalysisTab === 'build'"
        v-model:selected-player-account="selectedPlayerAccount"
        class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border"
        :recent-players="recentPlayers"
        :build-execution-data="buildExecutionData"
        :loading-build-execution="loadingBuildExecution"
        @run="runBuildExecution"
      />

      <AiAnalysisMomentsTab
        v-else-if="activeAnalysisTab === 'moments'"
        v-model:selected-fight-id="selectedFightId"
        class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border"
        :recent-fights="recentFights"
        :critical-moments-data="criticalMomentsData"
        :loading-critical-moments="loadingCriticalMoments"
        @run="runCriticalMoments"
      />
    </div>

    <AiReportDetailModal
      v-if="selectedReport"
      :report="selectedReport"
      @close="selectedReport = null"
    />
    <AiAnalyzingModal
      v-if="analyzing"
      :title="analyzingTitle"
      :message="analyzingMessage"
      :progress="analyzingProgress"
    />
    <AiNotificationToast
      v-bind="notification"
      @close="notification.show = false"
    />
  </div>
</template>

<script setup lang="ts">
import AiAnalysisBuildVerifyTab from '@/components/ai/AiAnalysisBuildVerifyTab.vue'
import AiAnalysisDeathTab from '@/components/ai/AiAnalysisDeathTab.vue'
import AiAnalysisGrowthTab from '@/components/ai/AiAnalysisGrowthTab.vue'
import AiAnalysisMomentsTab from '@/components/ai/AiAnalysisMomentsTab.vue'
import AiAnalysisOverviewTab from '@/components/ai/AiAnalysisOverviewTab.vue'
import AiAnalysisPageHeader from '@/components/ai/AiAnalysisPageHeader.vue'
import AiAnalysisSquadTab from '@/components/ai/AiAnalysisSquadTab.vue'
import AiAnalyzingModal from '@/components/ai/AiAnalyzingModal.vue'
import AiConfigPanel from '@/components/ai/AiConfigPanel.vue'
import AiNotificationToast from '@/components/ai/AiNotificationToast.vue'
import AiReportDetailModal from '@/components/ai/AiReportDetailModal.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { useAiAnalysis, useAiReports } from '@/composables/useAiAnalysis'
import { aiService, attendanceService, fightsService } from '@/services'
import {
  PAGE_TITLE,
  PAGE_SUBTITLE,
  BTN_REFRESH,
  BTN_REFRESHING,
  BTN_CONFIG_MANAGE,
  ANALYSIS_TABS,
  NOTIFY_TITLE_SUCCESS,
  NOTIFY_TITLE_WARNING,
  NOTIFY_TITLE_ERROR,
  NOTIFY_TITLE_TEST_SUCCESS,
  NOTIFY_TITLE_TEST_FAIL,
  NOTIFY_TITLE_ANALYZE_COMPLETE,
  NOTIFY_MSG_REFRESH_COMPLETE,
  NOTIFY_MSG_TEST_SUCCESS,
  NOTIFY_MSG_TEST_FAIL,
  NOTIFY_MSG_TEST_FAIL_SHORT,
  NOTIFY_MSG_NO_FIGHT_DATA,
  NOTIFY_MSG_NO_PLAYER_DATA,
  NOTIFY_MSG_FIGHT_ANALYZE_COMPLETE,
  NOTIFY_MSG_ANALYZE_FAIL,
  NOTIFY_MSG_PERSONAL_GROWTH_COMPLETE,
  NOTIFY_MSG_DEATH_ANALYSIS_COMPLETE,
  NOTIFY_MSG_SQUAD_SYNERGY_COMPLETE,
  NOTIFY_MSG_BUILD_VERIFY_COMPLETE,
  NOTIFY_MSG_CRITICAL_MOMENTS_COMPLETE,
  NOTIFY_MSG_VERIFY_FAIL,
  NOTIFY_MSG_GET_REPORT_FAIL,
  NOTIFY_MSG_DELETE_SUCCESS,
  NOTIFY_MSG_DELETE_FAIL,
  NOTIFY_MSG_CONFIG_UPDATED,
  LOG_REFRESH_FAIL,
  LOG_LOAD_FIGHTS_FAIL,
  LOG_LOAD_PLAYERS_FAIL,
} from '@/constants/aiAnalysis'
import { DECORATION_SIZE } from '@/constants/dimensions'
import { onMounted, reactive, ref } from 'vue'

const FIGHT_NAME_FALLBACK = '战斗'
const FIGHT_PLAYER_COUNT_UNIT = '人'
const UNKNOWN_PROFESSION = 'Unknown'

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
const decoStyle = { width: DECORATION_SIZE, height: DECORATION_SIZE }
const decoStyleDelayed = { width: DECORATION_SIZE, height: DECORATION_SIZE, animationDelay: '1.5s' }

interface FightOption { id: string; name: string; date: string }
interface PlayerOption { id: string; name: string; profession: string }
interface BuildOption { id: string; name: string; profession: string }

const showNotification = (message: string, type: 'success' | 'error' | 'warning' = 'success', title?: string) => {
  notification.title = title || (type === 'success' ? NOTIFY_TITLE_SUCCESS : type === 'warning' ? NOTIFY_TITLE_WARNING : NOTIFY_TITLE_ERROR)
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
    console.error(LOG_REFRESH_FAIL, error)
  } finally {
    isRefreshing.value = false
    showNotification(NOTIFY_MSG_REFRESH_COMPLETE, 'success')
  }
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    const response = await aiService.testConfiguration()
    if (response.success && response.data?.valid) {
      showNotification(NOTIFY_MSG_TEST_SUCCESS, 'success', NOTIFY_TITLE_TEST_SUCCESS)
    } else {
      showNotification(NOTIFY_MSG_TEST_FAIL, 'error', NOTIFY_TITLE_TEST_FAIL)
    }
  } catch (error) {
    showNotification(NOTIFY_MSG_TEST_FAIL_SHORT, 'error', NOTIFY_TITLE_TEST_FAIL)
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
        name: f.map_name ? `${f.map_name} (${f.duration_sec}s, ${f.player_count}${FIGHT_PLAYER_COUNT_UNIT})` : `${FIGHT_NAME_FALLBACK} ${f.id}`,
        date: ''
      })) || []
    }
  } catch (error) { console.error(LOG_LOAD_FIGHTS_FAIL, error) }
}

const loadRecentPlayers = async () => {
  try {
    const response = await attendanceService.getAccounts({ page: 1, page_size: 100 })
    if (response.success && response.data) {
      const data = response.data as { items?: Array<{ account: string; professions?: string[] }> }
      recentPlayers.value = (data.items || []).map(p => ({
        id: p.account,
        name: p.account,
        profession: p.professions?.[0] || UNKNOWN_PROFESSION
      }))
    }
  } catch (error) { console.error(LOG_LOAD_PLAYERS_FAIL, error) }
}

const handleQuickAnalyzeFight = async () => { if (!recentFights.value.length) { showNotification(NOTIFY_MSG_NO_FIGHT_DATA, 'error'); return } try { await analyzeFight(parseInt(recentFights.value[0].id)); showNotification(NOTIFY_MSG_FIGHT_ANALYZE_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE); loadReports() } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }

const handleAnalyze = async (type: string, id: string) => { try { if (type === 'fight') { await analyzeFight(parseInt(id)); loadReports() } else if (type === 'member') { await analyzeMember(parseInt(id)); loadReports() } else if (type === 'build') { await analyzeBuild(parseInt(id)); loadReports() } showNotification(`${type}${NOTIFY_TITLE_ANALYZE_COMPLETE}`, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }

const runPersonalGrowth = async () => { try { await analyzePersonalGrowth(selectedPlayerAccount.value, growthFightCount.value); showNotification(NOTIFY_MSG_PERSONAL_GROWTH_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }
const runDeathAttribution = async () => { try { await analyzeDeathAttribution(selectedPlayerAccount.value); showNotification(NOTIFY_MSG_DEATH_ANALYSIS_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }
const runSquadSynergy = async () => { try { await analyzeSquadSynergy(parseInt(selectedFightId.value)); showNotification(NOTIFY_MSG_SQUAD_SYNERGY_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }
const runBuildExecution = async () => { try { await analyzeBuildExecution(selectedPlayerAccount.value); showNotification(NOTIFY_MSG_BUILD_VERIFY_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_VERIFY_FAIL, 'error') } }
const runCriticalMoments = async () => { try { await analyzeCriticalMoments(parseInt(selectedFightId.value)); showNotification(NOTIFY_MSG_CRITICAL_MOMENTS_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE) } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') } }

const handleViewReport = async (id: string) => { try { await viewReport(id) } catch { showNotification(NOTIFY_MSG_GET_REPORT_FAIL, 'error') } }
const handleDeleteReport = async (id: string) => { try { await deleteReport(id); showNotification(NOTIFY_MSG_DELETE_SUCCESS, 'success') } catch { showNotification(NOTIFY_MSG_DELETE_FAIL, 'error') } }
const handleFilterChange = (filter: string) => { reportFilter.value = filter; loadReports() }
const handleTrendTimeRangeChange = (range: string) => { trendTimeRange.value = range; loadTrend(range) }
const handleConfigUpdated = () => { loadAiStatus(); showNotification(NOTIFY_MSG_CONFIG_UPDATED, 'success') }
const handleQuickAnalyzePlayer = async () => {
  if (!recentPlayers.value.length) { showNotification(NOTIFY_MSG_NO_PLAYER_DATA, 'error'); return }
  try { await analyzePersonalGrowth(recentPlayers.value[0].id, 30); showNotification(NOTIFY_MSG_PERSONAL_GROWTH_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE); loadReports() } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') }
}
const handleQuickAnalyzeTeam = async () => {
  if (!recentFights.value.length) { showNotification(NOTIFY_MSG_NO_FIGHT_DATA, 'error'); return }
  try { await analyzeSquadSynergy(parseInt(recentFights.value[0].id)); showNotification(NOTIFY_MSG_SQUAD_SYNERGY_COMPLETE, 'success', NOTIFY_TITLE_ANALYZE_COMPLETE); loadReports() } catch { showNotification(NOTIFY_MSG_ANALYZE_FAIL, 'error') }
}

onMounted(() => { handleRefresh() })
</script>

<script lang="ts">
export default { name: 'DataAiAnalysisView' }
</script>

<style scoped>
.animate-pulse-slow { animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 0.6; } }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
