<template>
  <transition name="color-panel">
    <div v-if="isOpen" class="color-panel" @click.stop>
      <div class="panel-header">
        <span class="panel-title">选择颜色</span>
        <button class="panel-close" @click="$emit('close')"><i class="pi pi-times text-xs" /></button>
      </div>
      <div class="current-preview">
        <div class="preview-large" :style="{ backgroundColor: isValidHex ? modelValue : undefined }">
          <span v-if="!isValidHex" class="preview-placeholder">{{ modelValue || '无' }}</span>
        </div>
        <div class="preview-info">
          <span class="preview-label">当前颜色</span>
          <span class="preview-value">{{ modelValue || '未设置' }}</span>
        </div>
      </div>
      <div class="preset-section">
        <span class="section-label">预设颜色</span>
        <div class="preset-grid">
          <button v-for="color in PRESET_COLORS" :key="color.value" type="button" class="preset-item" :class="{ active: modelValue === color.value }" :style="{ backgroundColor: color.value }" :title="color.label" @click="$emit('select', color.value)">
            <i v-if="modelValue === color.value" class="pi pi-check text-white text-xs" />
          </button>
        </div>
      </div>
      <div class="custom-section">
        <span class="section-label">自定义颜色</span>
        <div class="custom-input-row">
          <span class="hash-prefix">#</span>
          <InputText v-model="customHexInput" placeholder="RRGGBB" class="flex-1" maxlength="6" @blur="$emit('apply-custom')" @keydown.enter="$emit('apply-custom')" />
          <div class="custom-preview" :style="{ backgroundColor: isValidCustomHex ? '#' + customHexInput : undefined }" />
        </div>
        <small v-if="customError" class="error-text">{{ customError }}</small>
      </div>
      <div class="class-section">
        <span class="section-label">样式类名</span>
        <div class="class-tags">
          <button v-for="cls in CLASS_NAME_OPTIONS" :key="cls" type="button" class="class-tag" :class="{ active: modelValue === cls }" @click="$emit('select', cls)">{{ cls }}</button>
        </div>
      </div>
      <div class="panel-actions">
        <BaseButton label="清除" icon="pi pi-times" size="small" severity="secondary" text @click="$emit('clear')" />
        <BaseButton label="ȷ认" icon="pi pi-check" size="small" severity="primary" @click="$emit('close')" />
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import BaseButton from './BaseButton.vue'
import { PRESET_COLORS, CLASS_NAME_OPTIONS } from '@/composables/common/useColorPicker'

const props = defineProps<{
  isOpen: boolean
  modelValue: string
  customError: string
  isValidHex: boolean
  isValidCustomHex: boolean
}>()

const customHexInput = defineModel<string>('customHexInput', { required: true })

const emit = defineEmits<{
  select: [color: string]
  clear: []
  close: []
  'apply-custom': []
}>()
</script>
