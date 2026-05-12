<template>
  <div
    v-if="visible && player"
    class="modal-overlay fixed top-0 left-0 right-0 bottom-0 bg-black/[0.6] flex items-center justify-center z-[1000] p-4"
    @click="emit('close')"
  >
    <div
      class="modal-content bg-neutral-card rounded-2xl w-full max-w-[600px] max-h-[90vh] overflow-hidden flex flex-col"
      @click.stop
    >
      <!-- 头部 -->
      <div class="modal-header flex items-center justify-between p-5 bg-neutral-card-hover">
        <div class="player-header-info flex items-center gap-4">
          <img
            :src="getProfIcon(player.profession)"
            class="player-avatar w-14 h-14 rounded-full"
          >
          <div class="player-details flex flex-col gap-2">
            <h3 class="player-name text-xl font-semibold text-neutral-text m-0">
              {{ player.name }}
            </h3>
            <div class="player-meta flex items-center gap-2">
              <span
                class="profession-badge p-[0.25rem 0.75rem] rounded-md text-[0.8125rem] font-medium text-white"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >{{ getProfessionName(player.profession) }}</span>
              <span
                v-if="player.hasCommanderTag"
                class="commander-badge text-amber-500 text-base"
              >
                <i class="pi pi-star-fill" />
              </span>
            </div>
          </div>
        </div>
        <button
          class="modal-close-btn w-9 h-9 flex items-center justify-center bg-transparent rounded-md text-neutral-text-secondary cursor-pointer hover:bg-neutral-border hover:text-neutral-text"
          @click="emit('close')"
        >
          <i class="pi pi-times" />
        </button>
      </div>

      <!-- 标签 -->
      <div class="modal-tabs flex bg-neutral-bg-secondary">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn flex-1 flex items-center justify-center gap-2 p-[0.875rem 1rem] bg-transparent text-neutral-text-secondary text-sm font-medium cursor-pointer relative hover:text-neutral-text hover:bg-neutral-card-hover"
          :class="{ 'text-neutral-primary bg-neutral-card': activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon" />
          <span class="max-sm:hidden">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 内容 -->
      <div class="modal-body p-5 overflow-y-auto flex-1">
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
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
