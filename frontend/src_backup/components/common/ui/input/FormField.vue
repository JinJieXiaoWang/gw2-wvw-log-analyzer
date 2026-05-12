<template>
  <div v-bind="$attrs">
    <label class="block text-sm font-medium text-neutral-text mb-2">
      <slot name="label">
        {{ label }} <span
          v-if="required"
          class="text-red-500"
        >*</span>
      </slot>
    </label>
    <slot />
    <p
      v-if="hint && !error"
      class="mt-1 text-xs text-neutral-text-secondary"
    >
      {{ hint }}
    </p>
    <p
      v-if="error"
      class="mt-1 text-sm text-red-500"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  required?: boolean
  error?: string
  hint?: string
}>()
</script>
