<template>
  <div class="flex items-start gap-3">
    <div class="p-3 bg-red-500/20 rounded-xl"><SvgIcon icon="swords" :size="24" class="text-red-400" /></div>
    <div class="flex-1">
      <h3 class="font-semibold text-white mb-1">分析最近战斗</h3>
      <p class="text-sm text-neutral-text-secondary">自动选择最新战斗日志</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface FightOption { id: string; name: string; date: string }
defineProps<{ recentFights: FightOption[]; recentPlayers: Array<{ name: string; profession: string }>; disabled: boolean }>()
defineEmits<{ 'analyze-fight': []; 'analyze-player': []; 'analyze-team': [] }>()
</script>
