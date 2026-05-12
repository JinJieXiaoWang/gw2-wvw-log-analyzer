<template>
  <div class="target-summary-view flex flex-col gap-6">
    <!-- 目标统计卡片 -->
    <div class="targets-grid grid grid-cols-[repeat(auto-fit, minmax(320px, 1fr))] gap-4">
      <TargetStatsCard
        v-for="target in targets"
        :key="target.instanceID"
        :targets="[target]"
      />
    </div>

    <!-- 目标伤害贡献 -->
    <div class="damage-contribution card bg-neutral-card rounded-xl overflow-hidden p-5">
      <div class="section-header mb-4">
        <h3 class="section-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
          <i class="pi pi-chart-bar text-[var(--color-error)]" />
          目标伤害贡献
        </h3>
      </div>
      <div class="contribution-list flex flex-col gap-4">
        <div
          v-for="target in targetsWithDamage"
          :key="target.instanceID"
          class="contribution-item p-4 bg-neutral-card-hover rounded-lg"
        >
          <div class="target-info-row flex items-center gap-3 mb-3">
            <img
              v-if="target.icon"
              :src="target.icon"
              class="target-icon-sm w-8 h-8 rounded-md"
              alt=""
            >
            <span class="target-name text-sm font-semibold text-neutral-text flex-1">{{ target.name }}</span>
            <span
              class="target-status-badge text-xs p-[0.25rem 0.5rem] rounded-full bg-green-500/[0.1] text-green-500"
              :class="{ dead: target.finalHealth === 0, 'bg-red-500/10 text-red-500': target.finalHealth === 0, 'bg-green-500/[0.1] text-green-500': target.finalHealth !== 0 }"
            >
              {{ target.finalHealth === 0 ? '已击杀' : '存活' }}
            </span>
          </div>
          <div class="damage-bar-row flex items-center gap-3 mb-3">
            <div class="damage-bar-track flex-1 h-2 border-neutral-border rounded-[4px] overflow-hidden">
              <div
                class="damage-bar-fill h-full bg-[linear-gradient(90deg, var(--color-error), var(--color-secondary))] rounded-[4px]"
                :style="{ width: getDamagePercent(target) + '%' }"
              />
            </div>
            <span class="damage-value text-sm font-semibold text-neutral-text w-20 text-right">{{ formatDamage(getTargetDamage(target)) }}</span>
          </div>
          <div class="player-contributions flex flex-wrap gap-3">
            <div
              v-for="contrib in getTopContributors(target)"
              :key="contrib.playerId"
              class="contrib-player flex items-center gap-1.5 p-[0.375rem 0.625rem] bg-neutral-bg rounded-md text-[0.8125rem]"
            >
              <span
                class="contrib-dot w-2 h-2 rounded-full"
                :style="{ backgroundColor: contrib.color }"
              />
              <span class="contrib-name text-neutral-text">{{ contrib.name }}</span>
              <span class="contrib-dmg text-neutral-text-secondary font-medium">{{ formatDamage(contrib.damage) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, Target } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import TargetStatsCard from './TargetStatsCard.vue'

interface Props {
  targets: Target[]
  players: Player[]
}

const props = defineProps<Props>()

const targetsWithDamage = computed(() => {
  return [...props.targets].sort((a, b) => getTargetDamage(b) - getTargetDamage(a))
})

const maxTargetDamage = computed(() => {
  return Math.max(...props.targets.map(t => getTargetDamage(t)), 1)
})

function getTargetDamage(target: Target): number {
  return target.dpsAll?.[0]?.damage || target.statsAll?.[0]?.totalDmg || 0
}

function getDamagePercent(target: Target): number {
  return (getTargetDamage(target) / maxTargetDamage.value) * 100
}

function getTopContributors(target: Target) {
  const contributors = props.players.slice(0, 3).map(p => ({
    playerId: p.instanceID,
    name: p.name,
    damage: Math.floor(getTargetDamage(target) * (0.4 - props.players.indexOf(p) * 0.1)),
    color: getProfessionColor(p.profession)
  }))
  return contributors.sort((a, b) => b.damage - a.damage)
}
</script>


