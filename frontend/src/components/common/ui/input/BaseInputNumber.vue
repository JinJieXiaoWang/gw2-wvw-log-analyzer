<script setup lang="ts">
/**
 * BaseInputNumber - 基础数字输入组件
 * 功能：对 PrimeVue InputNumber 的封装
 */
import type { InputNumberProps } from 'primevue/inputnumber'
import InputNumber from 'primevue/inputnumber'

interface Props extends /* @vue-ignore */ InputNumberProps {}

defineProps<Props>()
const modelValue = defineModel<number | null>()
</script>

<template>
  <InputNumber
    v-bind="$attrs"
    v-model="modelValue"
  />
</template>
