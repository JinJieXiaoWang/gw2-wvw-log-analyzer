<template>
  <div class="sr-view-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="tab-btn"
      :class="{ active: modelValue === tab.value }"
      @click="$emit('update:modelValue', tab.value)"
    >
      <i :class="['pi', tab.icon]" />
      <span>{{ tab.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: 'stats' | 'timeline' | 'heatmap' | 'cycle'
}>()

defineEmits<{
  'update:modelValue': [value: 'stats' | 'timeline' | 'heatmap' | 'cycle']
}>()

const tabs: { value: 'stats' | 'timeline' | 'heatmap' | 'cycle'; label: string; icon: string }[] = [
  { value: 'stats', label: '技能统计', icon: 'pi pi-chart-pie' },
  { value: 'timeline', label: '时间轴', icon: 'pi pi-timeline' },
  { value: 'heatmap', label: '热力图', icon: 'pi pi-square' },
  { value: 'cycle', label: '循环视图', icon: 'pi pi-repeat' },
]
</script>

<style scoped>
.sr-view-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem;
  background: rgba(255,255,255,0.03);
  border-radius: 0.5rem;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: rgba(255,255,255,0.05);
  color: var(--color-text-primary, #f1f5f9);
}

.tab-btn.active {
  background: var(--color-primary, #165DFF);
  color: white;
}

.tab-btn i {
  font-size: 0.75rem;
}
</style>