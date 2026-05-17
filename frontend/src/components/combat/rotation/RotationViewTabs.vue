<template>
  <div class="flex gap-2 p-1 rounded-lg bg-white/[0.03]">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="flex items-center gap-1.5 px-3 py-2 rounded-md bg-transparent text-xs cursor-pointer transition-all duration-200 hover:bg-white/5 hover:text-neutral-text-primary"
      :class="modelValue === tab.value ? 'bg-primary text-white hover:bg-primary' : 'text-neutral-text-secondary'"
      @click="$emit('update:modelValue', tab.value)"
    >
      <i :class="['pi', tab.icon, 'text-xs']" />
      <span>{{ tab.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: 'stats' | 'rotation'
}>()

defineEmits<{
  'update:modelValue': [value: 'stats' | 'rotation']
}>()

const tabs: { value: 'stats' | 'rotation'; label: string; icon: string }[] = [
  { value: 'stats', label: '技能统计', icon: 'pi pi-chart-pie' },
  { value: 'rotation', label: '技能时间流', icon: 'pi pi-history' },
]
</script>
