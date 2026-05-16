<script setup lang="ts">
/**
 * BaseTextarea - 基础多行文本输入组件
 * 功能：对 PrimeVue Textarea 的封装
 */
import type { TextareaProps } from 'primevue/textarea';
import Textarea from 'primevue/textarea';

interface Props extends /* @vue-ignore */ TextareaProps {}

defineProps<Props>()
const modelValue = defineModel<string | null>()
</script>

<template>
  <Textarea
    v-bind="$attrs"
    v-model="modelValue"
    class="w-full"
  />
</template>
