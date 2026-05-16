<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.7s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-status-warning/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-trophy text-status-warning" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            {{ SECTION_TITLE }}
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            {{ SECTION_SUBTITLE }}
          </p>
        </div>
      </div>
      <Dropdown
        v-model="localRankType"
        :options="rankTypeOptions"
        option-label="label"
        option-value="value"
        class="w-32"
        @change="changeRankType"
      />
    </div>
    <div class="space-y-3">
      <div
        v-for="(player, index) in playerRanking"
        :key="player.id"
        class="flex items-center gap-4 p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all cursor-pointer"
      >
        <div
          class="flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg"
          :class="{
            'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white shadow-lg': index === 0,
            'bg-gradient-to-br from-gray-400 to-gray-600 text-white shadow-lg': index === 1,
            'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-lg': index === 2,
            'bg-neutral-card text-neutral-text-secondary': index > 2
          }"
        >
          {{ index + 1 }}
        </div>
        <!-- 动态值，无法使用 Tailwind 静态类 -->
        <div
          class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0 shadow-lg"
          :style="{ backgroundColor: getSvcProfessionColor(player.profession) }"
        >
          {{ player.name.charAt(0) }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-neutral-text font-bold text-lg truncate">
            {{ player.name }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ getProfessionName(player.profession) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-primary font-bold text-lg">
            {{ formatNumber((player as any)[rankType]) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ getRankTypeLabel(rankType) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getProfessionName, getProfessionColor as getSvcProfessionColor } from '@/services/professionService'
/**
 * 个人排名组件
 * 功能：显示个人排名信息
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, watch } from 'vue'
import Dropdown from 'primevue/dropdown'

// === 常量定义 ===
const SECTION_TITLE = '个人排名'
const SECTION_SUBTITLE = '谁是MVP？'

const NUMBER_THRESHOLDS = {
  MILLION: 1_000_000,
  THOUSAND: 1_000,
} as const

const RANK_TYPE_LABELS: Record<string, string> = {
  damage: '伤害',
  healing: '治疗',
  kills: '击杀',
  score: '评分',
}

// Props
const props = defineProps<{
  playerRanking: Array<{
    id: number
    name: string
    profession: string
    damage: number
    healing: number
    kills: number
    score: string
  }>
  rankType: string
  rankTypeOptions: Array<{ label: string; value: string }>
}>()

// Emits
const emit = defineEmits<{
  'change-rank-type': [type: string]
}>()

// 本地状态
const localRankType = ref(props.rankType)

// 监听props变化
watch(() => props.rankType, (newValue) => {
  localRankType.value = newValue
})

// 事件处理
const changeRankType = () => {
  emit('change-rank-type', localRankType.value)
}

// 方法
const formatNumber = (num: any) => {
  if (typeof num === 'number') {
    if (num >= NUMBER_THRESHOLDS.MILLION) {
      return (num / NUMBER_THRESHOLDS.MILLION).toFixed(1) + 'M'
    } else if (num >= NUMBER_THRESHOLDS.THOUSAND) {
      return (num / NUMBER_THRESHOLDS.THOUSAND).toFixed(1) + 'K'
    }
    return num.toString()
  }
  return num
}

const getRankTypeLabel = (type: string) => {
  return RANK_TYPE_LABELS[type] || type
}
</script>
