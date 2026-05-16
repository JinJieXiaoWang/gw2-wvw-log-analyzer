<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 1s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-history text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            最近战斗
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            最近的战场记录
          </p>
        </div>
      </div>
    </div>
    <div
      v-if="isLoading"
      class="py-12 flex items-center justify-center text-neutral-text-disabled"
    >
      <i class="pi pi-spin pi-spinner text-3xl" />
    </div>
    <div
      v-else
      class="overflow-x-auto -mx-4 px-4"
    >
      <DataTable
        :value="items"
        :paginator="items.length > 5"
        :rows="5"
        class="w-full game-table"
      >
        <Column
          field="start_time"
          header="时间"
        >
          <template #body="{ data }">
            <span class="text-sm text-neutral-text-secondary">{{ formatDateTime(data.start_time) }}</span>
          </template>
        </Column>
        <Column
          field="map_name"
          header="地图"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <i class="pi pi-map text-primary" />
              <span class="font-medium">{{ data.map_name }}</span>
            </div>
          </template>
        </Column>
        <Column
          field="duration_sec"
          header="时长"
        >
          <template #body="{ data }">
            <span class="text-neutral-text-secondary">{{ formatDuration(data.duration_sec) }}</span>
          </template>
        </Column>
        <Column
          field="player_count"
          header="人数"
        >
          <template #body="{ data }">
            <span class="game-badge game-badge-exotic">{{ data.player_count }}人</span>
          </template>
        </Column>
        <Column
          field="total_damage"
          header="总伤害"
        >
          <template #body="{ data }">
            <span class="text-status-error font-bold">{{ formatNumber(data.total_damage) }}</span>
          </template>
        </Column>
        <Column
          field="total_downed"
          header="击倒人数"
        >
          <template #body="{ data }">
            <span class="text-status-success font-semibold">{{ data.total_downed }}</span>
          </template>
        </Column>
        <Column
          field="kill_count"
          header="击杀/死亡"
        >
          <template #body="{ data }">
            <span class="text-secondary">{{ data.kill_count }}</span>
            <span class="text-neutral-text-disabled mx-1">/</span>
            <span class="text-status-error">{{ data.death_count }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 最近战斗表格组件 v2.0
 * 功能：绑定真实 recent-fights 接口数据
 * 更新：2026-05-04
 */

import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

defineProps<{
  items: Array<{
    fight_id: number
    log_id: number
    map_name: string
    server_name: string
    start_time: string
    duration_sec: number
    player_count: number
    total_damage: number
    total_downed: number
    kill_count: number
    death_count: number
  }>
  isLoading: boolean
}>()

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatDuration = (seconds: number): string => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}分${s}秒`
}

const formatDateTime = (iso: string): string => {
  try {
    const d = new Date(iso)
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}
</script>
