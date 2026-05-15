import { usePagination } from '@/composables/common/usePagination'
import { attendanceService } from '@/services'
import type { AttendanceListParams } from '@/services/data/attendanceService'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { scoringRulesService } from '@/services/core/scoringRulesService'
import { formatDateParam } from '@/utils/common/attendanceFormatters'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { AccountItem } from '@/components/attendance/AttendanceTable.vue'
import type { PaginatedResponse } from '@/types/api'

export function useAttendancePage() {
  const router = useRouter()
  const toast = useToast()

  const currentRuleVersion = ref(0)

  const fetchCurrentRuleVersion = async () => {
    try {
      const versions = await scoringRulesService.getVersions(0, 1)
      if (versions && versions.length > 0) {
        currentRuleVersion.value = versions[0].version
      }
    } catch (e) {
      console.error('获取评分规则版本失败', e)
    }
  }

  const loading = ref(false)
  const dateRange = ref<Date[] | null>(null)
  const searchQuery = ref('')
  const filterMap = ref<string | null>(null)
  const filterProfession = ref<string | null>(null)

  const filterOptions = ref({
    maps: [] as string[],
    professions: [] as string[]
  })

  const accountList = ref<AccountItem[]>([])
  const { page, pageSize, total, pagination, onPageChange: _onPageChange, resetPage: _resetPage } = usePagination({ defaultPageSize: 20 })
  const currentSort = ref({ field: 'attendance_count', order: 'desc' })

  const statCards = ref({
    totalAccounts: 0,
    totalDuration: 0,
    totalDamage: 0,
    totalDowned: 0
  })

  const scoreBreakdownVisible = ref(false)
  const scoreBreakdownLoading = ref(false)
  const scoreBreakdownData = ref<unknown>(null)
  const scoreBreakdownAccount = ref('')

  const scoringRulesVisible = ref(false)
  const scoringRulesLoading = ref(false)
  const scoringRulesData = ref<Record<string, unknown>>({})
  const scoringRulesActiveTab = ref(0)

  const openScoringRulesDialog = async () => {
    scoringRulesVisible.value = true
    scoringRulesLoading.value = true
    scoringRulesData.value = {}
    try {
      const result = await scoringRulesService.getRules()
      if (result) {
        scoringRulesData.value = result as Record<string, unknown>
      }
    } catch (e: unknown) {
      toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '获取评分规则失败', life: 5000 })
    } finally {
      scoringRulesLoading.value = false
    }
  }

  const fetchFilters = async () => {
    try {
      const result = await ApiResponseWrapper.wrap(
        attendanceService.getFilters(),
        { showErrorMessage: false }
      )
      if (result.success && result.data) {
        filterOptions.value.maps = result.data.maps || []
        filterOptions.value.professions = result.data.professions || []
      }
    } catch (e) {
      console.error('获取筛选选项失败', e)
    }
  }

  const fetchAccounts = async () => {
    loading.value = true
    try {
      const params: AttendanceListParams = {
        page: page.value,
        page_size: pageSize.value,
        sort_by: currentSort.value.field,
        sort_order: currentSort.value.order
      }
      if (dateRange.value && dateRange.value.length === 2) {
        const start = dateRange.value[0]
        const end = dateRange.value[1]
        if (start) params.start_date = formatDateParam(start)
        if (end) params.end_date = formatDateParam(end)
      }
      if (searchQuery.value.trim()) {
        params.search = searchQuery.value.trim()
      }
      if (filterMap.value) {
        params.map_name = filterMap.value
      }
      if (filterProfession.value) {
        params.profession = filterProfession.value
      }
      const result = await ApiResponseWrapper.wrap(
        attendanceService.getAccounts(params),
        { showErrorMessage: true }
      )
      if (result.success && result.data) {
        const data = result.data
        accountList.value = data.items || []
        total.value = data.total || 0
        statCards.value.totalAccounts = total.value
        statCards.value.totalDuration = accountList.value.reduce((sum, item) => sum + (item.total_duration_sec || 0), 0)
        statCards.value.totalDamage = accountList.value.reduce((sum, item) => sum + (item.total_damage || 0), 0)
        statCards.value.totalDowned = accountList.value.reduce((sum, item) => sum + (item.total_downed || 0), 0)
      } else {
        accountList.value = []
        total.value = 0
        toast.add({ severity: 'warn', summary: '提示', detail: '暂无数据', life: 3000 })
      }
    } catch (e: unknown) {
      toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '获取数据失败', life: 5000 })
    } finally {
      loading.value = false
    }
  }

  const openDetail = (account: string) => {
    router.push({ name: 'attendance-detail', params: { account } })
  }

  const openScoreBreakdown = async (account: string) => {
    scoreBreakdownAccount.value = account
    scoreBreakdownVisible.value = true
    scoreBreakdownLoading.value = true
    scoreBreakdownData.value = null
    try {
      let startDate: string | null = null
      let endDate: string | null = null
      if (dateRange.value && dateRange.value.length === 2) {
        if (dateRange.value[0]) startDate = formatDateParam(dateRange.value[0])
        if (dateRange.value[1]) endDate = formatDateParam(dateRange.value[1])
      }
      const result = await ApiResponseWrapper.wrap(
        attendanceService.getAccountScoreBreakdown(account, startDate, endDate),
        { showErrorMessage: true }
      )
      if (result.success && result.data) {
        scoreBreakdownData.value = result.data
      } else {
        toast.add({ severity: 'warn', summary: '提示', detail: '暂无评分数据', life: 3000 })
      }
    } catch (e: unknown) {
      toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '获取评分维度详情失败', life: 5000 })
    } finally {
      scoreBreakdownLoading.value = false
    }
  }

  const onPageChange = (event: { page: number }) => {
    _onPageChange(event)
    fetchAccounts()
  }

  const onSort = (event: { sortField: string; sortOrder: number }) => {
    if (event.sortField) {
      currentSort.value.field = event.sortField
      currentSort.value.order = event.sortOrder === 1 ? 'asc' : 'desc'
      fetchAccounts()
    }
  }

  const resetFilters = () => {
    dateRange.value = null
    searchQuery.value = ''
    filterMap.value = null
    filterProfession.value = null
    _resetPage()
    currentSort.value = { field: 'attendance_count', order: 'desc' }
    fetchAccounts()
  }

  onMounted(() => {
    fetchFilters()
    fetchAccounts()
    fetchCurrentRuleVersion()
  })

  return {
    currentRuleVersion,
    loading,
    dateRange,
    searchQuery,
    filterMap,
    filterProfession,
    filterOptions,
    accountList,
    pagination,
    currentSort,
    statCards,
    scoreBreakdownVisible,
    scoreBreakdownLoading,
    scoreBreakdownData,
    scoreBreakdownAccount,
    scoringRulesVisible,
    scoringRulesLoading,
    scoringRulesData,
    scoringRulesActiveTab,
    openScoringRulesDialog,
    openDetail,
    openScoreBreakdown,
    onPageChange,
    onSort,
    resetFilters,
    fetchAccounts
  }
}
