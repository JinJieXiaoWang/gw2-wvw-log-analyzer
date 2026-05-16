<template>
  <div>
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <div class="lg:col-span-8 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiQuickActions :recent-fights="recentFights" :recent-players="recentPlayers" :recent-builds="recentBuilds" :disabled="!aiEnabled || analyzing" @analyze-fight="$emit('quickAnalyzeFight')" @analyze-player="$emit('quickAnalyzePlayer')" @analyze-team="$emit('quickAnalyzeTeam')" />
      </div>
      <div class="lg:col-span-4 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiSystemStatus :config="aiConfig" :stats="aiStats" :testing-connection="testingConnection" @test-connection="$emit('testConnection')" />
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiSuggestionsPanel :data="suggestionsData" :loading="loadingSuggestions" @refresh="$emit('refreshSuggestions')" />
      </div>
      <div class="bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiTrendPanel :data="trendData" :loading="loadingTrend" :time-range="trendTimeRange" @refresh="$emit('refreshTrend')" @time-range-change="$emit('timeRangeChange', $event)" />
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="lg:col-span-4 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiAnalysisToolsPanel :recent-fights="recentFights" :recent-players="recentPlayers" :recent-builds="recentBuilds" :disabled="!aiEnabled" @analyze="(type, id) => $emit('analyze', type, id)" />
      </div>
      <div class="lg:col-span-8 bg-neutral-card/80 backdrop-blur-sm rounded-2xl p-6 border border-neutral-border">
        <AiReportPanel :reports="filteredReports" :loading="loading" :has-more="hasMore" :filter="reportFilter" @refresh="$emit('refreshReports')" @load-more="$emit('loadMoreReports')" @view="$emit('viewReport', $event)" @delete="$emit('deleteReport', $event)" @filter-change="$emit('filterChange', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AiAnalysisToolsPanel from './AiAnalysisToolsPanel.vue'
import AiQuickActions from './AiQuickActions.vue'
import AiReportPanel from './AiReportPanel.vue'
import AiSuggestionsPanel from './AiSuggestionsPanel.vue'
import AiSystemStatus from './AiSystemStatus.vue'
import AiTrendPanel from './AiTrendPanel.vue'

interface FightOption { id: string; name: string; date: string }
interface PlayerOption { id: string; name: string; profession: string }
interface BuildOption { id: string; name: string; profession: string }

interface Props {
  aiEnabled: boolean
  analyzing: boolean
  testingConnection: boolean
  recentFights: FightOption[]
  recentPlayers: PlayerOption[]
  recentBuilds: BuildOption[]
  aiConfig: { enabled: boolean; provider: string; has_api_key: boolean; cache_enabled: boolean; fallback_enabled: boolean }
  aiStats: { cache_hit_rate: number; cache_entries: number; today_count: number; response_time: number }
  suggestionsData: any
  loadingSuggestions: boolean
  trendData: any
  loadingTrend: boolean
  trendTimeRange: string
  filteredReports: any[]
  loading: boolean
  hasMore: boolean
  reportFilter: string
}

defineProps<Props>()

defineEmits<{
  quickAnalyzeFight: []
  quickAnalyzePlayer: []
  quickAnalyzeTeam: []
  analyze: [type: string, id: string]
  refreshSuggestions: []
  refreshTrend: []
  timeRangeChange: [range: string]
  refreshReports: []
  loadMoreReports: []
  viewReport: [id: string]
  deleteReport: [id: string]
  filterChange: [filter: string]
  testConnection: []
}>()
</script>

<script lang="ts">
export default { name: 'AiAnalysisOverviewTab' }
</script>
