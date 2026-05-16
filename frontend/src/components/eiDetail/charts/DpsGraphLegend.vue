<template>
  <div class="graph-header">
    <h3 class="graph-title">
      <i class="pi pi-chart-line" />
      {{ title }}
    </h3>
    <div class="graph-legend">
      <div
        v-for="player in players"
        :key="player.instanceID"
        class="legend-item"
      >
        <span
          class="legend-color"
          :style="{ backgroundColor: player.color }"
        />
        <span class="legend-name">{{ player.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface LegendPlayer {
  instanceID: number
  name: string
  color: string
}

defineProps<{
  title: string
  players: LegendPlayer[]
}>()
</script>

<style scoped lang="css">
.graph-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.graph-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.graph-title i {
  color: var(--color-primary);
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-name {
  color: var(--color-text-secondary);
}
</style>
