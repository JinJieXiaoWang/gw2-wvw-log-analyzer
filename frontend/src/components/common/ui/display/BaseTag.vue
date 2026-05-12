<template>
  <Tag
    v-bind="$attrs"
    :value="value"
    :severity="severity"
    :icon="icon"
  />
</template>

<script setup lang="ts">
/**
 * BaseTag - 基础标签组件
 * 功能：对 PrimeVue Tag 的封装，支持透传所有原生 props
 */

import Tag from 'primevue/tag'

defineProps<{
  value?: string
  severity?: string
  icon?: string
}>()
</script>
