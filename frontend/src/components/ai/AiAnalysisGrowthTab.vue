<template>
  <div class="growth-tab">
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
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-1.5">{{ LABEL_HISTORY_FIGHTS }}</label>
        <select
          :value="growthFightCount"
          class="bg-neutral-card-active text-white px-4 py-2.5 rounded-lg border border-neutral-border"
          @change="$emit('update:growthFightCount', Number(($event.target as HTMLSelectElement).value))"
        >
          <option
            v-for="opt in HISTORY_OPTIONS"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </select>
      </div>
      <button
        :disabled="!selectedPlayerAccount || loadingPersonalGrowth"
        class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-lg font-medium transition-all disabled:opacity-50"
        @click="$emit('run')"
      >
        {{ loadingPersonalGrowth ? BTN_ANALYZING : BTN_GENERATE }}
      </button>
    </div>
    <AiPersonalGrowthPanel
      :data="personalGrowthData"
      :loading="loadingPersonalGrowth"
    />
  </div>
</template>

<script setup lang="ts">
import AiPersonalGrowthPanel from './AiPersonalGrowthPanel.vue'
import {
  BTN_ANALYZING,
  BTN_GENERATE,
  LABEL_SELECT_PLAYER,
  LABEL_HISTORY_FIGHTS,
  PLACEHOLDER_SELECT_PLAYER,
  HISTORY_OPTIONS,
} from '@/constants/aiAnalysis'
import { getProfessionName } from '@/services/professionService'

import type { PersonalGrowthData } from '@/composables/useAiAnalysis'

interface PlayerOption {
  id: string
  name: string
  profession: string
}

interface Props {
  recentPlayers: PlayerOption[]
  selectedPlayerAccount: string
  growthFightCount: number
  personalGrowthData: PersonalGrowthData | null
  loadingPersonalGrowth: boolean
}

defineProps<Props>()

defineEmits<{
  'update:selectedPlayerAccount': [value: string]
  'update:growthFightCount': [value: number]
  'run': []
}>()
</script>

<script lang="ts">
export default { name: 'AiAnalysisGrowthTab' }
</script>
