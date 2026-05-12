<template>
  <div class="card relative overflow-hidden">
    <!-- 装饰性背景 -->
    <div
      class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-primary-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative z-10">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 flex items-center justify-center border border-primary/20">
          <i class="pi pi-circle-on text-primary text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            水印设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            配置页面显示水印与截图水印内容
          </p>
        </div>
      </div>

      <div class="space-y-8">
        <!-- 页面水印 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <i class="pi pi-desktop text-primary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              页面水印
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="启用页面水印"
              description="在页面背景显示半透明倾斜水印，防止信息泄露"
              icon="pi pi-eye"
              icon-color="primary"
            >
              <InputSwitch v-model="localSettings.watermarkEnabled" />
            </SettingItem>

            <Transition name="fade">
              <div
                v-if="localSettings.watermarkEnabled"
                class="mt-3"
              >
                <div class="bg-neutral-bg rounded-xl p-4 border border-neutral-border">
                  <label class="block text-sm font-medium text-neutral-text mb-2">
                    水印内容
                  </label>
                  <BaseInput
                    v-model="localSettings.watermarkText"
                    placeholder="留空则默认显示系统名+日期"
                    maxlength="50"
                  />
                  <p class="text-xs text-neutral-text-secondary mt-1.5">
                    支持自定义文字，最多 50 个字符。留空时默认显示 "GW2-APEX + 当前日期"。
                  </p>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <!-- 截图水印 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center">
              <i class="pi pi-camera text-secondary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              截图水印
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="截图自动添加水印"
              description="使用本系统的截图导出功能时，自动在右下角叠加水印与时间戳"
              icon="pi pi-image"
              icon-color="secondary"
            >
              <InputSwitch v-model="localSettings.watermarkScreenshotEnabled" />
            </SettingItem>
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <BaseButton
          label="保存设置"
          icon="pi pi-check"
          severity="primary"
          @click="saveWatermarkSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 水印设置组件
 * 功能：显示和编辑页面水印、截图水印设置
 * 更新日期：2026-05-05
 */

import { reactive, watch } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import InputSwitch from 'primevue/inputswitch'
import SettingItem from '../SettingItem.vue'

interface WatermarkSettingsModel {
  watermarkEnabled: boolean
  watermarkText: string
  watermarkScreenshotEnabled: boolean
}

const props = defineProps<{
  watermarkSettings: WatermarkSettingsModel
}>()

const emit = defineEmits<{
  'save-watermark-settings': [settings: WatermarkSettingsModel]
}>()

const localSettings = reactive<WatermarkSettingsModel>({
  watermarkEnabled: props.watermarkSettings.watermarkEnabled,
  watermarkText: props.watermarkSettings.watermarkText,
  watermarkScreenshotEnabled: props.watermarkSettings.watermarkScreenshotEnabled
})

watch(
  () => props.watermarkSettings,
  (newVal) => {
    localSettings.watermarkEnabled = newVal.watermarkEnabled
    localSettings.watermarkText = newVal.watermarkText
    localSettings.watermarkScreenshotEnabled = newVal.watermarkScreenshotEnabled
  },
  { deep: true }
)

const saveWatermarkSettings = () => {
  emit('save-watermark-settings', { ...localSettings })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
