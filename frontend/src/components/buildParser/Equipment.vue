<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rarity-legendary/30 to-rarity-exotic/30 flex items-center justify-center">
        <i class="pi pi-shield text-rarity-legendary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          装备配置
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          装备和符文配置
        </p>
      </div>
    </div>
    <div class="space-y-3">
      <div
        v-for="item in parsedBuild.equipment"
        :key="item.id"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center">
              <i class="pi pi-circle text-primary" />
            </div>
            <div>
              <p class="text-sm font-medium text-neutral-text">
                {{ item.name }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ item.type }}
              </p>
            </div>
          </div>
          <span :class="getRarityBadgeClass(item.rarity)">
            {{ item.rarity }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 装备配置组件
 * 功能：显示Build的装备和符文配置
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

defineProps<{
  parsedBuild: {
    equipment: Array<{
      id: number | string
      name: string
      type: string
      rarity: string
    }>
  }
}>()

// 方法
const getRarityBadgeClass = (rarity: string) => {
  const classes: Record<string, string> = {
    '传说': 'game-badge game-badge-legendary',
    '史诗': 'game-badge game-badge-error',
    '稀有': 'game-badge game-badge-rare',
    '优秀': 'game-badge game-badge-success',
    '普通': 'game-badge game-badge-secondary'
  }
  return classes[rarity] || 'game-badge game-badge-secondary'
}
</script>