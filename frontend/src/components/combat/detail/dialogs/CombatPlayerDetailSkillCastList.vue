<template>
  <div class="space-y-4">
    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="p-3 bg-neutral-card-active/40 rounded-lg border border-neutral-border text-center">
        <div class="text-lg font-bold text-primary">
          {{ sortedSkillCasts.length }}
        </div>
        <div class="text-xs text-neutral-text-secondary mt-0.5">
          技能种类
        </div>
      </div>
      <div class="p-3 bg-neutral-card-active/40 rounded-lg border border-neutral-border text-center">
        <div class="text-lg font-bold text-primary">
          {{ autoAttackRatio }}%
        </div>
        <div class="text-xs text-neutral-text-secondary mt-0.5">
          自动攻击占比
        </div>
      </div>
      <div class="p-3 bg-neutral-card-active/40 rounded-lg border border-neutral-border text-center">
        <div class="text-lg font-bold text-primary">
          {{ weaponSwapCount }}
        </div>
        <div class="text-xs text-neutral-text-secondary mt-0.5">
          武器切换
        </div>
      </div>
      <div
        v-if="weaponSwapIntervals"
        class="p-3 bg-neutral-card-active/40 rounded-lg border border-neutral-border text-center"
      >
        <div class="text-lg font-bold text-primary">
          {{ weaponSwapIntervals.average }}s
        </div>
        <div class="text-xs text-neutral-text-secondary mt-0.5">
          平均切换间隔
        </div>
      </div>
    </div>

    <!-- Top 10 技能 -->
    <div>
      <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
        <i class="pi pi-sort-amount-down text-primary" /> Top 10 技能释放
      </h4>
      <div class="space-y-1">
        <div
          v-for="s in top10SkillCasts"
          :key="s.skillId"
          class="flex items-center gap-2 p-2 rounded hover:bg-neutral-bg/50"
        >
          <img
            v-if="s.icon"
            :src="s.icon"
            class="w-6 h-6 rounded"
          >
          <div
            v-else
            class="w-6 h-6 rounded bg-neutral-bg flex items-center justify-center text-xs text-neutral-text-secondary"
          >
            {{ SKILLS_CONFIG.UNKNOWN_ICON_PLACEHOLDER }}
          </div>
          <span class="text-sm text-neutral-text flex-1 truncate">{{ s.name }}</span>
          <BaseTag
            :value="s.count"
            severity="primary"
          />
        </div>
        <div
          v-if="sortedSkillCasts.length > 10"
          class="text-center py-2 text-xs text-neutral-text-tertiary"
        >
          还有 {{ sortedSkillCasts.length - 10 }} 个技能未显示
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseTag from '@/components/common/ui/display/BaseTag.vue'

const SKILLS_CONFIG = {
  UNKNOWN_ICON_PLACEHOLDER: '?',
} as const

const props = defineProps<{
  sortedSkillCasts: any[]
  top10SkillCasts: any[]
  autoAttackRatio: number
  weaponSwapCount: number
  weaponSwapIntervals: { intervals: number[]; average: number; min: number; max: number } | null
}>()
</script>
