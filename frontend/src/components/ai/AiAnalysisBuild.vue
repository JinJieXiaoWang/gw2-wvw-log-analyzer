<template>
  <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-blue-500/30 transition-all duration-300">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-white flex items-center gap-2">
        <div class="p-2 bg-gradient-to-br from-blue-500/30 to-indigo-500/30 rounded-lg">
          <SvgIcon
            icon="code"
            :size="18"
            class="text-blue-400"
          />
        </div>
        {{ TOOLS_SECTION_ANALYZE_BUILD }}
      </h3>
      <button
        v-if="recentBuilds?.length"
        class="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors flex items-center gap-1"
        @click="autoSelectRecent"
      >
        <SvgIcon
          icon="zap"
          :size="12"
        />
        {{ TOOLS_BTN_AUTO_SELECT }}
      </button>
    </div>

    <div class="relative">
      <label class="block text-xs text-gray-400 mb-2">{{ TOOLS_LABEL_BUILD_CODE_ID }}</label>
      <div class="relative">
        <input
          :value="modelValue"
          type="text"
          class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-blue-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 transition-colors font-mono"
          :placeholder="TOOLS_PLACEHOLDER_BUILD_INPUT"
          :disabled="disabled"
          @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        >
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <SvgIcon
            icon="code"
            :size="16"
            class="text-gray-500"
          />
        </div>
      </div>

      <div
        v-if="recentBuilds?.length"
        class="mt-2 flex flex-wrap gap-2"
      >
        <button
          v-for="build in recentBuilds.slice(0, 3)"
          :key="build.id"
          class="text-xs px-2 py-1.5 rounded-lg transition-colors flex items-center gap-1"
          :class="modelValue === build.id ? 'bg-blue-500/30 text-blue-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
          @click="selectBuild(build)"
        >
          <div
            class="w-2 h-2 rounded-full"
            :class="getProfessionColor(build.profession)"
          />
          {{ build.name }}
        </button>
      </div>
    </div>

    <button
      class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20 font-medium"
      :disabled="disabled || !modelValue"
      @click="$emit('analyze')"
    >
      <svg
        v-if="disabled"
        class="animate-spin h-5 w-5 text-white"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
          fill="none"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <SvgIcon
        v-else
        icon="play"
        :size="18"
        class="text-white"
      />
      <span class="text-white">{{ disabled ? TOOLS_BTN_ANALYZING : TOOLS_BTN_START_ANALYZE }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import {
  TOOLS_SECTION_ANALYZE_BUILD,
  TOOLS_BTN_AUTO_SELECT,
  TOOLS_BTN_START_ANALYZE,
  TOOLS_BTN_ANALYZING,
  TOOLS_LABEL_BUILD_CODE_ID,
  TOOLS_PLACEHOLDER_BUILD_INPUT,
} from '@/constants/aiAnalysis'

interface BuildOption {
  id: string
  name: string
  profession: string
}

const props = defineProps<{
  modelValue: string
  recentBuilds?: BuildOption[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  analyze: []
}>()

const getProfessionColor = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'bg-red-400', 'Guardian': 'bg-blue-400', 'Ranger': 'bg-green-400',
    'Thief': 'bg-yellow-400', 'Engineer': 'bg-orange-400', 'Elementalist': 'bg-purple-400',
    'Necromancer': 'bg-gray-400', 'Mesmer': 'bg-pink-400', 'Revenant': 'bg-cyan-400',
    'Mechanist': 'bg-teal-400', 'Vindicator': 'bg-amber-400', 'Harbinger': 'bg-indigo-400',
  }
  return colors[professionKey] || 'bg-gray-400'
}

const autoSelectRecent = () => {
  if (props.recentBuilds?.length) {
    emit('update:modelValue', props.recentBuilds[0].id)
  }
}

const selectBuild = (build: BuildOption) => {
  emit('update:modelValue', build.id)
}
</script>
