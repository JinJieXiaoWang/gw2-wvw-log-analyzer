<template>
  <div class="mb-6">
    <h4 class="text-sm font-bold text-neutral-text-secondary mb-3 uppercase tracking-wider">
      {{ title }}
    </h4>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>
