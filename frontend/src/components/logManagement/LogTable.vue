<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <!-- 已选提示栏 -->
    <div
      v-if="selectedLogs.length > 0"
      class="flex items-center justify-between px-4 py-2 bg-primary/5 border-b border-primary/10 rounded-t-xl"
    >
      <div class="flex items-center gap-2">
        <i class="pi pi-check-circle text-primary text-sm" />
        <span class="text-sm text-neutral-text">
          已选择 <span class="text-primary font-bold">{{ selectedLogs.length }}</span> 项
          <span class="text-neutral-text-secondary text-xs ml-1">（跨页累加）</span>
        </span>
      </div>
      <Button
        icon="pi pi-times"
        label="清除"
        size="small"
        text
        severity="secondary"
        class="text-xs"
        @click="clearSelection"
      />
    </div>

    <DataTable
      v-model:selection="selectedLogs"
      :value="filteredLogs"
      data-key="id"
      :paginator="true"
      :rows="pageSize || 10"
      :rows-per-page-options="[10, 20, 50]"
      :total-records="totalRecords"
      :first="first || 0"
      :lazy="true"
      striped-rows
      :loading="isLoading"
      removable-sort
      sort-field="uploadTime"
      :sort-order="-1"
      class="w-full"
      :select-all="selectAllState"
      @row-select="onRowSelect"
      @row-unselect="onRowUnselect"
      @select-all-change="onSelectAllChange"
      @page="onPage"
    >
      <template #empty>
        <EmptyState
          icon="pi pi-inbox"
          title="暂无日志文件"
          description="请通过上方按钮上传战斗日志"
          :show-action="false"
        />
      </template>

      <Column
        selection-mode="multiple"
        header-style="width: 3rem"
      />

      <Column
        field="fileName"
        header="文件名"
        sortable
        style="min-width: 200px"
      >
        <template #body="{ data }">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center transition-transform hover:scale-105"
              :class="getRarityClass(data.status)"
            >
              <i class="pi pi-file text-white text-lg" />
            </div>
            <div class="min-w-0">
              <p
                class="text-neutral-text font-medium truncate"
                :title="data.fileName"
              >
                {{ data.fileName }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                SHA256: {{ data.fileSha256 ? data.fileSha256.substring(0, 12) + '...' : '-' }}
              </p>
            </div>
          </div>
        </template>
      </Column>

      <Column
        field="status"
        header="状态"
        sortable
        style="min-width: 100px"
      >
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span
              class="status-dot"
              :class="getStatusDotClass(data.status)"
            />
            <span
              class="game-badge"
              :class="getStatusBadgeClass(data.status)"
            >
              {{ data.statusText }}
            </span>
          </div>
        </template>
      </Column>

      <Column
        field="fileSize"
        header="原始大小"
        sortable
        style="min-width: 100px"
      >
        <template #body="{ data }">
          <span class="text-neutral-text-secondary">{{ formatFileSize(data.fileSize) }}</span>
        </template>
      </Column>

      <Column
        field="compressedSize"
        header="压缩大小"
        sortable
        style="min-width: 100px"
        class="hidden md:table-cell"
      >
        <template #body="{ data }">
          <span class="text-neutral-text-secondary">{{ formatFileSize(data.compressedSize) }}</span>
        </template>
      </Column>

      <Column
        field="parseTime"
        header="解析耗时"
        sortable
        style="min-width: 100px"
        class="hidden lg:table-cell"
      >
        <template #body="{ data }">
          <span class="text-neutral-text-secondary">{{ data.parseTime }}</span>
        </template>
      </Column>

      <Column
        field="uploadTime"
        header="上传时间"
        sortable
        style="min-width: 150px"
      >
        <template #body="{ data }">
          <span class="text-neutral-text-secondary text-xs">{{ data.uploadTime }}</span>
        </template>
      </Column>

      <Column
        field="uploadIp"
        header="上传IP"
        style="min-width: 100px"
        class="hidden xl:table-cell"
      >
        <template #body="{ data }">
          <span class="text-neutral-text-secondary text-xs">{{ data.uploadIp }}</span>
        </template>
      </Column>

      <Column
        header="操作"
        style="min-width: 200px"
        header-style="width: 200px"
      >
        <template #body="{ data }">
          <div class="table-actions flex items-center gap-3">
            <a
              v-if="data.dpsReportPermalink"
              :href="data.dpsReportPermalink"
              target="_blank"
              class="no-underline"
            >
              <Button
                v-tooltip.top="'查看 EI 报告'"
                icon="pi pi-external-link"
                size="small"
                text
                class="action-btn action-btn-ei"
              />
            </a>
            <Button
              :v-tooltip.top="data.status === 'pending' ? '数据尚未解析入库，暂时无法查看详情' : '查看详情'"
              icon="pi pi-eye"
              size="small"
              text
              class="action-btn action-btn-view"
              :disabled="data.status === 'pending'"
              :class="{ 'opacity-50 cursor-not-allowed': data.status === 'pending' }"
              @click="viewLogDetail(data)"
            />
            <Button
              v-permission="'write'"
              v-tooltip.top="'解析'"
              :icon="parsingLogs.includes(data.id) ? '' : 'pi pi-play'"
              size="small"
              text
              class="action-btn action-btn-parse"
              :disabled="data.status === 'parsing' || parsingLogs.includes(data.id)"
              :loading="parsingLogs.includes(data.id)"
              @click="parseLog(data)"
            />
            <Button
              v-permission="'delete'"
              v-tooltip.top="'删除'"
              icon="pi pi-trash"
              size="small"
              text
              class="action-btn action-btn-delete"
              @click="confirmDeleteLog(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
/**
 * 日志表格组件
 * 功能：显示日志列表和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import EmptyState from '@/components/common/EmptyState.vue'
import { formatBytes } from '@/utils/core/helpers'
import type { LogFile } from '@/types'

// Props
const props = defineProps<{
  logs: LogFile[]
  filteredLogs: LogFile[]
  isLoading: boolean
  totalRecords?: number
  pageSize?: number
  first?: number
}>()

// Emits
const emit = defineEmits([
  'update:selected-logs',
  'view-log-detail',
  'parse-log',
  'confirm-delete-log',
  'row-select',
  'row-unselect',
  'page-change'
])

// defineModel 和父组件双向同步选中项
const selectedLogs = defineModel('selectedLogs', {
  type: Array,
  default: () => []
})

// DataTable 分页状态（通过 @page 事件获取）
const dtFirst = ref(0)
const dtRows = ref(10)

// 获取当前页显示的数据（服务端分页模式下，传入的就是当前页数据）
const getCurrentPageData = (): LogFile[] => {
  return props.filteredLogs
}

// 表头复选框状态：当前页是否全部选中
const selectAllState = computed(() => {
  const pageData = getCurrentPageData()
  if (pageData.length === 0) return false
  return pageData.every((log) =>
    (selectedLogs.value as LogFile[]).some((s) => s.id === log.id)
  )
})

// 正在解析的日志ID列表
const parsingLogs = ref<string[]>([])

// 设置解析状态
const setParsing = (logId: string, isParsing: boolean) => {
  if (isParsing) {
    parsingLogs.value.push(logId)
  } else {
    parsingLogs.value = parsingLogs.value.filter((id) => id !== logId)
  }
}

// 暴露方法给父组件
defineExpose({ setParsing })

// 工具函数
const formatFileSize = formatBytes

const getRarityClass = (status: string): string => {
  const map: Record<string, string> = {
    completed: 'bg-gradient-to-br from-rarity-legendary to-primary',
    parsing: 'bg-gradient-to-br from-rarity-exotic to-secondary',
    failed: 'bg-gradient-to-br from-status-error to-status-error/70',
    pending: 'bg-gradient-to-br from-neutral-border to-neutral-bg'
  }
  return map[status] || 'bg-gradient-to-br from-neutral-border to-neutral-bg'
}

const getStatusDotClass = (status: string): string => {
  const map: Record<string, string> = {
    completed: 'status-dot-success',
    parsing: 'status-dot-warning',
    failed: 'status-dot-error',
    pending: 'status-dot-pending'
  }
  return map[status] || 'status-dot-pending'
}

const getStatusBadgeClass = (status: string): string => {
  const map: Record<string, string> = {
    completed: 'game-badge',
    parsing: 'game-badge',
    failed: 'game-badge',
    pending: 'game-badge'
  }
  return map[status] || 'game-badge'
}

// 事件处理
const onRowSelect = () => {
  emit('row-select')
}

const onRowUnselect = () => {
  emit('row-unselect')
}

// 分页变化时通知父组件
const onPage = (event: any) => {
  dtFirst.value = event.first
  dtRows.value = event.rows
  emit('page-change', { page: event.page, rows: event.rows })
}

/**
 * 全选/取消全选当前页（配合 selectAll prop，只控制可见行）
 */
const onSelectAllChange = (event: any) => {
  const checked = event.checked
  const pageData = getCurrentPageData()
  const pageIds = new Set(pageData.map((l) => l.id))

  if (checked) {
    // 保留其他页已选项，追加当前页
    const others = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
    selectedLogs.value = [...others, ...pageData]
  } else {
    // 只移除当前页，保留其他页
    selectedLogs.value = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
  }
  emit('row-select')
}

const clearSelection = () => {
  selectedLogs.value = []
}

const viewLogDetail = (log: any) => {
  emit('view-log-detail', log)
}

const parseLog = (log: any) => {
  emit('parse-log', log)
}

const confirmDeleteLog = (log: any) => {
  emit('confirm-delete-log', log)
}
</script>