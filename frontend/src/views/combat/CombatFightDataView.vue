<template>
  <div class="fight-data-view">
    <h1 class="text-2xl font-bold mb-6">
      战斗数据
    </h1>
    <FightFilterBar
      :filters="filters"
      @filter="onFilter"
    />
    <FightListPanel
      :fights="fights"
      :loading="loading"
      :has-more="hasMore"
      @view-detail="viewFightDetail"
      @view-stats="viewFightStats"
      @load-more="loadMoreFights"
    />
    <FightDetailPanel :fight="selectedFight" />
    <FightStatsPanel :stats="selectedFightStats" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fightsService } from '@/services'
import type { Fight, FightStats, FightQueryParams } from '@/services/combat/fightsService'
import FightFilterBar from '@/components/combat/fightData/FightFilterBar.vue'
import FightListPanel from '@/components/combat/fightData/FightListPanel.vue'
import FightDetailPanel from '@/components/combat/fightData/FightDetailPanel.vue'
import FightStatsPanel from '@/components/combat/fightData/FightStatsPanel.vue'

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
    const response = await fightsService.getFights({
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

const onFilter = (newFilters: FightQueryParams) => {
  filters.value = { ...newFilters, page: 1, pageSize: pageSize.value }
  loadFights()
}

const loadMoreFights = async () => {
  if (!hasMore.value || loading.value) return
  page.value++
  loading.value = true
  try {
    const response = await fightsService.getFights({
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
    const response = await fightsService.getFightDetail(fightId)
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
    const response = await fightsService.getFightStats(fightId)
    if (response.success && response.data) {
      selectedFightStats.value = response.data
      if (!selectedFight.value) {
        const fightResponse = await fightsService.getFightDetail(fightId)
        if (fightResponse.success && fightResponse.data) {
          selectedFight.value = fightResponse.data
        }
      }
    }
  } catch (error) {
    console.error('加载战斗统计失败:', error)
  }
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
