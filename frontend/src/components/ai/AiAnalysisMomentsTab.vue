<template>
  <div class="moments-tab">
    <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">{{ LABEL_SELECT_FIGHT }}</label>
        <select :value="selectedFightId" @change="$emit('update:selectedFightId', ($event.target as HTMLSelectElement).value)" class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border">
          <option value="">{{ PLACEHOLDER_SELECT_FIGHT }}</option>
          <option v-for="f in recentFights" :key="f.id" :value="f.id">{{ f.name }}</option>
        </select>
      </div>
      <button @click="$emit('run')" :disabled="!selectedFightId || loadingCriticalMoments" class="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-white rounded-lg font-medium transition-all disabled:opacity-50">
        {{ loadingCriticalMoments ? BTN_ANALYZING : BTN_CRITICAL_MOMENTS }}
      </button>
    </div>
    <div v-if="criticalMomentsData?.moments?.length" class="space-y-4">
      <div v-for="(m, i) in criticalMomentsData.moments" :key="i" class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
        <div class="flex items-center gap-3 mb-2">
          <span class="text-xs px-2 py-0.5 rounded font-medium" :class="m.importance === 'critical' ? 'bg-error/20 text-error' : 'bg-warning/20 text-warning'">{{ m.importance }}</span>
          <span class="font-semibold text-white">{{ m.label }}</span>
        </div>
        <p class="text-sm text-neutral-text-secondary mb-3">{{ m.description }}</p>
        <div v-if="m.evaluations?.length" class="space-y-2">
          <div v-for="(evalItem, j) in m.evaluations" :key="j" class="flex items-center justify-between p-2 bg-black/20 rounded-lg">
            <span class="text-sm text-white">{{ evalItem.character_name }} ({{ getProfessionName(evalItem.profession) }})</span>
            <span class="text-xs px-2 py-0.5 rounded" :class="getPerformanceRatingClass(evalItem.performance?.rating)">{{ evalItem.performance?.rating }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-12 text-neutral-text-tertiary">{{ TIP_SELECT_FIGHT_AND_REVIEW }}</div>
  </div>
</template>

<script setup lang="ts">
import {
  BTN_ANALYZING,
  BTN_CRITICAL_MOMENTS,
  LABEL_SELECT_FIGHT,
  PLACEHOLDER_SELECT_FIGHT,
  TIP_SELECT_FIGHT_AND_REVIEW,
} from '@/constants/aiAnalysis'
import { getProfessionName } from '@/services/professionService'

interface FightOption {
  id: string
  name: string
  date: string
}

interface Props {
  recentFights: FightOption[]
  selectedFightId: string
  criticalMomentsData: any
  loadingCriticalMoments: boolean
}

defineProps<Props>()

defineEmits<{
  'update:selectedFightId': [value: string]
  'run': []
}>()

const getPerformanceRatingClass = (rating: string | undefined) => {
  if (rating === 'excellent') return 'bg-status-success/20 text-status-success'
  if (rating === 'good') return 'bg-warning/20 text-warning'
  return 'bg-error/20 text-error'
}
</script>

<script lang="ts">
export default { name: 'AiAnalysisMomentsTab' }
</script>
