<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.4s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rarity-rare/30 to-rarity-rare/50 flex items-center justify-center">
        <i class="pi pi-chart-line text-rarity-rare" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          属性总览
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          核心属性统计
        </p>
      </div>
    </div>
    <div class="space-y-3">
      <div
        v-for="stat in parsedBuild.stats"
        :key="stat.name"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-neutral-text font-medium">{{ stat.name }}</span>
          <span class="text-sm font-bold game-number-legendary">{{ stat.value }}</span>
        </div>
        <div class="game-progress">
          <div
            class="game-progress-primary"
            :style="{ width: (stat.value / 3000 * 100) + '%' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 属性总览组件
 * 功能：显示Build的核心属性统计
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

defineProps<{
  parsedBuild: {
    stats: Array<{
      name: string
      value: number
    }>
  }
}>()
</script>