<template>
  <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-green-500/30 transition-all duration-300">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-white flex items-center gap-2">
        <div class="p-2 bg-gradient-to-br from-green-500/30 to-emerald-500/30 rounded-lg">
          <SvgIcon icon="user" :size="18" class="text-green-400" />
        </div>
        {{ TOOLS_SECTION_ANALYZE_PLAYER }}
      </h3>
      <span class="text-xs text-gray-500">{{ TOOLS_SUPPORT_NAME_OR_ID }}</span>
    </div>

    <div class="relative">
      <label class="block text-xs text-gray-400 mb-2">{{ TOOLS_LABEL_PLAYER_NAME_ID }}</label>
      <div class="relative">
        <input
          :value="modelValue"
          type="text"
          class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-green-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 transition-colors"
          :placeholder="TOOLS_PLACEHOLDER_PLAYER_INPUT"
          :disabled="disabled"
          @input="handleInput"
        />
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <SvgIcon icon="search" :size="16" class="text-gray-500" />
        </div>
      </div>

      <div v-if="memberSuggestions.length && modelValue.length >= 2" class="mt-2 bg-gray-700/80 rounded-lg overflow-hidden border border-gray-600/50">
        <div class="px-3 py-2 border-b border-gray-600/50">
          <span class="text-xs text-gray-400">{{ TOOLS_MATCH_RESULT_PREFIX }} {{ memberSuggestions.length }} {{ TOOLS_MATCH_RESULT_SUFFIX }}</span>
        </div>
        <button
          v-for="member in memberSuggestions"
          :key="member.id"
          @click="selectMember(member)"
          class="w-full px-3 py-2.5 text-left hover:bg-gray-600/50 transition-colors flex items-center gap-3"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="getProfessionBg(member.profession)">
            <SvgIcon icon="user" :size="14" :class="getProfessionText(member.profession)" />
          </div>
          <div class="flex-1">
            <span class="text-sm text-gray-200">{{ member.name }}</span>
            <span class="text-xs text-gray-500 ml-2">{{ getProfessionName(member.profession) }}</span>
          </div>
          <SvgIcon icon="chevron-right" :size="14" class="text-gray-500" />
        </button>
      </div>

      <div v-if="recentPlayers?.length && modelValue.length < 2" class="mt-2 flex flex-wrap gap-2">
        <button
          v-for="player in recentPlayers.slice(0, 4)"
          :key="player.id"
          @click="selectMember(player)"
          class="text-xs px-2 py-1.5 rounded-lg transition-colors flex items-center gap-1"
          :class="modelValue === player.id ? 'bg-green-500/30 text-green-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
        >
          <div class="w-2 h-2 rounded-full" :class="getProfessionColor(player.profession)" />
          {{ player.name.substring(0, 8) }}...
        </button>
      </div>
    </div>

    <button
      @click="$emit('analyze')"
      class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-green-500/20 font-medium"
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
import { ref, watch } from 'vue'
import { getProfessionName } from '@/services/professionService'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import {
  TOOLS_SECTION_ANALYZE_PLAYER,
  TOOLS_BTN_START_ANALYZE,
  TOOLS_BTN_ANALYZING,
  TOOLS_LABEL_PLAYER_NAME_ID,
  TOOLS_PLACEHOLDER_PLAYER_INPUT,
  TOOLS_SUPPORT_NAME_OR_ID,
  TOOLS_MATCH_RESULT_PREFIX,
  TOOLS_MATCH_RESULT_SUFFIX,
} from '@/constants/aiAnalysis'

interface PlayerOption {
  id: string
  name: string
  profession: string
}

const props = defineProps<{
  modelValue: string
  recentPlayers?: PlayerOption[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  analyze: []
}>()

const memberSuggestions = ref<PlayerOption[]>([])

const getProfessionColor = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'bg-red-400', 'Guardian': 'bg-blue-400', 'Ranger': 'bg-green-400',
    'Thief': 'bg-yellow-400', 'Engineer': 'bg-orange-400', 'Elementalist': 'bg-purple-400',
    'Necromancer': 'bg-gray-400', 'Mesmer': 'bg-pink-400', 'Revenant': 'bg-cyan-400',
    'Mechanist': 'bg-teal-400', 'Vindicator': 'bg-amber-400', 'Harbinger': 'bg-indigo-400',
  }
  return colors[professionKey] || 'bg-gray-400'
}

const getProfessionBg = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'bg-red-500/20', 'Guardian': 'bg-blue-500/20', 'Ranger': 'bg-green-500/20',
    'Thief': 'bg-yellow-500/20', 'Engineer': 'bg-orange-500/20', 'Elementalist': 'bg-purple-500/20',
    'Necromancer': 'bg-gray-500/20', 'Mesmer': 'bg-pink-500/20', 'Revenant': 'bg-cyan-500/20',
    'Mechanist': 'bg-teal-500/20', 'Vindicator': 'bg-amber-500/20', 'Harbinger': 'bg-indigo-500/20',
  }
  return colors[professionKey] || 'bg-gray-500/20'
}

const getProfessionText = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'text-red-400', 'Guardian': 'text-blue-400', 'Ranger': 'text-green-400',
    'Thief': 'text-yellow-400', 'Engineer': 'text-orange-400', 'Elementalist': 'text-purple-400',
    'Necromancer': 'text-gray-400', 'Mesmer': 'text-pink-400', 'Revenant': 'text-cyan-400',
    'Mechanist': 'text-teal-400', 'Vindicator': 'text-amber-400', 'Harbinger': 'text-indigo-400',
  }
  return colors[professionKey] || 'text-gray-400'
}

const selectMember = (member: PlayerOption) => {
  emit('update:modelValue', member.id)
  memberSuggestions.value = []
}

const handleInput = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  emit('update:modelValue', value)

  if (!value || value.length < 2) {
    memberSuggestions.value = []
    return
  }

  const query = value.toLowerCase()
  memberSuggestions.value = (props.recentPlayers || []).filter(p =>
    p.name.toLowerCase().includes(query) || p.profession.toLowerCase().includes(query)
  ).slice(0, 5)
}

watch(() => props.recentPlayers, () => {
  if (props.modelValue && props.modelValue.length >= 2) {
    const query = props.modelValue.toLowerCase()
    memberSuggestions.value = (props.recentPlayers || []).filter(p =>
      p.name.toLowerCase().includes(query) || p.profession.toLowerCase().includes(query)
    ).slice(0, 5)
  }
})
</script>
