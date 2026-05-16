<template>
  <!-- 动态值，无法使用 Tailwind 静态类 -->
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
          <i class="pi pi-list text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            {{ TABLE_TITLE }}
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            {{ TABLE_SUBTITLE_PREFIX }}{{ pagination.total }}{{ TABLE_SUBTITLE_SUFFIX }}
          </p>
        </div>
      </div>
    </div>

    <DataTable
      :value="accountList"
      :loading="loading"
      class="w-full game-table"
      removable-sort
      sort-field="attendance_count"
      :sort-order="-1"
      @sort="handleSort"
    >
      <Column
        field="account"
        header="账号"
        sortable
      >
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary/40 to-secondary/40 flex items-center justify-center text-white text-xs font-bold">
              {{ data.account.charAt(0).toUpperCase() }}
            </div>
            <span class="font-medium text-neutral-text">{{ data.account }}</span>
          </div>
        </template>
      </Column>

      <Column
        field="character_count"
        header="角色数"
        sortable
      >
        <template #body="{ data }">
          <Tag
            :value="String(data.character_count)"
            severity="info"
            class="game-badge"
          />
        </template>
      </Column>

      <Column
        field="attendance_count"
        header="出勤次数"
        sortable
      >
        <template #body="{ data }">
          <span class="text-primary font-bold">{{ data.attendance_count }}</span>
          <span class="text-xs text-neutral-text-secondary ml-1">{{ ATTENDANCE_UNIT }}</span>
        </template>
      </Column>

      <Column
        field="total_duration_sec"
        header="总时长"
        sortable
      >
        <template #body="{ data }">
          {{ formatDuration(data.total_duration_sec) }}
        </template>
      </Column>

      <Column
        field="total_damage"
        header="总伤害"
        sortable
      >
        <template #body="{ data }">
          <span class="text-status-error font-semibold">{{ formatNumber(data.total_damage) }}</span>
        </template>
      </Column>

      <Column
        field="total_downed"
        header="击倒人数"
        sortable
      >
        <template #body="{ data }">
          <span class="text-warning font-semibold">{{ data.total_downed }}</span>
        </template>
      </Column>

      <Column
        field="total_kills"
        header="击杀"
        sortable
      >
        <template #body="{ data }">
          <span class="text-secondary font-semibold">{{ data.total_kills }}</span>
        </template>
      </Column>

      <Column
        field="total_deaths"
        header="死亡"
        sortable
      >
        <template #body="{ data }">
          <span class="text-status-error font-semibold">{{ data.total_deaths }}</span>
        </template>
      </Column>

      <Column
        field="kd_ratio"
        header="K/D"
        sortable
      >
        <template #body="{ data }">
          <span
            :class="{
              'text-status-success font-bold': data.kd_ratio >= KD_RATIO_THRESHOLDS.EXCELLENT,
              'text-primary font-semibold': data.kd_ratio >= KD_RATIO_THRESHOLDS.GOOD && data.kd_ratio < KD_RATIO_THRESHOLDS.EXCELLENT,
              'text-status-error': data.kd_ratio < KD_RATIO_THRESHOLDS.GOOD
            }"
          >
            {{ data.kd_ratio }}
          </span>
        </template>
      </Column>

      <Column
        field="avg_score"
        header="平均评分"
        sortable
      >
        <template #body="{ data }">
          <span
            :class="{
              'game-badge game-badge-legendary cursor-pointer hover:scale-110 transition-transform': data.avg_score >= SCORE_THRESHOLDS.LEGENDARY,
              'game-badge game-badge-exotic cursor-pointer hover:scale-110 transition-transform': data.avg_score >= SCORE_THRESHOLDS.EXOTIC && data.avg_score < SCORE_THRESHOLDS.LEGENDARY,
              'game-badge game-badge-rare cursor-pointer hover:scale-110 transition-transform': data.avg_score >= SCORE_THRESHOLDS.RARE && data.avg_score < SCORE_THRESHOLDS.EXOTIC,
              'game-badge cursor-pointer hover:scale-110 transition-transform': data.avg_score < SCORE_THRESHOLDS.RARE
            }"
            :title="SCORE_TOOLTIP"
            @click="handleScoreClick(data.account)"
          >
            {{ data.avg_score }}
          </span>
        </template>
      </Column>

      <Column
        field="last_attendance"
        header="最后出勤"
        sortable
      >
        <template #body="{ data }">
          <span class="text-sm text-neutral-text-secondary">
            {{ data.last_attendance ? formatDate(data.last_attendance) : NO_DATE_PLACEHOLDER }}
          </span>
        </template>
      </Column>

      <!-- 动态值，无法使用 Tailwind 静态类（PrimeVue Column API） -->
      <Column
        header="操作"
        style="width: 100px"
      >
        <template #body="{ data }">
          <BaseButton
            icon="pi pi-eye"
            variant="ghost"
            size="small"
            @click="handleDetailClick(data.account)"
          />
        </template>
      </Column>
    </DataTable>

    <div class="flex items-center justify-between mt-4">
      <div class="text-sm text-neutral-text-secondary">
        {{ getPaginationText(accountList.length, pagination.total) }}
      </div>
      <Paginator
        :rows="pagination.pageSize"
        :total-records="pagination.total"
        :first="(pagination.page - 1) * pagination.pageSize"
        template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
        @page="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 考勤数据表格组件
 * 功能：显示账号出勤列表，支持排序、分页、详情查看、评分查看
 * 作者：Claude
 * 创建日期：2026-05-11
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { formatDate, formatDuration, formatNumber } from '@/utils/common/attendanceFormatters'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Paginator from 'primevue/paginator'
import Tag from 'primevue/tag'

// === 常量定义 ===
const TABLE_TITLE = '出勤账号列表'
const TABLE_SUBTITLE_PREFIX = '共 '
const TABLE_SUBTITLE_SUFFIX = ' 个账号 · 按自然日去重统计'
const ATTENDANCE_UNIT = '天'
const SCORE_TOOLTIP = '点击查看维度评分详情'
const NO_DATE_PLACEHOLDER = '-'

const KD_RATIO_THRESHOLDS = {
  EXCELLENT: 2,
  GOOD: 1,
} as const

const SCORE_THRESHOLDS = {
  LEGENDARY: 90,
  EXOTIC: 80,
  RARE: 70,
} as const

const getPaginationText = (current: number, total: number): string =>
  `显示 ${current} 条，共 ${total} 条`

export interface AccountItem {
  account: string
  character_count: number
  attendance_count: number
  total_duration_sec: number
  total_damage: number
  total_downed: number
  total_kills: number
  total_deaths: number
  kd_ratio: number
  avg_score: number
  last_attendance: string | null
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
}

defineProps<{
  accountList: AccountItem[]
  pagination: Pagination
  loading: boolean
}>()

const emit = defineEmits<{
  'page-change': [event: { page: number }]
  'sort': [event: { sortField: string; sortOrder: number }]
  'detail-click': [account: string]
  'score-click': [account: string]
}>()

const handlePageChange = (event: { page: number }) => emit('page-change', event)
const handleSort = (event: any) => emit('sort', { sortField: event.sortField, sortOrder: event.sortOrder })
const handleDetailClick = (account: string) => emit('detail-click', account)
const handleScoreClick = (account: string) => emit('score-click', account)
</script>
