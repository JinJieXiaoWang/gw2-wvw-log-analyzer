<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
    <div
      v-for="role in data.roles"
      :key="role.type"
      class="relative rounded-xl p-5 cursor-pointer transition-all duration-300 overflow-hidden border"
      :class="data.activeRole === role.type ? 'border-primary-500 shadow-lg shadow-primary-500/20 -translate-y-1' : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 hover:-translate-y-1 hover:shadow-xl'"
      :style="{ '--accent': data.roleColors[role.type] }"
      @click="emit('switch-role', role.type)"
    >
      <div class="absolute top-0 left-0 right-0 h-[3px] transition-opacity duration-300" :class="data.activeRole === role.type ? 'opacity-100' : 'opacity-0'" :style="{ background: data.roleColors[role.type] }" />
      <div class="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] rounded-full pointer-events-none transition-opacity duration-500" :class="data.activeRole === role.type ? 'opacity-[0.05]' : 'opacity-0'" :style="{ background: `radial-gradient(circle, ${data.roleColors[role.type]} 0%, transparent 70%)` }" />
      <div class="relative z-10 flex flex-col gap-3">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-lg flex items-center justify-center text-2xl text-white shrink-0 shadow-lg" :style="{ background: `linear-gradient(135deg, ${data.roleColors[role.type]}, ${data.roleGradients[role.type]})`, boxShadow: `0 8px 24px -8px ${data.roleColors[role.type]}` }">
            <i :class="role.icon" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-semibold text-color">{{ role.label }}</h3>
            <p class="text-sm text-color-secondary">{{ role.description }}</p>
          </div>
        </div>
        <div class="flex items-center justify-between mt-1">
          <span class="text-xs text-color-secondary px-2 py-1 rounded-full bg-surface-100 dark:bg-surface-800">{{ (data.currentRules[role.type]?.length || 0) }} ά度</span>
          <BaseTag v-if="data.hasUnsavedChanges(role.type)" value="待保瀛? severity="warning" class="text-xs" />
        </div>
      </div>
      <div class="absolute bottom-0 left-0 right-0 h-1 bg-surface-200 dark:bg-surface-700">
        <div class="h-full transition-all duration-300" :style="{ width: `${data.getWeightProgress(role.type)}%`, background: data.roleColors[role.type] }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseTag from '@/components/common/ui/BaseTag.vue'
import type { ScoringRule } from '@/services/scoring/scoringRulesService'

interface RoleData {
  type: string
  label: string
  description: string
  icon: string
  color: string
}

interface RoleCardsData {
  roles: RoleData[]
  activeRole: string
  currentRules: Record<string, ScoringRule[]>
  roleColors: Record<string, string>
  roleGradients: Record<string, string>
  hasUnsavedChanges: (role: string) => boolean
  getWeightProgress: (role: string) => number
}

const props = defineProps<{ data: RoleCardsData }>()
const emit = defineEmits<{ 'switch-role': [role: string] }>()
</script>
