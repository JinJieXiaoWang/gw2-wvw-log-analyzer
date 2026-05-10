<template>
  <InputNumber v-bind="$attrs" v-model="modelValue" />
</template>

<script setup lang="ts">
/**
 * BaseInputNumber - 基础数字输入组件
 * 功能：对 PrimeVue InputNumber 的封装
 */
import InputNumber from 'primevue/inputnumber'

const modelValue = defineModel<number | null>()
</script>
