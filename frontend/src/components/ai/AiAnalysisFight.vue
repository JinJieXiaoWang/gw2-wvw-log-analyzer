<template>
  <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-red-500/30 transition-all duration-300">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-white flex items-center gap-2">
        <div class="p-2 bg-gradient-to-br from-red-500/30 to-orange-500/30 rounded-lg">
          <SvgIcon icon="swords" :size="18" class="text-red-400" />
        </div>
        {{ TOOLS_SECTION_ANALYZE_FIGHT }}
      </h3>
      <button
        v-if="recentFights?.length"
        @click="autoSelectRecent"
        class="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors flex items-center gap-1"
      >
        <SvgIcon icon="zap" :size="12" />
        {{ TOOLS_BTN_AUTO_SELECT_LATEST }}
      </button>
    </div>

    <div class="relative">
      <label class="block text-xs text-gray-400 mb-2">{{ TOOLS_LABEL_SELECT_FIGHT }}</label>
      <div class="relative">
        <select
          :value="modelValue"
          @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
          class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-red-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white appearance-none cursor-pointer transition-colors"
        >
          <option value="">{{ TOOLS_PLACEHOLDER_SELECT_FIGHT }}</option>
          <option v-for="fight in recentFights" :key="fight.id" :value="fight.id">
            {{ fight.name }}
            <span class="text-gray-500 ml-2">({{ formatDate(fight.date) }})</span>
          </option>
        </select>
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <SvgIcon icon="chevron-down" :size="16" class="text-gray-400" />
        </div>
      </div>

      <div v-if="recentFights?.length" class="mt-2 flex flex-wrap gap-2">
        <button
          v-for="fight in recentFights.slice(0, 3)"
          :key="fight.id"
          @click="$emit('update:modelValue', fight.id)"
          class="text-xs px-2 py-1 rounded-lg transition-colors flex items-center gap-1"
          :class="modelValue === fight.id ? 'bg-red-500/30 text-red-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
        >
          <SvgIcon icon="clock" :size="12" />
          {{ fight.name.substring(0, 10) }}...
        </button>
      </div>
    </div>

    <button
      @click="$emit('analyze')"
      class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20 font-medium"
      :disabled="disabled || !modelValue"
    >
      <svg v-if="disabled" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
      <SvgIcon v-else icon="play" :size="18" class="text-white" />
      <span class="text-white">{{ disabled ? TOOLS_BTN_ANALYZING : TOOLS_BTN_START_ANALYZE }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import {
  TOOLS_SECTION_ANALYZE_FIGHT,
  TOOLS_BTN_AUTO_SELECT_LATEST,
  TOOLS_BTN_START_ANALYZE,
  TOOLS_BTN_ANALYZING,
  TOOLS_LABEL_SELECT_FIGHT,
  TOOLS_PLACEHOLDER_SELECT_FIGHT,
} from '@/constants/aiAnalysis'

interface FightOption {
  id: string
  name: string
  date: string
}

const props = defineProps<{
  modelValue: string
  recentFights?: FightOption[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  analyze: []
}>()

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const autoSelectRecent = () => {
  if (props.recentFights?.length) {
    emit('update:modelValue', props.recentFights[0].id)
  }
}
</script>
