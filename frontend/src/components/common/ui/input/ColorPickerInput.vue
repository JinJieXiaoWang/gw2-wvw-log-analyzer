<template>
  <div ref="pickerRef" class="color-picker-input relative w-full">
    <div class="input-wrapper flex items-center gap-2">
      <InputText :model-value="modelValue" placeholder="#165DFF 或 primary" class="flex-1" @update:model-value="handleInputChange" />
      <button type="button" class="color-trigger w-9 h-9 rounded-[8px] bg-neutral-bg cursor-pointer flex items-center justify-center shrink-0 hover:border-[var(--color-primary)] hover:scale-105 [&.has-color]:border-transparent [&.has-color]:shadow-[0_0_8px_var(--color-primary-alpha-20)] [&.is-class]:border-[var(--color-primary)] [&.is-class]:bg-[var(--color-primary-alpha-10)]" :class="{ 'has-color': isValidHex, 'is-class': isClassName }" :style="previewStyle" @click="togglePanel">
        <i v-if="isClassName" class="pi pi-palette text-xs" />
        <i v-else-if="!modelValue" class="pi pi-palette text-xs text-neutral-text-disabled" />
      </button>
    </div>
    <ColorPickerPanel
      :is-open="isOpen"
      :model-value="modelValue"
      v-model:custom-hex-input="customHexInput"
      :custom-error="customError"
      :is-valid-hex="isValidHex"
      :is-valid-custom-hex="isValidCustomHex"
      @select="selectColor"
      @clear="clearColor"
      @close="closePanel"
      @apply-custom="applyCustomHex"
    />
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import ColorPickerPanel from './ColorPickerPanel.vue'
import { useColorPicker } from '@/composables/common/useColorPicker'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const {
  isOpen, pickerRef, customHexInput, customError,
  isValidHex, isClassName, isValidCustomHex, previewStyle,
  togglePanel, closePanel, selectColor, clearColor, handleInputChange, applyCustomHex
} = useColorPicker(props, emit)
</script>

<style scoped>
.color-panel::before {
  content: ''; position: absolute; top: -6px; right: 12px; width: 12px; height: 12px; background: var(--color-card); border-left: 1px solid var(--color-border); border-top: 1px solid var(--color-border); transform: rotate(45deg);
}
.color-panel-enter-active, .color-panel-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.panel-close:hover {
  background: var(--color-bg); color: var(--color-text);
}
.preset-item:hover {
  transform: scale(1.1); z-index: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.preset-item.active {
  border-color: var(--color-text); box-shadow: 0 0 0 2px var(--color-card), 0 0 0 4px var(--color-primary);
}
.class-tag:hover {
  border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-alpha-10);
}
.class-tag.active {
  border-color: var(--color-primary); background: var(--color-primary); color: #fff;
}
</style>
