<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <div
      class="card-legendary animate-slide-in-up"
      style="animation-delay: 0.2s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总参与人数
          </p>
          <p class="text-3xl font-bold game-number-legendary">
            {{ totalPlayers }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i class="pi pi-arrow-up text-status-success text-sm" />
            <span class="text-status-success text-sm">活跃团队</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-users text-primary text-xl" />
        </div>
      </div>
    </div>
    <div
      class="card-exotic animate-slide-in-up"
      style="animation-delay: 0.3s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总参战时长
          </p>
          <p class="text-3xl font-bold game-number-exotic">
            {{ formatTotalTime(totalTime) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <span class="game-badge game-badge-mvp">持续作战</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-secondary/30 to-status-success/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-clock text-secondary text-xl" />
        </div>
      </div>
    </div>
    <div
      class="card-rare animate-slide-in-up"
      style="animation-delay: 0.4s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            场均伤害
          </p>
          <p class="text-3xl font-bold game-number-rare">
            {{ formatNumber(averageDamage) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i class="pi pi-chart-line text-status-success text-sm" />
            <span class="text-status-success text-sm">稳定输出</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-status-success/30 to-status-warning/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-bolt text-status-success text-xl" />
        </div>
      </div>
    </div>
    <div
      class="card-rare animate-slide-in-up"
      style="animation-delay: 0.5s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            场均评分
          </p>
          <p class="text-3xl font-bold game-number-rare">
            {{ averageScore }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <span class="game-badge game-badge-rare">精英团队</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-status-warning/30 to-primary/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-star text-status-warning text-xl" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤统计卡片组件
 * 功能：显示总参与人数、总参战时长、场均伤害和场均评分
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

defineProps<{
  totalPlayers: number
  totalTime: number
  averageDamage: number
  averageScore: string
}>()

// 方法
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatTotalTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const days = Math.floor(hours / 24)
  if (days > 0) {
    return `${days}天${hours % 24}小时`
  }
  return `${hours}小时`
}
</script>