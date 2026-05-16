<template>
  <div
    v-if="fight"
    class="bg-gray-800 rounded-lg p-4 mb-6"
  >
    <h2 class="text-xl font-semibold mb-4">
      战斗详情
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <p><strong>地图:</strong> {{ fight.mapName }}</p>
        <p><strong>服务器:</strong> {{ fight.serverName }}</p>
        <p><strong>开始时间:</strong> {{ formatDate(fight.startTime) }}</p>
        <p><strong>结束时间:</strong> {{ formatDate(fight.endTime) }}</p>
        <p><strong>持续时间:</strong> {{ formatDuration(fight.duration) }}</p>
        <p><strong>玩家数:</strong> {{ fight.playerCount }}</p>
        <p>
          <strong>结果:</strong>
          <span
            class="text-xs px-2 py-1 rounded"
            :class="resultClass(fight.result)"
          >
            {{ resultLabel(fight.result) }}
          </span>
        </p>
      </div>
      <div>
        <h3 class="font-medium mb-2">
          目标点
        </h3>
        <div class="space-y-2">
          <div
            v-for="(obj, i) in fight.objectives"
            :key="i"
            class="flex justify-between items-center bg-gray-700 rounded p-2"
          >
            <span>{{ obj.name }}</span>
            <span
              class="text-xs px-2 py-1 rounded"
              :class="obj.captured ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'"
            >
              {{ obj.captured ? '已占领' : '未占领' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Fight } from '@/services/combat/fightsService'

defineProps<{
  fight: Fight | null
}>()

const formatDate = (dateString: string) => new Date(dateString).toLocaleString()

const formatDuration = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

const resultClass = (result: string) => ({
  'bg-green-900 text-green-200': result === 'win',
  'bg-red-900 text-red-200': result === 'loss',
  'bg-yellow-900 text-yellow-200': result === 'draw',
})

const resultLabel = (result: string) =>
  result === 'win' ? '胜利' : result === 'loss' ? '失败' : '平局'
</script>
