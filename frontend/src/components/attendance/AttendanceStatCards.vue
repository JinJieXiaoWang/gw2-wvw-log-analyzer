<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <!-- 出勤账号 -->
    <div
      class="card-legendary animate-slide-in-up min-w-0"
      style="animation-delay: 0.1s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            出勤账号
          </p>
          <p class="text-3xl font-bold game-number-legendary truncate">
            {{ totalAccounts }}
          </p>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-primary/40 to-primary/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-users text-primary text-2xl" />
        </div>
      </div>
    </div>

    <!-- 总出勤时长 -->
    <div
      class="card-exotic animate-slide-in-up min-w-0"
      style="animation-delay: 0.2s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            总出勤时长
          </p>
          <p class="text-3xl font-bold game-number-exotic truncate">
            {{ formatDuration(totalDuration) }}
          </p>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-secondary/40 to-secondary/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-clock text-secondary text-2xl" />
        </div>
      </div>
    </div>

    <!-- 总伤害 -->
    <div
      class="card-rare animate-slide-in-up min-w-0"
      style="animation-delay: 0.3s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            总伤害
          </p>
          <p class="text-3xl font-bold game-number-rare truncate">
            {{ formatNumber(totalDamage) }}
          </p>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-status-error/40 to-status-error/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-bolt text-status-error text-2xl" />
        </div>
      </div>
    </div>

    <!-- 击倒人数 -->
    <div
      class="card-mythic animate-slide-in-up min-w-0"
      style="animation-delay: 0.4s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            击倒人数
          </p>
          <p class="text-3xl font-bold game-number-mythic truncate">
            {{ totalDowned }}
          </p>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-warning/40 to-warning/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-target text-warning text-2xl" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDuration, formatNumber } from '@/utils/common/attendanceFormatters';

defineProps<{
  totalAccounts: number
  totalDuration: number
  totalDamage: number
  totalDowned: number
}>()
</script>
