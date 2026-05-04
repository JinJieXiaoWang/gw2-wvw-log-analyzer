<template>
  <div class="card">
    <!-- 装饰性背景 -->
    <div class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-success-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-success/20 to-primary/10 flex items-center justify-center border border-success/20">
          <i class="pi pi-file-export text-status-success text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            导出格式设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            配置数据导出的默认格式和选项
          </p>
        </div>
      </div>

      <div class="space-y-8">
        <!-- 默认导出格式 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <i class="pi pi-file text-primary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              默认导出格式
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div
              v-for="format in exportFormats"
              :key="format.id"
              class="group relative p-4 bg-neutral-bg rounded-xl cursor-pointer text-center border-2 transition-all duration-200 hover:-translate-y-0.5"
              :class="exportSettings.defaultFormat === format.id
                ? 'border-primary shadow-lg shadow-primary/10'
                : 'border-transparent hover:border-neutral-border-light'"
              @click="exportSettings.defaultFormat = format.id"
            >
              <!-- 选中指示器 -->
              <div
                v-if="exportSettings.defaultFormat === format.id"
                class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-primary flex items-center justify-center shadow-md"
              >
                <i class="pi pi-check text-white text-[10px]" />
              </div>
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-2 transition-all duration-200"
                :class="exportSettings.defaultFormat === format.id ? 'bg-primary/15' : 'bg-neutral-card group-hover:bg-primary/5'"
              >
                <i
                  :class="format.icon"
                  class="text-xl transition-colors duration-200"
                  :style="{ color: format.color }"
                />
              </div>
              <p class="text-sm font-medium text-neutral-text">
                {{ format.label }}
              </p>
            </div>
          </div>
        </div>

        <!-- CSV 导出选项 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center">
              <i class="pi pi-cog text-secondary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              CSV 导出选项
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="包含表头"
              description="导出时包含列标题行"
              icon="pi pi-table"
              icon-color="primary"
            >
              <InputSwitch v-model="exportSettings.includeHeader" />
            </SettingItem>
            <SettingItem
              title="UTF-8 编码"
              description="使用 UTF-8 编码确保中文正确显示"
              icon="pi pi-language"
              icon-color="secondary"
            >
              <InputSwitch v-model="exportSettings.utf8Encoding" />
            </SettingItem>
          </div>
        </div>

        <!-- 数值格式 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-info/10 flex items-center justify-center">
              <i class="pi pi-hashtag text-status-info text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              数值格式
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="max-w-sm">
            <Dropdown
              v-model="exportSettings.numberFormat"
              :options="numberFormatOptions"
              option-label="label"
              option-value="value"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <Button
          label="保存设置"
          icon="pi pi-check"
          severity="primary"
          @click="saveExportSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 导出格式设置组件
 * 功能：显示和编辑导出格式设置
 * 更新日期：2026-05-04
 */

import Button from 'primevue/button'
import InputSwitch from 'primevue/inputswitch'
import Dropdown from 'primevue/dropdown'
import SettingItem from './SettingItem.vue'

defineProps<{
  exportSettings: {
    defaultFormat: string
    includeHeader: boolean
    utf8Encoding: boolean
    numberFormat: string
  }
  exportFormats: Array<{
    id: string
    label: string
    icon: string
    color: string
  }>
  numberFormatOptions: Array<{
    label: string
    value: string
  }>
}>()

const emit = defineEmits<{
  'save-export-settings': []
}>()

const saveExportSettings = () => {
  emit('save-export-settings')
}
</script>
