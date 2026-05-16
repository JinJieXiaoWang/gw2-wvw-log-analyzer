<script setup lang="ts">
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import type { EiAnalysisPlayer, PlayerRotationData } from '@/services/ei/eiAnalysisService'
import RotationViewTabs from '@/components/combat/rotation/RotationViewTabs.vue'
import RotationTimelineView from '@/components/combat/rotation/RotationTimelineView.vue'
import RotationHeatmapView from '@/components/combat/rotation/RotationHeatmapView.vue'
import RotationCycleView from '@/components/combat/rotation/RotationCycleView.vue'
import type { TimelineTick, SkillTrack, HeatmapRow, SkillCycle } from '@/utils/combat/rotationTypes'
import CombatPlayerDetailHeader from './CombatPlayerDetailHeader.vue'
import CombatPlayerDetailRotationMeta from './CombatPlayerDetailRotationMeta.vue'
import CombatPlayerDetailSkillCastList from './CombatPlayerDetailSkillCastList.vue'
import CombatPlayerDetailTooltip from './CombatPlayerDetailTooltip.vue'

/** 技能循环相关数据 */
interface RotationData {
  /** 玩家技能循环数据 */
  playerRotation: PlayerRotationData | null
  /** 是否正在加载技能数据 */
  rotationLoading: boolean
  /** 排序后的技能释放列表 */
  sortedSkillCasts: any[]
}

/** 时间轴视图数据 */
interface TimelineData {
  /** 时间轴刻度 */
  timelineTicks: TimelineTick[]
  /** 时间轴轨道 */
  timelineTracks: SkillTrack[]
}

/** 热力图视图数据 */
interface HeatmapData {
  /** 热力图行数据 */
  heatmapRows: HeatmapRow[]
}

/** 循环视图数据 */
interface CycleData {
  /** 技能循环数据 */
  skillCycles: SkillCycle[]
}

/** 悬浮提示数据 */
interface TooltipData {
  /** 当前悬浮的技能 */
  hoveredSkill: any
  /** 提示框位置 */
  tooltipPosition: { x: number; y: number } | null
}

// === 常量定义 ===
const DIALOG_CONFIG = {
  WIDTH: '900px',
  MAX_WIDTH: '95vw',
} as const

const PLAYER_DETAIL_LABELS = {
  HEADER_FALLBACK: '玩家详情',
} as const

const EMPTY_STATE_MESSAGES = {
  NO_DETAIL_DATA_TITLE: '暂无详细战斗数据',
  NO_DETAIL_DATA_DESC: '当前解析器暂未提供技能循环、武器配置等详细信息',
  NO_ROTATION_DATA_TITLE: '该日志未生成技能循环数据',
  NO_ROTATION_DATA_DESC: '请重新解析日志以获取技能详情',
} as const

const LOADING_CONFIG = {
  SPINNER_SIZE: '40px',
  TEXT: '加载技能数据中...',
} as const

const props = defineProps<{
  player: EiAnalysisPlayer | null
  hasPlayerDetailData: boolean
  rotationData: RotationData
  timelineData: TimelineData
  heatmapData: HeatmapData
  cycleData: CycleData
  tooltipData: TooltipData
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
    :header="player ? (player.character_name || player.account) : PLAYER_DETAIL_LABELS.HEADER_FALLBACK"
    :style="{ width: DIALOG_CONFIG.WIDTH, maxWidth: DIALOG_CONFIG.MAX_WIDTH }"
    :modal="true"
    :draggable="false"
    @update:visible="visible = $event"
  >
    <div
      v-if="player"
      class="space-y-5"
    >
      <CombatPlayerDetailHeader :player="player" />

      <!-- 加载状态 -->
      <div
        v-if="rotationData.rotationLoading"
        class="flex items-center justify-center py-8"
      >
        <ProgressSpinner :style="{ width: LOADING_CONFIG.SPINNER_SIZE, height: LOADING_CONFIG.SPINNER_SIZE }" />
        <span class="ml-3 text-neutral-text-secondary text-sm">{{ LOADING_CONFIG.TEXT }}</span>
      </div>

      <template v-else-if="rotationData.playerRotation">
        <CombatPlayerDetailRotationMeta
          :weapons="rotationData.playerRotation.weapons || []"
          :consumables="rotationData.playerRotation.consumables || { food: [], utility: [] }"
        />

        <!-- 无详细数据时统一提示 -->
        <div
          v-if="!hasPlayerDetailData"
          class="text-neutral-text-secondary text-sm text-center py-8"
        >
          <i class="pi pi-info-circle text-2xl mb-2 block" />
          <p>{{ EMPTY_STATE_MESSAGES.NO_DETAIL_DATA_TITLE }}</p>
          <p class="text-xs mt-1">
            {{ EMPTY_STATE_MESSAGES.NO_DETAIL_DATA_DESC }}
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

          <CombatPlayerDetailSkillCastList
            v-if="rotationViewMode === 'stats'"
            :sorted-skill-casts="rotationData.sortedSkillCasts"
          />

          <!-- 技能循环时序图 -->
          <div v-if="rotationViewMode === 'timeline'">
            <RotationTimelineView
              :ticks="timelineData.timelineTicks"
              :tracks="timelineData.timelineTracks"
              @hover-skill="emit('hover-skill', $event)"
              @leave-skill="emit('leave-skill')"
              @mousemove="emit('mousemove', $event)"
            />
          </div>

          <!-- 技能循环热力图 -->
          <div v-if="rotationViewMode === 'heatmap'">
            <RotationHeatmapView :rows="heatmapData.heatmapRows" />
          </div>

          <!-- 技能循环流程视图 -->
          <div v-if="rotationViewMode === 'cycle'">
            <RotationCycleView
              :cycles="cycleData.skillCycles"
              @hover-skill="emit('hover-skill', $event)"
              @leave-skill="emit('leave-skill')"
              @mousemove="emit('mousemove', $event)"
            />
          </div>

          <CombatPlayerDetailTooltip
            :hovered-skill="tooltipData.hoveredSkill"
            :tooltip-position="tooltipData.tooltipPosition"
          />
        </div>
      </template>

      <div
        v-else
        class="text-neutral-text-secondary text-sm text-center py-8"
      >
        <i class="pi pi-info-circle text-2xl mb-2 block" />
        <p>{{ EMPTY_STATE_MESSAGES.NO_ROTATION_DATA_TITLE }}</p>
        <p class="text-xs mt-1">
          {{ EMPTY_STATE_MESSAGES.NO_ROTATION_DATA_DESC }}
        </p>
      </div>
    </div>
  </Dialog>
</template>
