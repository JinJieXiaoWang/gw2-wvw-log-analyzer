<template>
  <div class="encounter-header">
    <div class="header-main">
      <div class="header-left">
        <div class="fight-icon">
          <i class="pi pi-sword" />
        </div>
        <div class="fight-info">
          <h1 class="fight-name">
            {{ fightName }}
          </h1>
          <div class="fight-meta">
            <span class="meta-item">
              <i class="pi pi-clock" />
              <span>{{ formattedDuration }}</span>
            </span>
            <span class="meta-divider">|</span>
            <span class="meta-item">
              <i class="pi pi-user" />
              <span>{{ recorder.name }}</span>
            </span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <div class="version-info">
          <div class="version-item">
            <span class="label">Elite Insights:</span>
            <span class="value">{{ versions.eliteInsights }}</span>
          </div>
          <div class="version-item">
            <span class="label">Arc:</span>
            <span class="value">{{ versions.arc }}</span>
          </div>
          <div class="version-item">
            <span class="label">GW2:</span>
            <span class="value">{{ versions.gw2 }}</span>
          </div>
        </div>

        <div class="theme-toggle">
          <button
            class="theme-btn"
            :class="{ active: !lightTheme }"
            title="黑色主题"
            @click="$emit('toggle-theme', false)"
          >
            <i class="pi pi-moon" />
          </button>
          <button
            class="theme-btn"
            :class="{ active: lightTheme }"
            title="白色主题"
            @click="$emit('toggle-theme', true)"
          >
            <i class="pi pi-sun" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 战斗信息头部组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { computed } from 'vue'
import { formatDuration } from '@/types/eliteInsights'

interface Props {
  fightName: string
  duration: number
  recorder: { name: string; account: string }
  versions: { eliteInsights: string; arc: string; gw2: number }
  lightTheme: boolean
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'toggle-theme', isLight: boolean): void
}>()

const formattedDuration = computed(() => formatDuration(props.duration))
</script>

<style scoped lang="css">
.encounter-header {
  padding: 1.25rem 1.5rem;
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.fight-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);
}

.fight-icon i {
  font-size: 1.5rem;
  color: white;
}

.fight-info {
  flex: 1;
}

.fight-name {
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  margin-bottom: 0.375rem;
}

.fight-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.meta-item i {
  font-size: 0.875rem;
  color: var(--color-accent);
}

.meta-divider {
  color: var(--color-border);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.version-info {
  display: flex;
  gap: 1rem;
}

.version-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.version-item .label {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.version-item .value {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text);
}

.theme-toggle {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
}

.theme-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.theme-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}

.theme-btn.active {
  background-color: var(--color-accent);
  color: white;
  box-shadow: 0 2px 8px var(--color-shadow);
}

.theme-btn i {
  font-size: 1rem;
}
</style>
