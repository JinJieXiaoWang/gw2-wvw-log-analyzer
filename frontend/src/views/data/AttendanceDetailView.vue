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
                出勤详情
              </h1>
              <p class="text-neutral-text-secondary text-sm mt-1">
                {{ account }} · {{ detailData?.summary?.server || '未知服务器' }}
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
          <ProgressSpinner style="width: 50px; height: 50px" />
          <div class="absolute inset-0 animate-ping opacity-20">
            <ProgressSpinner style="width: 50px; height: 50px" />
          </div>
        </div>
        <span class="text-neutral-text-secondary font-medium">加载出勤详情中...</span>
      </div>
    </div>

    <template v-else-if="detailData">
      <!-- 快速信息 -->
      <div class="card p-4 bg-gradient-to-r from-neutral-card to-neutral-bg-secondary border-neutral-border/50 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 border-2 border-primary/30">
              <span class="text-2xl font-bold text-white">{{ account?.charAt(0) || '?' }}</span>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">
                {{ account }}
              </h2>
              <p class="text-neutral-text-secondary text-sm mt-1">
                <span class="flex items-center gap-2">
                  <i class="pi pi-server text-primary" />
                  <span>{{ detailData?.summary?.server || '未知服务器' }}</span>
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
                  出勤天数
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
                  总时长
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
                  总伤害
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ formatNumber(summary.total_damage || 0) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 group cursor-pointer transition-colors hover:text-status-success">
              <div class="p-2 rounded-lg transition-colors bg-status-success/10 group-hover:bg-status-success/20">
                <i class="pi pi-trophy text-status-success" />
              </div>
              <div>
                <p class="text-xs text-neutral-text-secondary">
                  平均评分
                </p>
                <p class="text-sm font-semibold text-neutral-text">
                  {{ summary.avg_score || 0 }}
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
            label="出勤天数"
            :value="summary.attendance_count || 0"
            v-bind="getCardStyle('primary')"
          />
          <StatCard
            icon="pi pi-clock"
            label="总参战时长"
            :value="formatDuration(summary.total_duration_sec)"
            v-bind="getCardStyle('secondary')"
          />
          <StatCard
            icon="pi pi-bolt"
            label="总伤害"
            :value="formatNumber(summary.total_damage)"
            v-bind="getCardStyle('error')"
          />
          <StatCard
            icon="pi pi-heart-pulse"
            label="K/D"
            :value="summary.kd_ratio || '0.0'"
            v-bind="kdCardStyle"
          />
          <StatCard
            icon="pi pi-trophy"
            label="平均评分"
            :value="summary.avg_score || 0"
            v-bind="scoreCardStyle"
          />
        </div>
      </div>

      <!-- 图表 -->
      <AttendanceCharts
        :detail-data="detailData"
        @time-range-change="handleTimeRangeChange"
      />

      <!-- 角色和战斗 -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AttendanceCharactersPanel
            :characters="characters"
            @select="showCharDetail"
          />
          <AttendanceFightsPanel :fights="recentFights" />
        </div>
      </div>
    </template>

    <!-- 弹窗 -->
    <ScoringRulesDialog
      v-model:visible="showScoringModal"
      v-model:active-tab="scoringRulesActiveTab"
      :loading="scoringRulesLoading"
      :rules-data="scoringRulesData"
      :rule-version="currentRuleVersion"
      :role-type="currentRoleType"
    />
    <AttendanceCharDialog
      v-model:visible="showCharModal"
      :character="selectedCharacter"
      :fights="characterFights"
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
import AttendanceCharts from '@/components/attendance/detail/AttendanceCharts.vue'
import AttendanceCharactersPanel from '@/components/attendance/detail/AttendanceCharactersPanel.vue'
import AttendanceFightsPanel from '@/components/attendance/detail/AttendanceFightsPanel.vue'
import AttendanceCharDialog from '@/components/attendance/detail/AttendanceCharDialog.vue'
import ScoringRulesDialog from '@/components/attendance/ScoringRulesDialog.vue'
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail'
import { attendanceService } from '@/services'
import { scoringRulesService } from '@/services/core/scoringRulesService'
import { formatNumber, formatDuration, formatDateParam } from '@/utils/common/attendanceFormatters'

