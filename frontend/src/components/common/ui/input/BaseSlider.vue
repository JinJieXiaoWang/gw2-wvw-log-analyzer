<template>
  <div class="base-slider">
    <Slider
      :model-value="modelValue"
      :min="min"
      :max="max"
      :step="step"
      :disabled="disabled"
      :range="range"
      class="w-full"
      @update:model-value="$emit('update:modelValue', $event)"
      @change="$emit('change', $event)"
      @slide-end="$emit('slideEnd', $event)"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * BaseSlider - 滑块组件封装
 * 基于 PrimeVue Slider 二次封装，统一项目内滑块交互风格
 */

import Slider from 'primevue/slider'

interface Props {
  modelValue?: number | number[]
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  range?: boolean
}

withDefaults(defineProps<Props>(), {
  modelValue: 0,
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
  range: false
})

defineEmits<{
  'update:modelValue': [value: number | number[]]
  change: [value: number | number[]]
  slideEnd: [value: number | number[]]
}>()
</script>

<style scoped>
.base-slider :deep(.p-slider) {
  background: var(--neutral-border);
  border-radius: 9999px;
  height: 6px;
}

.base-slider :deep(.p-slider-range) {
  background: var(--color-primary);
  border-radius: 9999px;
}

.base-slider :deep(.p-slider-handle) {
  width: 18px;
  height: 18px;
  background: var(--color-primary);
  border: 2px solid var(--color-surface-0);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.base-slider :deep(.p-slider-handle:hover) {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);
}

.base-slider :deep(.p-slider-handle:focus) {
  box-shadow: 0 0 0 3px var(--color-primary-alpha-20);
}

.base-slider :deep(.p-slider.p-disabled) {
  opacity: 0.5;
}

.base-slider :deep(.p-slider.p-disabled .p-slider-handle) {
  cursor: not-allowed;
}
</style>
