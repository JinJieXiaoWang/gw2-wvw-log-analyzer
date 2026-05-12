<!-- TODO[PrimeVue]: 可使用PrimeVue Message 组件替代-->
<template>
  <div
    class="flex flex-col items-center justify-center py-12 px-4 text-center gap-3"
    role="status"
    aria-live="polite"
    v-bind="$attrs"
  >
    <div class="text-6xl text-neutral-text-secondary opacity-50 mb-2">
      <i
        :class="icon"
        aria-hidden="true"
      />
    </div>
    <h3 class="text-neutral-text text-lg font-semibold m-0">
      {{ title }}
    </h3>
    <p
      v-if="description"
      class="text-neutral-text-secondary text-sm max-w-xs m-0"
    >
      {{ description }}
    </p>
    <div class="flex items-center justify-center gap-3 mt-3">
      <slot name="actions">
        <BaseButton
          v-if="showAction"
          :label="actionText"
          :icon="actionIcon"
          :outlined="actionOutlined"
          @click="$emit('action')"
        />
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 空状态组件
 * 功能：展示数据为空时的提示信息
 * 创建时间：2026-04-27
 * 更新时间：2026-05-10 - 增强无障碍支持 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'

interface Props {
  icon?: string
  title?: string
  description?: string
  showAction?: boolean
  actionText?: string
  actionIcon?: string
  actionOutlined?: boolean
  actionButtonClass?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'pi pi-inbox',
  title: '暂无数据',
  description: '',
  showAction: false,
  actionText: '添加数据',
  actionIcon: '',
  actionOutlined: false
})

defineEmits(['action'])
</script>
