<template>
  <div class="card animate-slide-in-up" style="animation-delay: 0.9s">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-status-warning/30 to-status-success/30 flex items-center justify-center">
        <i class="pi pi-shield text-status-warning" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">Buff 概览</h3>
        <p class="text-xs text-neutral-text-secondary">平均覆盖率</p>
      </div>
    </div>
    <div v-if="isLoading" class="h-64 flex items-center justify-center text-neutral-text-disabled">
      <i class="pi pi-spin pi-spinner text-3xl" />
    </div>
    <div v-else-if="!buffs" class="h-64 flex items-center justify-center text-neutral-text-disabled">
      <span>暂无数据</span>
    </div>
    <div v-else class="space-y-4">
      <div
        v-for="item in buffList"
        :key="item.key"
        class="flex items-center gap-3"
      >
        <div class="w-20 text-xs text-neutral-text-secondary text-right">{{ item.label }}</div>
        <div class="flex-1 h-3 bg-neutral-bg rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="item.colorClass"
            :style="{ width: Math.min((buffs[item.key] || 0), 100) + '%' }"
          />
        </div>
        <div class="w-12 text-xs font-bold text-right" :class="item.textClass">
          {{ (buffs[item.key] || 0).toFixed(1) }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Buff 覆盖率概览组件 v2.0
 * 功能：展示平均 Buff 覆盖率进度条
 * 更新：2026-05-04 - 替代 AverageStats
 */

defineProps<{
  buffs: Record<string, number> | null
  isLoading: boolean
}>()

const buffList = [
  { key: 'might', label: '力量', colorClass: 'bg-status-error', textClass: 'text-status-error' },
  { key: 'fury', label: '狂怒', colorClass: 'bg-status-warning', textClass: 'text-status-warning' },
  { key: 'quickness', label: '急速', colorClass: 'bg-primary', textClass: 'text-primary' },
  { key: 'alacrity', label: '敏捷', colorClass: 'bg-secondary', textClass: 'text-secondary' },
  { key: 'protection', label: '保护', colorClass: 'bg-status-success', textClass: 'text-status-success' },
  { key: 'stability', label: '稳定', colorClass: 'bg-status-info', textClass: 'text-blue-400' },
]
</script>
