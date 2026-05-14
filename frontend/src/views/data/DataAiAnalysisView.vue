<template>
  <div class="ai-analysis-view">
    <h1 class="text-2xl font-bold mb-6">
      AI分析
    </h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <AiReportList
        :reports="reports"
        :loading="loading"
        :has-more="hasMore"
        @view-report="viewReport"
        @load-more="loadMoreReports"
      />
      
      <AiSuggestions
        :suggestions="suggestions"
        :loading="loadingSuggestions"
      />
    </div>
    
    <div class="mb-6">
      <AiTrendAnalysis
        :trend="trend"
        :loading="loadingTrend"
      />
    </div>
    
    <AiAnalysisTools
      @analyze-fight="analyzeFight"
      @analyze-member="analyzeMember"
      @analyze-build="analyzeBuild"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AiReportList from '@/components/ai/AiReportList.vue'
import AiSuggestions from '@/components/ai/AiSuggestions.vue'
import AiTrendAnalysis from '@/components/ai/AiTrendAnalysis.vue'
import AiAnalysisTools from '@/components/ai/AiAnalysisTools.vue'
import { aiService } from '@/services'
import type { AiReport, AiSuggestion, AiTrend } from '@/services/ai/aiService'

const reports = ref<AiReport[]>([])
const suggestions = ref<AiSuggestion[]>([])
const trend = ref<AiTrend[]>([])
const loading = ref(false)
const loadingSuggestions = ref(false)
const loadingTrend = ref(false)
const hasMore = ref(true)
const page = ref(1)
const pageSize = ref(10)

const loadReports = async () => {
  loading.value = true
  try {
    const response = await aiService.getReports({
      page: page.value,
      page_size: pageSize.value
    })
    if (response.success && response.data) {
      const data = response.data as AiReport[]
      if (page.value === 1) {
        reports.value = data
      } else {
        reports.value = [...reports.value, ...data]
      }
      hasMore.value = data.length === pageSize.value
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
      suggestions.value = response.data as AiSuggestion[]
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
      trend.value = response.data as AiTrend[]
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
      // 处理分析结果
      // 重新加载报告列表
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
      // 处理分析结果
      // 重新加载报告列表
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
      // 处理分析结果
      // 重新加载报告列表
      page.value = 1
      loadReports()
    }
  } catch (error) {
    console.error('分析Build失败:', error)
  }
}

onMounted(() => {
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