<template>
  <div class="ai-analysis-view">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">
        AI分析
      </h1>
      
      <!-- 标签切换 -->
      <div class="flex bg-gray-700 rounded-lg p-1">
        <button 
          @click="activeTab = 'analysis'"
          :class="[
            'px-4 py-2 rounded-md transition-colors',
            activeTab === 'analysis' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
          ]"
        >
          <span class="flex items-center gap-2">
            <SvgIcon icon="brain" :size="16" />
            分析中心
          </span>
        </button>
        <button 
          @click="activeTab = 'config'"
          :class="[
            'px-4 py-2 rounded-md transition-colors',
            activeTab === 'config' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
          ]"
        >
          <span class="flex items-center gap-2">
            <SvgIcon icon="settings" :size="16" />
            配置管理
          </span>
        </button>
      </div>
    </div>

    <!-- 配置管理面板 -->
    <div v-if="activeTab === 'config'">
      <AiConfigPanel />
    </div>

    <!-- 分析中心 -->
    <div v-else>
      <!-- 状态提示 -->
      <div 
        v-if="!aiEnabled"
        class="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mb-6"
      >
        <div class="flex items-center gap-2">
          <SvgIcon icon="alert-circle" :size="20" class="text-yellow-400" />
          <span class="text-yellow-300">
            AI功能尚未配置或未启用，请先在配置管理中完成API密钥配置。
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <AiReportList
          :reports="reports"
          :loading="loading"
          :has-more="hasMore"
          :disabled="!aiEnabled"
          @view-report="viewReport"
          @load-more="loadMoreReports"
        />
        
        <AiSuggestions
          :suggestions-data="suggestionsData"
          :loading="loadingSuggestions"
          :disabled="!aiEnabled"
        />
      </div>
      
      <div class="mb-6">
        <AiTrendAnalysis
          :trend-data="trendData"
          :loading="loadingTrend"
          :disabled="!aiEnabled"
        />
      </div>
      
      <AiAnalysisTools
        :disabled="!aiEnabled"
        @analyze-fight="analyzeFight"
        @analyze-member="analyzeMember"
        @analyze-build="analyzeBuild"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import AiAnalysisTools from '@/components/ai/AiAnalysisTools.vue'
import AiConfigPanel from '@/components/ai/AiConfigPanel.vue'
import AiReportList from '@/components/ai/AiReportList.vue'
import AiSuggestions from '@/components/ai/AiSuggestions.vue'
import AiTrendAnalysis from '@/components/ai/AiTrendAnalysis.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { aiService } from '@/services'
import type { AiReport } from '@/services/ai/aiService'
import { onMounted, ref } from 'vue'

const activeTab = ref<'analysis' | 'config'>('analysis')
const aiEnabled = ref(true)

const reports = ref<AiReport[]>([])

interface SuggestionsData {
  suggestions: string[]
  high_priority?: string[]
  _metadata?: unknown
}
const suggestionsData = ref<SuggestionsData | null>(null)

interface TrendData {
  data_points?: number
  total_damage?: number
  total_kills?: number
  avg_duration?: number
  trend?: string
  predictions?: unknown[]
  anomalies?: unknown[]
  insights?: string[]
  _metadata?: unknown
}
const trendData = ref<TrendData | null>(null)

const loading = ref(false)
const loadingSuggestions = ref(false)
const loadingTrend = ref(false)
const hasMore = ref(true)
const page = ref(1)
const pageSize = ref(10)

const loadAiStatus = async () => {
  try {
    const response = await aiService.getStatus()
    if (response.success && response.data) {
      aiEnabled.value = response.data.config?.enabled || false
    }
  } catch (error) {
    aiEnabled.value = false
    console.error('获取AI状态失败:', error)
  }
}

const loadReports = async () => {
  loading.value = true
  try {
    const response = await aiService.getReports({
      page: page.value,
      page_size: pageSize.value
    })
    if (response.success && response.data) {
      const data = response.data as any
      if (page.value === 1) {
        reports.value = data.items || []
      } else {
        reports.value = [...reports.value, ...(data.items || [])]
      }
      hasMore.value = (data.items || []).length === pageSize.value
    }
  } catch (error) {
    console.error('加载AI报告失败:', error)
  } finally {
    loading.value = false
  }
}

const loadMoreReports = () => {
  if (!hasMore.value || loading.value) return
  page.value++
  loadReports()
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

const loadTrend = async () => {
  loadingTrend.value = true
  try {
    const response = await aiService.getTrendAnalysis()
    if (response.success && response.data) {
      trendData.value = response.data as TrendData
    }
  } catch (error) {
    console.error('加载AI趋势分析失败:', error)
  } finally {
    loadingTrend.value = false
  }
}

const viewReport = (reportId: string) => {
  // 查看报告详情的逻辑
}

const analyzeFight = async (fightId: string) => {
  try {
    const response = await aiService.analyzeFight(parseInt(fightId))
    if (response.success) {
      page.value = 1
      loadReports()
    }
  } catch (error) {
    console.error('分析战斗失败:', error)
  }
}

const analyzeMember = async (memberId: string) => {
  try {
    const response = await aiService.analyzeMemberSkills(parseInt(memberId))
    if (response.success) {
      page.value = 1
      loadReports()
    }
  } catch (error) {
    console.error('分析成员失败:', error)
  }
}

const analyzeBuild = async (buildId: string) => {
  try {
    const response = await aiService.analyzeBuild(parseInt(buildId))
    if (response.success) {
      page.value = 1
      loadReports()
    }
  } catch (error) {
    console.error('分析Build失败:', error)
  }
}

onMounted(() => {
  loadAiStatus()
  loadReports()
  loadSuggestions()
  loadTrend()
})
</script>

<style scoped>
.ai-analysis-view {
  padding: 20px;
}
</style>