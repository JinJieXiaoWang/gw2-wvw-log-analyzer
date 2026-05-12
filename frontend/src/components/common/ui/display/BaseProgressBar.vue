<template>
  <ProgressBar v-bind="$attrs" :value="value" />
</template>

<script setup lang="ts">
/**
 * BaseProgressBar - 基础进度条组件
 * 功能：对 PrimeVue ProgressBar 的封装
 */
import ProgressBar from 'primevue/progressbar'

interface Props {
  value: number
}

defineProps<Props>()
</script>
