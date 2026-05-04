<template>
  <div class="flex flex-col items-center justify-center py-10 px-4 gap-4">
    <div class="text-primary">
      <i
        class="pi pi-spin pi-spinner"
        :style="{ fontSize: `${size}px` }"
      />
    </div>
    <p
      v-if="text"
      class="text-neutral-text-secondary text-sm m-0"
    >
      {{ text }}
    </p>
  </div>
</template>

<script setup lang="ts">
/**
 * 加载状态组件
 * 功能：展示数据加载中的状态
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

interface Props {
  text?: string
  size?: number
}

withDefaults(defineProps<Props>(), {
  text: '',
  size: 32
})
</script>
