<template>
  <div class="skill-cast-card bg-neutral-card rounded-xl p-5">
    <div class="card-header mb-4">
      <h3 class="card-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
        <i class="pi pi-bar-chart text-[var(--color-accent)]" />
        技能施放统计
      </h3>
    </div>
    <div class="card-content flex flex-col gap-5">
      <div class="skill-list flex flex-col gap-2.5">
        <div
          v-for="skill in skills"
          :key="skill.id"
          class="skill-item flex items-center gap-3"
        >
          <div class="skill-info w-[120px] shrink-0">
            <span class="skill-name text-[0.8125rem] text-neutral-text-secondary">{{ skill.name }}</span>
          </div>
          <div class="skill-bar-container flex-1 h-3 bg-neutral-card-hover rounded-[6px] overflow-hidden">
            <div
              class="skill-bar-fill h-full bg-[linear-gradient(90deg, var(--color-accent), #8b5cf6)] rounded-[6px]"
              :style="{ width: getBarWidth(skill) + '%' }"
            />
          </div>
          <div class="skill-count w-10 text-right text-[0.8125rem] font-semibold text-neutral-text">
            {{ skill.count }}
          </div>
        </div>
      </div>
      <div class="stats-row flex gap-6 pt-3">
        <div class="stat-item flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">技能施放</span>
          <span class="stat-value text-base font-semibold text-neutral-text">{{ totalCasts }}</span>
        </div>
        <div class="stat-item flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">技能效率</span>
          <span class="stat-value text-base font-semibold text-neutral-text">{{ uptime }}%</span>
        </div>
        <div class="stat-item flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">战斗时长</span>
          <span class="stat-value text-base font-semibold text-neutral-text">{{ formatDuration(duration) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Skill {
  id: number
  name: string
  count: number
}

const props = defineProps<{
  skills: Skill[]
  uptime: number
  duration: number
}>()

const maxCount = computed(() => {
  return Math.max(...props.skills.map(s => s.count), 1)
})

const totalCasts = computed(() => {
  return props.skills.reduce((sum, s) => sum + s.count, 0)
})

function getBarWidth(skill: Skill): number {
  return (skill.count / maxCount.value) * 100
}

function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}
</script>

