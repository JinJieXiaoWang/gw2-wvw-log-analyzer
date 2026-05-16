<template>
  <div>
    <h3 class="text-lg font-semibold text-white mb-2">快速操作</h3>
    <p class="text-sm text-neutral-text-tertiary mb-4">快速分析最近的战斗或玩家数据</p>
    <div class="flex flex-wrap gap-3">
      <BaseButton
        icon="pi pi-bolt"
        label="分析最新战斗"
        size="small"
        :disabled="disabled || !recentFights.length"
        @click="$emit('analyze-fight')"
      />
      <BaseButton
        icon="pi pi-user"
        label="分析最近玩家"
        size="small"
        :disabled="disabled || !recentPlayers.length"
        @click="$emit('analyze-player')"
      />
      <BaseButton
        icon="pi pi-users"
        label="分析团队协同"
        size="small"
        :disabled="disabled || !recentFights.length"
        @click="$emit('analyze-team')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

interface Props {
  recentFights: { id: string; name: string; date: string }[]
  recentPlayers: { id: string; name: string; profession: string }[]
  recentBuilds: { id: string; name: string; profession: string }[]
  disabled: boolean
}

defineProps<Props>()

defineEmits<{
  'analyze-fight': []
  'analyze-player': []
  'analyze-team': []
}>()
</script>

<script lang="ts">
export default { name: 'AiQuickActions' }
</script>
