<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-primary/10 via-transparent to-ai/10 rounded-xl p-6 border border-primary/20">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-3">
            <router-link
              to="/logs"
              class="p-2 rounded-lg bg-neutral-card/50 hover:bg-primary/10 transition-all duration-200 text-neutral-text-secondary hover:text-primary group"
            >
              <i class="pi pi-arrow-left group-hover:translate-x-[-2px] transition-transform" />
            </router-link>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-neutral-text tracking-tight">
                {{ PAGE_TITLE }}
              </h1>
              <p class="text-neutral-text-secondary text-sm mt-1">
                {{ logDetail.filename || LOG_DETAIL_FALLBACK }} · {{ fightSummary.map_name || MAP_NAME_FALLBACK }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <BaseButton
            v-permission="'write'"
            label="重新解析"
            icon="pi pi-refresh"
            :loading="parsing"
            class="transition-all duration-200 hover:shadow-lg hover:shadow-secondary/20"
            @click="reparseLog"
          />
        </div>
      </div>
    </div>

    <div
      v-if="loading"
      class="card flex items-center justify-center py-16 bg-neutral-card/50 border-neutral-border/50"
    >
      <div class="flex flex-col items-center gap-4">
        <div class="relative">
          <BaseProgressSpinner class="w-12 h-12" />
          <div class="absolute inset-0 animate-ping opacity-20">
            <BaseProgressSpinner class="w-12 h-12" />
          </div>
        </div>
        <span class="text-neutral-text-secondary font-medium">{{ LOADING_TEXT }}</span>
      </div>
    </div>
    <div
      v-else-if="error"
      class="card bg-error/10 border-error/30 text-error p-6 rounded-xl"
    >
      <div class="flex items-center gap-4">
        <div class="p-3 rounded-lg bg-error/20">
          <i class="pi pi-exclamation-triangle text-2xl" />
        </div>
        <div>
          <p class="font-semibold text-lg">
            {{ LOAD_ERROR_TITLE }}
          </p>
          <p class="text-sm text-error/80">
            {{ error }}
          </p>
        </div>
      </div>
    </div>

    <template v-else>
      <div class="card p-4 bg-gradient-to-r from-neutral-card to-neutral-bg-secondary border-neutral-border/50 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-6">
            <div
              v-for="item in quickInfoItems"
              :key="item.label"
              class="flex items-center gap-2 group cursor-pointer hover:text-primary transition-colors"
            >
              <div
                class="p-2 rounded-lg transition-colors"
                :class="item.iconBg"
              >
                <i :class="item.iconClass" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  {{ item.label }}
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ item.value }}
                </p>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <a
              v-if="summary?.dps_report_permalink"
              :href="summary.dps_report_permalink"
              target="_blank"
              class="no-underline"
            >
              <BaseTag
                :value="TAG_LABELS.EI_REPORT"
                icon="pi pi-external-link"
                severity="info"
                class="text-xs cursor-pointer hover:bg-info/30 transition-all"
              />
            </a>
            <BaseTag
              :value="`${TAG_LABELS.KILL_PREFIX}${fightSummary.kill_count || 0}`"
              severity="success"
              class="text-xs px-2 py-1"
            />
            <BaseTag
              :value="`${TAG_LABELS.DEATH_PREFIX}${fightSummary.death_count || 0}`"
              severity="danger"
              class="text-xs px-2 py-1"
            />
            <BaseTag
              v-if="agg.player_count"
              :value="`${TAG_LABELS.AVG_DPS_PREFIX}${fmtCompact(agg.avg_dps)}`"
              severity="info"
              class="text-xs px-2 py-1"
            />
          </div>
        </div>
      </div>

      <div class="card p-0 overflow-hidden">
        <TabMenu
          v-model:active-index="activeTab"
          :model="TAB_ITEMS"
        />
        <div class="p-5">
          <CombatOverviewTab
            v-if="activeTab === 0"
            :summary="summary"
            :agg="agg"
            :fight-summary="fightSummary"
            :stat-averages="statAverages"
            :donut="donut"
            :groups="groups"
            @open-stat-detail="openStatDetailDialog"
            @show-damage-detail="showDamageDetailDialog = true"
          />
          <CombatPlayerRankingTab
            v-if="activeTab === 1"
            :players="players"
            :sorted-player-list="sortedPlayerList"
            :groups="groups"
            :commanders="commanders"
            :ungrouped-players="ungroupedPlayers"
            :summary="summary"
            @row-click="onRowClick"
            @open-player-dialog="openPlayerDialog"
          />
        </div>
      </div>
    </template>
  </div>

  <DamageDetailDialog
    v-model:visible="showDamageDetailDialog"
    :donut="donut"
    :agg="agg"
    :top-dps-players="topDpsPlayers"
    :breakbar-pct="breakbarPct"
  />
  <StatDetailDialog
    v-model:visible="showStatDetailDialog"
    :title="statDetailTitle"
    :stat-detail-list="statDetailList"
    :stat-detail-average="statDetailAverage"
    :current-stat-type="currentStatType"
    :current-stat-category="currentStatCategory"
    @open-player-dialog="openPlayerDialog"
  />
  <CombatPlayerDetailDialog
    v-model:visible="dialogVisible"
    v-model:rotation-view-mode="rotationViewMode"
    :player="selectedPlayer"
    :has-player-detail-data="hasPlayerDetailData"
    :rotation-data="{ playerRotation, rotationLoading, sortedSkillCasts, top10SkillCasts, autoAttackRatio, weaponSwapCount, weaponSwapIntervals }"
    :timeline-data="{ timelineTicks, timelineTracks }"
    :heatmap-data="{ heatmapRows }"
    :cycle-data="{ skillCycles }"
    :tooltip-data="{ hoveredSkill, tooltipPosition }"
    @hover-skill="handleHoverSkill"
    @leave-skill="handleLeaveSkill"
    @mousemove="handleMouseMove"
  />

  <ConfirmDialog />
  <Toast />
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { fmtCompact } from '@/composables/combat/useCombatHelpers'
import { useStatDetail, CATEGORY_FIELDS, type StatCategory } from '@/composables/combat/useStatDetail'
import { usePlayerRotation } from '@/composables/combat/usePlayerRotation'
import { useCombatLogData } from '@/composables/combat/useCombatLogData'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import TabMenu from 'primevue/tabmenu'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import BaseProgressSpinner from '@/components/common/ui/display/BaseProgressSpinner.vue'

