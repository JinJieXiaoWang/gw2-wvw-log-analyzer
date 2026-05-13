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
import BaseButton from '@/components/common/ui/input/BaseButton.vue';
import type { Player } from '@/types/eliteInsights';
import { getProfessionIconUrl } from '@/utils/profession/professionUtils';
import PlayerSidebarContent from './PlayerSidebarContent.vue';

const { visible, player } = defineProps<{
  visible: boolean
  player: Player
}>()

defineEmits(['close'])

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
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

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: linear-gradient(180deg, var(--color-card) 0%, rgba(40,40,40,1) 100%);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.player-avatar {
  width: 56px;
  height: 56px;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  padding: 3px;
  flex-shrink: 0;
}

.player-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.commander-badge {
  color: var(--color-accent);
  font-size: 0.875rem;
}

.player-account {
  font-size: 0.75rem;
  color: var(--color-text-disabled);
  margin-top: 0.25rem;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.section-title i {
  color: var(--color-primary);
  font-size: 0.875rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.info-item .label {
  font-size: 0.7rem;
  color: var(--color-text-disabled);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.info-item .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.info-item .value.score {
  color: var(--color-primary);
  font-size: 1.125rem;
}

.damage-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.damage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 0.5rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.damage-item.primary {
  border-color: var(--color-primary-alpha-30);
  background-color: var(--color-primary-alpha-5);
}

.damage-item.power {
  border-color: rgba(239, 68, 68, 0.3);
  background-color: rgba(239, 68, 68, 0.05);
}

.damage-item.condi {
  border-color: rgba(34, 197, 94, 0.3);
  background-color: rgba(34, 197, 94, 0.05);
}

.damage-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.damage-item.power .damage-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.damage-item.condi .damage-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.damage-icon i {
  color: white;
  font-size: 1.25rem;
}

.damage-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.damage-label {
  font-size: 0.7rem;
  color: var(--color-text-disabled);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.damage-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text);
}

.total-damage {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--color-border);
}

.total-damage .value {
  font-weight: 700;
  color: var(--color-text);
  font-size: 0.875rem;
}

.survival-stats,
.support-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.survival-item,
.support-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.survival-item i,
.support-item i {
  font-size: 1.125rem;
  color: var(--color-primary);
}

.survival-item .label,
.support-item .label {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.survival-item .value,
.support-item .value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.score-row {
  display: flex;
  justify-content: space-between;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
}

.score-row .label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.score-row .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.boon-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 150px;
  overflow-y: auto;
}

.boon-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
  font-size: 0.75rem;
}

.boon-id {
  color: var(--color-text-secondary);
}

.boon-value {
  color: var(--color-text);
  font-weight: 500;
}

.empty-boons {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-disabled);
  padding: 1rem;
}

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
}

</style>
