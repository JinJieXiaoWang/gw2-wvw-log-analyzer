<template>
  <div class="flex items-center gap-2 mb-4">
    <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="iconBg">
      <i :class="[icon, iconColor, 'text-sm']" />
    </div>
    <h4 class="text-neutral-text font-semibold">{{ title }}</h4>
    <div class="flex-1 h-px bg-neutral-border ml-2" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ icon: string; iconBg: string; iconColor: string; title: string }>()
</script>