// 异步加载大型 combat detail 子组件，减少主 chunk 体积
const CombatOverviewTab = defineAsyncComponent(() => import('@/components/combat/detail/overview/CombatOverviewTab.vue'))
const CombatPlayerRankingTab = defineAsyncComponent(() => import('@/components/combat/detail/overview/CombatPlayerRankingTab.vue'))
const DamageDetailDialog = defineAsyncComponent(() => import('@/components/combat/detail/dialogs/DamageDetailDialog.vue'))
const StatDetailDialog = defineAsyncComponent(() => import('@/components/combat/detail/dialogs/StatDetailDialog.vue'))
const CombatPlayerDetailDialog = defineAsyncComponent(() => import('@/components/combat/detail/dialogs/CombatPlayerDetailDialog.vue'))

// === 常量定义 ===
const PAGE_TITLE = '战斗分析'
const LOG_DETAIL_FALLBACK = '日志详情'
const MAP_NAME_FALLBACK = '未知地图'
const LOADING_TEXT = '加载战斗数据中...'
const LOAD_ERROR_TITLE = '加载失败'

const TAB_ITEMS = [
  { label: '战斗概览', icon: 'pi pi-chart-bar' },
  { label: '玩家 & 小队', icon: 'pi pi-users' },
]

const TAG_LABELS = {
  EI_REPORT: 'EI报告',
  KILL_PREFIX: '击杀 ',
  DEATH_PREFIX: '死亡 ',
  AVG_DPS_PREFIX: '平均DPS ',
} as const

