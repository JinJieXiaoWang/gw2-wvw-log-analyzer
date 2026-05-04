<template>
  <div
    class="card hover:border-primary/50 transition-colors cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-start gap-4">
      <div
        class="w-12 h-12 rounded-xl flex items-center justify-center"
        :class="iconBgColor"
      >
        <i
          :class="icon"
          :style="{ color: iconColor }"
        />
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="text-neutral-text font-medium mb-1">
          {{ title }}
        </h4>
        <p class="text-sm text-neutral-text-secondary truncate">
          {{ description }}
        </p>
      </div>
      <i class="pi pi-chevron-right text-neutral-text-disabled" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  icon: string
  iconColor?: string
  iconBgColor?: string
  title: string
  description: string
}>()

defineEmits<{
  click: []
}>()

const iconBgColor = computed(() => props.iconBgColor || 'bg-primary/10')
const iconColor = computed(() => props.iconColor || 'text-primary')
</script>
