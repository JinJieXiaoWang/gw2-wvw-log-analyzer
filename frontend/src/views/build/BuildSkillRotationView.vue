<script setup lang="ts">
// 模块功能：技能循环主视图组件
// 作者：帅姐姐
// 创建日期：2026-05-04
// 更新日期：2026-05-14

import { skillRotationService } from '@/services/build/skillRotationService'
import AnalysisConfig from '@/components/skillRotation/AnalysisConfig.vue'
import CycleView from '@/components/skillRotation/CycleView.vue'
import HeatmapView from '@/components/skillRotation/HeatmapView.vue'
import ImportDialog from '@/components/skillRotation/ImportDialog.vue'
import MistakeStats from '@/components/skillRotation/MistakeStats.vue'
import OptimizationSuggestions from '@/components/skillRotation/OptimizationSuggestions.vue'
import RotationViewTabs from '@/components/skillRotation/RotationViewTabs.vue'
import SkillDetails from '@/components/skillRotation/SkillDetails.vue'
import StatsOverview from '@/components/skillRotation/StatsOverview.vue'
import TimelineView from '@/components/skillRotation/TimelineView.vue'
import PageHeader from '@/components/common/layout/PageHeader.vue'
import { useSkillRotationStore } from '@/store/skillRotation'
import { storeToRefs } from 'pinia'
import { useToast } from 'primevue/usetoast'
import { computed, ref } from 'vue'

const toast = useToast()
const rotationStore = useSkillRotationStore()
const {
  selectedLogId,
  selectedMemberId,
  viewMode,
  analysisResult,
  isLoading,
  error,
  hasResult,
  isReady,
  filteredEvents
} = storeToRefs(rotationStore)

const {
  performAnalysis,
  setViewMode,
  setCompareMode,
  setTimeRange,
  selectLog,
  selectMember
} = rotationStore

const showImportDialog = ref(false)

// 安全访问数据
const safeStats = computed(() => analysisResult.value?.stats)
const safeTopSkills = computed(() => safeStats.value?.top_skills)
const safeMistakes = computed(() => analysisResult.value?.mistakes)
const safeOptimizations = computed(() => analysisResult.value?.optimizations)
const safeFightDuration = computed(() => analysisResult.value?.fight_duration)

function handleLogIdUpdate(value: string | null) {
  selectLog(value)
}

function handleMemberIdUpdate(value: string | null) {
  selectMember(value)
}

function handleViewModeUpdate(value: string) {
  setViewMode(value as any)
}

function handleCompareModeUpdate(value: string) {
  setCompareMode(value as any)
}

function handleTimeRangeUpdate(value: string) {
  setTimeRange(value as any)
}

function handleShowImportDialog() {
  showImportDialog.value = true
}

async function handleExportReport() {
  if (!selectedLogId.value || !selectedMemberId.value) {
    toast.add({
      severity: 'warn',
      summary: '警告',
      detail: '请先选择日志和玩家',
      life: 3000
    })
    return
  }

  try {
    const reportData = await skillRotationService.exportReport(selectedLogId.value, selectedMemberId.value)
    if (reportData) {
      // 根据后端返回的格式选择导出类型，默认为JSON
      const format = reportData.format || 'json'
      let blob: Blob
      let filename: string

      if (format === 'json') {
        const jsonStr = JSON.stringify(reportData, null, 2)
        blob = new Blob([jsonStr], { type: 'application/json' })
        filename = `skill-rotation-report-${Date.now()}.json`
      } else {
        // PDF等其他格式暂不支持，回退到JSON
        const jsonStr = JSON.stringify(reportData, null, 2)
        blob = new Blob([jsonStr], { type: 'application/json' })
        filename = `skill-rotation-report-${Date.now()}.json`
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '报告导出成功',
        life: 3000
      })
    }
  } catch (err) {
    console.error('导出报告失败:', err)
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: '导出报告失败',
      life: 3000
    })
  }
}

