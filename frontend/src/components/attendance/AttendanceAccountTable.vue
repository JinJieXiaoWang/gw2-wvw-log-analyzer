<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30
                 flex items-center justify-center">
          <i class="pi pi-list text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            出勤账号列表
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            共 {{ pagination.total }} 个账号 · 按自然日去重统计
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
      @sort="onSort"
    >
      <Column
        field="account"
        header="账号"
        sortable
      >
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <div
              class="w-8 h-8 rounded-full bg-gradient-to-br from-primary/40 to-secondary/40 flex
                     items-center justify-center text-white text-xs font-bold">
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
          <span class="text-xs text-neutral-text-secondary ml-1">天</span>
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
              'text-status-success font-bold': data.kd_ratio >= 2,
              'text-primary font-semibold': data.kd_ratio >= 1 && data.kd_ratio < 2,
              'text-status-error': data.kd_ratio < 1
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
              'game-badge game-badge-legendary cursor-pointer hover:scale-110 transition-transform': data.avg_score >= 90,
              'game-badge game-badge-exotic cursor-pointer hover:scale-110 transition-transform': data.avg_score >= 80 && data.avg_score < 90,
              'game-badge game-badge-rare cursor-pointer hover:scale-110 transition-transform': data.avg_score >= 70 && data.avg_score < 80,
              'game-badge cursor-pointer hover:scale-110 transition-transform': data.avg_score < 70
            }"
            title="点击查看维度评分详情"
            @click="$emit('open-score-breakdown', data.account)"
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
            {{ data.last_attendance ? formatDate(data.last_attendance) : '-' }}
          </span>
        </template>
      </Column>

      <Column
        header="操作"
        style="width: 100px"
      >
        <template #body="{ data }">
          <BaseButton
            icon="pi pi-eye"
            variant="ghost"
            size="small"
            @click="$emit('open-detail', data.account)"
          />
        </template>
      </Column>
    </DataTable>

    <div class="flex items-center justify-between mt-4">
      <div class="text-sm text-neutral-text-secondary">
        显示 {{ accountList.length }} 条，共 {{ pagination.total }} 条
      </div>
      <Paginator
        :rows="pagination.pageSize"
        :total-records="pagination.total"
        :first="(pagination.page - 1) * pagination.pageSize"
        template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
        @page="onPageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤账号列表表格组件
 * 功能：显示账号出勤汇总数据列表
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { formatDate, formatDuration, formatNumber } from '@/utils/common/attendanceFormatters'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Paginator from 'primevue/paginator'
import Tag from 'primevue/tag'

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

export interface PaginationState {
  page: number
  pageSize: number
  total: number
}

defineProps<{
  accountList: AccountItem[]
  loading: boolean
  pagination: PaginationState
}>()

const emit = defineEmits<{
  'open-detail': [account: string]
  'open-score-breakdown': [account: string]
  'page-change': [event: { page: number }]
  'sort': [event: { sortField: string; sortOrder: number }]
}>()

const onPageChange = (event: any) => {
  emit('page-change', { page: (event.page || 0) + 1 })
}

const onSort = (event: any) => {
  emit('sort', event)
}
</script>
