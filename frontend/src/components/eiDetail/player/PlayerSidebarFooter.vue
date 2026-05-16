<template>
  <div class="sidebar-footer">
    <BaseButton
      label="查看完整技能循环"
      icon="pi pi-external-link"
      class="w-full"
      :disabled="true"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue';
</script>

<style scoped lang="css">
.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
}
</style>
