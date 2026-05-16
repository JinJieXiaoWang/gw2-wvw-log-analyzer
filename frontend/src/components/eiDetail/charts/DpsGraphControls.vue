<template>
  <div class="graph-controls card">
    <div class="control-group">
      <span class="control-label">图表类型</span>
      <div class="control-buttons">
        <button
          v-for="mode in graphModes"
          :key="mode.key"
          class="control-btn"
          :class="{ active: modelValue === mode.key }"
          @click="$emit('update:modelValue', mode.key)"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>
    <div class="control-group">
      <span class="control-label">时间间隔</span>
      <select
        :value="timeInterval"
        class="control-select"
        @change="$emit('update:timeInterval', Number(($event.target as HTMLSelectElement).value))"
      >
        <option :value="1">
          1�?
        </option>
        <option :value="5">
          5�?
        </option>
        <option :value="10">
          10�?
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
export type GraphMode = 'damage' | 'dps' | 'power' | 'condi'

defineProps<{
  modelValue: GraphMode
  timeInterval: number
}>()

defineEmits<{
  'update:modelValue': [mode: GraphMode]
  'update:timeInterval': [interval: number]
}>()

const graphModes: { key: GraphMode; label: string }[] = [
  { key: 'damage', label: '总伤害' },
  { key: 'dps', label: 'DPS' },
  { key: 'power', label: '直伤' },
  { key: 'condi', label: '症状' }
]
</script>

<style scoped lang="css">
.graph-controls {
  display: flex;
  gap: 1.5rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.control-buttons {
  display: flex;
  gap: 0.25rem;
}

.control-btn {
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-bg);
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  border-color: var(--color-primary-alpha-30);
}

.control-btn.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.control-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.8125rem;
}
</style>
