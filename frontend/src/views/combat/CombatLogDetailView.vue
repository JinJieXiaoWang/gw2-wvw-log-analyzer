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
                战斗分析
              </h1>
              <p class="text-neutral-text-secondary text-sm mt-1">
                {{ logDetail.filename || '日志详情' }} · {{ fightSummary.map_name || '未知地图' }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <Button
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
          <ProgressSpinner style="width: 50px; height: 50px" />
          <div class="absolute inset-0 animate-ping opacity-20">
            <ProgressSpinner style="width: 50px; height: 50px" />
          </div>
        </div>
        <span class="text-neutral-text-secondary font-medium">加载战斗数据中...</span>
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
            加载失败
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
              <Tag
                value="EI报告"
                icon="pi pi-external-link"
                severity="info"
                class="text-xs cursor-pointer hover:bg-info/30 transition-all"
              />
            </a>
            <Tag
              :value="`击杀 ${fightSummary.kill_count || 0}`"
              severity="success"
              class="text-xs px-2 py-1"
            />
            <Tag
              :value="`死亡 ${fightSummary.death_count || 0}`"
              severity="danger"
              class="text-xs px-2 py-1"
            />
            <Tag
              v-if="agg.player_count"
              :value="`平均DPS ${fmtCompact(agg.avg_dps)}`"
              severity="info"
              class="text-xs px-2 py-1"
            />
          </div>
        </div>
      </div>

      <div class="card p-0 overflow-hidden">
        <TabMenu
          v-model:active-index="activeTab"
          :model="tabItems"
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

  <CombatDamageDetailDialog
    v-model:visible="showDamageDetailDialog"
    :donut="donut"
    :agg="agg"
    :top-dps-players="topDpsPlayers"
    :breakbar-pct="breakbarPct"
  />
  <CombatStatDetailDialog
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
    :player-rotation="playerRotation"
    :rotation-loading="rotationLoading"
    :sorted-skill-casts="sortedSkillCasts"
    :has-player-detail-data="hasPlayerDetailData"
    :timeline-ticks="timelineTicks"
    :timeline-tracks="timelineTracks"
    :heatmap-rows="heatmapRows"
    :skill-cycles="skillCycles"
    :hovered-skill="hoveredSkill"
    :tooltip-position="tooltipPosition"
    @hover-skill="handleHoverSkill"
    @leave-skill="handleLeaveSkill"
    @mousemove="handleMouseMove"
  />

  <ConfirmDialog />
  <Toast />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { fmtCompact } from '@/composables/combat/useCombatHelpers'
import { useStatDetail, CATEGORY_FIELDS, type StatCategory } from '@/composables/combat/useStatDetail'
import { usePlayerRotation } from '@/composables/combat/usePlayerRotation'
import { useCombatLogData } from '@/composables/combat/useCombatLogData'
import Button from 'primevue/button'
import TabMenu from 'primevue/tabmenu'
import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'
import CombatOverviewTab from '@/components/combat/detail/overview/CombatOverviewTab.vue'
import CombatPlayerRankingTab from '@/components/combat/detail/overview/CombatPlayerRankingTab.vue'
import CombatDamageDetailDialog from '@/components/combat/detail/dialogs/CombatDamageDetailDialog.vue'
import CombatStatDetailDialog from '@/components/combat/detail/dialogs/CombatStatDetailDialog.vue'
import CombatPlayerDetailDialog from '@/components/combat/detail/dialogs/CombatPlayerDetailDialog.vue'

const activeTab = ref(0)
const showDamageDetailDialog = ref(false)
const showStatDetailDialog = ref(false)
const rotationViewMode = ref<'stats' | 'timeline' | 'heatmap' | 'cycle'>('stats')
const hoveredSkill = ref<any>(null)
const tooltipPosition = ref<{ x: number; y: number } | null>(null)
const currentStatType = ref<StatCategory>('protection')
const currentStatCategory = ref<string[]>([])
const statDetailTitle = ref('')

const tabItems = [
  { label: '战斗概览', icon: 'pi pi-chart-bar' },
  { label: '玩家 & 小队', icon: 'pi pi-users' },
]

const {
  loading, parsing, error, logDetail, summary, selectedPlayer, playerRotation, rotationLoading, dialogVisible,
  fightSummary, agg, players, topDpsPlayers, commanders, groups, ungroupedPlayers, sortedPlayerList, quickInfoItems,
  reparseLog, openPlayerDialog
} = useCombatLogData()

const statAverages = computed(() => summary.value?.stat_averages || { protection: 0, stability: 0, hitRate: 100, skillCastUptime: 0, stackDist: 0, distToCom: 0 })
const donut = computed(() => summary.value?.donut || { pd: '0 264', cd: '0 264', bd: '0 264', co: 0, bo: 0, total: 0, p: 0, c: 0, b: 0 })
const breakbarPct = computed(() => summary.value?.percentages?.breakbar || 0)

const { statDetailList, statDetailAverage } = useStatDetail(players, currentStatType, currentStatCategory)
const { sortedSkillCasts, hasPlayerDetailData, timelineTicks, timelineTracks, heatmapRows, skillCycles } = usePlayerRotation(playerRotation, fightSummary)

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
  const tooltipWidth = 220
  const tooltipHeight = 120
  let x = event.clientX + 15
  let y = event.clientY + 15
  const maxX = window.innerWidth - tooltipWidth - 15
  const maxY = window.innerHeight - tooltipHeight - 15
  if (x > maxX) x = event.clientX - tooltipWidth - 20
  if (y > maxY) y = event.clientY - tooltipHeight - 20
  tooltipPosition.value = { x: Math.max(15, Math.min(x, maxX)), y: Math.max(15, Math.min(y, maxY)) }
}
</script>
