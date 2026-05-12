<template>
  <div class="target-stats-card bg-neutral-card rounded-xl p-5 flex gap-6">
    <div class="card-header mb-4">
      <div class="header-title flex items-center gap-2 text-base font-semibold text-neutral-text">
        <i class="pi pi-crosshair" />
        <span>目标统计</span>
      </div>
    </div>

    <div class="target-list flex flex-col gap-3.5">
      <div
        v-for="target in targets"
        :key="target.instanceID"
        class="target-item p-3.5 bg-neutral-card-hover rounded-lg"
      >
        <div class="target-header flex items-center gap-3 mb-3">
          <img
            :src="target.icon"
            class="target-icon w-10 h-10 rounded-lg bg-neutral-card-hover"
          >
          <div class="target-info flex-1 flex flex-col gap-1">
            <span class="target-name text-sm font-semibold text-neutral-text">{{ target.name }}</span>
            <span class="target-meta text-[0.7rem]">
              <span
                v-if="target.enemyPlayer"
                class="player-tag p-[0.125rem 0.375rem] bg-red-500/[0.1] text-red-500 rounded-full"
              >敌方玩家</span>
              <span
                v-else
                class="npc-tag p-[0.125rem 0.375rem] bg-slate-400/[0.1] text-slate-400 rounded-full"
              >NPC</span>
            </span>
          </div>
          <div
            class="target-status w-8 h-8 flex items-center justify-center rounded-full bg-green-500/[0.1] text-green-500"
            :class="{ 'bg-red-500/[0.1] text-red-500': target.finalHealth === 0 }"
          >
            <i
              class="pi"
              :class="target.finalHealth === 0 ? 'pi-skull' : 'pi-heart'"
            />
          </div>
        </div>
        <div class="target-stats flex gap-6">
          <div class="stat-item flex flex-col gap-1">
            <span class="label">伤害承受</span>
            <span class="value">{{ formatDamage(getTargetDamageTaken(target)) }}</span>
          </div>
          <div class="stat-item flex flex-col gap-1">
            <span class="label">存活时间</span>
            <span class="value">{{ formatDuration(target.lastAware - target.firstAware) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Target } from '@/types/eliteInsights'
import { formatDamage, formatDuration } from '@/types/eliteInsights'

interface Props {
  targets: Target[]
}

defineProps<Props>()

function getTargetDamageTaken(target: Target): number {
  return target.statsAll?.[0]?.totalDmg || 0
}
</script>

<style scoped lang="css">
.header-title i {
  color: var(--color-accent);
}
.stat-item .label {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
.stat-item .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>