const route = useRoute()
const toast = useToast()
const account = computed(() => route.params.account as string)

const loading = ref(false)
const detailData = ref<any>(null)
const showCharModal = ref(false)
const showScoringModal = ref(false)
const selectedCharacter = ref<any>(null)
const dateRange = ref<[Date | null, Date | null]>([null, null])
const scoringRulesActiveTab = ref(0)
const scoringRulesLoading = ref(false)
const scoringRulesData = ref<Record<string, any>>({})
const currentRuleVersion = ref(0)
const currentRoleType = ref('dps')

const { summary, characters, recentFights } = useAttendanceDetail(() => detailData.value)

const characterFights = computed(() => {
  if (!selectedCharacter.value) return []
  const name = selectedCharacter.value.character_name
  return recentFights.value.filter((f: any) => f.character_name === name).slice(0, 5)
})

// 卡片样式辅助
function getCardStyle(color: string) {
  const map: Record<string, any> = {
    primary: { gradient: 'from-primary/20 to-primary/5', border: 'border-primary/30', iconBg: 'from-primary/40 to-primary/20', textColor: 'text-primary' },
    secondary: { gradient: 'from-secondary/20 to-secondary/5', border: 'border-secondary/30', iconBg: 'from-secondary/40 to-secondary/20', textColor: 'text-secondary' },
    error: { gradient: 'from-status-error/20 to-status-error/5', border: 'border-status-error/30', iconBg: 'from-status-error/40 to-status-error/20', textColor: 'text-status-error' },
    success: { gradient: 'from-status-success/20 to-status-success/5', border: 'border-status-success/30', iconBg: 'from-status-success/40 to-status-success/20', textColor: 'text-status-success' },
    warning: { gradient: 'from-status-warning/20 to-status-warning/5', border: 'border-status-warning/30', iconBg: 'from-status-warning/40 to-status-warning/20', textColor: 'text-status-warning' },
  }
  return map[color]
}

const kdCardStyle = computed(() => {
  const r = summary.value.kd_ratio
  if (r >= 2) return getCardStyle('success')
  if (r >= 1) return getCardStyle('primary')
  return getCardStyle('error')
})

const scoreCardStyle = computed(() => {
  const s = summary.value.avg_score
  if (s >= 85) return getCardStyle('success')
  if (s >= 70) return getCardStyle('primary')
  if (s >= 50) return getCardStyle('warning')
  return getCardStyle('error')
})

function showCharDetail(char: any) {
  selectedCharacter.value = char
  showCharModal.value = true
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
    toast.add({ severity: 'error', summary: '错误', detail: '获取评分规则失败', life: 5000 })
  } finally {
    scoringRulesLoading.value = false
  }
}

function handleTimeRangeChange(val: string) {
  toast.add({ severity: 'info', summary: '时间范围已更新', detail: `已切换到${val}`, life: 3000 })
}

async function exportExcel() {
  if (!account.value) return
  try {
    await attendanceService.exportAccountDetail(account.value, 'excel', dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null, dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null)
  } catch {
    toast.add({ severity: 'error', summary: '错误', detail: '导出失败', life: 3000 })
  }
}

async function exportCSV() {
  if (!account.value) return
  try {
    await attendanceService.exportAccountDetail(account.value, 'csv', dateRange.value?.[0] ? formatDateParam(dateRange.value[0]) : null, dateRange.value?.[1] ? formatDateParam(dateRange.value[1]) : null)
  } catch {
    toast.add({ severity: 'error', summary: '错误', detail: '导出失败', life: 3000 })
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
      toast.add({ severity: 'error', summary: '错误', detail: result.message || '获取详情失败', life: 5000 })
    } else if (!result) {
      toast.add({ severity: 'warn', summary: '提示', detail: '未找到账号数据', life: 5000 })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取详情失败', life: 5000 })
  } finally {
    loading.value = false
  }
}

watch(dateRange, () => fetchAccountDetail(), { deep: true })
onMounted(() => fetchAccountDetail())
</script>

<style scoped>
</style>
