<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.8s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
        <i class="pi pi-trophy text-primary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          玩家排行
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          按 {{ metricLabel }} 排序
        </p>
      </div>
    </div>

    <div class="flex gap-2 mb-4 flex-wrap">
      <Button
        v-for="tab in tabs"
        :key="tab.value"
        :label="tab.label"
        size="small"
        :class="sortBy === tab.value ? 'btn-game' : 'btn-ghost'"
        @click="switchSort(tab.value)"
      />
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
        class="w-full game-table"
        :rows="10"
        paginator
        :rows-per-page-options="[10, 20]"
      >
        <Column header="排名">
          <template #body="{ index }">
            <span
              class="font-bold"
              :class="rankClass(index)"
            >{{ index + 1 }}</span>
          </template>
        </Column>
        <Column
          field="account"
          header="账号"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary/40 to-secondary/40 flex items-center justify-center text-white text-xs font-bold">
                {{ data.account.charAt(0).toUpperCase() }}
              </div>
              <span class="font-medium">{{ data.account }}</span>
            </div>
          </template>
        </Column>
        <Column
          field="fight_count"
          header="场次"
          sortable
        >
          <template #body="{ data }">
            <Tag
              :value="String(data.fight_count)"
              severity="info"
              class="game-badge"
            />
          </template>
        </Column>
        <Column
          field="total_damage"
          header="总伤害"
          sortable
        >
          <template #body="{ data }">
            <span class="text-status-error font-semibold">{{ formatNumber(data.total_damage) }}</span>
          </template>
        </Column>
        <Column
          field="avg_dps"
          header="平均DPS"
          sortable
        >
          <template #body="{ data }">
            <span class="text-secondary font-semibold">{{ formatNumber(data.avg_dps) }}</span>
          </template>
        </Column>
        <Column
          field="total_healing"
          header="总治疗"
          sortable
        >
          <template #body="{ data }">
            <span class="text-status-success font-semibold">{{ formatNumber(data.total_healing) }}</span>
          </template>
        </Column>
        <Column
          field="total_kills"
          header="击杀/死亡"
          sortable
        >
          <template #body="{ data }">
            <span class="text-secondary">{{ data.total_kills }}</span>
            <span class="text-neutral-text-disabled mx-1">/</span>
            <span class="text-status-error">{{ data.total_deaths }}</span>
            <Tag
              :value="`K/D ${data.kd_ratio}`"
              :severity="data.kd_ratio >= 1 ? 'success' : 'danger'"
              class="ml-2 game-badge text-xs"
            />
          </template>
        </Column>
        <Column
          field="avg_ai_score"
          header="评分"
          sortable
        >
          <template #body="{ data }">
            <span
              :class="{
                'game-badge game-badge-legendary': data.avg_ai_score >= 90,
                'game-badge game-badge-exotic': data.avg_ai_score >= 80 && data.avg_ai_score < 90,
                'game-badge game-badge-rare': data.avg_ai_score >= 70 && data.avg_ai_score < 80,
                'game-badge': data.avg_ai_score < 70
              }"
            >
              {{ data.avg_ai_score }}
            </span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 玩家排行组件 v2.0
 * 功能：Tab 切换排序维度，DataTable 展示排行
 * 更新：2026-05-04
 */

import { computed } from 'vue'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const props = defineProps<{
  items: Array<any>
  sortBy: string
  isLoading: boolean
}>()

const emit = defineEmits<{
  'update:sortBy': [value: string]
}>()

const tabs = [
  { label: '伤害', value: 'damage' },
  { label: 'DPS', value: 'dps' },
  { label: '治疗', value: 'healing' },
  { label: '击杀', value: 'killed' },
  { label: '评分', value: 'ai_score' },
]

const metricLabel = computed(() => {
  const tab = tabs.find(t => t.value === props.sortBy)
  return tab?.label || '伤害'
})

const switchSort = (value: string) => {
  emit('update:sortBy', value)
}

const rankClass = (index: number): string => {
  if (index === 0) return 'text-status-warning'
  if (index === 1) return 'text-neutral-text-secondary'
  if (index === 2) return 'text-amber-600'
  return 'text-neutral-text-secondary'
}

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
