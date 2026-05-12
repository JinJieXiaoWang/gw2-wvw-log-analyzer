<template>
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
    <StatCard
      icon="pi pi-calendar"
      label="出勤天数"
      :value="summary.attendance_count || 0"
      gradient="from-primary/10 to-secondary/5"
      border="border-primary/20"
      icon-bg="from-primary/30 to-secondary/30"
      text-color="text-primary"
    />
    <StatCard
      icon="pi pi-clock"
      label="总时长"
      :value="formatDuration(summary.total_duration_sec)"
      gradient="from-secondary/10 to-status-success/5"
      border="border-secondary/20"
      icon-bg="from-secondary/30 to-status-success/30"
      text-color="text-secondary"
    />
    <StatCard
      icon="pi pi-bolt"
      label="总伤害"
      :value="formatNumber(summary.total_damage)"
      gradient="from-status-error/10 to-status-warning/5"
      border="border-status-error/20"
      icon-bg="from-status-error/30 to-status-warning/30"
      text-color="text-status-error"
    />
    <StatCard
      icon="pi pi-heart"
      label="K/D"
      :value="summary.kd_ratio || 0"
      gradient="from-status-success/10 to-primary/5"
      border="border-status-success/20"
      icon-bg="from-status-success/30 to-primary/30"
      text-color="text-status-success"
    />
  </div>
</template>

<script setup lang="ts">
import StatCard from './StatCard.vue'
import { formatDuration, formatNumber } from '@/utils/common/attendanceFormatters'

defineProps<{ summary: any }>()
</script>
