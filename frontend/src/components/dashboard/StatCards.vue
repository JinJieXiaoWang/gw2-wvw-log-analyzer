<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <!-- 总战斗数 -->
    <div
      class="card-legendary animate-slide-in-up min-w-0"
      style="animation-delay: 0.1s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            总战斗数
          </p>
          <p class="text-3xl font-bold game-number-legendary truncate">
            {{ isLoadingStats ? '...' : formatNumber(dashboardStats?.total_fights || 0) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i
              :class="changeIconClass(dashboardStats?.change?.fights)"
              class="text-sm"
            />
            <span
              :class="changeTextClass(dashboardStats?.change?.fights)"
              class="text-sm"
            >
              {{ Math.abs(dashboardStats?.change?.fights || 0) }}% 较上期
            </span>
          </div>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-primary/40 to-primary/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-file text-primary text-2xl" />
        </div>
      </div>
    </div>

    <!-- 活跃账号 -->
    <div
      class="card-exotic animate-slide-in-up min-w-0"
      style="animation-delay: 0.2s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            活跃账号
          </p>
          <p class="text-3xl font-bold game-number-exotic truncate">
            {{ isLoadingStats ? '...' : formatNumber(dashboardStats?.active_accounts || 0) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i
              :class="changeIconClass(dashboardStats?.change?.accounts)"
              class="text-sm"
            />
            <span
              :class="changeTextClass(dashboardStats?.change?.accounts)"
              class="text-sm"
            >
              {{ Math.abs(dashboardStats?.change?.accounts || 0) }}% 较上期
            </span>
          </div>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-secondary/40 to-secondary/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-users text-secondary text-2xl" />
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
            {{ isLoadingStats ? '...' : formatNumber(dashboardStats?.total_damage || 0) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i
              :class="changeIconClass(dashboardStats?.change?.damage)"
              class="text-sm"
            />
            <span
              :class="changeTextClass(dashboardStats?.change?.damage)"
              class="text-sm"
            >
              {{ Math.abs(dashboardStats?.change?.damage || 0) }}% 较上期
            </span>
          </div>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-status-error/40 to-status-error/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-bolt text-status-error text-2xl" />
        </div>
      </div>
    </div>

    <!-- 总治疗 -->
    <div
      class="card-mythic animate-slide-in-up min-w-0"
      style="animation-delay: 0.4s"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0 overflow-hidden">
          <p class="text-neutral-text-secondary text-sm mb-1">
            总治疗
          </p>
          <p class="text-3xl font-bold game-number-mythic truncate">
            {{ isLoadingStats ? '...' : formatNumber(dashboardStats?.total_healing || 0) }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i
              :class="changeIconClass(dashboardStats?.change?.healing)"
              class="text-sm"
            />
            <span
              :class="changeTextClass(dashboardStats?.change?.healing)"
              class="text-sm"
            >
              {{ Math.abs(dashboardStats?.change?.healing || 0) }}% 较上期
            </span>
          </div>
        </div>
        <div class="w-14 h-14 shrink-0 bg-gradient-to-br from-status-success/40 to-status-success/10 rounded-xl flex items-center justify-center">
          <i class="pi pi-heart text-status-success text-2xl" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据看板统计卡片组件 v2.0
 * 功能：显示总战斗数、活跃账号、总伤害、总治疗
 * 更新：2026-05-04 - 适配新 overview 接口数据结构
 */

defineProps<{
  isLoadingStats: boolean
  dashboardStats: any
}>()

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B'
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const changeIconClass = (val: number | undefined): string => {
  if (!val) return 'pi pi-minus text-neutral-text-disabled'
  return val >= 0 ? 'pi pi-arrow-up text-status-success' : 'pi pi-arrow-down text-status-error'
}

const changeTextClass = (val: number | undefined): string => {
  if (!val) return 'text-neutral-text-disabled'
  return val >= 0 ? 'text-status-success' : 'text-status-error'
}
</script>
