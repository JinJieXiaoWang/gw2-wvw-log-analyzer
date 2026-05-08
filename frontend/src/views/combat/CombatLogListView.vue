<template>
  <div class="space-y-6">
    <!-- 游戏化欢迎区 -->
    <WelcomeBanner
      :selected-logs="selectedLogs"
      @show-upload-dialog="showUploadDialog = true"
      @show-batch-parse-dialog="showBatchParseDialog = true"
    />

    <!-- 已选提示条 + 解析进度 -->
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
          <!-- 批量解析状态 -->
          <div
            v-if="isBatchParsing"
            class="flex items-center gap-2"
          >
            <i class="pi pi-spin pi-spinner text-primary text-xs" />
            <span class="text-xs text-neutral-text-secondary">批量解析进行中，请稍后刷新页面查看结果</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Button
            v-if="isBatchParsing"
            icon="pi pi-list"
            label="查看详情"
            size="small"
            text
            severity="secondary"
            @click="showParseDetailDialog = true"
          />
          <Button
            icon="pi pi-times"
            label="清除选择"
            size="small"
            text
            severity="secondary"
            @click="clearSelection"
          />
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <StatCards
      :logs="logs"
      :total-records="totalRecords"
    />

    <!-- 筛选和搜索 -->
    <LogFilters
      v-model:filters="filters"
    />

    <!-- 日志列表 -->
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
  </div>

  <!-- 上传弹窗 -->
  <LogUploadDialog
    v-model:visible="showUploadDialog"
    @upload-success="handleUploadSuccess"
  />

  <!-- 批量解析弹窗 -->
  <BatchParseDialog
    v-model:visible="showBatchParseDialog"
    :selected-logs="selectedLogs"
    @start-batch-parse="startBatchParse"
  />

  <!-- 确认删除弹窗 -->
  <DeleteConfirmDialog
    v-model:visible="showDeleteDialog"
    @delete-log="deleteLog"
  />

  <!-- 解析进度详情弹窗 -->
  <Dialog
    v-model:visible="showParseDetailDialog"
    header="解析进度详情"
    modal
    :style="{ width: '500px' }"
    class="custom-dialog"
  >
    <div class="space-y-2 max-h-80 overflow-y-auto">
      <div
        v-for="item in parseProgressList"
        :key="item.logId"
        class="flex items-center justify-between p-3 rounded-lg"
        :class="{
          'bg-status-success/10 border border-status-success/20': item.status === 'completed',
          'bg-status-error/10 border border-status-error/20': item.status === 'failed' || item.status === 'timeout',
          'bg-primary/5 border border-primary/10': item.status === 'parsing'
        }"
      >
        <div class="flex items-center gap-2 min-w-0">
          <i
            class="pi"
            :class="{
              'pi-check-circle text-status-success': item.status === 'completed',
              'pi-times-circle text-status-error': item.status === 'failed' || item.status === 'timeout',
              'pi-spin pi-spinner text-primary': item.status === 'parsing'
            }"
          />
          <span class="text-sm text-neutral-text truncate">{{ item.fileName }}</span>
        </div>
        <span class="text-xs font-medium flex-shrink-0 ml-2">
          <span
            v-if="item.status === 'completed'"
            class="text-status-success"
          >完成</span>
          <span
            v-else-if="item.status === 'failed'"
            class="text-status-error"
          >失败</span>
          <span
            v-else-if="item.status === 'timeout'"
            class="text-status-error"
          >超时</span>
          <span
            v-else
            class="text-primary"
          >{{ item.progress }}%</span>
        </span>
      </div>
    </div>
  </Dialog>

  <Toast />
  <ConfirmDialog />
</template>

