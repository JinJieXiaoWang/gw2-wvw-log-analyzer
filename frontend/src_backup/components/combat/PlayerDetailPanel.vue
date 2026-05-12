<template>
  <Dialog
    :visible="visible"
    :header="headerTitle"
    :style="{ width: '900px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
    :resizable="true"
    class="player-detail-dialog"
    @hide="emit('update:visible', false)"
  >
    <div
      v-if="player"
      class="space-y-5"
    >
      <PlayerDetailHeader :player="player" />
      <LoadingState
        v-if="loading"
        text="加载技能数据中..."
      />
      <PlayerDetailRotation
        v-else-if="rotation"
        :rotation="rotation"
        :events="events"
        :fight-duration="fightDuration"
        :loading="loading"
        @refresh="emit('refresh')"
      />
      <BaseState
        v-else
        icon="pi pi-file-text"
        title="该日志未生成技能循环数据"
        description="请重新解析日志以获取技能详情"
      />
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import BaseState from '@/components/common/ui/display/BaseState.vue'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import PlayerDetailHeader from './PlayerDetailHeader.vue'
import PlayerDetailRotation from './PlayerDetailRotation.vue'
import type { EiAnalysisPlayer, PlayerRotationData } from '@/services/ei/eiAnalysisService'

const props = defineProps<{
  visible: boolean
  player: EiAnalysisPlayer | null
  rotation: PlayerRotationData | null
  events: any[]
  fightDuration: number
  loading: boolean
}>()

const emit = defineEmits<{ (e: 'update:visible', value: boolean): void; (e: 'refresh'): void }>()

const headerTitle = computed(() => props.player?.character_name || props.player?.account || '玩家详情')
</script>

<style scoped>
@import '@/styles/components/combat/PlayerDetailPanel.css';
</style>
