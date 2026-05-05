<template>
  <div
    ref="pickerRef"
    class="color-picker-input"
  >
    <!-- 输入区域 -->
    <div class="input-wrapper">
      <InputText
        :model-value="modelValue"
        placeholder="#165DFF 或 primary"
        class="flex-1"
        @update:model-value="handleInputChange"
      />
      <!-- 颜色预览/触发按钮 -->
      <button
        type="button"
        class="color-trigger"
        :class="{ 'has-color': isValidHex, 'is-class': isClassName }"
        :style="previewStyle"
        @click="togglePanel"
      >
        <i
          v-if="isClassName"
          class="pi pi-palette text-xs"
        />
        <i
          v-else-if="!modelValue"
          class="pi pi-palette text-xs text-neutral-text-disabled"
        />
      </button>
    </div>

    <!-- 颜色面板 -->
    <transition name="color-panel">
      <div
        v-if="isOpen"
        class="color-panel"
        @click.stop
      >
        <!-- 面板头部 -->
        <div class="panel-header">
          <span class="panel-title">选择颜色</span>
          <button
            class="panel-close"
            @click="closePanel"
          >
            <i class="pi pi-times text-xs" />
          </button>
        </div>

        <!-- 当前颜色预览 -->
        <div class="current-preview">
          <div
            class="preview-large"
            :style="{ backgroundColor: isValidHex ? modelValue : undefined }"
          >
            <span
              v-if="!isValidHex"
              class="preview-placeholder"
            >
              {{ modelValue || '无' }}
            </span>
          </div>
          <div class="preview-info">
            <span class="preview-label">当前值</span>
            <span class="preview-value">{{ modelValue || '未设置' }}</span>
          </div>
        </div>

        <!-- 预设颜色 -->
        <div class="preset-section">
          <span class="section-label">预设颜色</span>
          <div class="preset-grid">
            <button
              v-for="color in presetColors"
              :key="color.value"
              type="button"
              class="preset-item"
              :class="{ active: modelValue === color.value }"
              :style="{ backgroundColor: color.value }"
              :title="color.label"
              @click="selectColor(color.value)"
            >
              <i
                v-if="modelValue === color.value"
                class="pi pi-check text-white text-xs"
              />
            </button>
          </div>
        </div>

        <!-- 自定义输入 -->
        <div class="custom-section">
          <span class="section-label">自定义颜色</span>
          <div class="custom-input-row">
            <span class="hash-prefix">#</span>
            <InputText
              v-model="customHexInput"
              placeholder="RRGGBB"
              class="flex-1"
              maxlength="6"
              @blur="applyCustomHex"
              @keydown.enter="applyCustomHex"
            />
            <div
              class="custom-preview"
              :style="{ backgroundColor: isValidCustomHex ? '#' + customHexInput : undefined }"
            />
          </div>
          <small
            v-if="customError"
            class="error-text"
          >{{ customError }}</small>
        </div>

        <!-- CSS 类名快捷输入 -->
        <div class="class-section">
          <span class="section-label">样式类名</span>
          <div class="class-tags">
            <button
              v-for="cls in classNameOptions"
              :key="cls"
              type="button"
              class="class-tag"
              :class="{ active: modelValue === cls }"
              @click="selectColor(cls)"
            >
              {{ cls }}
            </button>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="panel-actions">
          <Button
            label="清除"
            icon="pi pi-times"
            size="small"
            severity="secondary"
            text
            @click="clearColor"
          />
          <Button
            label="确认"
            icon="pi pi-check"
            size="small"
            severity="primary"
            @click="closePanel"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * ColorPickerInput - 颜色选择器输入组件
 * 功能：提供预设颜色选择、自定义Hex输入、CSS类名选择、颜色预览
 * 数据格式：支持 #RRGGBB 十六进制颜色码 或 CSS类名字符串
 * 更新日期：2026-05-04
 */

import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

// ============================================
// Props & Emits
// ============================================
const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// ============================================
// 预设颜色配置
// ============================================
const presetColors = [
  { value: '#165DFF', label: '电竞蓝' },
  { value: '#4080FF', label: '浅蓝' },
  { value: '#FF7D00', label: '战火橙' },
  { value: '#FBCF4B', label: '金黄' },
  { value: '#00C896', label: '科技青' },
  { value: '#00B42A', label: '成功绿' },
  { value: '#F53F3F', label: '危险红' },
  { value: '#722ED1', label: '神秘紫' },
  { value: '#E5E5E5', label: '常规文字' },
  { value: '#909399', label: '次要文字' },
  { value: '#141414', label: '深色背景' },
  { value: '#2A2A2A', label: '卡片背景' },
  { value: '#333333', label: '分割线' },
  { value: '#FFFFFF', label: '纯白' },
  { value: '#000000', label: '纯黑' },
  { value: '#1f77b4', label: '标准蓝' },
]

