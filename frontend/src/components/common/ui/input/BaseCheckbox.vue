<script setup lang="ts">
/**
 * BaseCheckbox - 基础复选框组件
 * 功能：对 PrimeVue Checkbox 的封装
 */
import type { CheckboxProps } from 'primevue/checkbox';
import Checkbox from 'primevue/checkbox';

interface Props extends /* @vue-ignore */ CheckboxProps {}

defineProps<Props>()
const modelValue = defineModel<boolean | null>()
</script>

<template>
  <Checkbox
    v-bind="$attrs"
    v-model="modelValue"
  />
</template>
