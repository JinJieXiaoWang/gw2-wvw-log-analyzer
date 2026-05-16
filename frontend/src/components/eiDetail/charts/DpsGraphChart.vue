<template>
  <div class="graph-body">
    <div class="y-axis">
      <span
        v-for="(tick, idx) in yAxisTicks"
        :key="idx"
        class="y-tick"
      >{{ formatDamage(tick) }}</span>
    </div>
    <div class="graph-area">
      <div
        v-for="line in lines"
        :key="line.instanceID"
        class="graph-line"
        :style="line.style"
      />
      <div class="graph-bars">
        <div
          v-for="(_, idx) in xAxisTicks"
          :key="idx"
          class="x-tick-line"
          :style="{ left: (idx / (xAxisTicks.length - 1)) * 100 + '%' }"
        />
      </div>
    </div>
  </div>
  <div class="x-axis">
    <span
      v-for="(tick, idx) in xAxisTicks"
      :key="idx"
      class="x-tick"
    >{{ tick }}s</span>
  </div>
</template>

<script setup lang="ts">
import { formatDamage } from '@/types/eliteInsights'

interface ChartLine {
  instanceID: number
  style: Record<string, string>
}

defineProps<{
  lines: ChartLine[]
  yAxisTicks: number[]
  xAxisTicks: number[]
}>()
</script>

<style scoped lang="css">
.graph-body {
  display: flex;
  height: 300px;
  gap: 0.5rem;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 0.5rem;
  width: 60px;
}

.y-tick {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.graph-area {
  flex: 1;
  position: relative;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  overflow: hidden;
}

.graph-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.6;
}

.graph-bars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.x-tick-line {
  position: absolute;
  top: 0;
  width: 1px;
  height: 100%;
  background-color: var(--color-border);
  opacity: 0.3;
}

.x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  padding-left: 68px;
}

.x-tick {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}
</style>
