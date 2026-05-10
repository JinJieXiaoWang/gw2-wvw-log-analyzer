<template>
  <div class="view-mode-bar">
    <div class="mode-tabs">
      <button class="mode-tab" :class="{ active: viewMode === 'simple' }" @click="$emit('update:viewMode', 'simple')">
        <i class="pi pi-th-large" /> 简单循环
      </button>
      <button class="mode-tab" :class="{ active: viewMode === 'advanced' }" @click="$emit('update:viewMode', 'advanced')">
        <i class="pi pi-chart-bar" /> 高级时间轴
      </button>
    </div>
    <div v-if="viewMode === 'simple'" class="simple-filters">
      <label class="filter-check">
        <input v-model="localShowAuto" type="checkbox"> <span>显示普攻</span>
      </label>
      <label class="filter-check">
        <input v-model="localShowInstant" type="checkbox"> <span>显示瞬发</span>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  viewMode: 'simple' | 'advanced'
  showAutoAttacks: boolean
  showInstantCast: boolean
}>()

const emit = defineEmits<{
  'update:viewMode': [mode: 'simple' | 'advanced']
  'update:showAutoAttacks': [val: boolean]
  'update:showInstantCast': [val: boolean]
}>()

const localShowAuto = computed({ get: () => props.showAutoAttacks, set: v => emit('update:showAutoAttacks', v) })
const localShowInstant = computed({ get: () => props.showInstantCast, set: v => emit('update:showInstantCast', v) })
</script>