const classNameOptions = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'contrast']

// ============================================
// 状态
// ============================================
const isOpen = ref(false)
const pickerRef = ref<HTMLElement>()
const customHexInput = ref('')
const customError = ref('')

// ============================================
// 计算属性
// ============================================
const isValidHex = computed(() => {
  return /^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$/.test(props.modelValue)
})

const isClassName = computed(() => {
  return props.modelValue && !props.modelValue.startsWith('#')
})

const isValidCustomHex = computed(() => {
  return /^[0-9A-Fa-f]{6}$/.test(customHexInput.value)
})

const previewStyle = computed(() => {
  if (isValidHex.value) {
    return {
      backgroundColor: props.modelValue,
      borderColor: props.modelValue
    }
  }
  if (isClassName.value) {
    return {
      backgroundColor: 'var(--color-primary-alpha-10)',
      borderColor: 'var(--color-primary)'
    }
  }
  return {}
})

// ============================================
// 方法
// ============================================
function togglePanel() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    // 打开时初始化自定义输入
    const hex = props.modelValue?.replace('#', '') || ''
    if (/^[0-9A-Fa-f]{6}$/.test(hex)) {
      customHexInput.value = hex.toUpperCase()
    } else {
      customHexInput.value = ''
    }
    customError.value = ''
  }
}

function closePanel() {
  isOpen.value = false
}

function selectColor(color: string) {
  emit('update:modelValue', color)
  customError.value = ''
}

function clearColor() {
  emit('update:modelValue', '')
  customHexInput.value = ''
  customError.value = ''
}

function handleInputChange(value: string | undefined) {
  emit('update:modelValue', value || '')
}

function applyCustomHex() {
  const input = customHexInput.value.trim().toUpperCase()

  if (!input) {
    customError.value = ''
    return
  }

  // 验证：必须是 6 位十六进制
  if (!/^[0-9A-Fa-f]{6}$/.test(input)) {
    customError.value = '请输入有效的 6 位十六进制颜色码（如 FF7D00）'
    return
  }

  const fullHex = '#' + input
  emit('update:modelValue', fullHex)
  customError.value = ''
}

// 监听 modelValue 变化，同步自定义输入
watch(() => props.modelValue, (newVal) => {
  if (!isOpen.value) return
  const hex = newVal?.replace('#', '') || ''
  if (/^[0-9A-Fa-f]{6}$/.test(hex)) {
    customHexInput.value = hex.toUpperCase()
    customError.value = ''
  }
})

// 点击外部关闭面板
function handleClickOutside(event: MouseEvent) {
  if (pickerRef.value && !pickerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.color-picker-input {
  position: relative;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-trigger {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 2px solid var(--color-border);
  background: var(--color-bg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.color-trigger:hover {
  border-color: var(--color-primary);
  transform: scale(1.05);
}

.color-trigger.has-color {
  border-color: transparent;
  box-shadow: 0 0 8px var(--color-primary-alpha-20);
}

.color-trigger.is-class {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha-10);
}

/* 颜色面板 */
.color-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  z-index: 1000;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 20px var(--color-primary-alpha-10);
}

.color-panel::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 12px;
  width: 12px;
  height: 12px;
  background: var(--color-card);
  border-left: 1px solid var(--color-border);
  border-top: 1px solid var(--color-border);
  transform: rotate(45deg);
}

/* 面板动画 */
.color-panel-enter-active,
.color-panel-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.color-panel-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}

.color-panel-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.panel-close {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.panel-close:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

/* 当前颜色预览 */
.current-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 10px;
  margin-bottom: 16px;
  border: 1px solid var(--color-border);
}

.preview-large {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background-color 0.2s;
}

.preview-placeholder {
  font-size: 10px;
  color: var(--color-text-secondary);
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.preview-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.preview-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  word-break: break-all;
}

/* 分区标签 */
.section-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

/* 预设颜色网格 */
.preset-section {
  margin-bottom: 16px;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 6px;
}

.preset-item {
  aspect-ratio: 1;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
}

.preset-item:hover {
  transform: scale(1.1);
  z-index: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.preset-item.active {
  border-color: var(--color-text);
  box-shadow: 0 0 0 2px var(--color-card), 0 0 0 4px var(--color-primary);
}

/* 自定义输入 */
.custom-section {
  margin-bottom: 16px;
}

.custom-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hash-prefix {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-secondary);
  font-family: monospace;
}

.custom-preview {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  flex-shrink: 0;
  transition: background-color 0.2s;
}

.error-text {
  display: block;
  color: var(--color-error);
  font-size: 11px;
  margin-top: 4px;
}

/* CSS 类名标签 */
.class-section {
  margin-bottom: 16px;
}

.class-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.class-tag {
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.class-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-alpha-10);
}

.class-tag.active {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}

/* 面板操作按钮 */
.panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}
</style>
