<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div
      v-if="selectedLogs.length > 0"
      class="flex items-center justify-between px-4 py-2 bg-primary/5 border-b border-primary/10 rounded-t-xl"
    >
      <div class="flex items-center gap-2">
        <i class="pi pi-check-circle text-primary text-sm" />
        <span class="text-sm text-neutral-text">
          已选择 <span class="text-primary font-bold">{{ selectedLogs.length }}</span> 项
          <span class="text-neutral-text-secondary text-xs ml-1">（跨页连续）</span>
        </span>
      </div>
      <BaseButton
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
      @row-select="$emit('row-select')"
      @row-unselect="$emit('row-unselect')"
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
            >{{ data.statusText }}</span>
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
          <LogTableActions
            :data="data"
            :parsing="parsingLogs.includes(data.id)"
            @view="$emit('view-log-detail', data)"
            @parse="$emit('parse-log', data)"
            @delete="$emit('confirm-delete-log', data)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import EmptyState from '@/components/common/ui/display/EmptyState.vue'
import LogTableActions from './LogTableActions.vue'
import { formatFileSize, getRarityClass, getStatusDotClass, getStatusBadgeClass } from '@/utils/core/logTableHelpers'
import type { LogFile } from '@/types'

const props = defineProps<{
  logs: LogFile[]
  filteredLogs: LogFile[]
  isLoading: boolean
  totalRecords?: number
  pageSize?: number
  first?: number
}>()

const emit = defineEmits([
  'update:selected-logs', 'view-log-detail', 'parse-log',
  'confirm-delete-log', 'row-select', 'row-unselect', 'page-change'
])

const selectedLogs = defineModel('selectedLogs', { type: Array, default: () => [] })
const dtFirst = ref(0)
const dtRows = ref(10)
const parsingLogs = ref<string[]>([])

const selectAllState = computed(() => {
  if (props.filteredLogs.length === 0) return false
  return props.filteredLogs.every((log) => (selectedLogs.value as LogFile[]).some((s) => s.id === log.id))
})

const setParsing = (logId: string, isParsing: boolean) => {
  if (isParsing) parsingLogs.value.push(logId)
  else parsingLogs.value = parsingLogs.value.filter((id) => id !== logId)
}

const onSelectAllChange = (event: any) => {
  const checked = event.checked
  const pageIds = new Set(props.filteredLogs.map((l) => l.id))
  if (checked) {
    const others = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
    selectedLogs.value = [...others, ...props.filteredLogs]
  } else {
    selectedLogs.value = (selectedLogs.value as LogFile[]).filter((l) => !pageIds.has(l.id))
  }
  emit('row-select')
}

const clearSelection = () => { selectedLogs.value = [] }

const onPage = (event: any) => {
  dtFirst.value = event.first
  dtRows.value = event.rows
  emit('page-change', { page: event.page, rows: event.rows })
}

const viewLogDetail = (log: any) => emit('view-log-detail', log)
const parseLog = (log: any) => emit('parse-log', log)
const confirmDeleteLog = (log: any) => emit('confirm-delete-log', log)

defineExpose({ setParsing })
</script>
