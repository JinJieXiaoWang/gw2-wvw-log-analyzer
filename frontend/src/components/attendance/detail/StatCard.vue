<template>
  <div :class="['p-4 bg-gradient-to-br', gradient, 'border', border, 'rounded-xl', 'transition-all', 'duration-300', 'hover:scale-[1.02]', 'hover:shadow-lg']">
    <div class="flex items-center gap-3">
      <div :class="['w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center', iconBg, 'transition-transform', 'duration-300', 'hover:scale-110']">
        <i :class="['text-lg', icon, textColor]" />
      </div>
      <div>
        <p class="text-xs text-neutral-text-secondary mb-1">
          {{ label }}
        </p>
        <div class="flex items-baseline gap-1">
          <span class="text-2xl font-bold">{{ value }}</span>
          <span
            v-if="unit"
            class="text-sm text-neutral-text-secondary"
          >{{ unit }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string
  label: string
  value: string | number
  unit?: string
  gradient: string
  border: string
  iconBg: string
  textColor: string
}>()
</script>