<script setup lang="ts">
import type { SelectProps } from 'primevue/select';
import Select from 'primevue/select';

interface Props extends /* @vue-ignore */ SelectProps {}

defineProps<Props>()
const modelValue = defineModel<any>()
</script>

<template>
  <Select
    v-bind="$attrs"
    v-model="modelValue"
  >
    <template
      v-for="(_, name) in $slots"
      :key="name"
      #[name]="slotData"
    >
      <slot
        :name="name"
        v-bind="slotData || {}"
      />
    </template>
  </Select>
</template>
