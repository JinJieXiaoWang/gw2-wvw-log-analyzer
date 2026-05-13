<template>
  <div
    class="card-exotic animate-slide-in-up"
    style="animation-delay: 0.3s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rarity-exotic/30 to-primary/30 flex items-center justify-center">
        <i class="pi pi-tasks text-rarity-exotic" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          天赋加点
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          核心天赋配置
        </p>
      </div>
    </div>
    <div class="space-y-4">
      <div
        v-for="traitLine in parsedBuild.traits"
        :key="traitLine.id"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-neutral-text">{{ traitLine.name }}</span>
          <div class="flex gap-1">
            <span
              v-for="i in 3"
              :key="i"
              class="w-6 h-2 rounded-full"
              :class="i <= traitLine.selected ? 'bg-gradient-to-r from-primary to-secondary' : 'bg-neutral-border'"
            />
          </div>
        </div>
        <p class="text-xs text-neutral-text-secondary">
          {{ traitLine.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 天赋加点组件
 * 功能：显示Build的天赋配置
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

defineProps<{
  parsedBuild: {
    traits: Array<{
      id: number | string
      name: string
      description: string
      selected: number
    }>
  }
}>()
</script>