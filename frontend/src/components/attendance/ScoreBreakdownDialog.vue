<template>
  <Dialog
    v-model:visible="localVisible"
    :header="dialogHeader"
    modal
    class="game-dialog w-[560px] max-w-[95vw]"
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
          class="flex flex-wrap items-center gap-2 pt-2 border-t border-neutral-border"
        >
          <!-- 职业定位（基于常用职业查表） -->
          <div
            v-if="data.profession_role_label"
            class="flex items-center gap-1"
          >
            <span class="text-xs text-neutral-text-secondary">职业定位：</span>
            <span class="px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">{{ data.profession_role_label }}</span>
          </div>
          <!-- 数据定位（基于实际战斗数据） -->
          <div
            v-if="data.data_role_label"
            class="flex items-center gap-1"
          >
            <span class="text-xs text-neutral-text-secondary">数据定位：</span>
            <span
              class="px-2 py-1 rounded-full text-xs"
              :class="dataRoleClass"
              :title="data.data_role_reason"
            >{{ data.data_role_label }}</span>
          </div>
          <div
            v-if="data.most_used_profession"
            class="flex items-center gap-1"
          >
            <span class="text-xs text-neutral-text-secondary">常用职业：</span>
            <span class="px-2 py-1 rounded-full text-xs bg-secondary/10 text-secondary">{{ getProfessionName(data.most_used_profession) }}</span>
          </div>
          <!-- 定位冲突提示 -->
          <div
            v-if="isRoleMismatch"
            class="flex items-center gap-1 text-xs text-warning"
            :title="`职业定位「${data.profession_role_label}」与数据定位「${data.data_role_label}」不一致`"
          >
            <i class="pi pi-exclamation-circle" />
            <span>定位冲突</span>
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
          <ProgressBar
            :value="dim.score"
            :class="progressBarClass(dim.score)"
            class="h-2"
            :show-value="false"
          />
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
import ProgressBar from 'primevue/progressbar'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import { getProfessionName } from '@/services/professionService'

const props = defineProps<{
  visible: boolean
  account: string
  profession?: string
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

const dialogHeader = computed(() => {
  const prof = props.profession ? ` · ${getProfessionName(props.profession)}` : ''
  return `维度评分详情：${props.account}${prof}`
})

const sortedDimensions = computed(() => {
  if (!props.data?.dimensions) return []
  const dims = props.data.dimensions as Record<string, any>
  return Object.entries(dims)
    .map(([key, val]) => ({ key, ...val }))
    .sort((a, b) => (b.weighted_score || 0) - (a.weighted_score || 0))
})

/** 数据定位与职业定位是否冲突 */
const isRoleMismatch = computed(() => {
  return props.data?.profession_role_type && props.data?.data_role_type
    && props.data.profession_role_type !== props.data.data_role_type
})

const dataRoleClass = computed(() => {
  const roleType = props.data?.data_role_type
  if (roleType === 'tank') return 'bg-status-error/10 text-status-error'
  if (roleType === 'support') return 'bg-status-success/10 text-status-success'
  if (roleType === 'control') return 'bg-warning/10 text-warning'
  return 'bg-primary/10 text-primary'
})

function gradeClass(g?: string) {
  const base = 'game-badge text-lg'
  if (g === 's') return `${base} game-badge-legendary`
  if (g === 'a') return `${base} game-badge-exotic`
  if (g === 'b') return `${base} game-badge-rare`
  return base
}

function progressBarClass(score: number) {
  if (score >= 80) return 'progress-bar-high'
  if (score >= 60) return 'progress-bar-medium'
  if (score >= 40) return 'progress-bar-low'
  return 'progress-bar-very-low'
}
</script>
