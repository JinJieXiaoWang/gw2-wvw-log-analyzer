<template>
  <div class="death-tab">
    <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">{{ LABEL_SELECT_PLAYER }}</label>
        <select
          :value="selectedPlayerAccount"
          class="w-full bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border"
          @change="$emit('update:selectedPlayerAccount', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">
            {{ PLACEHOLDER_SELECT_PLAYER }}
          </option>
          <option
            v-for="p in recentPlayers"
            :key="p.id"
            :value="p.name"
          >
            {{ p.name }} ({{ getProfessionName(p.profession) }})
          </option>
        </select>
      </div>
      <button
        :disabled="!selectedPlayerAccount || loadingDeathAttribution"
        class="px-6 py-2.5 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-400 hover:to-orange-400 text-white rounded-lg font-medium transition-all disabled:opacity-50"
        @click="$emit('run')"
      >
        {{ loadingDeathAttribution ? BTN_ANALYZING : BTN_DEATH_ANALYSIS }}
      </button>
    </div>
    <AiDeathAttributionPanel
      :data="deathAttributionData"
      :loading="loadingDeathAttribution"
    />
  </div>
</template>

<script setup lang="ts">
import AiDeathAttributionPanel from './AiDeathAttributionPanel.vue'
import {
  BTN_ANALYZING,
  BTN_DEATH_ANALYSIS,
  LABEL_SELECT_PLAYER,
  PLACEHOLDER_SELECT_PLAYER,
} from '@/constants/aiAnalysis'
import { getProfessionName } from '@/services/professionService'

import type { DeathAttributionData } from '@/composables/useAiAnalysis'

interface PlayerOption {
  id: string
  name: string
  profession: string
}

interface Props {
  recentPlayers: PlayerOption[]
  selectedPlayerAccount: string
  deathAttributionData: DeathAttributionData | null
  loadingDeathAttribution: boolean
}

defineProps<Props>()

defineEmits<{
  'update:selectedPlayerAccount': [value: string]
  'run': []
}>()
</script>

<script lang="ts">
export default { name: 'AiAnalysisDeathTab' }
</script>
