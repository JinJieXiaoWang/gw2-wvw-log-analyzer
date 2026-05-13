<script setup lang="ts">
/**
 * BaseInput - 基础文本输入组件
 * 功能：对 PrimeVue InputText 的封装，提供项目统一的输入框样式
 */
import type { InputTextProps } from 'primevue/inputtext'
import InputText from 'primevue/inputtext'

interface Props extends /* @vue-ignore */ InputTextProps {}

const props = defineProps<Props>()
const modelValue = defineModel<string | null | undefined>()
</script>

<template>
  <InputText
    v-bind="$attrs"
    v-model="modelValue"
    class="w-full"
  />
</template>
