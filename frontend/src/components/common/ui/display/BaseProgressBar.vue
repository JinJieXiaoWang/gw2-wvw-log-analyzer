<script setup lang="ts">
/**
 * BaseProgressBar - 基础进度条组件
 * 功能：对 PrimeVue ProgressBar 的封装，支持透传所有原生 props
 */

import type { ProgressBarProps } from 'primevue/progressbar'
import ProgressBar from 'primevue/progressbar'

interface Props extends /* @vue-ignore */ ProgressBarProps {
  value: number
}

defineProps<Props>()
</script>

<template>
  <ProgressBar
    v-bind="$attrs"
    :value="value"
  />
</template>
