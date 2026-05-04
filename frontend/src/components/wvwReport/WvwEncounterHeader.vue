<template>
  <div class="wvw-encounter-header">
    <div class="header-main">
      <div class="header-left">
        <div class="fight-icon">
          <i class="pi pi-users" />
        </div>
        <div class="fight-info">
          <h1 class="fight-name">
            {{ fightName }}
          </h1>
          <div class="fight-meta">
            <span class="meta-item meta-badge wvw">
              <i class="pi pi-globe" />
              <span>WvW</span>
            </span>
            <span class="meta-item">
              <i class="pi pi-clock" />
              <span>{{ formattedDuration }}</span>
            </span>
            <span class="meta-item">
              <i class="pi pi-users" />
              <span>{{ playerCount }} 人</span>
            </span>
            <span class="meta-item">
              <i class="pi pi-calendar" />
              <span>{{ formattedDate }}</span>
            </span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <div
          v-if="hasSyncedData"
          class="sync-badge"
        >
          <i class="pi pi-check-circle" />
          <span>ZEVTC 已同步</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  fightName: string
  durationMs: number
  playerCount: number
  uploadedAt: string | null
  hasSyncedData: boolean
}

const props = defineProps<Props>()

const formattedDuration = computed(() => {
  const totalSec = Math.floor(props.durationMs / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
})

const formattedDate = computed(() => {
  if (!props.uploadedAt) return '未知时间'
  try {
    const date = new Date(props.uploadedAt)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return props.uploadedAt
  }
})
</script>

<style scoped>
.wvw-encounter-header {
  padding: 1.25rem 1.5rem;
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
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
  background: linear-gradient(135deg, #dc2626, #991b1b);
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
  color: white;
  font-size: 1.5rem;
}

.fight-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
  line-height: 1.3;
}

.fight-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.375rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.meta-item i {
  font-size: 0.875rem;
}

.meta-badge.wvw {
  background: linear-gradient(135deg, #dc2626, #991b1b);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.75rem;
}

.sync-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.sync-badge i {
  font-size: 1rem;
}
</style>
