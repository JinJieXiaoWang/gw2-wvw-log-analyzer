<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-ai/20 to-emerald-500/20 rounded-xl"><SvgIcon icon="trending-up" :size="24" class="text-ai" /></div>
        <h2 class="text-xl font-bold text-white">战斗趋势分析</h2>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="localTimeRange" @change="$emit('time-range-change', localTimeRange)" class="appearance-none bg-neutral-card-active text-white text-sm px-4 py-2 pr-8 rounded-lg border border-neutral-border cursor-pointer">
          <option value="7d">最近7天</option><option value="30d">最近30天</option><option value="90d">最近90天</option>
        </select>
        <button @click="$emit('refresh')" :disabled="loading" class="flex items-center gap-2 px-4 py-2 bg-neutral-card-active/50 hover:bg-neutral-card-active rounded-lg transition-colors">
          <SvgIcon icon="refresh-cw" :size="16" :class="{ 'animate-spin': loading }" class="text-neutral-text-tertiary" />
          <span class="text-sm text-neutral-text-tertiary">刷新</span>
        </button>
      </div>
    </div>
    <div v-if="loading" class="h-48 bg-neutral-card-active/50 rounded-xl animate-pulse" />
    <div v-else-if="data" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="p-4 bg-neutral-card-active/50 rounded-xl"><p class="text-sm text-neutral-text-tertiary">数据点数</p><p class="text-2xl font-bold text-white">{{ data.data_points || 0 }}</p></div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl"><p class="text-sm text-neutral-text-tertiary">总伤害</p><p class="text-2xl font-bold text-primary">{{ formatNumber(data.total_damage) }}</p></div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl"><p class="text-sm text-neutral-text-tertiary">击杀/死亡</p><p class="text-2xl font-bold text-ai">{{ data.total_kills || 0 }}</p></div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl"><p class="text-sm text-neutral-text-tertiary">趋势</p><p class="text-2xl font-bold" :class="trendClass">{{ data.trend || '未知' }}</p></div>
      </div>
      <div v-if="data.insights?.length" class="p-4 bg-neutral-card-active/50 rounded-xl">
        <p class="text-sm text-neutral-text-tertiary mb-2">关键洞察</p>
        <p v-for="(insight, i) in data.insights.slice(0, 3)" :key="i" class="text-sm text-neutral-text-secondary mb-1">{{ insight }}</p>
      </div>
    </div>
    <div v-else class="text-center py-8"><p class="text-neutral-text-tertiary">暂无趋势数据</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface TrendData { data_points?: number; total_damage?: number; total_kills?: number; avg_duration?: number; trend?: string; insights?: string[] }

const props = defineProps<{ data: TrendData | null; loading: boolean; timeRange: string }>()
const emit = defineEmits<{ refresh: []; 'time-range-change': [range: string] }>()

const localTimeRange = ref(props.timeRange)

const trendClass = computed(() => {
  if (props.data?.trend === '上升') return 'text-status-success'
  if (props.data?.trend === '下降') return 'text-error'
  return 'text-warning'
})

const formatNumber = (num?: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