function handleImportRotation(data: { ideal: string; actual: string }) {
  // TODO: 实现导入对比功能
  toast.add({
    severity: 'info',
    summary: '提示',
    detail: '导入功能开发中',
    life: 3000
  })
}
</script>

<template>
  <div class="skill-rotation-page min-h-screen bg-[#0d0d0f] text-white p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 欢迎横幅 -->
      <PageHeader
        title="技能循环分析"
        subtitle="对比理想循环与实战循环，优化技能释放顺序"
        icon="pi pi-sync"
        icon-gradient="bg-gradient-to-br from-secondary to-status-warning"
      >
        <template #actions>
          <BaseButton
            label="导入对比"
            icon="pi pi-upload"
            variant="secondary"
            @click="handleShowImportDialog"
          />
          <BaseButton
            label="导出报告"
            icon="pi pi-download"
            variant="game"
            @click="handleExportReport"
          />
        </template>
      </PageHeader>

      <div class="mt-6 space-y-6">
        <!-- 配置区域 -->
        <AnalysisConfig
          :selected-log-id="selectedLogId"
          :selected-member-id="selectedMemberId"
          :loading="isLoading"
          :disabled="!isReady"
          @update:selected-log-id="handleLogIdUpdate"
          @update:selected-member-id="handleMemberIdUpdate"
          @update:compare-mode="handleCompareModeUpdate"
          @update:time-range="handleTimeRangeUpdate"
          @analyze="performAnalysis"
        />

        <!-- 错误提示 -->
        <div
          v-if="error"
          class="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400"
        >
          {{ error }}
        </div>

        <!-- 空数据提示 -->
        <div
          v-else-if="hasResult && analysisResult && (!filteredEvents || filteredEvents.length === 0)"
          class="bg-neutral-bg-secondary border border-neutral-border/30 rounded-lg p-8 text-center"
        >
          <i class="pi pi-info-circle text-4xl text-neutral-text-secondary mb-4" />
          <p class="text-neutral-text font-medium mb-2">
            暂无技能循环数据
          </p>
          <p class="text-neutral-text-secondary text-sm mb-4">
            可能的原因：EI解析器版本过旧、该日志未包含技能循环信息、或所选职业无技能数据。
          </p>
          <p class="text-neutral-text-secondary text-xs">
            建议尝试重新解析日志，或选择其他玩家查看。
          </p>
        </div>

        <!-- 分析结果 -->
        <template v-if="hasResult && analysisResult && filteredEvents && filteredEvents.length > 0">
          <!-- 统计概览 -->
          <StatsOverview :stats="safeStats" />

          <!-- 视图切换 -->
          <RotationViewTabs
            :model-value="viewMode"
            @update:model-value="handleViewModeUpdate"
          />

          <!-- 视图内容 -->
          <template v-if="viewMode === 'cycle'">
            <CycleView :events="filteredEvents" />
          </template>
          <template v-else-if="viewMode === 'timeline'">
            <TimelineView
              :events="filteredEvents"
              :total-duration="safeFightDuration"
            />
          </template>
          <template v-else-if="viewMode === 'heatmap'">
            <HeatmapView
              :events="filteredEvents"
              :top-skills="safeTopSkills"
              :total-duration="safeFightDuration"
            />
          </template>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <!-- 技能详情 -->
            <SkillDetails :top-skills="safeTopSkills" />

            <!-- 错误统计 -->
            <MistakeStats :mistakes="safeMistakes" />
          </div>

          <!-- 优化建议 -->
          <OptimizationSuggestions :suggestions="safeOptimizations" />
        </template>
      </div>
    </div>

    <!-- 导入对话框 -->
    <ImportDialog
      v-model:visible="showImportDialog"
      @import-rotation="handleImportRotation"
    />
  </div>
</template>

<style scoped lang="postcss"></style>
