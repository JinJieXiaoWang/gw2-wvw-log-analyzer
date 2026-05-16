<template>
  <div class="skill-section">
    <div class="section-header">
      <h3 class="section-title">
        <i class="pi pi-sword" />
        {{ HEALING_SKILLS_TITLE }}
      </h3>
    </div>
    <div class="skill-grid">
      <div
        v-for="skill in skills"
        :key="skill.id"
        class="skill-card"
      >
        <div class="skill-header">
          <span class="skill-name">{{ skill.name }}</span>
          <span class="skill-count">{{ skill.count }} {{ LABEL_TIMES_SUFFIX }}</span>
        </div>
        <div class="skill-stats">
          <div class="skill-stat">
            <span class="stat-label">{{ LABEL_HEALING_AMOUNT }}</span>
            <span class="stat-value">{{ formatLargeNumber(skill.healing) }}</span>
          </div>
          <div class="skill-stat">
            <span class="stat-label">{{ LABEL_OVERHEAL_PERCENT }}</span>
            <span class="stat-value">{{ skill.overhealPercent }}%</span>
          </div>
          <div class="skill-stat">
            <span class="stat-label">{{ LABEL_TARGETS }}</span>
            <span class="stat-value">{{ skill.targets }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  HEALING_SKILLS_TITLE,
  LABEL_HEALING_AMOUNT,
  LABEL_OVERHEAL_PERCENT,
  LABEL_TARGETS,
  LABEL_TIMES_SUFFIX,
} from '@/constants/eiLabels'

interface HealingSkill {
  id: number
  name: string
  count: number
  healing: number
  overhealPercent: number
  targets: number
}

defineProps<{
  skills: HealingSkill[]
}>()

function formatLargeNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped lang="css">
.skill-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.section-header {
  margin-bottom: 1rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.section-title i {
  color: var(--color-accent);
}

.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.skill-card {
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  padding: 1rem;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.skill-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.skill-count {
  font-size: 0.75rem;
  color: var(--color-status-success);
  font-weight: 500;
}

.skill-stats {
  display: flex;
  gap: 1rem;
}

.skill-stat {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.skill-stat .stat-label {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
}

.skill-stat .stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
