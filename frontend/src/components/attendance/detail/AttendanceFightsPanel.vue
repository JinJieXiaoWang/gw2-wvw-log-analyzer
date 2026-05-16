<template>
  <div class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
    <div class="card-header flex items-center justify-between p-4 border-b border-neutral-border/20">
      <div class="flex items-center gap-2">
        <i class="pi pi-swords text-status-error text-lg" />
        <h3 class="font-semibold text-neutral-text">
          最近战斗
        </h3>
        <span class="text-xs px-2 py-0.5 rounded-full bg-status-error/20 text-status-error">{{ fights.length }} 场</span>
      </div>
      <button
        v-if="fights.length > 5"
        type="button"
        class="text-xs text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
        @click="showAll = !showAll"
      >
        <span>{{ showAll ? '收起' : '查看全部' }}</span>
        <i :class="['pi', showAll ? 'pi-chevron-up' : 'pi-chevron-down']" />
      </button>
    </div>
    <div class="card-body p-4">
      <div class="space-y-3">
        <div
          v-for="(fight, index) in displayFights"
          :key="index"
          class="group p-4 rounded-xl bg-surface-700/50 border border-neutral-border/20 hover:border-status-error/40 transition-all duration-300"
        >
          <div class="flex flex-wrap items-start gap-3">
            <div class="flex items-center gap-2 shrink-0">
              <i class="pi pi-clock text-neutral-text-secondary text-sm" />
              <span class="text-sm text-neutral-text">{{ formatDateTime(fight.fight_date) }}</span>
            </div>
            <div class="flex items-center gap-2 shrink-0">
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
            <div class="flex items-center gap-2 flex-1 shrink-0 min-w-[120px]">
              <i class="pi pi-map-marker text-neutral-text-secondary text-sm" />
              <span class="text-sm text-neutral-text truncate">{{ fight.map_name }}</span>
            </div>
            <div class="flex flex-wrap gap-4 justify-end flex-1">
              <div class="text-right min-w-[80px]">
                <span class="text-xs text-neutral-text-secondary">伤害</span>
                <p class="font-bold text-status-error">
                  {{ formatNumber(fight.damage) }}
                </p>
              </div>
              <div class="text-right min-w-[80px]">
                <span class="text-xs text-neutral-text-secondary">DPS</span>
                <p class="font-bold text-status-error">
                  {{ formatDps(fight.dps) }}
                </p>
              </div>
              <div class="text-right min-w-[80px]">
                <span class="text-xs text-neutral-text-secondary">击倒</span>
                <p class="font-bold text-warning">
                  {{ fight.downed }}
                </p>
              </div>
              <div class="text-right min-w-[60px]">
                <span class="text-xs text-neutral-text-secondary">评分</span>
                <span
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
        <i class="pi pi-swords text-4xl mb-3 opacity-50" />
        <p>暂无战斗记录</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getProfessionLabel, getScoreColor, formatNumber, formatDps, formatDateTime } from '@/utils/common/attendanceFormatters'

const { fights } = defineProps<{
  fights: any[]
}>()

const showAll = ref(false)
const displayFights = computed(() => showAll.value ? fights : fights.slice(0, 5))
</script>