<script setup lang="ts">
/**
 * 日志管理页面
 * 功能：展示日志列表，支持筛选、批量操作、上传解析等
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 * 更新日期：2026-04-27
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { logsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatDate } from '@/utils/core/helpers'
import type { LogFile } from '@/types'

// 导入子组件
import WelcomeBanner from '@/components/logManagement/WelcomeBanner.vue'
import StatCards from '@/components/logManagement/StatCards.vue'
import LogFilters from '@/components/logManagement/LogFilters.vue'
import LogTable from '@/components/logManagement/LogTable.vue'
import LogUploadDialog from '@/components/logManagement/LogUploadDialog.vue'
import BatchParseDialog from '@/components/logManagement/BatchParseDialog.vue'
import DeleteConfirmDialog from '@/components/logManagement/DeleteConfirmDialog.vue'

// 解析进度项
interface ParseProgressItem {
  logId: number
  fileName: string
  status: 'pending' | 'parsing' | 'completed' | 'failed' | 'timeout'
  progress: number
  errorMessage?: string
}

// ============================================
// 路由与提示
// ============================================
const router = useRouter()
const toast = useToast()

// ============================================
// 状态定义
// ============================================
const isLoading = ref(false)
const selectedLogs = ref<LogFile[]>([])
const showUploadDialog = ref(false)
const showBatchParseDialog = ref(false)
const showDeleteDialog = ref(false)
const showParseDetailDialog = ref(false)
const logToDelete = ref<LogFile | null>(null)

// 表格引用
const logTableRef = ref<InstanceType<typeof LogTable> | null>(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 列表请求锁，防止并发重复请求
let isFetchingLogs = false

// 批量解析任务相关状态
const batchTaskId = ref<number | null>(null)
const batchTaskLogNameMap = ref<Map<number, string>>(new Map())

// 批量解析进度追踪
const parseProgressMap = ref<Map<number, ParseProgressItem>>(new Map())
const batchParseTotal = ref(0)
const batchParseCompleted = ref(0)
const batchParseFailed = ref(0)

// 是否在批量解析中（提交后有10秒缓冲期显示解析中状态）
const isBatchParsing = computed(() => {
  return batchParseTotal.value > 0
})

// 解析进度列表（用于弹窗显示）
const parseProgressList = computed(() => {
  return Array.from(parseProgressMap.value.values())
})

// ============================================
// 筛选器
// ============================================
const filters = ref({
  search: '',
  status: null as string | null
})

// 监听筛选条件变化，重置到第一页并重新获取数据
watch(filters, () => {
  currentPage.value = 1
  fetchLogs()
}, { deep: true })

// ============================================
// 模拟数据（初始为空，从API获取）
// ============================================
const logs = ref<LogFile[]>([])

// ============================================
// API数据获取函数
// ============================================

/**
 * 获取日志列表
 * API: GET /api/v1/logs
 */
const fetchLogs = async (): Promise<void> => {
  if (isFetchingLogs) return
  isFetchingLogs = true
  isLoading.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      logsService.getLogs({
        page: currentPage.value,
        page_size: pageSize.value,
        parse_status: filters.value.status,
        search: filters.value.search || null
      }),
      {
        showErrorMessage: false,
        errorHandler: (error) => {
          console.error('获取日志列表失败:', error)
        }
      }
    )

    if (result.success && result.data) {
      const responseData = result.data as any
      const dataWrapper = responseData.data || responseData
      logs.value = (dataWrapper.items || []).map((log: any) => ({
        id: String(log.id),
        fileName: log.filename,
        uploadTime: formatDate(log.upload_time, 'YYYY-MM-DD HH:mm'),
        status: log.parse_status,
        statusText: getStatusText(log.parse_status),
        fileSize: log.file_size_raw || log.file_size || 0,
        compressedSize: log.file_size_compressed || 0,
        fileSha256: log.file_sha256 || '',
        logUuid: log.log_uuid || '',
        parseTime: log.parse_time_ms ? (log.parse_time_ms / 1000).toFixed(2) + 's' : '-',
        parsedAt: log.parsed_at ? formatDate(log.parsed_at, 'YYYY-MM-DD HH:mm') : '-',
        errorMessage: log.error_message || null,
        dpsReportPermalink: log.dps_report_permalink || null,
        uploadIp: log.upload_ip || '-'
      }))
      totalRecords.value = dataWrapper.total || 0
    }
  } catch (error) {
    console.error('获取日志列表异常:', error)
    toast.add({
      severity: 'error',
      summary: '数据加载失败',
      detail: '无法获取日志列表，请检查网络连接后重试',
      life: 5000
    })
  } finally {
    isLoading.value = false
    isFetchingLogs = false
  }
}