const TOOLTIP_DIMENSIONS = {
  WIDTH: 220,
  HEIGHT: 120,
  OFFSET: 15,
  FLIP_OFFSET: 20,
  MIN_POSITION: 15,
} as const

const activeTab = ref(0)
const showDamageDetailDialog = ref(false)
const showStatDetailDialog = ref(false)
const rotationViewMode = ref<'stats' | 'timeline' | 'heatmap' | 'cycle'>('stats')
const hoveredSkill = ref<any>(null)
const tooltipPosition = ref<{ x: number; y: number } | null>(null)
const currentStatType = ref<StatCategory>('protection')
const currentStatCategory = ref<string[]>([])
const statDetailTitle = ref('')

const {
  loading, parsing, error, logDetail, summary, selectedPlayer, playerRotation, rotationLoading, dialogVisible,
  fightSummary, agg, players, topDpsPlayers, commanders, groups, ungroupedPlayers, sortedPlayerList, quickInfoItems,
  reparseLog, openPlayerDialog
} = useCombatLogData()

const statAverages = computed(() => summary.value?.stat_averages || { protection: 0, stability: 0, hitRate: 100, skillCastUptime: 0, stackDist: 0, distToCom: 0 })
const donut = computed(() => summary.value?.donut || { pd: '0 264', cd: '0 264', bd: '0 264', co: 0, bo: 0, total: 0, p: 0, c: 0, b: 0 })
const breakbarPct = computed(() => summary.value?.percentages?.breakbar || 0)

const { statDetailList, statDetailAverage } = useStatDetail(players, currentStatType, currentStatCategory)
const { sortedSkillCasts, top10SkillCasts, autoAttackRatio, weaponSwapCount, weaponSwapIntervals, hasPlayerDetailData, timelineTicks, timelineTracks, heatmapRows, skillCycles } = usePlayerRotation(playerRotation, fightSummary)

const openStatDetailDialog = (type: string, title: string) => {
  currentStatType.value = type as StatCategory
  statDetailTitle.value = title
  const cfg = CATEGORY_FIELDS[type as StatCategory]
  currentStatCategory.value = cfg ? cfg.fields : [type]
  showStatDetailDialog.value = true
}

const onRowClick = (event: any) => {
  const player = event.data
  if (player) openPlayerDialog(player)
}

const handleHoverSkill = (skill: any) => { hoveredSkill.value = skill }
const handleLeaveSkill = () => { hoveredSkill.value = null; tooltipPosition.value = null }

const handleMouseMove = (event: MouseEvent) => {
  const tooltipWidth = TOOLTIP_DIMENSIONS.WIDTH
  const tooltipHeight = TOOLTIP_DIMENSIONS.HEIGHT
  let x = event.clientX + TOOLTIP_DIMENSIONS.OFFSET
  let y = event.clientY + TOOLTIP_DIMENSIONS.OFFSET
  const maxX = window.innerWidth - tooltipWidth - TOOLTIP_DIMENSIONS.OFFSET
  const maxY = window.innerHeight - tooltipHeight - TOOLTIP_DIMENSIONS.OFFSET
  if (x > maxX) x = event.clientX - tooltipWidth - TOOLTIP_DIMENSIONS.FLIP_OFFSET
  if (y > maxY) y = event.clientY - tooltipHeight - TOOLTIP_DIMENSIONS.FLIP_OFFSET
  tooltipPosition.value = { x: Math.max(TOOLTIP_DIMENSIONS.MIN_POSITION, Math.min(x, maxX)), y: Math.max(TOOLTIP_DIMENSIONS.MIN_POSITION, Math.min(y, maxY)) }
}
</script>
