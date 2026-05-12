<template>
  <div class="player-summary-view">
    <!-- 玩家选择 -->
    <div class="player-selector card">
      <div class="selector-header">
        <h3 class="selector-title">
          <i class="pi pi-user" />
          玩家详细统计
        </h3>
      </div>
      <div class="selector-list">
        <button
          v-for="player in players"
          :key="player.instanceID"
          class="player-btn"
          :class="{ active: selectedId === player.instanceID }"
          @click="selectPlayer(player.instanceID)"
        >
          <img
            :src="getProfIcon(player.profession)"
            class="btn-avatar"
            alt=""
          >
          <div class="btn-info">
            <span class="btn-name">{{ player.name }}</span>
            <span class="btn-prof">{{ getProfessionName(player.profession) }}</span>
          </div>
          <span class="btn-dps">{{ formatDamage(player.dps) }} DPS</span>
        </button>
      </div>
    </div>

    <!-- 选中玩家详情 -->
    <div
      v-if="selectedPlayer"
      class="player-detail card"
    >
      <div class="detail-header">
        <div class="detail-player-info">
          <img
            :src="getProfIcon(selectedPlayer.profession)"
            class="detail-avatar"
            alt=""
          >
          <div>
            <h3 class="detail-name">
              {{ selectedPlayer.name }}
            </h3>
            <span
              class="detail-prof-badge"
              :style="{ backgroundColor: getProfessionColor(selectedPlayer.profession) }"
            >
              {{ getProfessionName(selectedPlayer.profession) }}
            </span>
          </div>
        </div>
      </div>

      <div class="detail-stats">
        <div class="stat-group">
          <h4 class="group-title">
            <i class="pi pi-bolt" />
            伤害数据
          </h4>
          <div class="stat-items">
            <div class="stat-item">
              <span class="stat-label">总伤�?/span>
                <span class="stat-value">{{ formatDamage(getDps(selectedPlayer).damage) }}</span>
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">DPS</span>
              <span class="stat-value">{{ formatDamage(selectedPlayer.dps) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">直伤</span>
              <span class="stat-value">{{ formatDamage(getDps(selectedPlayer).powerDamage) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">症状</span>
              <span class="stat-value">{{ formatDamage(getDps(selectedPlayer).condiDamage) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">破控伤害</span>
              <span class="stat-value">{{ formatDamage(getDps(selectedPlayer).breakbarDamage) }}</span>
            </div>
          </div>
        </div>

        <div class="stat-group">
          <h4 class="group-title">
            <i class="pi pi-shield" />
            防御数据
          </h4>
          <div class="stat-items">
            <div class="stat-item">
              <span class="stat-label">承受伤害</span>
              <span class="stat-value">{{ formatDamage(getDefense(selectedPlayer).damageTaken) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">格挡</span>
              <span class="stat-value">{{ getDefense(selectedPlayer).blockedCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">闪避</span>
              <span class="stat-value">{{ getDefense(selectedPlayer).evadedCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">翻滚</span>
              <span class="stat-value">{{ getDefense(selectedPlayer).dodgeCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">屏障</span>
              <span class="stat-value">{{ formatDamage(getDefense(selectedPlayer).damageBarrier) }}</span>
            </div>
          </div>
        </div>

        <div class="stat-group">
          <h4 class="group-title">
            <i class="pi pi-sparkles" />
            表现数据
          </h4>
          <div class="stat-items">
            <div class="stat-item">
              <span class="stat-label">暴击�?/span>
                <span class="stat-value">{{ formatPercent(getStats(selectedPlayer).criticalRate) }}</span>
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">侧身�?/span>
                <span class="stat-value">{{ formatPercent(getStats(selectedPlayer).flankingRate) }}</span>
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">技能浪�?/span>
                <span class="stat-value">{{ getStats(selectedPlayer).wasted }}</span>
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">技能节�?/span>
                <span class="stat-value">{{ getStats(selectedPlayer).saved }}</span>
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">武器切换</span>
              <span class="stat-value">{{ getStats(selectedPlayer).swapCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Player, PlayerDps, PlayerDefense, PlayerStats } from '@/types/eliteInsights'
import { formatDamage, formatPercent } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  selectedPlayerId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null
})

const emit = defineEmits<{
  (e: 'select-player', id: number | null): void
}>()

const selectedId = ref<number | null>(props.selectedPlayerId)

const selectedPlayer = computed(() => {
  return props.players.find(p => p.instanceID === selectedId.value) || null
})

function selectPlayer(id: number) {
  selectedId.value = id
  emit('select-player', id)
}

function getDps(player: Player): PlayerDps {
  return player.dpsAll?.[0] || {
    dps: 0, damage: 0, condiDps: 0, condiDamage: 0,
    powerDps: 0, powerDamage: 0, breakbarDamage: 0,
    actorDps: 0, actorDamage: 0, actorCondiDps: 0,
    actorCondiDamage: 0, actorPowerDps: 0, actorPowerDamage: 0,
    actorBreakbarDamage: 0
  }
}

function getDefense(player: Player): PlayerDefense {
  return player.defenses?.[0] || {
    damageTaken: 0, downedDamageTaken: 0, breakbarDamageTaken: 0,
    blockedCount: 0, evadedCount: 0, missedCount: 0, dodgeCount: 0,
    invulnedCount: 0, damageBarrier: 0, interruptedCount: 0,
    downCount: 0, downDuration: 0, deadCount: 0, deadDuration: 0,
    dcCount: 0, dcDuration: 0, boonStrips: 0, boonStripsTime: 0,
    conditionCleanses: 0, conditionCleansesTime: 0
  }
}

function getStats(player: Player): PlayerStats {
  return player.statsAll?.[0] || {
    wasted: 0, timeWasted: 0, saved: 0, timeSaved: 0,
    stackDist: 0, distToCom: 0, avgBoons: 0, avgActiveBoons: 0,
    avgConditions: 0, avgActiveConditions: 0, swapCount: 0,
    skillCastUptime: 0, skillCastUptimeNoAA: 0, totalDamageCount: 0,
    totalDmg: 0, directDamageCount: 0, directDmg: 0,
    connectedDirectDamageCount: 0, connectedDirectDmg: 0,
    connectedDamageCount: 0, connectedDmg: 0,
    critableDirectDamageCount: 0, criticalRate: 0, criticalDmg: 0,
    flankingRate: 0, againstMovingRate: 0, glanceRate: 0,
    missed: 0, evaded: 0, blocked: 0, interrupts: 0, invulned: 0,
    killed: 0, downed: 0, downContribution: 0,
    connectedPowerCount: 0, connectedPowerAbove90HPCount: 0,
    connectedConditionCount: 0, connectedConditionAbove90HPCount: 0,
    againstDownedCount: 0, againstDownedDamage: 0
  }
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>


