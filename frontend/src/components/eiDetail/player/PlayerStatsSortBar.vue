<template>
  <div class="sort-selector">
    <span class="label">排序:</span>
    <Button
      v-for="sort in sortOptions"
      :key="sort.key"
      size="small"
      :outlined="modelValue !== sort.key"
      :label="sort.label"
      @click="$emit('update:modelValue', sort.key)"
    />
  </div>
</template>

<script setup lang="ts">
interface SortOption {
  key: string
  label: string
}

defineProps<{
  modelValue: string
  sortOptions: SortOption[]
}>()

defineEmits<{
  (e: 'update:modelValue', key: string): void
}>()
</script>

<style scoped lang="css">
.sort-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.sort-selector .label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
