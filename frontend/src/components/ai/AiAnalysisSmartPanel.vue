<template>
  <div>
    <!-- 智能分析模式切换 -->
    <div class="mt-4 p-4 bg-gray-700/30 rounded-xl border border-gray-600/30">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-gray-300 flex items-center gap-2">
          <SvgIcon
            icon="brain"
            :size="16"
            class="text-purple-400"
          />
          {{ TOOLS_SMART_MODE }}
        </h4>
        <button
          class="relative w-12 h-6 rounded-full transition-colors"
          :class="smartMode ? 'bg-purple-600' : 'bg-gray-600'"
          @click="$emit('update:smartMode', !smartMode)"
        >
          <span
            class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform"
            :class="smartMode ? 'translate-x-7' : 'translate-x-1'"
          />
        </button>
      </div>
      <p class="text-xs text-gray-500">
        {{ smartMode ? TOOLS_SMART_MODE_ON : TOOLS_SMART_MODE_OFF }}
      </p>
    </div>

    <!-- 一键分析按钮 -->
    <button
      class="w-full mt-4 flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-500 hover:via-blue-500 hover:to-cyan-500 disabled:from-gray-600 disabled:via-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20 text-white font-semibold hover:scale-[1.02]"
      :disabled="analyzing"
      @click="$emit('analyze-all')"
    >
      <SvgIcon
        icon="zap"
        :size="20"
      />
      <span>{{ analyzing ? TOOLS_BTN_FULL_ANALYZING : TOOLS_BTN_ONE_CLICK_ANALYZE }}</span>
      <SvgIcon
        icon="arrow-right"
        :size="18"
      />
    </button>

    <!-- 提示信息 -->
    <div class="mt-4 p-4 bg-gray-700/30 rounded-xl border border-gray-600/30">
      <div class="flex items-start gap-3">
        <SvgIcon
          icon="info"
          :size="16"
          class="text-blue-400 flex-shrink-0 mt-0.5"
        />
        <div>
          <p class="text-sm text-gray-300">
            {{ TOOLS_AI_ANALYZE_HINT }}
          </p>
          <p class="text-xs text-gray-500 mt-1">
            {{ TOOLS_ANALYZE_RESULT_HINT }}
          </p>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <Transition name="slide-down">
      <div
        v-if="errorMessage"
        class="mt-4 p-4 bg-red-900/40 border border-red-700/50 rounded-xl"
      >
        <div class="flex items-center gap-3">
          <SvgIcon
            icon="alert-circle"
            :size="18"
            class="text-red-400 flex-shrink-0"
          />
          <p class="text-red-300 text-sm">
            {{ errorMessage }}
          </p>
          <button
            class="ml-auto"
            @click="$emit('clear-error')"
          >
            <SvgIcon
              icon="x"
              :size="16"
              class="text-red-400/70 hover:text-red-300"
            />
          </button>
        </div>
      </div>
    </Transition>

    <!-- 智能关联提示 -->
    <Transition name="slide-up">
      <div
        v-if="smartMode && smartSuggestion"
        class="mt-4 p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-700/30 rounded-xl"
      >
        <div class="flex items-start gap-3">
          <div class="p-2 bg-purple-500/20 rounded-lg">
            <SvgIcon
              icon="lightbulb"
              :size="16"
              class="text-purple-400"
            />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-purple-300">
              {{ smartSuggestion.title }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
              {{ smartSuggestion.message }}
            </p>
            <button
              v-if="smartSuggestion.action"
              class="mt-2 text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 transition-colors"
              @click="$emit('execute-smart-action')"
            >
              <SvgIcon
                icon="arrow-right"
                :size="12"
              />
              {{ smartSuggestion.action }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import {
  TOOLS_SMART_MODE,
  TOOLS_SMART_MODE_ON,
  TOOLS_SMART_MODE_OFF,
  TOOLS_BTN_ONE_CLICK_ANALYZE,
  TOOLS_BTN_FULL_ANALYZING,
  TOOLS_AI_ANALYZE_HINT,
  TOOLS_ANALYZE_RESULT_HINT,
} from '@/constants/aiAnalysis'

interface SmartSuggestion {
  title: string
  message: string
  action?: string
  actionType?: 'fight' | 'player' | 'build'
  actionId?: string
}

defineProps<{
  smartMode: boolean
  analyzing: boolean
  errorMessage: string
  smartSuggestion: SmartSuggestion | null
}>()

defineEmits<{
  'update:smartMode': [value: boolean]
  'analyze-all': []
  'clear-error': []
  'execute-smart-action': []
}>()
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
