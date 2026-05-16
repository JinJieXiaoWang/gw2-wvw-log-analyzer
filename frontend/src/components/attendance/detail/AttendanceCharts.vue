<template>
  <div class="container mx-auto px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <AttendanceTrendChart
        class="lg:col-span-2"
        :detail-data="detailData"
        @time-range-change="emit('timeRangeChange', $event)"
      />
      <AttendanceRadarChart
        :detail-data="detailData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import AttendanceTrendChart from './AttendanceTrendChart.vue'
import AttendanceRadarChart from './AttendanceRadarChart.vue'

defineProps<{
  detailData: any
}>()

const emit = defineEmits(['timeRangeChange'])
</script>
