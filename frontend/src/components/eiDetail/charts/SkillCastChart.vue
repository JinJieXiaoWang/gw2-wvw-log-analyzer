<template>
  <div class="skill-cast-card">
    <div class="card-header">
      <h3 class="card-title">
        <i class="pi pi-bar-chart" />
        技能施放统计
      </h3>
    </div>
    <div class="card-content">
      <div class="skill-list">
        <div
          v-for="skill in skills"
          :key="skill.id"
          class="skill-item"
        >
          <div class="skill-info">
            <span class="skill-name">{{ skill.name }}</span>
          </div>
          <div class="skill-bar-container">
            <div
              class="skill-bar-fill"
              :style="{ width: getBarWidth(skill) + '%' }"
            />
          </div>
          <div class="skill-count">
            {{ skill.count }}
          </div>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-label">技能施放</span>
          <span class="stat-value">{{ totalCasts }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">技能效率</span>
          <span class="stat-value">{{ uptime }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">战斗时长</span>
          <span class="stat-value">{{ formatDuration(duration) }}</span>
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

<style scoped lang="css">
.skill-cast-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.card-header {
  margin-bottom: 1rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.card-title i {
  color: var(--color-accent);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.skill-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.skill-info {
  width: 120px;
  flex-shrink: 0;
}

.skill-name {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.skill-bar-container {
  flex: 1;
  height: 12px;
  background-color: var(--color-card-hover);
  border-radius: 6px;
  overflow: hidden;
}

.skill-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent), #8b5cf6);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.skill-count {
  width: 40px;
  text-align: right;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text);
}

.stats-row {
  display: flex;
  gap: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>