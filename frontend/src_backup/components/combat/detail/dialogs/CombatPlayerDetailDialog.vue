<script setup lang="ts">
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import type { EiAnalysisPlayer, PlayerRotationData } from '@/services/ei/eiAnalysisService'
import { WEAPON_NAME_MAP } from '@/config/combatConstants'
import { fmtCompact, getProfessionIconUrl, getProfessionName } from '@/composables/combat/useCombatHelpers'
import RotationViewTabs from '@/components/combat/rotation/RotationViewTabs.vue'
import RotationTimelineView from '@/components/combat/rotation/RotationTimelineView.vue'
import RotationHeatmapView from '@/components/combat/rotation/RotationHeatmapView.vue'
import RotationCycleView from '@/components/combat/rotation/RotationCycleView.vue'
import type { TimelineTick, SkillTrack, HeatmapRow, SkillCycle } from '@/utils/combat/rotationTypes'

const props = defineProps<{
  player: EiAnalysisPlayer | null
  playerRotation: PlayerRotationData | null
  rotationLoading: boolean
  sortedSkillCasts: any[]
  hasPlayerDetailData: boolean
  timelineTicks: TimelineTick[]
  timelineTracks: SkillTrack[]
  heatmapRows: HeatmapRow[]
  skillCycles: SkillCycle[]
  hoveredSkill: any
  tooltipPosition: { x: number; y: number } | null
}>()

const visible = defineModel<boolean>('visible', { default: false })
const rotationViewMode = defineModel<'stats' | 'timeline' | 'heatmap' | 'cycle'>('rotationViewMode', { default: 'stats' })

const emit = defineEmits<{
  'hover-skill': [skill: any]
  'leave-skill': []
  'mousemove': [event: MouseEvent]
}>()
</script>

