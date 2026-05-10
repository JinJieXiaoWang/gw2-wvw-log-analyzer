<template>
  <div ref="pickerRef" class="color-picker-input">
    <div class="input-wrapper">
      <InputText :model-value="modelValue" placeholder="#165DFF 或 primary" class="flex-1" @update:model-value="handleInputChange" />
      <button type="button" class="color-trigger" :class="{ 'has-color': isValidHex, 'is-class': isClassName }" :style="previewStyle" @click="togglePanel">
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
.color-picker-input { position: relative; width: 100%; }
.input-wrapper { display: flex; align-items: center; gap: 8px; }
.color-trigger { width: 36px; height: 36px; border-radius: 8px; border: 2px solid var(--color-border); background: var(--color-bg); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; flex-shrink: 0; }
.color-trigger:hover { border-color: var(--color-primary); transform: scale(1.05); }
.color-trigger.has-color { border-color: transparent; box-shadow: 0 0 8px var(--color-primary-alpha-20); }
.color-trigger.is-class { border-color: var(--color-primary); background: var(--color-primary-alpha-10); }

.color-panel { position: absolute; top: calc(100% + 8px); right: 0; width: 320px; background: var(--color-card); border: 1px solid var(--color-border); border-radius: 12px; padding: 16px; z-index: 1000; box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 20px var(--color-primary-alpha-10); }
.color-panel::before { content: ''; position: absolute; top: -6px; right: 12px; width: 12px; height: 12px; background: var(--color-card); border-left: 1px solid var(--color-border); border-top: 1px solid var(--color-border); transform: rotate(45deg); }
.color-panel-enter-active, .color-panel-leave-active { transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.color-panel-enter-from { opacity: 0; transform: translateY(-8px) scale(0.96); }
.color-panel-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-title { font-size: 14px; font-weight: 600; color: var(--color-text); }
.panel-close { width: 24px; height: 24px; border-radius: 6px; border: none; background: transparent; color: var(--color-text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.panel-close:hover { background: var(--color-bg); color: var(--color-text); }

.current-preview { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--color-bg); border-radius: 10px; margin-bottom: 16px; border: 1px solid var(--color-border); }
.preview-large { width: 48px; height: 48px; border-radius: 10px; border: 1px solid var(--color-border); display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background-color 0.2s; }
.preview-placeholder { font-size: 10px; color: var(--color-text-secondary); }
.preview-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.preview-label { font-size: 11px; color: var(--color-text-secondary); }
.preview-value { font-size: 13px; font-weight: 500; color: var(--color-text); font-family: 'JetBrains Mono', 'Fira Code', monospace; word-break: break-all; }

.section-label { display: block; font-size: 12px; font-weight: 500; color: var(--color-text-secondary); margin-bottom: 8px; }
.preset-section { margin-bottom: 16px; }
.preset-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 6px; }
.preset-item { aspect-ratio: 1; border-radius: 8px; border: 2px solid transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; position: relative; }
.preset-item:hover { transform: scale(1.1); z-index: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.preset-item.active { border-color: var(--color-text); box-shadow: 0 0 0 2px var(--color-card), 0 0 0 4px var(--color-primary); }

.custom-section { margin-bottom: 16px; }
.custom-input-row { display: flex; align-items: center; gap: 8px; }
.hash-prefix { font-size: 16px; font-weight: 500; color: var(--color-text-secondary); font-family: monospace; }
.custom-preview { width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-bg); flex-shrink: 0; transition: background-color 0.2s; }
.error-text { display: block; color: var(--color-error); font-size: 11px; margin-top: 4px; }

.class-section { margin-bottom: 16px; }
.class-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.class-tag { padding: 4px 10px; border-radius: 6px; border: 1px solid var(--color-border); background: var(--color-bg); color: var(--color-text-secondary); font-size: 12px; cursor: pointer; transition: all 0.2s; }
.class-tag:hover { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-alpha-10); }
.class-tag.active { border-color: var(--color-primary); background: var(--color-primary); color: #fff; }

.panel-actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 12px; border-top: 1px solid var(--color-border); }
</style>
