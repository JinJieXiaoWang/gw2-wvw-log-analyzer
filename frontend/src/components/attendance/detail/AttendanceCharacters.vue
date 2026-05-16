<template>
  <div class="card">
    <div class="flex items-center gap-2 mb-4">
      <i class="pi pi-users text-primary" />
      <span class="font-semibold">角色统计</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">{{ characters.length }} 个角色</span>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="char in characters"
        :key="char.character_name"
        class="p-4 rounded-xl bg-surface-100/30 border border-neutral-border/30 hover:border-primary/50 transition-all duration-300 cursor-pointer"
        @click="$emit('show-char', char)"
      >
        <div class="flex items-start gap-3">
          <!-- 动态值，无法使用 Tailwind 静态类 -->
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shrink-0"
            :style="{ background: getProfessionGradient(char.profession) }"
          >
            {{ char.character_name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-semibold text-neutral-text truncate">{{ char.character_name }}</span>
              <!-- 动态值，无法使用 Tailwind 静态类 -->
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :style="{ backgroundColor: getProfessionColorVal(char.profession) + '30', color: getProfessionColorVal(char.profession) }"
              >
                {{ getProfessionLabel(char.profession) }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span class="text-neutral-text-secondary">出勤</span><p class="font-bold text-primary">
                  {{ char.attendance_count }}天
                </p>
              </div>
              <div>
                <span class="text-neutral-text-secondary">DPS</span><p class="font-bold text-status-error">
                  {{ formatDps(char.avg_dps) }}
                </p>
              </div>
              <div>
                <span class="text-neutral-text-secondary">伤害</span><p class="font-bold text-status-error">
                  {{ formatNumber(char.total_damage) }}
                </p>
              </div>
              <div>
                <span class="text-neutral-text-secondary">评分</span><span
                  :class="getScoreColor(char.avg_score)"
                  class="font-bold"
                >{{ char.avg_score }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t border-neutral-border/30">
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-text-secondary">K/D</span>
            <span
              :class="char.kd_ratio >= 2 ? 'text-status-success' : char.kd_ratio >= 1 ? 'text-primary' : 'text-status-error'"
              class="font-semibold"
            >{{ char.kd_ratio }}</span>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!characters.length"
      class="text-center py-8 text-neutral-text-secondary"
    >
      <i class="pi pi-users text-3xl mb-2 opacity-50" />
      <p>暂无角色数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getProfessionLabel, getScoreColor, formatNumber, formatDps } from '@/utils/common/attendanceFormatters'

defineProps<{ characters: any[] }>()

defineEmits<{
  (e: 'show-char', char: any): void
}>()

function getProfessionGradient(profession: string) {
  const color = getProfessionColor(profession)
  return `linear-gradient(135deg, ${color}60, ${color}20)`
}

function getProfessionColorVal(profession: string) {
  return getProfessionColor(profession)
}
</script>
