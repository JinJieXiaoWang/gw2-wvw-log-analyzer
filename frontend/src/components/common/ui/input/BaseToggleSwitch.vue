<template>
  <div
    class="base-toggle-switch inline-flex items-center"
    :class="{ 'cursor-not-allowed opacity-60': disabled }"
  >
    <ToggleSwitch
      :model-value="modelValue"
      :disabled="disabled"
      :aria-label="ariaLabel"
      @update:model-value="$emit('update:modelValue', $event)"
      @change="$emit('change', !modelValue)"
    />
    <span
      v-if="label"
      class="ml-2 text-sm select-none"
      :class="disabled ? 'text-neutral-text-disabled' : 'text-neutral-text-secondary'"
      @click="!disabled && $emit('update:modelValue', !modelValue)"
    >
      {{ label }}
    </span>
  </div>
</template>

<script setup lang="ts">
/**
 * BaseToggleSwitch - 开关组件封装
 * 基于 PrimeVue ToggleSwitch / InputSwitch 二次封装
 */

import ToggleSwitch from 'primevue/toggleswitch'

interface Props {
  modelValue?: boolean
  disabled?: boolean
  label?: string
  ariaLabel?: string
}

withDefaults(defineProps<Props>(), {
  modelValue: false,
  disabled: false,
  label: '',
  ariaLabel: '切换开关'
})

defineEmits<{
  'update:modelValue': [value: boolean]
  change: [value: boolean]
}>()
</script>

<style scoped>
.base-toggle-switch :deep(.p-toggleswitch) {
  width: 40px;
  height: 22px;
}

.base-toggle-switch :deep(.p-toggleswitch-slider) {
  background: var(--neutral-border);
  border-radius: 9999px;
  transition: background-color 0.2s ease;
}

.base-toggle-switch :deep(.p-toggleswitch-checked .p-toggleswitch-slider) {
  background: var(--color-primary);
}

.base-toggle-switch :deep(.p-toggleswitch-handle) {
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.base-toggle-switch :deep(.p-toggleswitch-checked .p-toggleswitch-handle) {
  transform: translateX(18px);
}

.base-toggle-switch :deep(.p-toggleswitch:not(.p-disabled):hover .p-toggleswitch-slider) {
  background: var(--neutral-border-light);
}

.base-toggle-switch :deep(.p-toggleswitch-checked:not(.p-disabled):hover .p-toggleswitch-slider) {
  background: var(--color-primary-hover);
}

.base-toggle-switch :deep(.p-toggleswitch.p-disabled) {
  opacity: 0.6;
}
</style>
