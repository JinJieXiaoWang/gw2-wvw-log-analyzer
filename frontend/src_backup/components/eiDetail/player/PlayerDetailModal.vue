<template>
  <div
    v-if="visible && player"
    class="modal-overlay"
    @click="emit('close')"
  >
    <div
      class="modal-content"
      @click.stop
    >
      <!-- 头部 -->
      <div class="modal-header">
        <div class="player-header-info">
          <img
            :src="getProfIcon(player.profession)"
            class="player-avatar"
          >
          <div class="player-details">
            <h3 class="player-name">
              {{ player.name }}
            </h3>
            <div class="player-meta">
              <span
                class="profession-badge"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >{{ getProfessionName(player.profession) }}</span>
              <span
                v-if="player.hasCommanderTag"
                class="commander-badge"
              >
                <i class="pi pi-star-fill" />
              </span>
            </div>
          </div>
        </div>
        <button
          class="modal-close-btn"
          @click="emit('close')"
        >
          <i class="pi pi-times" />
        </button>
      </div>

      <!-- 标签 -->
      <div class="modal-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- 内容 -->
      <div class="modal-body">
        <PlayerStatsTab
          v-if="activeTab === 'stats'"
          :player="player"
        />
        <PlayerRotationTab
          v-if="activeTab === 'rotation'"
          :player="player"
          :log-id="logId"
        />
        <PlayerSkillsTab
          v-if="activeTab === 'skills'"
          :player="player"
          :log-id="logId"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import PlayerStatsTab from '../tabs/PlayerStatsTab.vue'
import PlayerRotationTab from '../tabs/PlayerRotationTab.vue'
import PlayerSkillsTab from '../tabs/PlayerSkillsTab.vue'

interface Props {
  visible: boolean
  player: Player | null
  logId?: number
}

const { visible, player, logId } = defineProps<Props>()
const emit = defineEmits(['close'])

const tabs = [
  { key: 'stats', label: '战斗详情', icon: 'pi pi-user' },
  { key: 'rotation', label: '循环序列图', icon: 'pi pi-repeat' },
  { key: 'skills', label: '技能统计', icon: 'pi pi-bar-chart' },
]

const activeTab = ref('stats')

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}
.modal-content {
  background-color: var(--color-card);
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}
.player-header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.player-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
}
.player-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.player-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}
.player-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.profession-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
}
.commander-badge {
  color: #f59e0b;
  font-size: 1rem;
}
.modal-close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.modal-close-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}
.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
}
.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
}
.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-card-hover);
}
.tab-btn.active {
  color: var(--color-primary);
  background-color: var(--color-card);
}
.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background-color: var(--color-primary);
  border-radius: 1px;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (max-width: 640px) {
  .tab-btn span {
    display: none;
  }
}
</style>
