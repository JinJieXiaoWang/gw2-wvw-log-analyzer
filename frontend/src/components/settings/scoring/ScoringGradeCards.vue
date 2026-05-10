<template>
  <div>
    <h4 class="flex items-center gap-2 text-lg font-semibold text-color mb-4"><i class="pi pi-info-circle text-primary-500" />评分等级说明</h4>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
      <div v-for="g in GRADE_LIST" :key="g.grade" class="relative bg-surface-0 dark:bg-surface-900 border rounded-xl p-4 text-center overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl" :style="{ borderColor: g.color + '40' }">
        <div class="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] rounded-full pointer-events-none opacity-[0.08]" :style="{ background: `radial-gradient(circle, ${g.color} 0%, transparent 70%)` }" />
        <div class="text-4xl font-extrabold mb-2" :style="{ background: `linear-gradient(135deg, ${g.color}, ${g.color2})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }">{{ g.grade }}</div>
        <div class="flex flex-col gap-1">
          <span class="text-sm font-semibold text-color">{{ g.range }}</span>
          <span class="text-xs text-color-secondary">{{ g.desc }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { GRADE_LIST } from '@/utils/combat/scoringConstants'
</script>
