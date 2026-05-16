<template>
  <div class="card relative overflow-hidden">
    <!-- 装饰性背景 -->
    <div
      class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-secondary-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative z-10">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-secondary/20 to-primary/10 flex items-center justify-center border border-secondary/20">
          <i class="pi pi-sliders-h text-secondary text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            解析参数设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            配置日志解析的核心参数与计算规则
          </p>
        </div>
      </div>

      <div class="space-y-8">
        <!-- 伤害计算 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <i class="pi pi-calculator text-primary text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              伤害计算
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="包含 overkill 伤害"
              description="计算总伤害时包含过量伤害"
              icon="pi pi-calculator"
              icon-color="primary"
            >
              <InputSwitch v-model="localParsingSettings.includeOverkill" />
            </SettingItem>
            <SettingItem
              title="忽略 1 点伤害以下"
              description="过滤微小的伤害数据，减少噪声"
              icon="pi pi-filter"
              icon-color="secondary"
            >
              <InputSwitch v-model="localParsingSettings.ignoreSmallDamage" />
            </SettingItem>
          </div>
        </div>

        <!-- 时间设置 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-success/10 flex items-center justify-center">
              <i class="pi pi-clock text-status-success text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              时间设置
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="战斗开始前缓冲时间"
              description="加载数据时包含战斗开始前的秒数"
              icon="pi pi-history"
              icon-color="success"
            >
              <div class="flex items-center gap-2">
                <BaseInputNumber
                  v-model="localParsingSettings.preFightBuffer"
                  :min="0"
                  :max="30"
                  class="w-20"
                />
                <span class="text-neutral-text-secondary text-sm">秒</span>
              </div>
            </SettingItem>
          </div>
        </div>

        <!-- 技能分类 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-warning/10 flex items-center justify-center">
              <i class="pi pi-tags text-status-warning text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              技能分类
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="自动分类技能"
              description="根据技能类型自动分组，便于分析"
              icon="pi pi-sitemap"
              icon-color="warning"
            >
              <InputSwitch v-model="localParsingSettings.autoCategorizeSkills" />
            </SettingItem>
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <BaseButton
          label="保存设置"
          icon="pi pi-check"
          @click="saveParsingSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 解析参数设置组件
 * 功能：显示和编辑解析参数设置
 * 更新日期：2026-05-04
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import InputSwitch from 'primevue/inputswitch'
import SettingItem from '../SettingItem.vue'
import { reactive, watch } from 'vue'

interface ParsingSettings {
  includeOverkill: boolean
  ignoreSmallDamage: boolean
  preFightBuffer: number
  autoCategorizeSkills: boolean
}

const props = defineProps<{
  parsingSettings: ParsingSettings
}>()

const emit = defineEmits<{
  'save-parsing-settings': []
  'update:parsingSettings': [parsingSettings: ParsingSettings]
}>()

const localParsingSettings = reactive({ ...props.parsingSettings })

watch(() => props.parsingSettings, (val) => {
  Object.assign(localParsingSettings, val)
}, { deep: true })

watch(localParsingSettings, (val) => {
  emit('update:parsingSettings', { ...val })
}, { deep: true })

const saveParsingSettings = () => {
  emit('save-parsing-settings')
}
</script>
