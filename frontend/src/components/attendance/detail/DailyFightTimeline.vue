<template>
  <div class="card animate-slide-in-up">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
        <i class="pi pi-calendar text-primary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          {{ TITLE }}
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          {{ subtitle }}
        </p>
      </div>
    </div>

    <div class="space-y-3">
      <div
        v-for="(day, index) in dailyFights"
        :key="day.date"
        class="rounded-xl border border-neutral-border/50 overflow-hidden"
      >
        <!-- 日期头部 -->
        <div
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-neutral-bg-secondary/50 transition-colors"
          @click="toggleDay(index)"
        >
          <div class="flex items-center gap-3">
            <i
              class="pi text-neutral-text-secondary transition-transform"
              :class="expandedDays.has(index) ? 'pi-chevron-down' : 'pi-chevron-right'"
            />
            <div>
              <span class="font-semibold text-neutral-text">{{ day.date }}</span>
              <span class="text-xs text-neutral-text-secondary ml-2">{{ day.day_of_week }}</span>
            </div>
          </div>
          <div class="flex items-center gap-4 text-sm">
            <span class="text-neutral-text-secondary">
              {{ day.fight_count }}场
            </span>
            <span class="text-neutral-text-secondary">
              {{ formatDuration(day.total_duration_sec) }}
            </span>
            <span class="text-status-error font-medium">
              {{ formatNumber(day.total_damage) }}
            </span>
            <span class="text-neutral-text-secondary">
              K/D {{ day.total_kills }}/{{ day.total_deaths }}
            </span>
          </div>
        </div>

        <!-- 战斗列表 -->
        <div
          v-show="expandedDays.has(index)"
          class="border-t border-neutral-border/30"
        >
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-neutral-text-secondary text-xs border-b border-neutral-border/20">
                  <th class="text-left p-3">
                    时间
                  </th>
                  <th class="text-left p-3">
                    地图
                  </th>
                  <th class="text-left p-3">
                    角色
                  </th>
                  <th class="text-right p-3">
                    时长
                  </th>
                  <th class="text-right p-3">
                    伤害
                  </th>
                  <th class="text-right p-3">
                    K/D
                  </th>
                  <th class="text-right p-3">
                    评分
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="fight in day.fights"
                  :key="fight.fight_id"
                  class="border-b border-neutral-border/10 hover:bg-neutral-bg-secondary/30 transition-colors"
                >
                  <td class="p-3 text-neutral-text">
                    {{ fight.time }}
                  </td>
                  <td class="p-3 text-neutral-text">
                    {{ fight.map_name }}
                  </td>
                  <td class="p-3">
                    <span class="text-xs text-neutral-text-secondary">{{ fight.character_name }}</span>
                  </td>
                  <td class="p-3 text-right text-neutral-text-secondary">
                    {{ formatDuration(fight.duration_sec) }}
                  </td>
                  <td class="p-3 text-right text-status-error font-medium">
                    {{ formatNumber(fight.damage) }}
                  </td>
                  <td class="p-3 text-right text-neutral-text">
                    {{ fight.killed }}/{{ fight.dead_count }}
                  </td>
                  <td class="p-3 text-right">
                    <span :class="getScoreColor(fight.ai_score)">{{ fight.ai_score }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { formatNumber, formatDuration, getScoreColor } from '@/utils/common/attendanceFormatters'

const TITLE = '每日战斗日志'

interface DailyFight {
  fight_id: number
  time: string
  map_name: string
  duration_sec: number
  character_name: string
  profession: string
  damage: number
  dps: number
  killed: number
  dead_count: number
  ai_score: number
}

interface DailyFightGroup {
  date: string
  day_of_week: string
  fight_count: number
  total_duration_sec: number
  total_damage: number
  total_kills: number
  total_deaths: number
  fights: DailyFight[]
}

const props = defineProps<{
  dailyFights: DailyFightGroup[]
}>()

const expandedDays = ref<Set<number>>(new Set([0]))

const subtitle = computed(() => `共 ${props.dailyFights.length} 天战斗记录`)

function toggleDay(index: number) {
  const next = new Set(expandedDays.value)
  if (next.has(index)) {
    next.delete(index)
  } else {
    next.add(index)
  }
  expandedDays.value = next
}
</script>
