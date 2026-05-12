<template>
  <Dialog
    v-model:visible="localVisible"
    :header="`维度评分详情：${account}`"
    modal
    :style="{ width: '560px', maxWidth: '95vw' }"
    :breakpoints="{ '960px': '95vw' }"
    class="game-dialog"
  >
    <LoadingState
      v-if="loading"
      text="加载评分详情中..."
    />
    <div
      v-else-if="data"
      class="space-y-5"
    >
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <div>
            <p class="text-xs text-neutral-text-secondary mb-1">
              平均总分
            </p>
            <p class="text-3xl font-bold text-primary">
              {{ data.avg_total_score }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-xs text-neutral-text-secondary mb-1">
              等级
            </p>
            <span :class="gradeClass(data.avg_grade)">{{ data.avg_grade?.toUpperCase() }}</span>
          </div>
          <div class="text-right">
            <p class="text-xs text-neutral-text-secondary mb-1">
              统计场次
            </p>
            <p class="text-xl font-semibold text-neutral-text">
              {{ data.total_fights }}
            </p>
          </div>
        </div>
        <div
          v-if="data.role_label || data.most_used_profession"
          class="flex items-center gap-2 pt-2 border-t border-neutral-border"
        >
          <div
            v-if="data.role_label"
            class="flex items-center gap-1"
          >
            <span class="text-xs text-neutral-text-secondary">角色定位：</span>
            <span class="px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">{{ data.role_label }}</span>
          </div>
          <div
            v-if="data.most_used_profession"
            class="flex items-center gap-1"
          >
            <span class="text-xs text-neutral-text-secondary">常用职业：</span>
            <span class="px-2 py-1 rounded-full text-xs bg-secondary/10 text-secondary">{{ data.most_used_profession }}</span>
          </div>
        </div>
      </div>
      <div class="space-y-3">
        <div
          v-for="dim in sortedDimensions"
          :key="dim.key"
          class="card p-3"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-neutral-text">{{ dim.label }}</span>
            <span class="text-sm text-neutral-text-secondary">
              权重 {{ dim.weight }} × 得分 {{ dim.score }} = <span class="font-semibold text-primary">{{ dim.weighted_score }}</span>
            </span>
          </div>
          <div class="w-full h-2 bg-neutral-border rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="scoreBarClass(dim.score)"
              :style="{ width: dim.score + '%' }"
            />
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 评分维度详情对话框组件
 * 功能：展示单个账号的评分维度详情
 */

import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'

const props = defineProps<{
  visible: boolean
  account: string
  loading: boolean
  data: any
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})

const sortedDimensions = computed(() => {
  if (!props.data?.dimensions) return []
  const dims = props.data.dimensions as Record<string, any>
  return Object.entries(dims)
    .map(([key, val]) => ({ key, ...val }))
    .sort((a, b) => (b.weighted_score || 0) - (a.weighted_score || 0))
})

function gradeClass(g?: string) {
  const base = 'game-badge text-lg'
  if (g === 's') return `${base} game-badge-legendary`
  if (g === 'a') return `${base} game-badge-exotic`
  if (g === 'b') return `${base} game-badge-rare`
  return base
}

function scoreBarClass(score: number) {
  if (score >= 80) return 'bg-gradient-to-r from-status-error to-status-warning'
  if (score >= 60) return 'bg-gradient-to-r from-status-warning to-primary'
  if (score >= 40) return 'bg-gradient-to-r from-primary to-secondary'
  return 'bg-neutral-text-secondary'
}
</script>
