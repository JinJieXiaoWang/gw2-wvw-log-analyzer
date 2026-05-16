<script setup lang="ts">
/**
 * BaseRadioButton - 基础单选按钮组件
 * 功能：对 PrimeVue RadioButton 的封装，支持透传所有原生 props
 */

import type { RadioButtonProps } from 'primevue/radiobutton';
import RadioButton from 'primevue/radiobutton';

interface Props extends /* @vue-ignore */ RadioButtonProps {
  value: any
}

defineProps<Props>()
const modelValue = defineModel<any>()
</script>

<template>
  <RadioButton
    v-bind="$attrs"
    v-model="modelValue"
    :value="value"
  />
</template>