/**
 * 获取状态文本
 * @param status 状态值
 */
const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    completed: '已完成',
    parsing: '解析中',
    pending: '待解析',
    failed: '失败'
  }
  return map[status] || status
}



// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchLogs()
})

// ============================================
// 分页事件
// ============================================
const handlePageChange = (event: { page: number; rows: number }) => {
  currentPage.value = event.page + 1  // PrimeVue 分页从 0 开始
  pageSize.value = event.rows
  fetchLogs()
}

// ============================================
// 事件处理
// ============================================

/**
 * 处理上传成功
 */
const handleUploadSuccess = () => {
  fetchLogs()
}

/**
 * 开始批量解析
 * API: POST /api/v1/logs/batch-parse
 */
const startBatchParse = async (): Promise<void> => {
  if (selectedLogs.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: '提示',
      detail: '请先选择要解析的日志文件',
      life: 3000
    })
    return
  }

  // 初始化批量解析进度追踪
  batchParseTotal.value = selectedLogs.value.length
  batchParseCompleted.value = 0
  batchParseFailed.value = 0
  parseProgressMap.value.clear()

  // 立即将选中日志在前端表格中标记为解析中（乐观更新）
  // 这样用户无需等待后端 worker 开始处理就能看到"解析中"状态
  selectedLogs.value.forEach(log => {
    const targetLog = logs.value.find(l => l.id === log.id)
    if (targetLog) {
      targetLog.status = 'parsing'
      targetLog.statusText = '解析中'
    }
    logTableRef.value?.setParsing(log.id, true)
    parseProgressMap.value.set(Number(log.id), {
      logId: Number(log.id),
      fileName: log.fileName,
      status: 'parsing',
      progress: 0
    })
  })

  const logIds = selectedLogs.value.map(log => Number(log.id))

  const result = await ApiResponseWrapper.wrap(
    logsService.batchParseLogs({
      task_name: `${new Date().toLocaleDateString('zh-CN')}批量解析任务`,
      log_ids: logIds,
      overwrite: true
    }),
    {
      showSuccessMessage: false,
      showErrorMessage: false
    }
  )

  if (result.success) {
    showBatchParseDialog.value = false

    // 保存批量任务ID和文件名映射，启动批量任务轮询
    const taskData = result.data as any
    const taskId = taskData?.id || taskData?.data?.id
    // 用后端实际处理数量更新总数（可能有部分日志已在解析中被跳过）
    const actualTotal = taskData?.total_count ?? taskData?.data?.total_count ?? selectedLogs.value.length
    if (actualTotal < selectedLogs.value.length) {
      batchParseTotal.value = actualTotal
      const skipped = selectedLogs.value.length - actualTotal
      toast.add({
        severity: 'warn',
        summary: '批量解析已启动',
        detail: `已启动 ${actualTotal} 个日志的解析，${skipped} 个日志已在解析中被跳过`,
        life: 5000
      })
    } else {
      toast.add({
        severity: 'info',
        summary: '批量解析已提交',
        detail: `已提交 ${selectedLogs.value.length} 个日志文件到后台解析，请稍后刷新页面查看结果`,
        life: 4000
      })
    }

    if (taskId) {
      batchTaskId.value = taskId
      selectedLogs.value.forEach(log => {
        batchTaskLogNameMap.value.set(Number(log.id), log.fileName)
      })
      // 10秒后自动清理批量解析状态，避免UI一直显示"解析中"
      setTimeout(() => {
        parseProgressMap.value.clear()
        batchParseTotal.value = 0
        batchParseCompleted.value = 0
        batchParseFailed.value = 0
        batchTaskId.value = null
        batchTaskLogNameMap.value.clear()
      }, 10000)
    }
  } else {
    // 请求失败后解除解析中状态并刷新列表恢复真实状态
    selectedLogs.value.forEach(log => {
      logTableRef.value?.setParsing(log.id, false)
    })
    batchParseTotal.value = 0
    parseProgressMap.value.clear()
    fetchLogs() // 刷新列表恢复真实状态
    const errorMessage = result.error?.message || '批量解析失败，请重试'
    toast.add({
      severity: 'error',
      summary: '批量解析失败',
      detail: errorMessage,
      life: 5000
    })
  }
}



