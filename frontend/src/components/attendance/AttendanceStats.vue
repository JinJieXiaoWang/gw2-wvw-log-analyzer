<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <!-- 动态值，无法使用 Tailwind 静态类 -->
    <div
      class="card-legendary animate-slide-in-up"
      style="animation-delay: 0.1s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            出勤账号
          </p>
          <p class="text-3xl font-bold game-number-legendary">
            {{ totalAccounts }}
          </p>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-users text-primary text-xl" />
        </div>
      </div>
    </div>
    <!-- 动态值，无法使用 Tailwind 静态类 -->
    <div
      class="card-exotic animate-slide-in-up"
      style="animation-delay: 0.2s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总出勤时长
          </p>
          <p class="text-3xl font-bold game-number-exotic">
            {{ formatDuration(totalDuration) }}
          </p>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-secondary/30 to-status-success/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-clock text-secondary text-xl" />
        </div>
      </div>
    </div>
    <!-- 动态值，无法使用 Tailwind 静态类 -->
    <div
      class="card-rare animate-slide-in-up"
      style="animation-delay: 0.3s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总伤害
          </p>
          <p class="text-3xl font-bold game-number-rare">
            {{ formatNumber(totalDamage) }}
          </p>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-status-error/30 to-status-warning/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-bolt text-status-error text-xl" />
        </div>
      </div>
    </div>
    <!-- 动态值，无法使用 Tailwind 静态类 -->
    <div
      class="card-mythic animate-slide-in-up"
      style="animation-delay: 0.4s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总治疗
          </p>
          <p class="text-3xl font-bold game-number-mythic">
            {{ formatNumber(totalHealing) }}
          </p>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-status-success/30 to-primary/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-heart text-status-success text-xl" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 考勤统计卡片组件
 * 功能：显示出勤账号数、总时长、总伤害、总治疗的统计卡片
 * 作者：Claude
 * 创建日期：2026-05-11
 */

import { formatNumber, formatDuration } from '@/utils/common/attendanceFormatters'

defineProps<{
  totalAccounts: number
  totalDuration: number
  totalDamage: number
  totalHealing: number
}>()
</script>

<style scoped lang="css">
.card-mythic {
  position: relative;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);
  overflow: hidden;
  box-shadow: 0 1px 3px var(--color-shadow);
  border-left: 3px solid var(--color-mythic);
}
</style>
