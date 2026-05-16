<script setup lang="ts">
/**
 * BaseProgressSpinner - 基础加载动画组件
 * 功能：对 PrimeVue ProgressSpinner 的封装
 */
import type { ProgressSpinnerProps } from 'primevue/progressspinner';
import ProgressSpinner from 'primevue/progressspinner';

interface Props extends /* @vue-ignore */ ProgressSpinnerProps {}

defineProps<Props>()
</script>

<template>
  <ProgressSpinner v-bind="$attrs" />
</template>
