<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl"><SvgIcon icon="file-text" :size="24" class="text-purple-400" /></div>
        <h2 class="text-xl font-bold text-white">分析报告</h2>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="localFilter" @change="$emit('filter-change', localFilter)" class="appearance-none bg-neutral-card-active text-white text-sm px-4 py-2 pr-8 rounded-lg border border-neutral-border cursor-pointer">
          <option value="all">全部</option><option value="fight">战斗分析</option><option value="player">玩家分析</option><option value="build">Build分析</option>
        </select>
        <button @click="$emit('refresh')" :disabled="loading" class="flex items-center gap-2 px-4 py-2 bg-neutral-card-active/50 hover:bg-neutral-card-active rounded-lg transition-colors">
          <SvgIcon icon="refresh-cw" :size="16" :class="{ 'animate-spin': loading }" class="text-neutral-text-tertiary" />
          <span class="text-sm text-neutral-text-tertiary">刷新</span>
        </button>
      </div>
    </div>
    <div v-if="loading && !reports.length" class="space-y-3"><div v-for="i in 3" :key="i" class="h-20 bg-neutral-card-active/50 rounded-xl animate-pulse" /></div>
    <div v-else-if="reports.length" class="space-y-3">
      <div v-for="report in reports" :key="report.id" class="p-4 bg-neutral-card-active/50 rounded-xl hover:bg-neutral-card-active transition-all cursor-pointer" @click="$emit('view', String(report.id))">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-white">{{ getReportTypeName(report.report_type) }}</span>
          <span v-if="report.ai_score" class="text-sm font-semibold" :class="getScoreClass(report.ai_score)">{{ report.ai_score.toFixed(0) }}</span>
        </div>
        <p class="text-sm text-neutral-text-secondary truncate mb-2">{{ report.summary || '无摘要' }}</p>
        <div class="flex items-center justify-between">
          <span class="text-xs text-neutral-text-tertiary">{{ formatDate(report.created_at) }}</span>
          <button @click.stop="$emit('delete', String(report.id))" class="text-xs text-error hover:text-error/80">删除</button>
        </div>
      </div>
      <button v-if="hasMore" @click="$emit('load-more')" :disabled="loading" class="w-full py-3 text-center text-sm text-neutral-text-secondary hover:text-white transition-colors">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>
    <div v-else class="text-center py-12"><p class="text-neutral-text-tertiary">暂无报告</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import type { AiReport } from '@/services/ai/aiService'

interface LocalAiReport { id: string | number; report_type: string; target_type: string; summary?: string; ai_score?: number; created_at: string }

const props = defineProps<{ reports: LocalAiReport[]; loading: boolean; hasMore: boolean; filter: string }>()
const emit = defineEmits<{ refresh: []; 'load-more': []; view: [id: string]; delete: [id: string]; 'filter-change': [filter: string] }>()

const localFilter = ref(props.filter)
watch(() => props.filter, (v) => { localFilter.value = v })

const getReportTypeName = (type: string) => {
  const map: Record<string, string> = { fight: '战斗分析', player: '玩家分析', build: 'Build分析' }
  return map[type] || type
}
const getScoreClass = (score: number) => score >= 80 ? 'text-status-success' : score >= 60 ? 'text-warning' : 'text-error'
const formatDate = (date: string) => new Date(date).toLocaleDateString('zh-CN')
</script>
