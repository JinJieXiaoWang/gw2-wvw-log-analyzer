<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-secondary/30 to-primary/30 flex items-center justify-center">
          <i class="pi pi-users text-secondary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            团队排名
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            最强战队榜单
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          label="总览"
          size="small"
          :class="teamView === 'overview' ? 'btn-game' : 'btn-ghost'"
          @click="changeTeamView('overview')"
        />
        <Button
          label="详情"
          size="small"
          :class="teamView === 'detail' ? 'btn-game' : 'btn-ghost'"
          @click="changeTeamView('detail')"
        />
      </div>
    </div>
    <div class="space-y-3">
      <div
        v-for="(team, index) in teamRanking"
        :key="team.id"
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
        <div class="flex-1">
          <p class="text-neutral-text font-bold text-lg">
            {{ team.name }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ team.server }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-primary font-bold text-lg">
            {{ formatNumber(team.damage) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            总伤害
          </p>
        </div>
        <div class="text-right">
          <p class="text-status-success font-bold text-lg">
            {{ team.attendance }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            出勤率
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 团队排名组件
 * 功能：显示团队排名信息
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'

defineProps<{
  teamRanking: Array<{
    id: number
    name: string
    server: string
    damage: number
    attendance: string
  }>
  teamView: string
}>()

// Emits
const emit = defineEmits<{
  'change-team-view': [view: string]
}>()

// 事件处理
const changeTeamView = (view: string) => {
  emit('change-team-view', view)
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
</script>