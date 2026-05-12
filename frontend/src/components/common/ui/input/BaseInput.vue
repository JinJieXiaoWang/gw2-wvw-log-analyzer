<template>
  <InputText v-bind="$attrs" v-model="modelValue" class="w-full" />
</template>

<script setup lang="ts">
/**
 * BaseInput - 基础文本输入组件
 * 功能：对 PrimeVue InputText 的封装，提供项目统一的输入框样式
 */
import InputText from 'primevue/inputtext'

const modelValue = defineModel<string | null | undefined>()
</script>
