<template>
  <div class="space-y-6">
    <PageHeader
      title="战斗日志"
      subtitle="管理和解析您的 WvW 战斗日志"
      icon="pi pi-folder-open"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    >
      <template #actions>
        <BaseButton
          v-permission="'write'"
          label="上传日志"
          icon="pi pi-upload"
          variant="game"
          @click="handleUploadClick"
        />
        <BaseButton
          v-permission="'write'"
          :disabled="selectedLogs.length === 0"
          label="批量解析"
          icon="pi pi-refresh"
          variant="game"
          class="ml-2"
          @click="handleBatchParseClick"
        />
      </template>
    </PageHeader>

    <div
      v-if="selectedLogs.length > 0 || isBatchParsing"
      class="card p-3 rounded-xl border-primary/20 bg-gradient-to-r from-primary/5 to-transparent animate-slide-in-up"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <i class="pi pi-check-circle text-primary" />
            <span class="text-sm font-medium text-neutral-text">
              已选择 <span class="text-primary font-bold">{{ selectedLogs.length }}</span> 项
            </span>
          </div>
          <div
            v-if="isBatchParsing"
            class="flex items-center gap-2"
          >
            <i class="pi pi-spin pi-spinner text-primary text-xs" />
            <span class="text-xs text-neutral-text-secondary">批量解析进行中，请稍后刷新页面查看结果</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <BaseButton
            icon="pi pi-times"
            label="清除选择"
            size="small"
            text
            variant="secondary"
            @click="clearSelection"
          />
        </div>
      </div>
    </div>

    <StatCards
      :logs="logs"
      :total-records="totalRecords"
    />
    <LogFilters v-model:filters="filters" />
    <LogTable
      ref="logTableRef"
      v-model:selected-logs="selectedLogs"
      :logs="logs"
      :filtered-logs="logs"
      :is-loading="isLoading"
      :total-records="totalRecords"
      :page-size="pageSize"
      :first="(currentPage - 1) * pageSize"
      @view-log-detail="viewLogDetail"
      @parse-log="parseLog"
      @confirm-delete-log="confirmDeleteLog"
      @row-select="onRowSelect"
      @row-unselect="onRowUnselect"
      @page-change="handlePageChange"
    />

    <LogUploadDialog
      v-model:visible="showUploadDialog"
      @upload-success="handleUploadSuccess"
    />
    <BatchParseDialog
      v-model:visible="showBatchParseDialog"
      :selected-logs="selectedLogs"
      @start-batch-parse="startBatchParse"
    />
    <DeleteConfirmDialog
      v-model:visible="showDeleteDialog"
      @delete-log="deleteLog"
    />
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BatchParseDialog from '@/components/log/BatchParseDialog.vue'
import DeleteConfirmDialog from '@/components/log/DeleteConfirmDialog.vue'
import LogFilters from '@/components/log/LogFilters.vue'
import LogTable from '@/components/log/LogTable.vue'
import LogUploadDialog from '@/components/log/LogUploadDialog.vue'
import StatCards from '@/components/log/StatCards.vue'
import { useCombatLogList } from '@/composables/combat/useCombatLogList'
import { authStore } from '@/composables/system/usePermission'
import PageHeader from '@/layout/components/PageHeader.vue'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const logTableRef = ref()

const {
  isLoading,
  selectedLogs,
  logs,
  currentPage,
  pageSize,
  totalRecords,
  filters,
  isBatchParsing,
  showUploadDialog,
  showBatchParseDialog,
  showDeleteDialog,
  fetchLogs,
  handlePageChange,
  handleUploadSuccess,
  startBatchParse,
  viewLogDetail,
  parseLog,
  confirmDeleteLog,
  deleteLog,
  clearSelection
} = useCombatLogList()

/**
 * 前置校验登录状态
 * 未登录则保存当前路径并跳转登录页
 */
const checkAuthAndRedirect = (): boolean => {
  if (!authStore.isAuthenticated) {
    sessionStorage.setItem('auth_redirect', router.currentRoute.value.fullPath)
    router.push('/login')
    return false
  }
  return true
}

/**
 * 处理上传按钮点击事件
 */
const handleUploadClick = () => {
  if (!checkAuthAndRedirect()) return
  showUploadDialog.value = true
}

/**
 * 处理批量解析按钮点击事件
 */
const handleBatchParseClick = () => {
  if (!checkAuthAndRedirect()) return
  showBatchParseDialog.value = true
}

const onRowSelect = () => {
  // 空实现，保持接口兼容性
}

const onRowUnselect = () => {
  // 空实现，保持接口兼容性
}

onMounted(() => {
  fetchLogs()
})
</script>
