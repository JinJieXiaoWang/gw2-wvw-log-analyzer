<template>
  <Select v-bind="$attrs" v-model="modelValue">
    <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
      <slot :name="name" v-bind="slotData || {}" />
    </template>
  </Select>
</template>

<script setup lang="ts">
import Select from 'primevue/select'

const modelValue = defineModel<any>()
</script>
