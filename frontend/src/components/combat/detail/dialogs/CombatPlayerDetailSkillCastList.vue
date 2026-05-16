<template>
  <div>
    <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
      <i class="pi pi-sort-amount-down text-primary" /> {{ LABELS.SKILL_CAST_COUNT }}
    </h4>
    <div :class="[SKILLS_CONFIG.LIST_MAX_HEIGHT_CLASS, 'overflow-auto', 'space-y-1']">
      <div
        v-for="s in sortedSkillCasts"
        :key="s.skillId"
        class="flex items-center gap-3 p-2 rounded hover:bg-neutral-bg/50"
      >
        <img
          v-if="s.icon"
          :src="s.icon"
          class="w-8 h-8 rounded"
        >
        <div
          v-else
          class="w-8 h-8 rounded bg-neutral-bg flex items-center justify-center text-xs text-neutral-text-secondary"
        >
          {{ SKILLS_CONFIG.UNKNOWN_ICON_PLACEHOLDER }}
        </div>
        <span class="text-sm text-neutral-text flex-1 truncate">{{ s.name }}</span>
        <span class="text-sm font-bold text-primary w-10 text-right">{{ s.count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const LABELS = {
  SKILL_CAST_COUNT: '技能释放次数',
} as const

const SKILLS_CONFIG = {
  LIST_MAX_HEIGHT_CLASS: 'max-h-[400px]',
  UNKNOWN_ICON_PLACEHOLDER: '?',
} as const

defineProps<{
  sortedSkillCasts: any[]
}>()
</script>