<template>
  <Dialog
    :visible="visible"
    :header="player ? (player.character_name || player.account) : '玩家详情'"
    :style="{ width: '900px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
    @update:visible="visible = $event"
  >
    <div
      v-if="player"
      class="space-y-5"
    >
      <!-- 玩家信息头 -->
      <div class="flex items-center gap-4 pb-4 border-b border-neutral-border">
        <img
          :src="getProfessionIconUrl(player.profession)"
          class="w-12 h-12 rounded-full"
        >
        <div>
          <p class="text-lg font-bold text-neutral-text">
            {{ player.character_name || player.account }}
          </p>
          <p
            v-if="player.account && player.character_name"
            class="text-sm text-neutral-text-secondary"
          >
            {{ player.account }}
          </p>
          <p class="text-sm text-neutral-text-secondary">
            {{ getProfessionName(player.profession) }}
          </p>
        </div>
        <div class="ml-auto flex gap-3 text-sm">
          <div class="text-center">
            <p class="font-bold text-primary">
              {{ fmtCompact(player.damage) }}
            </p><p class="text-xs text-neutral-text-secondary">
              总伤害
            </p>
          </div>
          <div class="text-center">
            <p class="font-bold text-primary">
              {{ fmtCompact(player.dps) }}
            </p><p class="text-xs text-neutral-text-secondary">
              DPS
            </p>
          </div>
          <div class="text-center">
            <p class="font-bold text-status-success">
              {{ player.score_grade || '-' }}
            </p><p class="text-xs text-neutral-text-secondary">
              评分
            </p>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div
        v-if="rotationLoading"
        class="flex items-center justify-center py-8"
      >
        <ProgressSpinner style="width: 40px; height: 40px" />
        <span class="ml-3 text-neutral-text-secondary text-sm">加载技能数据中...</span>
      </div>

      <template v-else-if="playerRotation">
        <!-- 武器配置 -->
        <div
          v-if="playerRotation.weapons?.length"
          class="pb-4 border-b border-neutral-border"
        >
          <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
            <i class="pi pi-wrench text-primary" /> 武器配置
          </h4>
          <div class="flex items-center gap-3 flex-wrap">
            <div
              v-for="(w, idx) in playerRotation.weapons.filter((x: string) => x && x !== 'Unknown').slice(0, 4)"
              :key="idx"
              class="px-2 py-1 rounded bg-neutral-bg text-xs text-neutral-text"
            >
              {{ WEAPON_NAME_MAP[w] || w }}
            </div>
          </div>
        </div>

        <!-- 食物/扳手 -->
        <div
          v-if="playerRotation.consumables?.food?.length || playerRotation.consumables?.utility?.length"
          class="pb-4 border-b border-neutral-border"
        >
          <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
            <i class="pi pi-sparkles text-status-success" /> 食物 / 扳手
          </h4>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(f, idx) in playerRotation.consumables.food"
              :key="`food-${idx}`"
              class="flex items-center gap-2 px-2 py-1 rounded bg-status-success/10 text-xs text-neutral-text"
            >
              <img
                v-if="f.icon"
                :src="f.icon"
                class="w-5 h-5 rounded"
              >
              <span>{{ f.name || '未知食物' }}</span>
            </div>
            <div
              v-for="(u, idx) in playerRotation.consumables.utility"
              :key="`util-${idx}`"
              class="flex items-center gap-2 px-2 py-1 rounded bg-primary/10 text-xs text-neutral-text"
            >
              <img
                v-if="u.icon"
                :src="u.icon"
                class="w-5 h-5 rounded"
              >
              <span>{{ u.name || '未知扳手' }}</span>
            </div>
          </div>
        </div>

        <!-- 无详细数据时统一提示 -->
        <div
          v-if="!hasPlayerDetailData"
          class="text-neutral-text-secondary text-sm text-center py-8"
        >
          <i class="pi pi-info-circle text-2xl mb-2 block" />
          <p>暂无详细战斗数据</p>
          <p class="text-xs mt-1">
            当前解析器暂未提供技能循环、武器配置等详细信息
          </p>
        </div>

        <div
          v-else
          class="space-y-4"
        >
          <!-- 视图切换栏 -->
          <RotationViewTabs
            v-model="rotationViewMode"
          />

          <!-- 技能释放次数统计 -->
          <div v-if="rotationViewMode === 'stats'">
            <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
              <i class="pi pi-sort-amount-down text-primary" /> 技能释放次数
            </h4>
            <div class="max-h-[400px] overflow-auto space-y-1">
              <div
                v-for="s in sortedSkillCasts"
                :key="s.skillId"
                class="flex items-center gap-3 p-2 rounded hover:bg-neutral-bg/50"
              >
                <img
                  v-if="s.icon"
                  :src="s.icon"
                  class="w-8 h-8 rounded"
                >
                <div
                  v-else
                  class="w-8 h-8 rounded bg-neutral-bg flex items-center justify-center text-xs text-neutral-text-secondary"
                >
                  ?
                </div>
                <span class="text-sm text-neutral-text flex-1 truncate">{{ s.name }}</span>
                <span class="text-sm font-bold text-primary w-10 text-right">{{ s.count }}</span>
              </div>
            </div>
          </div>

          <!-- 技能循环时序图 -->
          <div v-if="rotationViewMode === 'timeline'">
            <RotationTimelineView
              :ticks="timelineTicks"
              :tracks="timelineTracks"
              @hover-skill="emit('hover-skill', $event)"
              @leave-skill="emit('leave-skill')"
              @mousemove="emit('mousemove', $event)"
            />
          </div>

          <!-- 技能循环热力图 -->
          <div v-if="rotationViewMode === 'heatmap'">
            <RotationHeatmapView :rows="heatmapRows" />
          </div>

          <!-- 技能循环流程视图 -->
          <div v-if="rotationViewMode === 'cycle'">
            <RotationCycleView
              :cycles="skillCycles"
              @hover-skill="emit('hover-skill', $event)"
              @leave-skill="emit('leave-skill')"
              @mousemove="emit('mousemove', $event)"
            />
          </div>

          <!-- 悬浮提示 -->
          <div
            v-if="hoveredSkill && tooltipPosition"
            class="fixed z-50 p-3 rounded-lg bg-neutral-card border border-neutral-border shadow-xl pointer-events-none"
            :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
          >
            <div class="flex items-center gap-2 mb-2">
              <img
                v-if="hoveredSkill.icon"
                :src="hoveredSkill.icon"
                class="w-6 h-6 rounded"
              >
              <span class="font-semibold text-neutral-text">{{ hoveredSkill.name }}</span>
            </div>
            <div class="text-xs text-neutral-text-secondary space-y-1">
              <p v-if="hoveredSkill.count">
                释放次数: {{ hoveredSkill.count }}
              </p>
              <p v-if="hoveredSkill.time !== undefined">
                时间: {{ hoveredSkill.time.toFixed(1) }}s
              </p>
              <p v-if="hoveredSkill.duration">
                持续时间: {{ hoveredSkill.duration }}ms
              </p>
            </div>
          </div>
        </div>
      </template>

      <div
        v-else
        class="text-neutral-text-secondary text-sm text-center py-8"
      >
        <i class="pi pi-info-circle text-2xl mb-2 block" />
        <p>该日志未生成技能循环数据</p>
        <p class="text-xs mt-1">
          请重新解析日志以获取技能详情
        </p>
      </div>
    </div>
  </Dialog>
</template>
