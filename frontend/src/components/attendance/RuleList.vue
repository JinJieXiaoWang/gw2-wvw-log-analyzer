<template>
  <div class="space-y-3">
    <div
      v-if="rules.length"
      class="text-xs text-neutral-text-secondary mb-2"
    >
      共 {{ rules.length }} 个评分维度
    </div>
    <div
      v-for="rule in rules"
      :key="rule.id || rule.dimension"
      class="card p-3 rounded-lg border border-neutral-border/40"
      :class="rule.is_active ? '' : 'opacity-50'"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-semibold text-neutral-text">{{ rule.dimension }}</span>
            <Tag
              v-if="!rule.is_active"
              value="已禁用"
              severity="secondary"
              class="text-[10px] px-1 py-0"
            />
          </div>
          <p
            v-if="rule.description"
            class="text-xs text-neutral-text-secondary truncate"
          >
            {{ rule.description }}
          </p>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <span class="text-lg font-bold text-primary">{{ (rule.weight * 100).toFixed(0) }}%</span>
          <div class="w-24">
            <div class="h-2 rounded-full bg-neutral-bg overflow-hidden">
              <div
                class="h-full rounded-full bg-primary transition-all"
                :style="{ width: Math.min(rule.weight * 100, 100) + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!rules.length"
      class="text-center py-8 text-neutral-text-secondary text-sm"
    >
      <i class="pi pi-info-circle text-lg mb-2 block" />{{ emptyText }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 评分规则列表组件
 * 功能：展示单个角色类型的评分规则列表
 */

import Tag from 'primevue/tag'

interface RuleItem {
  id?: number
  dimension: string
  description?: string
  weight: number
  is_active: boolean
}

defineProps<{
  rules: RuleItem[]
  emptyText: string
}>()
</script>
