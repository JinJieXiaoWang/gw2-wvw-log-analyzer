import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { attendanceService } from '@/services'
import { scoringRulesService } from '@/services/core/scoringRulesService'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { configManager } from '@/services/core/configManager'
import { formatDateParam } from '@/utils/common/attendanceFormatters'

const ROLE_LABEL_MAP: Record<string, string> = { dps: '输出', support: '辅助', tank: '承伤' }

export function useDataAttendance() {
  const toast = useToast()

  // 评分角色
  const currentRoleType = ref('dps')
  const currentRoleLabel = computed(() => ROLE_LABEL_MAP[currentRoleType.value] || '输出')
  const currentRuleVersion = ref(0)

  // 防抖
  let sortDebounceTimer: ReturnType<typeof setTimeout> | null = null
  const debounce = <T extends (...args: any[]) => void>(fn: T, delay: number) => {
    return (...args: Parameters<T>) => {
      if (sortDebounceTimer) clearTimeout(sortDebounceTimer)
      sortDebounceTimer = setTimeout(() => fn(...args), delay)
    }
  }
  const clearDebounce = () => {
    if (sortDebounceTimer) { clearTimeout(sortDebounceTimer); sortDebounceTimer = null }
  }

  // ״̬
  const loading = ref(false)
  const detailLoading = ref(false)
  const dateRange = ref<Date[] | null>(null)
  const searchQuery = ref('')
  const filterMap = ref<string | null>(null)
  const filterProfession = ref<string | null>(null)
  const filterOptions = ref({ maps: [] as string[], professions: [] as string[] })

  const accountList = ref<any[]>([])
  const pagination = ref({ page: 1, pageSize: 20, total: 0 })
  const currentSort = ref({ field: 'attendance_count', order: 'desc' })

  const statCards = ref({ totalAccounts: 0, totalDuration: 0, totalDamage: 0, totalDowned: 0 })

  // 详情
  const detailVisible = ref(false)
  const selectedAccount = ref('')
  const detailData = ref<any>(null)

  // 评分维度
  const scoreBreakdownVisible = ref(false)
  const scoreBreakdownLoading = ref(false)
  const scoreBreakdownData = ref<any>(null)
  const scoreBreakdownAccount = ref('')

  // 评分规则
  const scoringRulesVisible = ref(false)
  const scoringRulesLoading = ref(false)
  const scoringRulesData = ref<Record<string, any>>({})
  const scoringRulesActiveTab = ref(0)

  const fetchCurrentRuleVersion = async () => {
    try {
      const versions = await scoringRulesService.getVersions(0, 1)
      if (versions?.length) currentRuleVersion.value = versions[0].version
    } catch (e) { console.error('获取评分规则版本失败', e) }
  }

  const openScoringRulesDialog = async () => {
    scoringRulesVisible.value = true
    scoringRulesLoading.value = true
    scoringRulesData.value = {}
    try {
      const result = await scoringRulesService.getRules()
      if (result) scoringRulesData.value = result
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      scoringRulesLoading.value = false
    }
  }

  const fetchFilters = async () => {
    try {
      const result = await ApiResponseWrapper.wrap(attendanceService.getFilters(), { showErrorMessage: false })
      if (result.success && result.data) {
        const data = result.data as any
        filterOptions.value.maps = data.maps || []
        filterOptions.value.professions = data.professions || []
      }
    } catch (e) { console.error('获取筛选选项失败', e) }
  }

  const buildParams = () => {
    const params: any = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      sort_by: currentSort.value.field,
      sort_order: currentSort.value.order
    }
    if (dateRange.value?.length === 2) {
      if (dateRange.value[0]) params.start_date = formatDateParam(dateRange.value[0])
      if (dateRange.value[1]) params.end_date = formatDateParam(dateRange.value[1])
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterMap.value) params.map_name = filterMap.value
    if (filterProfession.value) params.profession = filterProfession.value
    return params
  }

  const fetchAccounts = async () => {
    loading.value = true
    try {
      const result = await ApiResponseWrapper.wrap(attendanceService.getAccounts(buildParams()), { showErrorMessage: true })
      if (result.success && result.data) {
        const data = result.data as any
        accountList.value = data.items || []
        pagination.value.total = data.total || 0
        statCards.value.totalAccounts = pagination.value.total
        statCards.value.totalDuration = accountList.value.reduce((s, i) => s + (i.total_duration_sec || 0), 0)
        statCards.value.totalDamage = accountList.value.reduce((s, i) => s + (i.total_damage || 0), 0)
        statCards.value.totalDowned = accountList.value.reduce((s, i) => s + (i.total_downed || 0), 0)
      } else {
        accountList.value = []
        pagination.value.total = 0
        toast.add({ severity: 'warn', summary: '提示', detail: '暂无数据', life: configManager.get('ui').toastLife })
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取数据失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      loading.value = false
    }
  }

  const getDateRangeParams = () => {
    let start: string | null = null, end: string | null = null
    if (dateRange.value?.length === 2) {
      if (dateRange.value[0]) start = formatDateParam(dateRange.value[0])
      if (dateRange.value[1]) end = formatDateParam(dateRange.value[1])
    }
    return { start, end }
  }

  const openDetail = async (account: string) => {
    selectedAccount.value = account
    detailVisible.value = true
    detailLoading.value = true
    detailData.value = null
    try {
      const { start, end } = getDateRangeParams()
      const result = await ApiResponseWrapper.wrap(attendanceService.getAccountDetail(account, start, end), { showErrorMessage: true })
      if (result.success && result.data) detailData.value = result.data
      else toast.add({ severity: 'warn', summary: '提示', detail: '暂无详情数据', life: configManager.get('ui').toastLife })
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取详情失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      detailLoading.value = false
    }
  }

  const openScoreBreakdown = async (account: string) => {
    scoreBreakdownAccount.value = account
    scoreBreakdownVisible.value = true
    scoreBreakdownLoading.value = true
    scoreBreakdownData.value = null
    try {
      const { start, end } = getDateRangeParams()
      const result = await ApiResponseWrapper.wrap(attendanceService.getAccountScoreBreakdown(account, start, end), { showErrorMessage: true })
      if (result.success && result.data) scoreBreakdownData.value = result.data
      else toast.add({ severity: 'warn', summary: '提示', detail: '暂无评分数据', life: configManager.get('ui').toastLife })
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分维度详情失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      scoreBreakdownLoading.value = false
    }
  }

  const onPageChange = (event: any) => {
    pagination.value.page = (event.page || 0) + 1
    fetchAccounts()
  }

  const onSort = debounce((event: any) => {
    if (event.sortField) {
      currentSort.value.field = event.sortField
      currentSort.value.order = event.sortOrder === 1 ? 'asc' : 'desc'
      fetchAccounts()
    }
  }, 300)

  const resetFilters = () => {
    dateRange.value = null
    searchQuery.value = ''
    filterMap.value = null
    filterProfession.value = null
    pagination.value.page = 1
    currentSort.value = { field: 'attendance_count', order: 'desc' }
    fetchAccounts()
  }

  const exportExcel = () => {
    toast.add({ severity: 'info', summary: '导出', detail: 'Excel 导出功能开发中', life: configManager.get('ui').toastLife })
  }

  const exportCSV = () => {
    toast.add({ severity: 'info', summary: '导出', detail: 'CSV 导出功能开发中', life: configManager.get('ui').toastLife })
  }

  return {
    currentRoleLabel, currentRuleVersion,
    loading, detailLoading,
    dateRange, searchQuery, filterMap, filterProfession, filterOptions,
    accountList, pagination, currentSort, statCards,
    detailVisible, selectedAccount, detailData,
    scoreBreakdownVisible, scoreBreakdownAccount, scoreBreakdownData, scoreBreakdownLoading,
    scoringRulesVisible, scoringRulesLoading, scoringRulesData, scoringRulesActiveTab,
    clearDebounce,
    fetchCurrentRuleVersion, openScoringRulesDialog,
    fetchFilters, fetchAccounts, openDetail, openScoreBreakdown,
    onPageChange, onSort, resetFilters, exportExcel, exportCSV
  }
}
