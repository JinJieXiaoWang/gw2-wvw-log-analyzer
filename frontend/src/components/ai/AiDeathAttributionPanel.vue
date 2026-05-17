<template>
  <div class="space-y-6">
    <!-- 头部 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl">
          <SvgIcon
            icon="shield-alert"
            :size="24"
            class="text-red-400"
          />
        </div>
        <div>
          <h2 class="text-xl font-bold text-white">
            死亡归因与生存分析
          </h2>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            死亡原因分类 · 生存评分 · 改进方案
          </p>
        </div>
      </div>
      <div
        v-if="data?.survival_score !== undefined"
        class="flex items-center gap-2"
      >
        <span class="text-sm text-neutral-text-secondary">生存评分</span>
        <span
          class="text-2xl font-bold"
          :class="getScoreClass(data.survival_score)"
        >{{ data.survival_score }}</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="space-y-4"
    >
      <div class="h-32 bg-neutral-card-active/50 rounded-xl animate-pulse" />
      <div class="h-48 bg-neutral-card-active/50 rounded-xl animate-pulse" />
    </div>

    <div
      v-else-if="error"
      class="p-6 bg-error/10 border border-error/20 rounded-xl text-center"
    >
      <SvgIcon
        icon="alert-circle"
        :size="32"
        class="text-error mx-auto mb-2"
      />
      <p class="text-error">
        {{ error }}
      </p>
    </div>

    <div
      v-else-if="data"
      class="space-y-6"
    >
      <!-- 死亡统计卡片 -->
      <div
        v-if="data.death_stats"
        class="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border text-center">
          <div class="text-2xl font-bold text-white">
            {{ data.death_stats.total_fights }}
          </div>
          <div class="text-xs text-neutral-text-secondary mt-1">
            总战斗
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border text-center">
          <div
            class="text-2xl font-bold"
            :class="data.death_stats.death_rate > 50 ? 'text-error' : 'text-white'"
          >
            {{ data.death_stats.death_rate }}%
          </div>
          <div class="text-xs text-neutral-text-secondary mt-1">
            死亡率
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border text-center">
          <div class="text-2xl font-bold text-white">
            {{ data.death_stats.total_deaths }}
          </div>
          <div class="text-xs text-neutral-text-secondary mt-1">
            总死亡
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border text-center">
          <div class="text-2xl font-bold text-white">
            {{ data.death_stats.avg_dodge_per_fight }}
          </div>
          <div class="text-xs text-neutral-text-secondary mt-1">
            场均翻滚
          </div>
        </div>
      </div>

      <!-- 归因分布 -->
      <div
        v-if="data.attributions?.length"
        class="bg-neutral-card-active/40 rounded-xl p-4 border border-neutral-border"
      >
        <h3 class="text-sm font-semibold text-white mb-3">
          死亡归因分析
        </h3>
        <div class="space-y-3">
          <div
            v-for="(attr, i) in data.attributions"
            :key="i"
            class="p-3 bg-black/20 rounded-lg"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span
                  class="text-xs px-2 py-0.5 rounded font-medium"
                  :class="attributionBadgeClass(attr.primary_reason)"
                >
                  {{ attr.primary_label }}
                </span>
                <span class="text-xs text-neutral-text-secondary">{{ formatDate(attr.start_time) }}</span>
              </div>
              <span class="text-xs text-neutral-text-secondary">置信度: {{ Math.round(attr.confidence * 100) }}%</span>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="reason in attr.all_reasons"
                :key="reason"
                class="text-xs px-1.5 py-0.5 bg-neutral-card-active rounded text-neutral-text-tertiary"
              >
                {{ reason }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 生存建议 -->
      <div
        v-if="data.suggestions?.length"
        class="bg-neutral-card-active/40 rounded-xl p-4 border border-neutral-border"
      >
        <h3 class="text-sm font-semibold text-white mb-3">
          生存改进方案
        </h3>
        <div class="space-y-2">
          <div
            v-for="(s, i) in data.suggestions"
            :key="i"
            class="p-3 rounded-lg"
            :class="suggestionBg(s.priority)"
          >
            <div class="flex items-start gap-3">
              <div
                class="mt-0.5 w-1.5 h-1.5 rounded-full shrink-0"
                :class="suggestionDot(s.priority)"
              />
              <div>
                <div class="text-sm text-white font-medium">
                  {{ s.message }}
                </div>
                <div
                  v-if="s.actions?.length"
                  class="mt-1.5 flex flex-wrap gap-2"
                >
                  <span
                    v-for="(action, j) in s.actions"
                    :key="j"
                    class="text-xs px-2 py-0.5 bg-black/20 rounded text-neutral-text-secondary"
                  >{{ action }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无死亡提示 -->
      <div
        v-else-if="!data.attributions?.length && data.death_stats?.total_deaths === 0"
        class="p-6 bg-status-success/10 border border-status-success/20 rounded-xl text-center"
      >
        <SvgIcon
          icon="shield-check"
          :size="32"
          class="text-status-success mx-auto mb-2"
        />
        <p class="text-status-success font-medium">
          近期无死亡记录，生存能力出色！
        </p>
      </div>

      <!-- LLM深度洞察 -->
      <div
        v-if="data.llm_analysis"
        class="bg-gradient-to-r from-red-500/10 to-orange-500/10 rounded-xl p-4 border border-red-500/20"
      >
        <h3 class="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <SvgIcon
            icon="sparkles"
            :size="16"
            class="text-red-400"
          />
          AI 深度洞察
        </h3>
        <p class="text-sm text-neutral-text-secondary leading-relaxed">
          {{ data.llm_analysis.narrative }}
        </p>
      </div>
    </div>

    <div
      v-else
      class="text-center py-12"
    >
      <p class="text-neutral-text-tertiary">
        选择玩家并点击分析生成死亡归因报告
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import type { DeathAttributionData } from '@/composables/useAiAnalysis'

defineProps<{
  data: DeathAttributionData | null
  loading: boolean
  error?: string
}>()

const getScoreClass = (score: number) => score >= 80 ? 'text-status-success' : score >= 60 ? 'text-warning' : 'text-error'

const attributionBadgeClass = (reason: string) => {
  const map: Record<string, string> = {
    focused_fire: 'bg-red-500/20 text-red-400',
    positioning_error: 'bg-orange-500/20 text-orange-400',
    buff_gap: 'bg-yellow-500/20 text-yellow-400',
    cooldown_mismatch: 'bg-blue-500/20 text-blue-400',
    healing_deficit: 'bg-purple-500/20 text-purple-400',
    cc_chain: 'bg-pink-500/20 text-pink-400',
  }
  return map[reason] || 'bg-neutral-card-active text-neutral-text-secondary'
}

const suggestionBg = (p: string) => p === 'high' ? 'bg-error/10 border border-error/20' : p === 'medium' ? 'bg-warning/10 border border-warning/20' : 'bg-neutral-card-active/50'
const suggestionDot = (p: string) => p === 'high' ? 'bg-error' : p === 'medium' ? 'bg-warning' : 'bg-neutral-text-secondary'

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
