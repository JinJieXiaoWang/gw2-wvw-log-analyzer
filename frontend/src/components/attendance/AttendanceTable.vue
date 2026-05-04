<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.8s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
          <i class="pi pi-list text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            详细出勤记录
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            完整战斗数据
          </p>
        </div>
      </div>
      <Button
        label="导出"
        icon="pi pi-download"
        class="btn-ghost"
        size="small"
        @click="exportDetail"
      />
    </div>
    <DataTable
      :value="attendanceRecords"
      :paginator="true"
      :rows="10"
      class="w-full game-table"
      removable-sort
      sort-field="date"
      :sort-order="-1"
    >
      <Column
        field="date"
        header="日期"
        sortable
      />
      <Column
        field="playerName"
        header="玩家"
      >
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-md"
              :style="{ backgroundColor: getProfessionColor(data.profession) }"
            >
              {{ data.playerName.charAt(0) }}
            </div>
            <span class="font-medium">{{ data.playerName }}</span>
          </div>
        </template>
      </Column>
      <Column
        field="profession"
        header="职业"
      />
      <Column
        field="mapName"
        header="地图"
      />
      <Column
        field="serverName"
        header="服务器"
      />
      <Column
        field="attendanceTime"
        header="参战时长"
      >
        <template #body="{ data }">
          {{ formatDuration(data.attendanceTime) }}
        </template>
      </Column>
      <Column
        field="damage"
        header="伤害"
      >
        <template #body="{ data }">
          <span class="text-primary font-semibold">{{ formatNumber(data.damage) }}</span>
        </template>
      </Column>
      <Column
        field="healing"
        header="治疗"
      >
        <template #body="{ data }">
          <span class="text-status-success font-semibold">{{ formatNumber(data.healing) }}</span>
        </template>
      </Column>
      <Column
        field="kills"
        header="击杀"
      >
        <template #body="{ data }">
          <span class="text-secondary font-semibold">{{ data.kills }}</span>
        </template>
      </Column>
      <Column
        field="deaths"
        header="死亡"
      >
        <template #body="{ data }">
          <span class="text-status-error font-semibold">{{ data.deaths }}</span>
        </template>
      </Column>
      <Column
        field="score"
        header="评分"
      >
        <template #body="{ data }">
          <span
            :class="{
              'game-badge game-badge-legendary': data.score.startsWith('A+'),
              'game-badge game-badge-exotic': data.score.startsWith('A'),
              'game-badge game-badge-rare': data.score.startsWith('B'),
              'game-badge': data.score.startsWith('C') || data.score.startsWith('D')
            }"
          >
            {{ data.score }}
          </span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤记录表格组件
 * 功能：显示详细的出勤记录数据
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

defineProps<{
  attendanceRecords: Array<{
    date: string
    playerName: string
    profession: string
    mapName: string
    serverName: string
    attendanceTime: number
    damage: number
    healing: number
    kills: number
    deaths: number
    score: string
  }>
}>()

// Emits
const emit = defineEmits<{
  'export-detail': []
}>()

// 事件处理
const exportDetail = () => {
  emit('export-detail')
}

// 方法
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

const getProfessionColor = (profession: string) => {
  const colors: Record<string, string> = {
    '战士': '#E85D04',
    '守护者': '#FAA307',
    '潜行者': '#9D4EDD',
    '元素使': '#FF6B6B',
    '工程师': '#7B8FA1',
    '猎人': '#06D6A0',
    '唤灵师': '#8D0801',
    '镜像师': '#4361EE',
    '游侠': '#2EC4B6'
  }
  return colors[profession] || '#6C757D'
}
</script>