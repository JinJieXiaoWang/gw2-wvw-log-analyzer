<script setup lang="ts">
// 模块功能：失误统计组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { Mistake } from '@/models/skillRotation';
import { computed } from 'vue';

interface Props {
  mistakes?: Mistake[] | null
}

const props = withDefaults(defineProps<Props>(), {
  mistakes: null
})

const safeMistakes = computed(() => {
  if (!Array.isArray(props.mistakes)) return []
  return props.mistakes.filter(mistake => mistake !== null && mistake !== undefined)
})
</script>

<template>
  <div class="mistake-stats bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <div class="flex items-center gap-3 mb-4">
      <div
        class="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500/30 to-red-500/30 flex items-center justify-center"
      >
        <i class="pi pi-exclamation-triangle text-yellow-500" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-white">
          失误统计
        </h3>
        <p class="text-xs text-[#909399]">
          需要改进的地方
        </p>
      </div>
    </div>
    <div
      v-if="safeMistakes.length > 0"
      class="space-y-3"
    >
      <div
        v-for="(mistake, index) in safeMistakes"
        :key="index"
        class="p-3 bg-[#2a2a2e] rounded-md"
      >
        <div class="flex items-start justify-between mb-2">
          <div>
            <p class="text-white font-bold text-sm">
              {{
                mistake.type === 'interrupt' ? '技能被打断' :
                mistake.type === 'cancel' ? '技能取消' :
                mistake.type === 'early' ? '过早施放' :
                mistake.type === 'late' ? '过晚施放' : mistake.type
              }}
            </p>
            <p class="text-xs text-[#909399]">
              {{ mistake.description }}
            </p>
          </div>
          <span
            class="text-xs px-2 py-1 rounded"
            :class="
              mistake.impact === 'high' ? 'bg-red-500/20 text-red-400' :
              mistake.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-blue-500/20 text-blue-400'
            "
          >
            {{
              mistake.impact === 'high' ? '高影响' :
              mistake.impact === 'medium' ? '中影响' : '低影响'
            }}
          </span>
        </div>
      </div>
    </div>
    <div
      v-else
      class="text-[#909399] text-center py-8"
    >
      暂无失误数据
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
