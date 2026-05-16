<template>
  <div class="sidebar-content">
    <PlayerSidebarBasicInfo :player="player" />
    <PlayerSidebarDamageStats :player="player" />
    <PlayerSidebarSurvivalStats :player="player" />
    <PlayerSidebarSupportStats :player="player" />
    <PlayerSidebarScoreDetails :player="player" />
    <PlayerSidebarBoonList :player="player" />
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';
import PlayerSidebarBasicInfo from './PlayerSidebarBasicInfo.vue';
import PlayerSidebarBoonList from './PlayerSidebarBoonList.vue';
import PlayerSidebarDamageStats from './PlayerSidebarDamageStats.vue';
import PlayerSidebarScoreDetails from './PlayerSidebarScoreDetails.vue';
import PlayerSidebarSupportStats from './PlayerSidebarSupportStats.vue';
import PlayerSidebarSurvivalStats from './PlayerSidebarSurvivalStats.vue';

interface Props {
  player: Player
}

defineProps<Props>()
</script>

<style scoped lang="css">
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
</style>
