<template>
  <div class="build-tab">
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
        :disabled="!selectedPlayerAccount || loadingBuildExecution"
        class="px-6 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white rounded-lg font-medium transition-all disabled:opacity-50"
        @click="$emit('run')"
      >
        {{ loadingBuildExecution ? BTN_VERIFYING : BTN_BUILD_VERIFY }}
      </button>
    </div>
    <div v-if="buildExecutionData">
      <!-- 评分与分类汇总 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            {{ LABEL_BUILD_TYPE }}
          </div>
          <div class="text-lg font-semibold text-white">
            {{ buildExecutionData.build_type }}
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            {{ LABEL_EXECUTION_SCORE }}
          </div>
          <div
            class="text-lg font-semibold"
            :class="getScoreClass(ruleResult.overallScore)"
          >
            {{ ruleResult.overallScore }}
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            规则通过
          </div>
          <div class="text-lg font-semibold text-status-success">
            {{ totalPassed }} / {{ ruleResult.rules.length }}
          </div>
        </div>
      </div>

      <!-- 分类汇总标签 -->
      <div
        v-if="ruleResult.rules.length"
        class="flex flex-wrap gap-2 mb-4"
      >
        <div
          v-for="(summary, cat) in ruleResult.categorySummary"
          :key="cat"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-card-active/30 rounded-lg text-xs"
        >
          <span class="text-neutral-text-secondary">{{ CATEGORY_LABELS[cat as RuleCategory] }}</span>
          <span
            v-if="summary.pass"
            class="text-status-success"
          >{{ summary.pass }}✓</span>
          <span
            v-if="summary.fail"
            class="text-error"
          >{{ summary.fail }}✗</span>
          <span
            v-if="summary.warn"
            class="text-warning"
          >{{ summary.warn }}!</span>
        </div>
      </div>

      <!-- 规则检查列表 -->
      <div
        v-if="ruleResult.rules.length"
        class="space-y-2"
      >
        <div
          v-for="rule in ruleResult.rules"
          :key="rule.id"
          class="flex items-start justify-between p-3 bg-neutral-card-active/30 rounded-lg"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <span class="text-xs px-1.5 py-0.5 rounded bg-black/20 text-neutral-text-tertiary">{{ CATEGORY_LABELS[rule.category] }}</span>
              <span class="text-sm text-white font-medium">{{ rule.label }}</span>
            </div>
            <p class="text-xs text-neutral-text-secondary">
              {{ rule.description }}
            </p>
            <p
              v-if="rule.actual"
              class="text-xs text-neutral-text-tertiary mt-0.5"
            >
              {{ LABEL_ACTUAL_PREFIX }} {{ rule.actual }}
            </p>
          </div>
          <span
            class="text-xs px-2 py-0.5 rounded font-medium shrink-0 ml-2"
            :class="getRuleStatusClass(rule.status)"
          >{{ rule.status.toUpperCase() }}</span>
        </div>
      </div>
    </div>
    <div
      v-else
      class="text-center py-12 text-neutral-text-tertiary"
    >
      {{ TIP_SELECT_PLAYER_AND_VERIFY }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BuildExecutionData } from '@/composables/useAiAnalysis'
import { evaluateBuildRules, CATEGORY_LABELS } from '@/composables/ai/useBuildRules'
import type { RuleCategory } from '@/composables/ai/useBuildRules'
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
  buildExecutionData: BuildExecutionData | null
  loadingBuildExecution: boolean
}

const props = defineProps<Props>()

defineEmits<{
  'update:selectedPlayerAccount': [value: string]
  'run': []
}>()

const ruleResult = computed(() => evaluateBuildRules(props.buildExecutionData))
const totalPassed = computed(() => ruleResult.value.rules.filter(r => r.status === 'pass').length)

const SCORE_THRESHOLDS = {
  excellent: 80,
  good: 60,
} as const

const getScoreClass = (score: number) => score >= SCORE_THRESHOLDS.excellent ? 'text-status-success' : score >= SCORE_THRESHOLDS.good ? 'text-warning' : 'text-error'

const getRuleStatusClass = (status: string) => {
  if (status === 'pass') return 'bg-status-success/20 text-status-success'
  if (status === 'fail') return 'bg-error/20 text-error'
  return 'bg-warning/20 text-warning'
}
</script>

<script lang="ts">
export default { name: 'AiAnalysisBuildVerifyTab' }
</script>
