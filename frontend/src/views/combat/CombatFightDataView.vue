<template>
  <div class="fight-data-view">
    <h1 class="text-2xl font-bold mb-6">
      战斗数据
    </h1>
    
    <div class="mb-6">
      <div class="flex flex-wrap gap-4 mb-4">
        <div class="flex items-center">
          <label class="mr-2 text-sm">地图:</label>
          <select
            v-model="filters.mapName"
            class="bg-gray-700 rounded px-3 py-2 text-sm"
          >
            <option value="">
              全部
            </option>
            <option value="永恒战场">
              永恒战场
            </option>
            <option value="红沙漠">
              红沙漠
            </option>
            <option value="蓝宝石海岸">
              蓝宝石海岸
            </option>
            <option value="翠绿之林">
              翠绿之林
            </option>
          </select>
        </div>
        
        <div class="flex items-center">
          <label class="mr-2 text-sm">服务器:</label>
          <select
            v-model="filters.serverName"
            class="bg-gray-700 rounded px-3 py-2 text-sm"
          >
            <option value="">
              全部
            </option>
            <option value="卓玛">
              卓玛
            </option>
            <option value="巴萨泽">
              巴萨泽
            </option>
            <option value="梅兰朵">
              梅兰朵
            </option>
            <option value="古兰斯">
              古兰斯
            </option>
          </select>
        </div>
        
        <div class="flex items-center">
          <label class="mr-2 text-sm">结果:</label>
          <select
            v-model="filters.result"
            class="bg-gray-700 rounded px-3 py-2 text-sm"
          >
            <option value="">
              全部
            </option>
            <option value="win">
              胜利
            </option>
            <option value="loss">
              失败
            </option>
            <option value="draw">
              平局
            </option>
          </select>
        </div>
        
        <button 
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors" 
          @click="loadFights"
        >
          筛选
        </button>
      </div>
    </div>
    
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
                  :class="{
                    'bg-green-900 text-green-200': fight.result === 'win',
                    'bg-red-900 text-red-200': fight.result === 'loss',
                    'bg-yellow-900 text-yellow-200': fight.result === 'draw'
                  }"
                >
                  {{ fight.result === 'win' ? '胜利' : fight.result === 'loss' ? '失败' : '平局' }}
                </span>
              </td>
              <td class="py-3 px-4">
                <button 
                  class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors mr-2" 
                  @click="viewFightDetail(fight.id)"
                >
                  详情
                </button>
                <button 
                  class="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors" 
                  @click="viewFightStats(fight.id)"
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
          @click="loadMoreFights"
        >
          加载更多
        </button>
      </div>
    </div>
    
    <!-- 战斗详情 -->
    <div
      v-if="selectedFight"
      class="bg-gray-800 rounded-lg p-4 mb-6"
    >
      <h2 class="text-xl font-semibold mb-4">
        战斗详情
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p><strong>地图:</strong> {{ selectedFight.mapName }}</p>
          <p><strong>服务器:</strong> {{ selectedFight.serverName }}</p>
          <p><strong>开始时间:</strong> {{ formatDate(selectedFight.startTime) }}</p>
          <p><strong>结束时间:</strong> {{ formatDate(selectedFight.endTime) }}</p>
          <p><strong>持续时间:</strong> {{ formatDuration(selectedFight.duration) }}</p>
          <p><strong>玩家数:</strong> {{ selectedFight.playerCount }}</p>
          <p>
            <strong>结果:</strong> 
            <span 
              class="text-xs px-2 py-1 rounded" 
              :class="{
                'bg-green-900 text-green-200': selectedFight.result === 'win',
                'bg-red-900 text-red-200': selectedFight.result === 'loss',
                'bg-yellow-900 text-yellow-200': selectedFight.result === 'draw'
              }"
            >
              {{ selectedFight.result === 'win' ? '胜利' : selectedFight.result === 'loss' ? '失败' : '平局' }}
            </span>
          </p>
        </div>
        <div>
          <h3 class="font-medium mb-2">
            目标点
          </h3>
          <div class="space-y-2">
            <div 
              v-for="(objective, index) in selectedFight.objectives" 
              :key="index" 
              class="flex justify-between items-center bg-gray-700 rounded p-2"
            >
              <span>{{ objective.name }}</span>
              <span 
                class="text-xs px-2 py-1 rounded" 
                :class="objective.captured ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'"
              >
                {{ objective.captured ? '已占领' : '未占领' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 战斗统计 -->
    <div
      v-if="selectedFightStats"
      class="bg-gray-800 rounded-lg p-4"
    >
      <h2 class="text-xl font-semibold mb-4">
        战斗统计数据
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">
            总伤害
          </p>
          <p class="text-lg font-semibold">
            {{ selectedFightStats.totalDamage.toLocaleString() }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">
            总治疗
          </p>
          <p class="text-lg font-semibold">
            {{ selectedFightStats.totalHealing.toLocaleString() }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">
            总击杀
          </p>
          <p class="text-lg font-semibold">
            {{ selectedFightStats.totalKills }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">
            总死亡
          </p>
          <p class="text-lg font-semibold">
            {{ selectedFightStats.totalDeaths }}
          </p>
        </div>
      </div>
      
      <h3 class="font-medium mb-2">
        玩家统计
      </h3>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700">
              <th class="text-left py-3 px-4">
                玩家
              </th>
              <th class="text-left py-3 px-4">
                职业
              </th>
              <th class="text-left py-3 px-4">
                伤害
              </th>
              <th class="text-left py-3 px-4">
                治疗
              </th>
              <th class="text-left py-3 px-4">
                击杀
              </th>
              <th class="text-left py-3 px-4">
                死亡
              </th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(player, index) in selectedFightStats.playerStats" 
              :key="index" 
              class="border-b border-gray-700 hover:bg-gray-700 transition-colors"
            >
              <td class="py-3 px-4">
                {{ player.accountName }}
              </td>
              <td class="py-3 px-4">
                {{ player.profession }}
              </td>
              <td class="py-3 px-4">
                {{ player.damage.toLocaleString() }}
              </td>
              <td class="py-3 px-4">
                {{ player.healing.toLocaleString() }}
              </td>
              <td class="py-3 px-4">
                {{ player.kills }}
              </td>
              <td class="py-3 px-4">
                {{ player.deaths }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fightsApi } from '@/api'
import type { Fight, FightStats, FightQueryParams } from '@/api/combat/fights'

const fights = ref<Fight[]>([])
const selectedFight = ref<Fight | null>(null)
const selectedFightStats = ref<FightStats | null>(null)
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const pageSize = ref(20)

const filters = ref<FightQueryParams>({
  mapName: '',
  serverName: '',
  result: undefined,
  page: 1,
  pageSize: pageSize.value
})

const loadFights = async () => {
  loading.value = true
  try {
    const response = await fightsApi.getFights({
      ...filters.value,
      page: 1,
      pageSize: pageSize.value
    })
    if (response.success && response.data) {
      fights.value = response.data
      hasMore.value = response.data.length === pageSize.value
      page.value = 1
    }
  } catch (error) {
    console.error('加载战斗列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadMoreFights = () => {
  if (!hasMore.value || loading.value) return
  page.value++
  loadMoreFightsData()
}

const loadMoreFightsData = async () => {
  loading.value = true
  try {
    const response = await fightsApi.getFights({
      ...filters.value,
      page: page.value,
      pageSize: pageSize.value
    })
    if (response.success && response.data) {
      fights.value = [...fights.value, ...response.data]
      hasMore.value = response.data.length === pageSize.value
    }
  } catch (error) {
    console.error('加载更多战斗失败:', error)
  } finally {
    loading.value = false
  }
}

const viewFightDetail = async (fightId: string) => {
  try {
    const response = await fightsApi.getFightDetail(fightId)
    if (response.success && response.data) {
      selectedFight.value = response.data
      selectedFightStats.value = null
    }
  } catch (error) {
    console.error('加载战斗详情失败:', error)
  }
}

const viewFightStats = async (fightId: string) => {
  try {
    const response = await fightsApi.getFightStats(fightId)
    if (response.success && response.data) {
      selectedFightStats.value = response.data
      // 如果还没有加载战斗详情，加载一下
      if (!selectedFight.value) {
        const fightResponse = await fightsApi.getFightDetail(fightId)
        if (fightResponse.success && fightResponse.data) {
          selectedFight.value = fightResponse.data
        }
      }
    }
  } catch (error) {
    console.error('加载战斗统计失败:', error)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

onMounted(() => {
  loadFights()
})
</script>

<style scoped>
.fight-data-view {
  padding: 20px;
}
</style>