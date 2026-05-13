import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { usePagination } from '@/composables/common/usePagination'
import { logsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatDate } from '@/utils/core/helpers'
import { configManager } from '@/services/core/configManager'
import type { LogFile } from '@/types'

interface ParseProgressItem {
  logId: number
  fileName: string
  status: 'pending' | 'parsing' | 'completed' | 'failed' | 'timeout'
  progress: number
  errorMessage?: string
}

const STATUS_TEXT_MAP: Record<string, string> = {
  completed: '已完成', parsing: '解析中', pending: '待解析', failed: '失败'
}

export function useCombatLogList() {
  const router = useRouter()
  const toast = useToast()

  const isLoading = ref(false)
  const selectedLogs = ref<LogFile[]>([])
  const showUploadDialog = ref(false)
  const showBatchParseDialog = ref(false)
  const showDeleteDialog = ref(false)
  const showParseDetailDialog = ref(false)
  const logToDelete = ref<LogFile | null>(null)
  const {
    page: currentPage,
    pageSize,
    total: totalRecords,
    onPageChange: _handlePageChange,
    resetPage: _resetPage
  } = usePagination({ defaultPageSize: 10 })
  let isFetchingLogs = false

  const batchTaskId = ref<number | null>(null)
  const batchTaskLogNameMap = ref<Map<number, string>>(new Map())
  let batchParseCleanupTimer: ReturnType<typeof setTimeout> | null = null

  const parseProgressMap = ref<Map<number, ParseProgressItem>>(new Map())
  const batchParseTotal = ref(0)
  const batchParseCompleted = ref(0)
  const batchParseFailed = ref(0)

  const isBatchParsing = computed(() => batchParseTotal.value > 0)
  const parseProgressList = computed(() => Array.from(parseProgressMap.value.values()))

  const filters = ref({ search: '', status: null as string | null })
  watch(filters, () => { _resetPage(); fetchLogs() }, { deep: true })

  const logs = ref<LogFile[]>([])

  async function fetchLogs() {
    if (isFetchingLogs) return
    isFetchingLogs = true
    isLoading.value = true
    try {
      const result = await ApiResponseWrapper.wrap(
        logsService.getLogs({ page: currentPage.value, page_size: pageSize.value, parse_status: filters.value.status, search: filters.value.search || null }),
        { showErrorMessage: false, errorHandler: (err) => console.error('获取日志列表失败:', err) }
      )
      if (result.success && result.data) {
        const responseData = result.data as any
        const dataWrapper = responseData.data || responseData
        logs.value = (dataWrapper.items || []).map((log: any) => ({
          id: String(log.id), fileName: log.filename,
          uploadTime: formatDate(log.upload_time, 'YYYY-MM-DD HH:mm'),
          status: log.parse_status, statusText: STATUS_TEXT_MAP[log.parse_status] || log.parse_status,
          fileSize: log.file_size_raw || log.file_size || 0,
          compressedSize: log.file_size_compressed || 0,
          fileSha256: log.file_sha256 || '', logUuid: log.log_uuid || '',
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
      toast.add({ severity: 'error', summary: '数据加载失败', detail: '无法获取日志列表，请检查网络连接后重试', life: configManager.get('ui').toastErrorLife })
    } finally {
      isLoading.value = false
      isFetchingLogs = false
    }
  }

  function handlePageChange(event: { page: number; rows: number }) {
    _handlePageChange(event)
    fetchLogs()
  }

  function handleUploadSuccess() { fetchLogs() }

  async function startBatchParse() {
    if (selectedLogs.value.length === 0) {
      toast.add({ severity: 'warn', summary: '提示', detail: '请先选择要解析的日志文件', life: configManager.get('ui').toastLife })
      return
    }
    if (batchParseCleanupTimer) { clearTimeout(batchParseCleanupTimer); batchParseCleanupTimer = null }
    batchParseTotal.value = selectedLogs.value.length
    batchParseCompleted.value = 0
    batchParseFailed.value = 0
    parseProgressMap.value.clear()

    selectedLogs.value.forEach(log => {
      const targetLog = logs.value.find(l => l.id === log.id)
      if (targetLog) { targetLog.status = 'parsing'; targetLog.statusText = '解析中' }
      parseProgressMap.value.set(Number(log.id), { logId: Number(log.id), fileName: log.fileName, status: 'parsing', progress: 0 })
    })

    try {
      const result = await ApiResponseWrapper.wrap(
        logsService.batchParseLogs({ task_name: `${new Date().toLocaleDateString('zh-CN')}批量解析任务`, log_ids: selectedLogs.value.map(log => Number(log.id)), overwrite: true }),
        { showSuccessMessage: false, showErrorMessage: false }
      )

      if (result.success) {
        showBatchParseDialog.value = false
        const taskData = result.data as any
        const taskId = taskData?.id || taskData?.data?.id
        const actualTotal = taskData?.total_count ?? taskData?.data?.total_count ?? selectedLogs.value.length
        if (actualTotal < selectedLogs.value.length) {
          batchParseTotal.value = actualTotal
          toast.add({ severity: 'warn', summary: '批量解析已启动', detail: `已启动 ${actualTotal} 个日志的解析，${selectedLogs.value.length - actualTotal} 个日志已在解析中被跳过`, life: configManager.get('ui').toastErrorLife })
        } else {
          toast.add({ severity: 'info', summary: '批量解析已提交', detail: `已提交 ${selectedLogs.value.length} 个日志文件到后台解析，请稍后刷新页面查看结果`, life: configManager.get('ui').toastLife })
        }
        if (taskId) {
          batchTaskId.value = taskId
          selectedLogs.value.forEach(log => batchTaskLogNameMap.value.set(Number(log.id), log.fileName))
          batchParseCleanupTimer = setTimeout(() => {
            parseProgressMap.value.clear(); batchParseTotal.value = 0; batchParseCompleted.value = 0; batchParseFailed.value = 0
            batchTaskId.value = null; batchTaskLogNameMap.value.clear()
          }, 10000)
        }
      } else {
        selectedLogs.value.forEach(log => { const entry = parseProgressMap.value.get(Number(log.id)); if (entry) entry.status = 'failed' })
        batchParseTotal.value = 0; parseProgressMap.value.clear(); fetchLogs()
        toast.add({ severity: 'error', summary: '批量解析失败', detail: result.error?.message || '批量解析失败，请重试', life: configManager.get('ui').toastErrorLife })
      }
    } catch (e: any) {
      selectedLogs.value.forEach(log => { const entry = parseProgressMap.value.get(Number(log.id)); if (entry) entry.status = 'failed' })
      batchParseTotal.value = 0; parseProgressMap.value.clear(); fetchLogs()
      toast.add({ severity: 'error', summary: '批量解析异常', detail: e?.message || '网络异常，请检查网络后重试', life: configManager.get('ui').toastErrorLife })
    }
  }

  function viewLogDetail(log: LogFile) { router.push(`/logs/${log.id}`) }

  async function parseLog(log: LogFile) {
    const logId = Number(log.id)
    if (parseProgressMap.value.has(logId)) {
      toast.add({ severity: 'warn', summary: '解析中', detail: `${log.fileName} 正在解析中，请勿重复操作`, life: configManager.get('ui').toastLife })
      return
    }
    parseProgressMap.value.set(logId, { logId, fileName: log.fileName, status: 'parsing', progress: 0 })
    try {
      const result = await ApiResponseWrapper.wrap(logsService.parseLog(logId), { showSuccessMessage: false, showErrorMessage: false })
      if (result.success) {
        toast.add({ severity: 'info', summary: '解析已提交', detail: `${log.fileName} 解析任务已提交，请稍后刷新页面查看结果`, life: configManager.get('ui').toastLife })
      } else {
        parseProgressMap.value.delete(logId)
        toast.add({ severity: 'error', summary: '解析失败', detail: result.error?.message || '解析失败，请重试', life: configManager.get('ui').toastErrorLife })
      }
    } catch (e: any) {
      parseProgressMap.value.delete(logId)
      toast.add({ severity: 'error', summary: '解析异常', detail: e?.message || '网络异常，请检查网络后重试', life: configManager.get('ui').toastErrorLife })
    }
  }

  function confirmDeleteLog(log: LogFile) { logToDelete.value = log; showDeleteDialog.value = true }

  async function deleteLog() {
    if (!logToDelete.value) return
    const result = await ApiResponseWrapper.wrap(
      logsService.deleteLog(Number(logToDelete.value.id)),
      { showSuccessMessage: true, successMessage: `${logToDelete.value.fileName} 已删除`, showErrorMessage: true }
    )
    if (result.success) { showDeleteDialog.value = false; logToDelete.value = null; fetchLogs() }
  }

  function clearSelection() { selectedLogs.value = [] }

  onMounted(() => { fetchLogs() })
  onUnmounted(() => { if (batchParseCleanupTimer) { clearTimeout(batchParseCleanupTimer); batchParseCleanupTimer = null } })

  return {
    isLoading, selectedLogs, showUploadDialog, showBatchParseDialog, showDeleteDialog, showParseDetailDialog,
    logToDelete, currentPage, pageSize, totalRecords, isBatchParsing, parseProgressList, filters, logs,
    fetchLogs, handlePageChange, handleUploadSuccess, startBatchParse, viewLogDetail, parseLog,
    confirmDeleteLog, deleteLog, clearSelection
  }
}
