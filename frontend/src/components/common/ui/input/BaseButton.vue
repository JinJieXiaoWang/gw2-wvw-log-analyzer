<template>
  <Button v-bind="$attrs">
    <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </Button>
</template>

<script setup lang="ts">
/**
 * BaseButton - 按钮基础封装组件
 * 功能：对PrimeVue Button 的基础封装，用于项目中按钮使用时传递的props / events / slots
 */
import Button from 'primevue/button'
</script>
