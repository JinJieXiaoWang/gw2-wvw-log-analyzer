<template>
  <div class="stat-item">
    <div
      class="stat-icon"
      :style="{ borderColor: color, backgroundColor: color + '20' }"
    >
      <div
        class="stat-value"
        :style="{ color: color }"
      >
        {{ value }}
      </div>
    </div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
/**
 * 属性统计项组件
 * 功能：展示单个属性的数值
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

defineProps<{
  label: string;
  value: number;
  color: string;
}>();
</script>

<style scoped lang="postcss">
.stat-item {
  @apply flex flex-col items-center gap-2 p-4 bg-neutral-800 rounded-xl;
}

.stat-icon {
  @apply w-14 h-14 rounded-full flex items-center justify-center border-2;
}

.stat-value {
  @apply text-xl font-bold;
}

.stat-label {
  @apply text-sm text-neutral-text-secondary;
}
</style>