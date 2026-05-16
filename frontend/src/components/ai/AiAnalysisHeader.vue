<template>
  <div class="p-4 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-700/30 mb-4">
    <div class="flex items-start gap-3">
      <div class="p-2 bg-blue-500/20 rounded-lg">
        <SvgIcon icon="sparkles" :size="18" class="text-blue-400" />
      </div>
      <div>
        <p class="text-sm font-medium text-blue-300">{{ TOOLS_SMART_RECOMMEND }}</p>
        <p class="text-xs text-gray-400 mt-1">{{ TOOLS_SMART_RECOMMEND_HINT }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { TOOLS_SMART_RECOMMEND, TOOLS_SMART_RECOMMEND_HINT } from '@/constants/aiAnalysis'
</script>
