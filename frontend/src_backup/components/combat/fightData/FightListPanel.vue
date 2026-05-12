<template>
  <div class="bg-gray-800 rounded-lg p-4 mb-6">
    <h2 class="text-xl font-semibold mb-4">
      战斗列表
    </h2>
    <div
      v-if="loading"
      class="flex justify-center py-8"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
    </div>
    <div
      v-else-if="fights.length === 0"
      class="text-center py-8 text-gray-400"
    >
      暂无战斗数据
    </div>
    <div
      v-else
      class="overflow-x-auto"
    >
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-700">
            <th class="text-left py-3 px-4">
              地图
            </th>
            <th class="text-left py-3 px-4">
              服务器
            </th>
            <th class="text-left py-3 px-4">
              时间
            </th>
            <th class="text-left py-3 px-4">
              持续时间
            </th>
            <th class="text-left py-3 px-4">
              玩家数
            </th>
            <th class="text-left py-3 px-4">
              结果
            </th>
            <th class="text-left py-3 px-4">
              操作
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="fight in fights"
            :key="fight.id"
            class="border-b border-gray-700 hover:bg-gray-700 transition-colors"
          >
            <td class="py-3 px-4">
              {{ fight.mapName }}
            </td>
            <td class="py-3 px-4">
              {{ fight.serverName }}
            </td>
            <td class="py-3 px-4">
              {{ formatDate(fight.startTime) }}
            </td>
            <td class="py-3 px-4">
              {{ formatDuration(fight.duration) }}
            </td>
            <td class="py-3 px-4">
              {{ fight.playerCount }}
            </td>
            <td class="py-3 px-4">
              <span
                class="text-xs px-2 py-1 rounded"
                :class="resultClass(fight.result)"
              >
                {{ resultLabel(fight.result) }}
              </span>
            </td>
            <td class="py-3 px-4">
              <button
                class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors mr-2"
                @click="$emit('view-detail', fight.id)"
              >
                详情
              </button>
              <button
                class="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
                @click="$emit('view-stats', fight.id)"
              >
                统计
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="mt-4 flex justify-center">
      <button
        v-if="hasMore"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
        @click="$emit('load-more')"
      >
        加载更多
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Fight } from '@/api/combat/fights'

defineProps<{
  fights: Fight[]
  loading: boolean
  hasMore: boolean
}>()

defineEmits<{
  'view-detail': [string]
  'view-stats': [string]
  'load-more': []
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
