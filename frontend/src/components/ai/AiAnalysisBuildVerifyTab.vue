<template>
  <div class="build-tab">
    <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">{{ LABEL_SELECT_PLAYER }}</label>
        <select :value="selectedPlayerAccount" @change="$emit('update:selectedPlayerAccount', ($event.target as HTMLSelectElement).value)" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
          <option value="">{{ PLACEHOLDER_SELECT_PLAYER }}</option>
          <option v-for="p in recentPlayers" :key="p.id" :value="p.name">{{ p.name }} ({{ getProfessionName(p.profession) }})</option>
        </select>
      </div>
      <button @click="$emit('run')" :disabled="!selectedPlayerAccount || loadingBuildExecution" class="px-6 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
        {{ loadingBuildExecution ? BTN_VERIFYING : BTN_BUILD_VERIFY }}
      </button>
    </div>
    <div v-if="buildExecutionData">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">{{ LABEL_BUILD_TYPE }}</div>
          <div class="text-lg font-semibold text-white">{{ buildExecutionData.build_type }}</div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">{{ LABEL_EXECUTION_SCORE }}</div>
          <div class="text-lg font-semibold" :class="getScoreClass(buildExecutionData.execution_score)">{{ buildExecutionData.execution_score }}</div>
        </div>
      </div>
      <div v-if="buildExecutionData.execution_check?.checks?.length" class="space-y-2">
        <div v-for="(check, i) in buildExecutionData.execution_check.checks" :key="i" class="flex items-center justify-between p-3 bg-neutral-card-active/30 rounded-lg">
          <span class="text-sm text-white">{{ check.label }}</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-neutral-text-secondary">{{ LABEL_ACTUAL_PREFIX }} {{ check.actual }}</span>
            <span class="text-xs px-2 py-0.5 rounded font-medium" :class="getCheckStatusClass(check.status)">{{ check.status.toUpperCase() }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12 text-neutral-text-tertiary">{{ TIP_SELECT_PLAYER_AND_VERIFY }}</div>
  </div>
</template>

<script setup lang="ts">
import { CheckStatus } from '@/constants/dictValues'
import {
  BTN_VERIFYING,
  BTN_BUILD_VERIFY,
  LABEL_SELECT_PLAYER,
  PLACEHOLDER_SELECT_PLAYER,
  LABEL_BUILD_TYPE,
  LABEL_EXECUTION_SCORE,
  LABEL_ACTUAL_PREFIX,
  TIP_SELECT_PLAYER_AND_VERIFY,
} from '@/constants/aiAnalysis'
import { getProfessionName } from '@/services/professionService'

interface PlayerOption {
  id: string
  name: string
  profession: string
}

interface Props {
  recentPlayers: PlayerOption[]
  selectedPlayerAccount: string
  buildExecutionData: any
  loadingBuildExecution: boolean
}

defineProps<Props>()

defineEmits<{
  'update:selectedPlayerAccount': [value: string]
  'run': []
}>()

const SCORE_THRESHOLDS = {
  excellent: 80,
  good: 60,
} as const

const getScoreClass = (score: number) => score >= SCORE_THRESHOLDS.excellent ? 'text-status-success' : score >= SCORE_THRESHOLDS.good ? 'text-warning' : 'text-error'

const getCheckStatusClass = (status: string) => {
  if (status === CheckStatus.PASS) return 'bg-status-success/20 text-status-success'
  if (status === CheckStatus.FAIL) return 'bg-error/20 text-error'
  return 'bg-neutral-card-active text-neutral-text-secondary'
}
</script>

<script lang="ts">
export default { name: 'AiAnalysisBuildVerifyTab' }
</script>
