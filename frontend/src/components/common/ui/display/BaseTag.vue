<template>
  <Tag v-bind="$attrs" :value="value" :severity="severity" :icon="icon" />
</template>

<script setup lang="ts">
import Tag from 'primevue/tag'

defineProps<{
  value?: string
  severity?: string
  icon?: string
}>()
</script>
