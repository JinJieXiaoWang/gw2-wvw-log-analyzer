<script setup lang="ts">
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import BaseProgressSpinner from '@/components/common/ui/display/BaseProgressSpinner.vue'
import type { EiAnalysisPlayer, PlayerRotationData } from '@/services/ei/eiAnalysisService'
import CombatPlayerDetailHeader from './CombatPlayerDetailHeader.vue'
import CombatPlayerDetailRotationMeta from './CombatPlayerDetailRotationMeta.vue'
import CombatPlayerDetailSkillCastList from './CombatPlayerDetailSkillCastList.vue'
import RotationViewTabs from '@/components/combat/rotation/RotationViewTabs.vue'
import SkillRotationFlow from '@/components/combat/rotation/SkillRotationFlow.vue'

interface Props {
  player: EiAnalysisPlayer | null
  playerRotation: PlayerRotationData | null
  rotationLoading: boolean
  hasPlayerDetailData: boolean
  sortedSkillCasts: any[]
  top10SkillCasts: any[]
  autoAttackRatio: number
  weaponSwapCount: number
  weaponSwapIntervals: { intervals: number[]; average: number; min: number; max: number } | null
  rotationEvents: any[]
}

defineProps<Props>()

const visible = defineModel<boolean>('visible', { default: false })
const rotationViewMode = defineModel<'stats' | 'rotation'>('rotationViewMode', { default: 'stats' })

const LABELS = {
  LOADING: '加载技能数据中...',
  NO_DETAIL_DATA_TITLE: '暂无详细战斗数据',
  NO_DETAIL_DATA_DESC: '当前解析器暂未提供技能循环、武器配置等详细信息',
  NO_ROTATION_DATA_TITLE: '该日志未生成技能循环数据',
  NO_ROTATION_DATA_DESC: '请重新解析日志以获取技能详情',
} as const
</script>

<template>
  <BaseDialog
    :visible="visible"
    :header="player ? (player.character_name || player.account) : '玩家详情'"
    width="900px"
    :modal="true"
    :draggable="false"
    :show-footer="false"
    @update:visible="visible = $event"
  >
    <div
      v-if="player"
      class="space-y-5"
    >
      <!-- 玩家信息头 -->
      <CombatPlayerDetailHeader :player="player" />

      <!-- 加载状态 -->
      <div
        v-if="rotationLoading"
        class="flex items-center justify-center py-8"
      >
        <BaseProgressSpinner class="w-10 h-10" />
        <span class="ml-3 text-neutral-text-secondary text-sm">{{ LABELS.LOADING }}</span>
      </div>

      <template v-else-if="playerRotation">
        <!-- 武器配置 + 食物/扳手 -->
        <CombatPlayerDetailRotationMeta
          :weapons="playerRotation.weapons || []"
          :consumables="playerRotation.consumables || {}"
        />

        <!-- 无详细数据时统一提示 -->
        <div
          v-if="!hasPlayerDetailData"
          class="text-neutral-text-secondary text-sm text-center py-8"
        >
          <i class="pi pi-info-circle text-2xl mb-2 block" />
          <p>{{ LABELS.NO_DETAIL_DATA_TITLE }}</p>
          <p class="text-xs mt-1">
            {{ LABELS.NO_DETAIL_DATA_DESC }}
          </p>
        </div>

        <template v-else>
          <!-- 视图切换栏 -->
          <RotationViewTabs v-model="rotationViewMode" />

          <!-- 技能统计视图 -->
          <div v-if="rotationViewMode === 'stats'">
            <CombatPlayerDetailSkillCastList
              :sorted-skill-casts="sortedSkillCasts"
              :top10-skill-casts="top10SkillCasts"
              :auto-attack-ratio="autoAttackRatio"
              :weapon-swap-count="weaponSwapCount"
              :weapon-swap-intervals="weaponSwapIntervals"
            />
          </div>

          <!-- 技能时间流视图 -->
          <div v-else-if="rotationViewMode === 'rotation'">
            <SkillRotationFlow :events="rotationEvents" />
          </div>
        </template>
      </template>

      <div
        v-else
        class="text-neutral-text-secondary text-sm text-center py-8"
      >
        <i class="pi pi-info-circle text-2xl mb-2 block" />
        <p>{{ LABELS.NO_ROTATION_DATA_TITLE }}</p>
        <p class="text-xs mt-1">
          {{ LABELS.NO_ROTATION_DATA_DESC }}
        </p>
      </div>
    </div>
  </BaseDialog>
</template>
