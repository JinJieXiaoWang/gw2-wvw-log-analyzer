<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <MetricCard
      v-for="(card, index) in statCards"
      :key="index"
      v-bind="card"
    >
      <template #extra>
        <template v-if="index === 0">
          <i class="pi pi-arrow-up text-status-success text-sm" />
          <span class="text-status-success text-sm">活跃团队</span>
        </template>
        <span
          v-else-if="index === 1"
          class="game-badge game-badge-mvp"
        >持续作战</span>
        <template v-else-if="index === 2">
          <i class="pi pi-chart-line text-status-success text-sm" />
          <span class="text-status-success text-sm">稳定输出</span>
        </template>
        <span
          v-else-if="index === 3"
          class="game-badge game-badge-rare"
        >精英团队</span>
      </template>
    </MetricCard>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤统计卡片组件
 * 功能：显示总参与人数、总参战时长、场均伤害和场均评分
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 * 更新：2026-05-14 - 重构为使用 MetricCard 配置数组方式
 */

import { computed } from 'vue'
import MetricCard from '@/components/common/feedback/MetricCard.vue'

const props = defineProps<{
  totalPlayers: number
  totalTime: number
  averageDamage: number
  averageScore: string
}>()

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

const statCards = computed(() => [
  {
    label: '总参与人数',
    value: props.totalPlayers,
    icon: 'pi pi-users',
    iconColor: 'text-primary',
    cardClass: 'card-legendary',
    valueClass: 'game-number-legendary',
    iconBgClass: 'bg-gradient-to-br from-primary/30 to-secondary/30',
    animationDelay: 0.2
  },
  {
    label: '总参战时长',
    value: formatTotalTime(props.totalTime),
    icon: 'pi pi-clock',
    iconColor: 'text-secondary',
    cardClass: 'card-exotic',
    valueClass: 'game-number-exotic',
    iconBgClass: 'bg-gradient-to-br from-secondary/30 to-status-success/30',
    animationDelay: 0.3
  },
  {
    label: '场均伤害',
    value: formatNumber(props.averageDamage),
    icon: 'pi pi-bolt',
    iconColor: 'text-status-success',
    cardClass: 'card-rare',
    valueClass: 'game-number-rare',
    iconBgClass: 'bg-gradient-to-br from-status-success/30 to-status-warning/30',
    animationDelay: 0.4
  },
  {
    label: '场均评分',
    value: props.averageScore,
    icon: 'pi pi-star',
    iconColor: 'text-status-warning',
    cardClass: 'card-rare',
    valueClass: 'game-number-rare',
    iconBgClass: 'bg-gradient-to-br from-status-warning/30 to-primary/30',
    animationDelay: 0.5
  }
])
</script>
