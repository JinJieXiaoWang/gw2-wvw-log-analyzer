<template>
  <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 flex items-center justify-center border border-primary/20">
      <i class="pi pi-chart-line text-primary text-xl" />
    </div>
    <div>
      <h3 class="text-lg font-bold text-neutral-text">
        评分规则配置
      </h3>
      <p class="text-sm text-neutral-text-secondary mt-0.5">
        Ϊ不同角色类型定制评分维度和权重
      </p>
    </div>
  </div>

  <div class="grid grid-cols-3 gap-4 mb-8">
    <button
      v-for="role in ROLE_TYPES"
      :key="role.type"
      class="relative p-4 rounded-xl border-2 transition-all duration-200 text-left"
      :class="activeRole === role.type ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10' : 'border-neutral-border bg-neutral-bg-secondary hover:border-neutral-border-dark'"
      @click="$emit('switch-role', role.type)"
    >
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-base"
          :class="roleIconBgClass(role.type)"
        >
          <i :class="role.icon" />
        </div>
        <div>
          <h4 class="font-semibold text-neutral-text text-sm">
            {{ role.label }}
          </h4>
          <p class="text-xs text-neutral-text-secondary">
            {{ role.description }}
          </p>
        </div>
      </div>
      <div
        v-if="hasUnsavedChanges(role.type)"
        class="absolute top-2 right-2"
      >
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-warning/20 text-warning">已修改</span>
      </div>
    </button>
  </div>

  <div
    class="mb-6 p-4 rounded-xl"
    :class="weightStatus.bg"
  >
    <div class="flex items-center justify-between mb-2">
      <span
        class="text-sm font-medium"
        :class="weightStatus.text"
      >Ȩ重总和: {{ totalWeight.toFixed(2) }} / 1.00</span>
      <span
        v-if="Math.abs(totalWeight - 1.0) > 0.01"
        class="text-xs text-warning flex items-center gap-1"
      ><i class="pi pi-exclamation-circle" />建议调整Ϊ 1.0</span>
    </div>
    <div class="h-2 rounded-full bg-neutral-bg-secondary overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="weightStatus.bar"
        :style="{ width: `${Math.min(totalWeight * 100, 100)}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ROLE_TYPES } from '@/composables/settings/useScoringRulesSettings'

defineProps<{
  activeRole: string
  totalWeight: number
  weightStatus: { bg: string; text: string; bar: string }
  roleIconBgClass: (role: string) => string
  hasUnsavedChanges: (role: string) => boolean
}>()

defineEmits<{
  'switch-role': [role: string]
}>()
</script>
