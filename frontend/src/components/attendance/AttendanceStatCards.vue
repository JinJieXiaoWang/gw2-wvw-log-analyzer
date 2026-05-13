<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <MetricCard
      v-for="(card, index) in statCards"
      :key="index"
      v-bind="card"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤统计卡片组件（详细版）
 * 功能：显示出勤账号、总出勤时长、总伤害、击倒人数
 * 更新：2026-05-14 - 重构为使用 MetricCard 配置数组方式
 */

import { computed } from 'vue'
import MetricCard from '@/components/common/feedback/MetricCard.vue'
import { formatDuration, formatNumber } from '@/utils/common/attendanceFormatters'

const props = defineProps<{
  totalAccounts: number
  totalDuration: number
  totalDamage: number
  totalDowned: number
}>()

const statCards = computed(() => [
  {
    label: '出勤账号',
    value: props.totalAccounts,
    icon: 'pi pi-users',
    iconColor: 'text-primary',
    cardClass: 'card-legendary min-w-0',
    valueClass: 'game-number-legendary',
    iconBgClass: 'bg-gradient-to-br from-primary/40 to-primary/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.1
  },
  {
    label: '总出勤时长',
    value: formatDuration(props.totalDuration),
    icon: 'pi pi-clock',
    iconColor: 'text-secondary',
    cardClass: 'card-exotic min-w-0',
    valueClass: 'game-number-exotic',
    iconBgClass: 'bg-gradient-to-br from-secondary/40 to-secondary/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.2
  },
  {
    label: '总伤害',
    value: formatNumber(props.totalDamage),
    icon: 'pi pi-bolt',
    iconColor: 'text-status-error',
    cardClass: 'card-rare min-w-0',
    valueClass: 'game-number-rare',
    iconBgClass: 'bg-gradient-to-br from-status-error/40 to-status-error/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.3
  },
  {
    label: '击倒人数',
    value: props.totalDowned,
    icon: 'pi pi-target',
    iconColor: 'text-warning',
    cardClass: 'card-mythic min-w-0',
    valueClass: 'game-number-mythic',
    iconBgClass: 'bg-gradient-to-br from-warning/40 to-warning/10',
    iconSizeClass: 'w-14 h-14',
    iconTextClass: 'text-2xl',
    animationDelay: 0.4
  }
])
</script>
