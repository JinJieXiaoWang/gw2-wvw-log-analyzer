<template>
  <div class="boons-uptime-card bg-neutral-card rounded-xl p-5">
    <div class="card-header mb-4">
      <div class="header-title flex items-center gap-2 text-base font-semibold text-neutral-text">
        <i class="pi pi-shield text-[var(--color-accent)]" />
        <span>增益覆盖</span>
      </div>
    </div>

    <div class="boons-container flex flex-col gap-3.5">
      <div
        v-for="boon in topBoons"
        :key="boon.id"
        class="boon-item p-3 bg-neutral-card-hover rounded-lg"
      >
        <div class="boon-header flex justify-between items-center mb-2">
          <span class="boon-name text-sm font-semibold text-neutral-text">{{ boon.name }}</span>
          <span
            class="boon-uptime text-sm font-bold p-[0.125rem 0.5rem] rounded-full bg-slate-400/[0.1] text-slate-400"
            :class="getUptimeClass(boon.uptime)"
          >
            {{ boon.uptime }}%
          </span>
        </div>
        <div class="boon-bar-container h-1.5 border-neutral-border rounded-[3px] overflow-hidden mb-2">
          <div
            class="boon-bar-fill h-full rounded-[3px]"
            :style="{ width: boon.uptime + '%', backgroundColor: boon.color }"
          />
        </div>
        <div class="boon-stats flex gap-4">
          <span class="stat text-[0.7rem] text-[var(--color-text-tertiary)]">应用: {{ boon.applied }}</span>
          <span class="stat text-[0.7rem] text-[var(--color-text-tertiary)]">浪费: {{ boon.wasted }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface BoonData {
  id: number
  name: string
  uptime: number
  applied: number
  wasted: number
  color: string
}

interface Props {
  boonsData: BoonData[]
}

const props = defineProps<Props>()

const topBoons = computed(() => {
  return [...props.boonsData].sort((a, b) => b.uptime - a.uptime).slice(0, 6)
})

function getUptimeClass(uptime: number): string {
  if (uptime >= 80) return 'high bg-green-500/10 text-green-500'
  if (uptime >= 50) return 'medium bg-amber-500/10 text-amber-500'
  return 'low bg-red-500/10 text-red-500'
}
</script>

