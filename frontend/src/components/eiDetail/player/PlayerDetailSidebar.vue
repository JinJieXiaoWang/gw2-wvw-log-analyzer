<template>
  <div
    v-if="visible"
    class="player-detail-overlay"
    @click.self="$emit('close')"
  >
    <div class="player-detail-sidebar">
      <PlayerSidebarHeader
        :player="player"
        @close="$emit('close')"
      />

      <PlayerSidebarContent :player="player" />

      <PlayerSidebarFooter />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';
import PlayerSidebarContent from './PlayerSidebarContent.vue';
import PlayerSidebarFooter from './PlayerSidebarFooter.vue';
import PlayerSidebarHeader from './PlayerSidebarHeader.vue';

interface Props {
  visible: boolean
  player: Player
}

defineProps<Props>()

defineEmits<{
  (e: 'close'): void
}>()
</script>

<style scoped lang="css">
.player-detail-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.player-detail-sidebar {
  width: 400px;
  height: 100%;
  background-color: var(--color-card);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>
