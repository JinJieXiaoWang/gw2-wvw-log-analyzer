<template>
  <div class="bg-neutral-card rounded-lg border border-neutral-border overflow-hidden">
    <div class="p-4 border-b border-neutral-border">
      <slot name="header">
        <h3 class="text-lg font-semibold text-neutral-text">
          {{ title }}
        </h3>
        <p
          v-if="subtitle"
          class="text-sm text-neutral-text-secondary"
        >
          {{ subtitle }}
        </p>
      </slot>
    </div>
    <div class="p-4">
      <slot />
    </div>
    <div
      v-if="$slots.footer"
      class="p-4 border-t border-neutral-border"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
}>()
</script>
