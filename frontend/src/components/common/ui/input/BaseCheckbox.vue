<template>
  <Checkbox v-bind="$attrs" v-model="modelValue" />
</template>

<script setup lang="ts">
/**
 * BaseCheckbox - 基础复选框组件
 * 功能：对 PrimeVue Checkbox 的封装
 */
import Checkbox from 'primevue/checkbox'

const modelValue = defineModel<boolean | null>()
</script>
