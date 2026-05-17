<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl">
          <SvgIcon
            icon="file-text"
            :size="24"
            class="text-purple-400"
          />
        </div>
        <h2 class="text-xl font-bold text-white">
          分析报告
        </h2>
      </div>
      <div class="flex items-center gap-3">
        <BaseSelect
          v-model="localFilter"
          :options="filterOptions"
          option-label="label"
          option-value="value"
          class="w-36"
          @change="$emit('filter-change', localFilter)"
        />
        <BaseButton
          icon="pi pi-refresh"
          size="small"
          text
          :loading="loading"
          @click="$emit('refresh')"
        >
          <span class="text-sm text-neutral-text-tertiary">刷新</span>
        </BaseButton>
      </div>
    </div>
    <div
      v-if="loading && !reports.length"
      class="space-y-3"
    >
      <div
        v-for="i in 3"
        :key="i"
        class="h-20 bg-neutral-card-active/50 rounded-xl animate-pulse"
      />
    </div>
    <div
      v-else-if="reports.length"
      class="space-y-3"
    >
      <div
        v-for="report in reports"
        :key="report.id"
        class="p-4 bg-neutral-card-active/50 rounded-xl hover:bg-neutral-card-active transition-all cursor-pointer"
        @click="$emit('view', String(report.id))"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-white">{{ getReportTypeName(report.report_type) }}</span>
          <span
            v-if="report.ai_score"
            class="text-sm font-semibold"
            :class="getScoreClass(report.ai_score)"
          >{{ report.ai_score.toFixed(0) }}</span>
        </div>
        <p class="text-sm text-neutral-text-secondary truncate mb-2">
          {{ report.summary || '无摘要' }}
        </p>
        <div class="flex items-center justify-between">
          <span class="text-xs text-neutral-text-tertiary">{{ formatDate(report.created_at) }}</span>
          <BaseButton
            severity="danger"
            size="small"
            text
            @click.stop="$emit('delete', String(report.id))"
          >
            <span class="text-xs">删除</span>
          </BaseButton>
        </div>
      </div>
      <BaseButton
        v-if="hasMore"
        class="w-full"
        text
        :loading="loading"
        @click="$emit('load-more')"
      >
        <span class="text-sm text-neutral-text-secondary">{{ loading ? '加载中...' : '加载更多' }}</span>
      </BaseButton>
    </div>
    <div
      v-else
      class="text-center py-12"
    >
      <p class="text-neutral-text-tertiary">
        暂无报告
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import type { AiReport } from '@/services/ai/aiService'

interface LocalAiReport { id: string | number; report_type: string; target_type: string; summary?: string; ai_score?: number; created_at: string }

const props = defineProps<{ reports: LocalAiReport[]; loading: boolean; hasMore: boolean; filter: string }>()
const emit = defineEmits<{ refresh: []; 'load-more': []; view: [id: string]; delete: [id: string]; 'filter-change': [filter: string] }>()

const localFilter = ref(props.filter)
watch(() => props.filter, (v) => { localFilter.value = v })

const filterOptions = [
  { value: 'all', label: '全部' },
  { value: 'fight', label: '战斗分析' },
  { value: 'player', label: '玩家分析' },
  { value: 'build', label: 'Build分析' },
  { value: 'personal_growth', label: '成长档案' },
  { value: 'death_attribution', label: '死亡归因' },
  { value: 'squad_synergy', label: '小队协同' },
  { value: 'build_execution', label: 'Build验证' },
  { value: 'critical_moments', label: '关键片段' },
]

const getReportTypeName = (type: string) => {
  const map: Record<string, string> = {
    fight: '战斗分析',
    player: '玩家分析',
    build: 'Build分析',
    personal_growth: '成长档案',
    death_attribution: '死亡归因',
    squad_synergy: '小队协同',
    build_execution: 'Build验证',
    critical_moments: '关键片段',
  }
  return map[type] || type
}
const getScoreClass = (score: number) => score >= 80 ? 'text-status-success' : score >= 60 ? 'text-warning' : 'text-error'
const formatDate = (date: string) => new Date(date).toLocaleDateString('zh-CN')
</script>

<script lang="ts">
export default { name: 'AiReportPanel' }
</script>
