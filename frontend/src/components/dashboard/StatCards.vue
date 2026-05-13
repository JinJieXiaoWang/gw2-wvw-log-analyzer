<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <MetricCard
      v-for="(card, index) in statCards"
      :key="index"
      v-bind="card"
    >
      <template #extra>
        <i :class="[changeIconClass(changeValues[index]), 'text-sm']" />
        <span :class="[changeTextClass(changeValues[index]), 'text-sm']">
          {{ Math.abs(changeValues[index] || 0) }}% 较上期
        </span>
      </template>
    </MetricCard>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据看板统计卡片组件 v2.0
 * 功能：显示总战斗数、活跃账号、总伤害、总治疗
 * 更新：2026-05-04 - 适配新 overview 接口数据结构
 * 更新：2026-05-14 - 重构为使用 MetricCard 配置数组方式
 */

import { computed } from 'vue'
import MetricCard from '@/components/common/feedback/MetricCard.vue'

const props = defineProps<{
  isLoadingStats: boolean
  dashboardStats: any
}>()

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B'
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
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

const statCards = computed(() => [
  {
    label: '总战斗数',
    value: props.isLoadingStats ? '...' : formatNumber(props.dashboardStats?.total_fights || 0),
    icon: 'pi pi-file',
    iconColor: 'text-primary',
    cardClass: 'card-legendary min-w-0',
    valueClass: 'game-number-legendary',
    iconBgClass: 'bg-gradient-to-br from-primary/40 to-primary/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.1
  },
  {
    label: '活跃账号',
    value: props.isLoadingStats ? '...' : formatNumber(props.dashboardStats?.active_accounts || 0),
    icon: 'pi pi-users',
    iconColor: 'text-secondary',
    cardClass: 'card-exotic min-w-0',
    valueClass: 'game-number-exotic',
    iconBgClass: 'bg-gradient-to-br from-secondary/40 to-secondary/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.2
  },
  {
    label: '击倒',
    value: props.isLoadingStats ? '...' : formatNumber(props.dashboardStats?.total_downs || 0),
    icon: 'pi pi-arrow-circle-down',
    iconColor: 'text-status-error',
    cardClass: 'card-rare min-w-0',
    valueClass: 'game-number-rare',
    iconBgClass: 'bg-gradient-to-br from-status-error/40 to-status-error/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.3
  },
  {
    label: '击杀',
    value: props.isLoadingStats ? '...' : formatNumber(props.dashboardStats?.total_kills || 0),
    icon: 'pi pi-flag',
    iconColor: 'text-status-success',
    cardClass: 'card-mythic min-w-0',
    valueClass: 'game-number-mythic',
    iconBgClass: 'bg-gradient-to-br from-status-success/40 to-status-success/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.4
  }
])

const changeValues = computed(() => [
  props.dashboardStats?.change?.fights,
  props.dashboardStats?.change?.accounts,
  props.dashboardStats?.change?.downs,
  props.dashboardStats?.change?.kills
])
</script>
