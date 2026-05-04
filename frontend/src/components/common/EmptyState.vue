<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center gap-3">
    <div class="text-6xl text-neutral-text-secondary opacity-50 mb-2">
      <i :class="icon" />
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
        <Button 
          v-if="showAction" 
          :label="actionText" 
          class="btn-game"
          @click="$emit('action')"
        />
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 空状态组件
 * 功能：展示数据为空的状态
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import Button from 'primevue/button'

interface Props {
  icon?: string
  title?: string
  description?: string
  showAction?: boolean
  actionText?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'pi pi-inbox',
  title: '暂无数据',
  description: '',
  showAction: false,
  actionText: '添加数据'
})

defineEmits(['action'])
</script>
