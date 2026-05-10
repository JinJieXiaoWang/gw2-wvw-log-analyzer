<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <div v-for="(card, i) in cards" :key="card.label" class="card animate-slide-in-up" :style="{ animationDelay: `${(i + 1) * 0.1}s` }">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">{{ card.label }}</p>
          <p class="text-3xl font-bold" :class="card.valueClass">{{ card.formatter(card.value) }}</p>
        </div>
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="card.iconBg">
          <i :class="card.icon" class="text-xl" :class="card.iconColor" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatNumber, formatDuration } from '@/utils/attendance/attendanceFormatters'

const props = defineProps<{
  totalAccounts: number
  totalDuration: number
  totalDamage: number
  totalHealing: number
}>()

const cards = computed(() => [
  { label: '出勤账号', value: props.totalAccounts, formatter: (v: number) => String(v), valueClass: 'game-number-legendary', icon: 'pi pi-users', iconBg: 'bg-gradient-to-br from-primary/30 to-secondary/30', iconColor: 'text-primary' },
  { label: '总出勤时长', value: props.totalDuration, formatter: formatDuration, valueClass: 'game-number-exotic', icon: 'pi pi-clock', iconBg: 'bg-gradient-to-br from-secondary/30 to-status-success/30', iconColor: 'text-secondary' },
  { label: '总伤害', value: props.totalDamage, formatter: formatNumber, valueClass: 'game-number-rare', icon: 'pi pi-bolt', iconBg: 'bg-gradient-to-br from-status-error/30 to-status-warning/30', iconColor: 'text-status-error' },
  { label: '总治疗', value: props.totalHealing, formatter: formatNumber, valueClass: 'game-number-mythic', icon: 'pi pi-heart', iconBg: 'bg-gradient-to-br from-status-success/30 to-primary/30', iconColor: 'text-status-success' }
])
</script>
