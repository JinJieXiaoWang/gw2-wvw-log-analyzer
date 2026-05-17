<template>
  <div class="min-h-screen bg-neutral-bg py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="space-y-6">
        <!-- 页面头部 -->
        <div class="bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 rounded-xl p-4 sm:p-6 border border-primary/20">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-3">
                <router-link
                  to="/attendance"
                  class="p-2 rounded-lg bg-neutral-card/50 hover:bg-primary/10 transition-all duration-200 text-neutral-text-secondary hover:text-primary group"
                >
                  <i class="pi pi-arrow-left group-hover:translate-x-[-2px] transition-transform" />
                </router-link>
                <div>
                  <h1 class="text-2xl sm:text-3xl font-bold text-neutral-text tracking-tight">
                    {{ PAGE_TITLE }}
                  </h1>
                  <p class="text-neutral-text-secondary text-sm mt-1">
                    {{ account }} · {{ detailData?.summary?.server || SERVER_FALLBACK }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex flex-wrap gap-3">
              <BaseButton
                label="查看评分规则"
                icon="pi pi-chart-line"
                class="btn-ghost"
                size="small"
                @click="openScoringRules"
              />
              <BaseButton
                label="导出Excel"
                icon="pi pi-file-excel"
                severity="secondary"
                @click="exportExcel"
              />
              <BaseButton
                label="导出CSV"
                icon="pi pi-file-pdf"
                @click="exportCSV"
              />
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div
          v-if="loading"
          class="card flex items-center justify-center py-16 bg-neutral-card/50 border-neutral-border/50"
        >
          <div class="flex flex-col items-center gap-4">
            <div class="relative">
              <ProgressSpinner class="w-[50px] h-[50px]" />
              <div class="absolute inset-0 animate-ping opacity-20">
                <ProgressSpinner class="w-[50px] h-[50px]" />
              </div>
            </div>
            <span class="text-neutral-text-secondary font-medium">{{ LOADING_TEXT }}</span>
          </div>
        </div>

        <template v-else-if="detailData">
          <!-- 快速信息 -->
          <div class="card p-4 bg-gradient-to-r from-neutral-card to-neutral-bg-secondary border-neutral-border/50 rounded-xl">
            <div class="flex flex-wrap items-center justify-between gap-4">
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 border-2 border-primary/30">
                  <span class="text-2xl font-bold text-white">{{ account?.charAt(0) || DEFAULT_AVATAR_CHAR }}</span>
                </div>
                <div>
                  <h2 class="text-xl font-bold text-white">
                    {{ account }}
                  </h2>
                  <p class="text-neutral-text-secondary text-sm mt-1">
                    <span class="flex items-center gap-2">
                      <i class="pi pi-server text-primary" />
                      <span>{{ detailData?.summary?.server || SERVER_FALLBACK }}</span>
                    </span>
                  </p>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-6">
                <div class="flex items-center gap-2 group cursor-pointer transition-colors hover:text-primary">
                  <div class="p-2 rounded-lg transition-colors bg-primary/10 group-hover:bg-primary/20">
                    <i class="pi pi-calendar-check text-primary" />
                  </div>
                  <div>
                    <p class="text-xs text-neutral-text-secondary">
                      {{ LABELS.ATTENDANCE_DAYS }}
                    </p>
                    <p class="text-sm font-semibold text-neutral-text">
                      {{ summary.attendance_count || 0 }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2 group cursor-pointer transition-colors hover:text-secondary">
                  <div class="p-2 rounded-lg transition-colors bg-secondary/10 group-hover:bg-secondary/20">
                    <i class="pi pi-clock text-secondary" />
                  </div>
                  <div>
                    <p class="text-xs text-neutral-text-secondary">
                      {{ LABELS.TOTAL_DURATION }}
                    </p>
                    <p class="text-sm font-semibold text-neutral-text">
                      {{ formatDuration(summary.total_duration_sec || 0) }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2 group cursor-pointer transition-colors hover:text-status-error">
                  <div class="p-2 rounded-lg transition-colors bg-status-error/10 group-hover:bg-status-error/20">
                    <i class="pi pi-bolt text-status-error" />
                  </div>
                  <div>
                    <p class="text-xs text-neutral-text-secondary">
                      {{ LABELS.TOTAL_DAMAGE }}
                    </p>
                    <p class="text-sm font-semibold text-neutral-text">
                      {{ formatNumber(summary.total_damage || 0) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 统计卡片 -->
          <div class="container mx-auto px-4 py-6">
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              <StatCard
                icon="pi pi-calendar-check"
                :label="LABELS.ATTENDANCE_DAYS"
                :value="summary.attendance_count || 0"
                v-bind="getCardStyle('primary')"
              />
              <StatCard
                icon="pi pi-clock"
                :label="LABELS.TOTAL_DURATION"
                :value="formatDuration(summary.total_duration_sec)"
                v-bind="getCardStyle('secondary')"
              />
              <StatCard
                icon="pi pi-bolt"
                :label="LABELS.TOTAL_DAMAGE"
                :value="formatNumber(summary.total_damage)"
                v-bind="getCardStyle('error')"
              />
              <StatCard
                icon="pi pi-heart-pulse"
                label="K/D"
                :value="summary.kd_ratio || '0.0'"
                v-bind="kdCardStyle"
              />
            </div>
          </div>

          <!-- 角色评分卡片 -->
          <div
            v-if="characters.length > 0"
            class="container mx-auto px-4 py-4"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="char in characters"
                :key="char.character_name"
                class="card p-4 rounded-xl border border-neutral-border/50 bg-gradient-to-br from-neutral-card to-neutral-bg-secondary cursor-pointer hover:border-primary/40 transition-all"
                @click="showCharDetail(char)"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center text-white text-sm font-bold">
                      {{ char.character_name?.charAt(0) || '?' }}
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-text">
                        {{ char.character_name }}
                      </p>
                      <p class="text-xs text-neutral-text-secondary">
                        {{ char.profession }}
                      </p>
                    </div>
                  </div>
                  <div
                    class="flex flex-col items-end cursor-pointer"
                    @click.stop="openScoreBreakdown(char)"
                  >
                    <span
                      :class="{
                        'text-status-success font-bold': char.avg_score >= 85,
                        'text-primary font-semibold': char.avg_score >= 70 && char.avg_score < 85,
                        'text-status-warning': char.avg_score >= 60 && char.avg_score < 70,
                        'text-status-error': char.avg_score < 60
                      }"
                    >
                      {{ char.score_grade }}
                    </span>
                    <span class="text-xs text-neutral-text-secondary">{{ char.avg_score }}分</span>
                  </div>
                </div>
                <div class="mt-3 flex items-center gap-4 text-xs text-neutral-text-secondary">
                  <span>出勤{{ char.attendance_count }}天</span>
                  <span>伤害{{ formatNumber(char.total_damage) }}</span>
                  <span>K/D {{ char.kd_ratio }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 角色列表 -->
          <div class="container mx-auto px-4 py-6">
            <AttendanceCharactersPanel
              :characters="characters"
              @select="showCharDetail"
            />
          </div>

          <!-- 每日战斗日志 -->
          <div class="container mx-auto px-4 py-6">
            <DailyFightTimeline :daily-fights="dailyFights" />
          </div>
        </template>

        <!-- 弹窗 -->
        <ScoringRulesDialog
          v-model:visible="showScoringModal"
          v-model:active-tab="scoringRulesActiveTab"
          :loading="scoringRulesLoading"
          :rules-data="scoringRulesData"
          :rule-version="currentRuleVersion"
        />
        <AttendanceCharDialog
          v-model:visible="showCharModal"
          :character="selectedCharacter"
          :fights="characterFights"
        />
        <ScoreBreakdownDialog
          v-model:visible="showScoreBreakdownModal"
          :account="account"
          :profession="scoreBreakdownData?.most_used_profession_cn || selectedCharacter?.profession"
          :loading="scoreBreakdownLoading"
          :data="scoreBreakdownData"
        />
        <Toast />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import StatCard from '@/components/attendance/detail/StatCard.vue'

import AttendanceCharactersPanel from '@/components/attendance/detail/AttendanceCharactersPanel.vue'
import DailyFightTimeline from '@/components/attendance/detail/DailyFightTimeline.vue'
import AttendanceCharDialog from '@/components/attendance/detail/AttendanceCharDialog.vue'
import ScoringRulesDialog from '@/components/attendance/ScoringRulesDialog.vue'
import ScoreBreakdownDialog from '@/components/attendance/ScoreBreakdownDialog.vue'
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail'
import { attendanceService } from '@/services'
import { scoringRulesService } from '@/services/core/scoringRulesService'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatNumber, formatDuration, formatDateParam } from '@/utils/common/attendanceFormatters'

// === 常量定义 ===
const PAGE_TITLE = '出勤详情'
const SERVER_FALLBACK = '未知服务器'
const LOADING_TEXT = '加载出勤详情中...'
const DEFAULT_AVATAR_CHAR = '?'

const LABELS = {
  ATTENDANCE_DAYS: '出勤天数',
  TOTAL_DURATION: '总时长',
  TOTAL_DAMAGE: '总伤害',
} as const

const TOAST_MESSAGES = {
  SCORING_RULES_ERROR: '获取评分规则失败',
  TIME_RANGE_UPDATED: '时间范围已更新',
  TIME_RANGE_DETAIL_PREFIX: '已切换到',
  EXPORT_ERROR: '导出失败',
  FETCH_DETAIL_ERROR: '获取详情失败',
  ACCOUNT_NOT_FOUND: '未找到账号数据',
  ERROR_SUMMARY: '错误',
  WARN_SUMMARY: '提示',
} as const

const LIFE_TIME = {
  NORMAL: 3000,
  LONG: 5000,
} as const

const KD_THRESHOLDS = {
  EXCELLENT: 2,
  GOOD: 1,
} as const

const SLICE_LIMITS = {
  CHARACTER_FIGHTS: 5,
} as const

const route = useRoute()
const toast = useToast()
const account = computed(() => route.params.account as string)

const loading = ref(false)
const detailData = ref<any>(null)
const showCharModal = ref(false)
const showScoringModal = ref(false)
const showScoreBreakdownModal = ref(false)
const scoreBreakdownLoading = ref(false)
const scoreBreakdownData = ref<any>(null)
const selectedCharacter = ref<any>(null)
const dateRange = ref<[Date | null, Date | null]>([null, null])
const scoringRulesActiveTab = ref(0)
const scoringRulesLoading = ref(false)
const scoringRulesData = ref<Record<string, any>>({})
const currentRuleVersion = ref(0)

const { summary, characters, recentFights, dailyFights } = useAttendanceDetail(() => detailData.value)

const characterFights = computed(() => {
  if (!selectedCharacter.value) return []
  const name = selectedCharacter.value.character_name
  return recentFights.value.filter((f: any) => f.character_name === name).slice(0, SLICE_LIMITS.CHARACTER_FIGHTS)
})

// 卡片样式辅助
function getCardStyle(color: string) {
  const map: Record<string, any> = {
    primary: { theme: { gradient: 'from-primary/20 to-primary/5', border: 'border-primary/30', iconBg: 'from-primary/40 to-primary/20', textColor: 'text-primary' } },
    secondary: { theme: { gradient: 'from-secondary/20 to-secondary/5', border: 'border-secondary/30', iconBg: 'from-secondary/40 to-secondary/20', textColor: 'text-secondary' } },
    error: { theme: { gradient: 'from-status-error/20 to-status-error/5', border: 'border-status-error/30', iconBg: 'from-status-error/40 to-status-error/20', textColor: 'text-status-error' } },
    success: { theme: { gradient: 'from-status-success/20 to-status-success/5', border: 'border-status-success/30', iconBg: 'from-status-success/40 to-status-success/20', textColor: 'text-status-success' } },
    warning: { theme: { gradient: 'from-status-warning/20 to-status-warning/5', border: 'border-status-warning/30', iconBg: 'from-status-warning/40 to-status-warning/20', textColor: 'text-status-warning' } },
  }
  return map[color]
}

const kdCardStyle = computed(() => {
  const r = summary.value.kd_ratio
  if (r >= KD_THRESHOLDS.EXCELLENT) return getCardStyle('success')
  if (r >= KD_THRESHOLDS.GOOD) return getCardStyle('primary')
  return getCardStyle('error')
})

function showCharDetail(char: any) {
  selectedCharacter.value = char
  showCharModal.value = true
}

async function openScoreBreakdown(char: any) {
  showScoreBreakdownModal.value = true
  scoreBreakdownLoading.value = true
  scoreBreakdownData.value = null
  try {
    const startDate = dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null
    const endDate = dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null
    // 从 profession_service 获取英文职业名（后端需要英文 key）
    const professionEn = char.profession_en || char.profession
    const result = await ApiResponseWrapper.wrap(
      attendanceService.getAccountScoreBreakdown(account.value, professionEn, startDate, endDate),
      { showErrorMessage: true }
    )
    if (result.success && result.data) {
      scoreBreakdownData.value = result.data
    } else {
      toast.add({ severity: 'warn', summary: '提示', detail: '暂无该角色的评分数据', life: 3000 })
    }
  } catch (e: unknown) {
    toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '获取评分维度详情失败', life: 5000 })
  } finally {
    scoreBreakdownLoading.value = false
  }
}

function openScoringRules() {
  showScoringModal.value = true
  fetchScoringRules()
}

async function fetchScoringRules() {
  scoringRulesLoading.value = true
  try {
    const result = await scoringRulesService.getRules()
    if (result) scoringRulesData.value = result
    const versions = await scoringRulesService.getVersions(0, 1)
    if (versions?.length) currentRuleVersion.value = versions[0].version
  } catch (e) {
    toast.add({ severity: 'error', summary: TOAST_MESSAGES.ERROR_SUMMARY, detail: TOAST_MESSAGES.SCORING_RULES_ERROR, life: LIFE_TIME.LONG })
  } finally {
    scoringRulesLoading.value = false
  }
}

async function exportExcel() {
  if (!account.value) return
  try {
    await attendanceService.exportAccountDetail(account.value, 'excel', dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null, dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null)
  } catch {
    toast.add({ severity: 'error', summary: TOAST_MESSAGES.ERROR_SUMMARY, detail: TOAST_MESSAGES.EXPORT_ERROR, life: LIFE_TIME.NORMAL })
  }
}

async function exportCSV() {
  if (!account.value) return
  try {
    await attendanceService.exportAccountDetail(account.value, 'csv', dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null, dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null)
  } catch {
    toast.add({ severity: 'error', summary: TOAST_MESSAGES.ERROR_SUMMARY, detail: TOAST_MESSAGES.EXPORT_ERROR, life: LIFE_TIME.NORMAL })
  }
}

async function fetchAccountDetail() {
  if (!account.value) return
  loading.value = true
  try {
    const result = await attendanceService.getAccountDetail(account.value, dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null, dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null)
    if (result?.success && result.data) {
      detailData.value = result.data
    } else if (result && !result.success) {
      toast.add({ severity: 'error', summary: TOAST_MESSAGES.ERROR_SUMMARY, detail: result.message || TOAST_MESSAGES.FETCH_DETAIL_ERROR, life: LIFE_TIME.LONG })
    } else if (!result) {
      toast.add({ severity: 'warn', summary: TOAST_MESSAGES.WARN_SUMMARY, detail: TOAST_MESSAGES.ACCOUNT_NOT_FOUND, life: LIFE_TIME.LONG })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: TOAST_MESSAGES.ERROR_SUMMARY, detail: e?.message || TOAST_MESSAGES.FETCH_DETAIL_ERROR, life: LIFE_TIME.LONG })
  } finally {
    loading.value = false
  }
}

watch(dateRange, () => fetchAccountDetail(), { deep: true })
onMounted(() => fetchAccountDetail())
</script>

<style scoped>
</style>
