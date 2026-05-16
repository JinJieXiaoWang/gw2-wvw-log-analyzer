<template>
  <div class="squad-tab">
    <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">{{ LABEL_SELECT_FIGHT }}</label>
        <select :value="selectedFightId" @change="$emit('update:selectedFightId', ($event.target as HTMLSelectElement).value)" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
          <option value="">{{ PLACEHOLDER_SELECT_FIGHT }}</option>
          <option v-for="f in recentFights" :key="f.id" :value="f.id">{{ f.name }}</option>
        </select>
      </div>
      <button @click="$emit('run')" :disabled="!selectedFightId || loadingSquadSynergy" class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-400 hover:to-indigo-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
        {{ loadingSquadSynergy ? BTN_ANALYZING : BTN_SQUAD_SYNERGY }}
      </button>
    </div>
    <div v-if="squadSynergyData" class="space-y-4">
      <div v-for="sq in squadSynergyData.squads || []" :key="sq.group_id" class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-white">{{ LABEL_SQUAD_PREFIX }} {{ sq.group_id }}</h3>
          <span class="text-lg font-bold" :class="getScoreClass(sq.synergy_score)">{{ sq.synergy_score }}</span>
        </div>
        <div class="text-sm text-neutral-text-secondary mb-2">{{ sq.member_count }}{{ LABEL_SQUAD_MEMBERS_SUFFIX }} {{ formatRoleDistribution(sq.role_distribution) }}</div>
        <div v-if="sq.suggestions?.length" class="space-y-1.5 mt-3">
          <div v-for="(s, i) in sq.suggestions" :key="i" class="text-xs p-2 rounded" :class="s.priority === 'high' ? 'bg-error/10 text-error' : 'bg-warning/10 text-warning'">
            {{ s.message }}
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12 text-neutral-text-tertiary">{{ TIP_SELECT_FIGHT_AND_ANALYZE }}</div>
  </div>
</template>

<script setup lang="ts">
import type { SquadSynergyData } from '@/composables/useAiAnalysis'
import {
  BTN_ANALYZING,
  BTN_SQUAD_SYNERGY,
  LABEL_SELECT_FIGHT,
  PLACEHOLDER_SELECT_FIGHT,
  LABEL_SQUAD_PREFIX,
  LABEL_SQUAD_MEMBERS_SUFFIX,
  TIP_SELECT_FIGHT_AND_ANALYZE,
} from '@/constants/aiAnalysis'

interface FightOption {
  id: string
  name: string
  date: string
}

interface Props {
  recentFights: FightOption[]
  selectedFightId: string
  squadSynergyData: SquadSynergyData | null
  loadingSquadSynergy: boolean
}

defineProps<Props>()

defineEmits<{
  'update:selectedFightId': [value: string]
  'run': []
}>()

const SCORE_THRESHOLDS = {
  excellent: 80,
  good: 60,
} as const

const getScoreClass = (score: number) => score >= SCORE_THRESHOLDS.excellent ? 'text-status-success' : score >= SCORE_THRESHOLDS.good ? 'text-warning' : 'text-error'

const formatRoleDistribution = (distribution: Record<string, number> | undefined): string => {
  if (!distribution) return ''
  return Object.entries(distribution).map(([k, v]) => `${k} ${v}`).join(', ')
}
</script>

<script lang="ts">
export default { name: 'AiAnalysisSquadTab' }
</script>
