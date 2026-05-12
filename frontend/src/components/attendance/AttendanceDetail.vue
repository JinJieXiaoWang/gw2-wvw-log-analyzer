<template>
  <div class="attendance-detail-page bg-surface-900">
    <LoadingState
      v-if="loading"
      text="加载详情中..."
      class="min-h-screen flex items-center justify-center"
    />

    <template v-else>
      <!-- Header -->
      <div class="relative overflow-hidden bg-gradient-to-r from-primary/20 via-secondary/10 to-primary/20">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(22,93,255,0.1)_0%,_transparent_70%)]" />
        <div class="relative container mx-auto px-4 py-8">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div class="flex items-center gap-4">
              <div class="relative">
                <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 border-2 border-primary/30">
                  <span class="text-3xl font-bold text-white">{{ data?.account?.charAt(0) || '?' }}</span>
                </div>
                <div class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-status-success border-2 border-surface-900 flex items-center justify-center">
                  <i class="pi pi-check text-white text-xs" />
                </div>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-white mb-1">
                  {{ data?.account || '未知玩家' }}
                </h1>
                <p class="text-neutral-text-secondary text-sm">
                  <span class="flex items-center gap-2"><i class="pi pi-server text-primary" /><span>{{ data?.server || '未知服务器' }}</span></span>
                </p>
                <div class="flex items-center gap-4 mt-2">
                  <span
                    v-if="data?.rank"
                    class="text-xs px-3 py-1 rounded-full bg-primary/20 text-primary font-medium"
                  >{{ data.rank }}</span>
                  <span class="text-xs px-3 py-1 rounded-full bg-secondary/20 text-secondary font-medium">加入 {{ data?.join_date || '--' }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <BaseButton
                label="查看评分规则"
                icon="pi pi-chart-line"
                class="btn-ghost"
                size="small"
                @click="showScoringModal = true"
              />
              <BaseButton
                label="导出Excel"
                icon="pi pi-file-excel"
                class="btn-game"
                severity="secondary"
                @click="exportExcel"
              />
              <BaseButton
                label="导出CSV"
                icon="pi pi-file-pdf"
                class="btn-game"
                @click="exportCSV"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatCard
            icon="pi pi-calendar-check"
            label="出勤天数"
            :value="summary.attendance_count || 0"
            unit="天"
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
            v-bind="kdStyle"
          />
          <StatCard
            icon="pi pi-trophy"
            label="平均评分"
            :value="summary.avg_score || 0"
            v-bind="scoreStyle"
          />
        </div>
      </div>

      <!-- Charts -->
      <AttendanceCharts
        :detail-data="data"
        @time-range-change="handleTimeRangeChange"
      />

      <!-- Characters & Fights -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AttendanceCharactersPanel
            :characters="characters"
            @select="showCharDetail"
          />
          <AttendanceFightsPanel :fights="recentFights" />
        </div>
      </div>

      <div
        v-if="!data"
        class="min-h-screen flex items-center justify-center"
      >
        <EmptyState
          icon="pi pi-inbox"
          title="暂无数据"
          description="请选择一个玩家查看详情"
        />
      </div>
    </template>

    <AttendanceCharDialog
      v-model:visible="showCharModal"
      :character="selectedCharacter"
      :fights="characterFights"
    />

    <BaseDialog
      v-if="showScoringModal"
      :visible="showScoringModal"
      header="评分规则"
      style-class="w-full max-w-3xl"
      @update:visible="showScoringModal = false"
    >
      <div class="p-4">
        <p class="text-neutral-text-secondary text-sm mb-4">
          评分规则说明...
        </p>
      </div>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import EmptyState from '@/components/common/ui/display/EmptyState.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import StatCard from './detail/StatCard.vue'
import AttendanceCharts from './detail/AttendanceCharts.vue'
import AttendanceCharactersPanel from './detail/AttendanceCharactersPanel.vue'
import AttendanceFightsPanel from './detail/AttendanceFightsPanel.vue'
import AttendanceCharDialog from './detail/AttendanceCharDialog.vue'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getScoreColor, formatNumber, formatDps, formatDateTime, formatDuration } from '@/utils/common/attendanceFormatters'

const toast = useToast()
const props = defineProps<{ data?: any; loading?: boolean }>()

const showAllChars = ref(false)
const showAllFights = ref(false)
const showCharModal = ref(false)
const showScoringModal = ref(false)
const selectedCharacter = ref<any>(null)
const timeRange = ref('7d')

const { summary, characters, recentFights } = useAttendanceDetail(() => props.data)

const characterFights = computed(() => {
  if (!selectedCharacter.value) return []
  const name = selectedCharacter.value.character_name
  return recentFights.value.filter((f: any) => f.character_name === name).slice(0, 5)
})

function showCharDetail(char: any) {
  selectedCharacter.value = char
  showCharModal.value = true
}

function handleTimeRangeChange(val: string) {
  toast.add({ severity: 'info', summary: '时间范围已更新', detail: `已切换到${val}`, life: 3000 })
}

function exportExcel() {
  toast.add({ severity: 'success', summary: '导出成功', detail: 'Excel文件已下载', life: 3000 })
}

function exportCSV() {
  toast.add({ severity: 'success', summary: '导出成功', detail: 'CSV文件已下载', life: 3000 })
}

const cardStyles: Record<string, any> = {
  primary: { gradient: 'from-primary/20 to-primary/5', border: 'border-primary/30', iconBg: 'from-primary/40 to-primary/20', textColor: 'text-primary' },
  secondary: { gradient: 'from-secondary/20 to-secondary/5', border: 'border-secondary/30', iconBg: 'from-secondary/40 to-secondary/20', textColor: 'text-secondary' },
  error: { gradient: 'from-status-error/20 to-status-error/5', border: 'border-status-error/30', iconBg: 'from-status-error/40 to-status-error/20', textColor: 'text-status-error' },
  success: { gradient: 'from-status-success/20 to-status-success/5', border: 'border-status-success/30', iconBg: 'from-status-success/40 to-status-success/20', textColor: 'text-status-success' },
  warning: { gradient: 'from-status-warning/20 to-status-warning/5', border: 'border-status-warning/30', iconBg: 'from-status-warning/40 to-status-warning/20', textColor: 'text-status-warning' },
}

function getCardStyle(color: string) {
  return cardStyles[color]
}

const kdStyle = computed(() => {
  const r = summary.value.kd_ratio
  if (r >= 2) return getCardStyle('success')
  if (r >= 1) return getCardStyle('primary')
  return getCardStyle('error')
})

const scoreStyle = computed(() => {
  const s = summary.value.avg_score
  if (s >= 85) return getCardStyle('success')
  if (s >= 70) return getCardStyle('primary')
  if (s >= 50) return getCardStyle('warning')
  return getCardStyle('error')
})
</script>

<style scoped>
</style>
