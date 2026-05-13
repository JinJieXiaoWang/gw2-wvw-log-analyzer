<template>
  <div class="card relative overflow-hidden">
    <!-- 装饰性背景 -->
    <div class="deco-bg-ai" />

    <div class="relative z-10">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-ai/20 to-primary/10 flex items-center justify-center border border-ai/20">
          <i class="pi pi-palette text-ai text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            界面主题设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            自定义系统外观与视觉风格
          </p>
        </div>
      </div>

      <div class="space-y-8">
        <!-- 主题模式 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <i class="pi pi-moon text-primary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              主题模式
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div
              class="theme-mode-card group"
              :class="localThemeSettings.mode === 'dark' ? 'theme-mode-active' : 'theme-mode-inactive'"
              @click="localThemeSettings.mode = 'dark'"
            >
              <div
                v-if="localThemeSettings.mode === 'dark'"
                class="theme-check-badge"
              >
                <i class="pi pi-check text-white text-[10px]" />
              </div>
              <div class="theme-icon-box">
                <i class="pi pi-moon text-primary text-2xl" />
              </div>
              <p class="text-sm font-semibold text-neutral-text text-center">
                深色模式
              </p>
              <p class="text-xs text-neutral-text-secondary text-center mt-1">
                适合夜间使用
              </p>
            </div>
            <div
              class="theme-mode-card group"
              :class="localThemeSettings.mode === 'light' ? 'theme-mode-active' : 'theme-mode-inactive'"
              @click="localThemeSettings.mode = 'light'"
            >
              <div
                v-if="localThemeSettings.mode === 'light'"
                class="theme-check-badge"
              >
                <i class="pi pi-check text-white text-[10px]" />
              </div>
              <div class="theme-icon-box theme-icon-light">
                <i class="pi pi-sun text-yellow-500 text-2xl" />
              </div>
              <p class="text-sm font-semibold text-neutral-text text-center">
                浅色模式
              </p>
              <p class="text-xs text-neutral-text-secondary text-center mt-1">
                适合白天使用
              </p>
            </div>
          </div>
        </div>

        <!-- 主题色 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-ai/10 flex items-center justify-center">
              <i class="pi pi-sparkles text-ai text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              主题色
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="flex gap-4">
            <div
              v-for="color in themeColors"
              :key="color.id"
              class="theme-color-item group"
              @click="localThemeSettings.primaryColor = color.value"
            >
              <div
                class="theme-color-circle"
                :class="localThemeSettings.primaryColor === color.value ? 'theme-color-active' : 'theme-color-hover'"
                :style="{
                  backgroundColor: color.value,
                  boxShadow: localThemeSettings.primaryColor === color.value ? `0 0 20px ${color.value}50` : 'none'
                }"
              >
                <i
                  v-if="localThemeSettings.primaryColor === color.value"
                  class="pi pi-check text-white text-lg"
                />
              </div>
              <p class="text-xs text-neutral-text-secondary text-center mt-2 capitalize">
                {{ color.id }}
              </p>
            </div>
          </div>
        </div>

        <!-- 界面缩放 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-warning/10 flex items-center justify-center">
              <i class="pi pi-expand text-status-warning text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              界面缩放
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="bg-neutral-bg rounded-xl p-5 border border-neutral-border">
            <div class="flex items-center gap-4 mb-2">
              <span class="text-sm text-neutral-text-secondary w-10">80%</span>
              <BaseSlider
                v-model="localThemeSettings.zoom"
                :min="80"
                :max="120"
                class="flex-1"
                @change="applyZoom"
              />
              <span class="text-sm text-neutral-text-secondary w-10 text-right">120%</span>
            </div>
            <p class="text-sm text-neutral-text text-center mt-3 font-medium">
              当前缩放: <span class="text-primary">{{ localThemeSettings.zoom }}%</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 应用按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <BaseButton
          label="应用主题"
          icon="pi pi-check"
          severity="primary"
          @click="applyTheme"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 界面主题设置组件
 * 功能：显示和编辑界面主题设置
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSlider from '@/components/common/ui/input/BaseSlider.vue'
import { reactive, ref, watch } from 'vue'

interface Props {
  themeSettings: {
    mode: string
    primaryColor: string
    zoom: number
  }
  themeColors: Array<{
    id: string
    value: string
  }>
}

const props = withDefaults(defineProps<Props>(), {
  themeSettings: () => ({ mode: 'dark', primaryColor: '#165DFF', zoom: 100 }),
  themeColors: () => []
})

const emit = defineEmits<{
  'apply-theme': []
  'update:themeSettings': [themeSettings: Props['themeSettings']]
}>()

const localThemeSettings = reactive({ ...props.themeSettings })

watch(() => props.themeSettings, (val) => {
  Object.assign(localThemeSettings, val)
}, { deep: true })

watch(localThemeSettings, (val) => {
  emit('update:themeSettings', { ...val })
}, { deep: true })

const isApplyingZoom = ref(false)

const applyZoom = () => {
  // 防抖处理缩放变化
  if (isApplyingZoom.value) return
  isApplyingZoom.value = true
  setTimeout(() => {
    document.documentElement.style.setProperty('--app-zoom', `${localThemeSettings.zoom}%`)
    isApplyingZoom.value = false
  }, 100)
}

const applyTheme = () => {
  emit('apply-theme')
}
</script>

<style scoped>
.deco-bg-ai {
  @apply absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30;
  background: radial-gradient(circle, var(--color-ai-alpha-10) 0%, transparent 70%);
}

.theme-mode-card {
  @apply relative p-5 bg-neutral-bg rounded-xl cursor-pointer border-2 transition-all duration-200;
}

.theme-mode-card:hover {
  @apply -translate-y-0.5;
}

.theme-mode-active {
  @apply border-primary shadow-lg shadow-primary/10;
}

.theme-mode-inactive {
  @apply border-transparent hover:border-neutral-border-light;
}

.theme-check-badge {
  @apply absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-primary flex items-center justify-center shadow-md;
}

.theme-icon-box {
  @apply w-14 h-14 rounded-xl bg-neutral-card border border-neutral-border flex items-center justify-center mx-auto mb-3 shadow-inner transition-transform duration-200 group-hover:scale-105;
}

.theme-icon-light {
  @apply bg-white;
}

.theme-color-item {
  @apply relative cursor-pointer transition-all duration-200;
}

.theme-color-circle {
  @apply w-14 h-14 rounded-2xl transition-all duration-200 flex items-center justify-center;
}

.theme-color-active {
  @apply scale-110 shadow-lg;
}

.theme-color-hover {
  @apply hover:scale-105;
}
</style>