/**
 * 查看日志详情
 * @param log 日志对象
 */
const viewLogDetail = (log: LogFile): void => {
  router.push(`/logs/${log.id}`)
}

/**
 * 解析单个日志
 * API: POST /api/v1/logs/{logId}/parse
 * @param log 日志对象
 */
const parseLog = async (log: LogFile): Promise<void> => {
  const logId = Number(log.id)
  const fileName = log.fileName

  // 防重入：如果该日志已经在解析中（包括等待API响应期间），跳过
  if (parseProgressMap.value.has(logId)) {
    toast.add({
      severity: 'warn',
      summary: '解析中',
      detail: `${fileName} 正在解析中，请勿重复操作`,
      life: 3000
    })
    return
  }

  // 立即标记为解析中，防止API请求期间的重复点击
  parseProgressMap.value.set(logId, {
    logId,
    fileName,
    status: 'parsing',
    progress: 0
  })
  logTableRef.value?.setParsing(log.id, true)

  const result = await ApiResponseWrapper.wrap(
    logsService.parseLog(logId),
    {
      showSuccessMessage: false,
      showErrorMessage: false
    }
  )

  if (result.success) {
    // 解析任务已提交到后台，不再轮询，用户手动刷新查看结果
    toast.add({
      severity: 'info',
      summary: '解析已提交',
      detail: `${fileName} 解析任务已提交，请稍后刷新页面查看结果`,
      life: 4000
    })
  } else {
    // 立即失败：清除解析中标记
    parseProgressMap.value.delete(logId)
    logTableRef.value?.setParsing(log.id, false)
    const errorMessage = result.error?.message || '解析失败，请重试'
    toast.add({
      severity: 'error',
      summary: '解析失败',
      detail: errorMessage,
      life: 5000
    })
  }
}

/**
 * 确认删除日志
 * @param log 日志对象
 */
const confirmDeleteLog = (log: LogFile): void => {
  logToDelete.value = log
  showDeleteDialog.value = true
}

/**
 * 执行删除日志
 * API: DELETE /api/v1/logs/{logId}
 */
const deleteLog = async (): Promise<void> => {
  if (logToDelete.value) {
    const result = await ApiResponseWrapper.wrap(
      logsService.deleteLog(Number(logToDelete.value.id)),
      {
        showSuccessMessage: true,
        successMessage: `${logToDelete.value.fileName} 已删除`,
        showErrorMessage: true
      }
    )
    
    if (result.success) {
      showDeleteDialog.value = false
      logToDelete.value = null
      fetchLogs()
    }
  }
}

// ============================================
// 表格事件
// ============================================
const onRowSelect = (): void => {
  // 选中行时的处理
}

const onRowUnselect = (): void => {
  // 取消选中行时的处理
}

/**
 * 清除所有选择
 */
const clearSelection = (): void => {
  selectedLogs.value = []
}

// ============================================
// 生命周期清理
// ============================================
onUnmounted(() => {
  // 组件卸载时清理
})
</script>
