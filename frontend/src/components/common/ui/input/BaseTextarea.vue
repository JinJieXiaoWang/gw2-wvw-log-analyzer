<template>
  <Textarea
    v-bind="$attrs"
    v-model="modelValue"
    class="w-full"
  />
</template>

<script setup lang="ts">
/**
 * BaseTextarea - 基础多行文本输入组件
 * 功能：对 PrimeVue Textarea 的封装
 */
import Textarea from 'primevue/textarea'

const modelValue = defineModel<string | null>()
</script>
