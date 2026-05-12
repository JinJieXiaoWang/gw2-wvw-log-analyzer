<template>
  <div
    v-if="visible"
    class="player-detail-overlay"
    @click.self="$emit('close')"
  >
    <div class="player-detail-sidebar">
      <div class="sidebar-header">
        <div class="header-left">
          <div class="player-avatar">
            <img
              :src="getProfIcon(player.profession)"
              :alt="player.profession"
            >
          </div>
          <div class="player-info">
            <div class="player-name">
              {{ player.name }}
              <span
                v-if="player.hasCommanderTag"
                class="commander-badge"
              ><i class="pi pi-star-fill" /></span>
            </div>
            <div class="player-account">
              {{ player.account }}
            </div>
          </div>
        </div>
        <button
          class="close-btn"
          @click="$emit('close')"
        >
          <i class="pi pi-times" />
        </button>
      </div>

      <PlayerSidebarContent :player="player" />

      <div class="sidebar-footer">
        <BaseButton
          label="查看完整技能循环"
          icon="pi pi-external-link"
          class="w-full"
          :disabled="true"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionIconUrl } from '@/utils/profession/professionUtils'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import PlayerSidebarContent from './PlayerSidebarContent.vue'

const { visible, player } = defineProps<{
  visible: boolean
  player: Player
}>()

defineEmits(['close'])

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>


