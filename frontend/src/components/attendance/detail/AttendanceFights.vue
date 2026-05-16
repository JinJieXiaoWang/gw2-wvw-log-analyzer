<template>
  <div class="card">
    <div class="flex items-center gap-2 mb-4">
      <i class="pi pi-swords text-status-error" />
      <span class="font-semibold">最近战斗</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-status-error/20 text-status-error">{{ fights.length }} 场</span>
    </div>
    <div class="space-y-3">
      <div
        v-for="(fight, index) in fights"
        :key="index"
        class="p-4 rounded-xl bg-surface-100/30 border border-neutral-border/30 hover:border-status-error/50 transition-all duration-300"
      >
        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center gap-2">
            <i class="pi pi-clock text-neutral-text-secondary" />
            <span class="text-sm text-neutral-text">{{ formatDateTime(fight.fight_date) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <!-- 动态值，无法使用 Tailwind 静态类 -->
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold"
              :style="{ backgroundColor: getProfessionColor(fight.profession) }"
            >
              {{ fight.character_name?.charAt(0) }}
            </div>
            <span class="text-sm font-medium">{{ fight.character_name }}</span>
            <!-- 动态值，无法使用 Tailwind 静态类 -->
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :style="{ backgroundColor: getProfessionColor(fight.profession) + '30', color: getProfessionColor(fight.profession) }"
            >
              {{ getProfessionLabel(fight.profession) }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <i class="pi pi-map-marker text-neutral-text-secondary" />
            <span class="text-sm text-neutral-text">{{ fight.map_name }}</span>
          </div>
          <div class="flex-1 flex flex-wrap gap-6 justify-end">
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">伤害</span><p class="font-bold text-status-error">
                {{ formatNumber(fight.damage) }}
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">DPS</span><p class="font-bold text-status-error">
                {{ formatDps(fight.dps) }}
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">击倒</span><p class="font-bold text-warning">
                {{ fight.downed }}
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">击ɱ</span><p class="font-bold text-secondary">
                {{ fight.killed }}
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">死亡</span><p class="font-bold text-status-error">
                {{ fight.dead_count }}
              </p>
            </div>
            <div class="text-right">
              <span class="text-xs text-neutral-text-secondary">评分</span><span
                :class="getScoreColor(fight.ai_score)"
                class="font-bold"
              >{{ fight.ai_score }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!fights.length"
      class="text-center py-8 text-neutral-text-secondary"
    >
      <i class="pi pi-swords text-3xl mb-2 opacity-50" />
      <p>暂无战斗记¼</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getProfessionLabel, getScoreColor, formatNumber, formatDps, formatDateTime } from '@/utils/common/attendanceFormatters'

defineProps<{ fights: any[] }>()
</script>
