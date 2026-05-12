<template>
  <div class="mb-6">
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="flex items-center">
        <label class="mr-2 text-sm">地图:</label>
        <select
          v-model="localFilters.mapName"
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
          v-model="localFilters.serverName"
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
          v-model="localFilters.result"
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
        @click="onFilter"
      >
        筛选
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { FightQueryParams } from '@/api/combat/fights'

const props = defineProps<{
  filters: FightQueryParams
}>()

const emit = defineEmits<{
  filter: [FightQueryParams]
}>()

const localFilters = reactive({ ...props.filters })

watch(() => props.filters, (v) => {
  Object.assign(localFilters, v)
}, { deep: true })

const onFilter = () => {
  emit('filter', { ...localFilters })
}
</script>
