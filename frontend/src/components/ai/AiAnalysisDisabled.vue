<template>
  <div class="text-center py-8 px-4">
    <div class="inline-flex items-center justify-center p-4 bg-yellow-500/20 rounded-xl mb-4">
      <SvgIcon icon="lock" :size="40" class="text-yellow-400 opacity-80" />
    </div>
    <p class="text-yellow-400 font-medium">{{ TOOLS_CONFIG_REQUIRED }}</p>
    <p class="text-gray-500 text-sm mt-2">{{ TOOLS_CONFIG_HINT }}</p>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { TOOLS_CONFIG_REQUIRED, TOOLS_CONFIG_HINT } from '@/constants/aiAnalysis'
</script>
