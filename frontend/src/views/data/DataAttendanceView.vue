<template>
  <div class="space-y-6">
    <!-- 欢迎横幅 -->
    <WelcomeBanner
      @export-excel="exportExcel"
      @export-csv="exportCSV"
    />

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <div class="card-legendary animate-slide-in-up" style="animation-delay: 0.1s">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-neutral-text-secondary text-sm mb-1">出勤账号</p>
            <p class="text-3xl font-bold game-number-legendary">{{ statCards.totalAccounts }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-xl flex items-center justify-center">
            <i class="pi pi-users text-primary text-xl" />
          </div>
        </div>
      </div>
      <div class="card-exotic animate-slide-in-up" style="animation-delay: 0.2s">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-neutral-text-secondary text-sm mb-1">总出勤时长</p>
            <p class="text-3xl font-bold game-number-exotic">{{ formatDuration(statCards.totalDuration) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-secondary/30 to-status-success/30 rounded-xl flex items-center justify-center">
            <i class="pi pi-clock text-secondary text-xl" />
          </div>
        </div>
      </div>
      <div class="card-rare animate-slide-in-up" style="animation-delay: 0.3s">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-neutral-text-secondary text-sm mb-1">总伤害</p>
            <p class="text-3xl font-bold game-number-rare">{{ formatNumber(statCards.totalDamage) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-status-error/30 to-status-warning/30 rounded-xl flex items-center justify-center">
            <i class="pi pi-bolt text-status-error text-xl" />
          </div>
        </div>
      </div>
      <div class="card-mythic animate-slide-in-up" style="animation-delay: 0.4s">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-neutral-text-secondary text-sm mb-1">总治疗</p>
            <p class="text-3xl font-bold game-number-mythic">{{ formatNumber(statCards.totalHealing) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-status-success/30 to-primary/30 rounded-xl flex items-center justify-center">
            <i class="pi pi-heart text-status-success text-xl" />
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="card animate-slide-in-up" style="animation-delay: 0.5s">
      <div class="flex flex-col lg:flex-row gap-4 items-end">
        <div class="flex-1">
          <label class="block text-sm text-neutral-text-secondary mb-2">日期范围</label>
          <Calendar
            v-model="dateRange"
            selection-mode="range"
            date-format="yy-mm-dd"
            placeholder="选择日期范围"
            show-icon
            class="w-full"
          />
        </div>
        <div class="flex-1">
          <label class="block text-sm text-neutral-text-secondary mb-2">搜索账号或角色</label>
          <InputText
            v-model="searchQuery"
            placeholder="输入账号或角色名..."
            class="w-full"
          />
        </div>
        <div class="w-full lg:w-40">
          <label class="block text-sm text-neutral-text-secondary mb-2">地图</label>
          <Dropdown
            v-model="filterMap"
            :options="filterOptions.maps"
            placeholder="全部地图"
            show-clear
            class="w-full"
          />
        </div>
        <div class="w-full lg:w-40">
          <label class="block text-sm text-neutral-text-secondary mb-2">职业</label>
          <Dropdown
            v-model="filterProfession"
            :options="filterOptions.professions"
            placeholder="全部职业"
            show-clear
            class="w-full"
          />
        </div>
        <Button
          label="应用筛选"
          icon="pi pi-search"
          class="btn-game"
          :loading="loading"
          @click="fetchAccounts"
        />
        <Button
          label="重置"
          icon="pi pi-refresh"
          class="btn-ghost"
          :disabled="loading"
          @click="resetFilters"
        />
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="card animate-slide-in-up" style="animation-delay: 0.6s">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
            <i class="pi pi-list text-primary" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-neutral-text">出勤账号列表</h3>
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
        <Column field="account" header="账号" sortable>
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary/40 to-secondary/40 flex items-center justify-center text-white text-xs font-bold">
                {{ data.account.charAt(0).toUpperCase() }}
              </div>
              <span class="font-medium text-neutral-text">{{ data.account }}</span>
            </div>
          </template>
        </Column>

        <Column field="character_count" header="角色数" sortable>
          <template #body="{ data }">
            <Tag :value="String(data.character_count)" severity="info" class="game-badge" />
          </template>
        </Column>

        <Column field="attendance_count" header="出勤次数" sortable>
          <template #body="{ data }">
            <span class="text-primary font-bold">{{ data.attendance_count }}</span>
            <span class="text-xs text-neutral-text-secondary ml-1">天</span>
          </template>
        </Column>

        <Column field="total_duration_sec" header="总时长" sortable>
          <template #body="{ data }">
            {{ formatDuration(data.total_duration_sec) }}
          </template>
        </Column>

        <Column field="total_damage" header="总伤害" sortable>
          <template #body="{ data }">
            <span class="text-status-error font-semibold">{{ formatNumber(data.total_damage) }}</span>
          </template>
        </Column>

        <Column field="total_healing" header="总治疗" sortable>
          <template #body="{ data }">
            <span class="text-status-success font-semibold">{{ formatNumber(data.total_healing) }}</span>
          </template>
        </Column>

        <Column field="total_kills" header="击杀" sortable>
          <template #body="{ data }">
            <span class="text-secondary font-semibold">{{ data.total_kills }}</span>
          </template>
        </Column>

        <Column field="total_deaths" header="死亡" sortable>
          <template #body="{ data }">
            <span class="text-status-error font-semibold">{{ data.total_deaths }}</span>
          </template>
        </Column>

        <Column field="kd_ratio" header="K/D" sortable>
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

        <Column field="avg_score" header="平均评分" sortable>
          <template #body="{ data }">
            <span
              :class="{
                'game-badge game-badge-legendary': data.avg_score >= 90,
                'game-badge game-badge-exotic': data.avg_score >= 80 && data.avg_score < 90,
                'game-badge game-badge-rare': data.avg_score >= 70 && data.avg_score < 80,
                'game-badge': data.avg_score < 70
              }"
            >
              {{ data.avg_score }}
            </span>
          </template>
        </Column>

        <Column field="last_attendance" header="最后出勤" sortable>
          <template #body="{ data }">
            <span class="text-sm text-neutral-text-secondary">
              {{ data.last_attendance ? formatDate(data.last_attendance) : '-' }}
            </span>
          </template>
        </Column>

        <Column header="操作" style="width: 100px">
          <template #body="{ data }">
            <Button
              icon="pi pi-eye"
              class="btn-ghost"
              size="small"
              @click="openDetail(data.account)"
            />
          </template>
        </Column>
      </DataTable>

      <!-- 分页 -->
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

    <!-- 账号详情对话框 -->
    <Dialog
      v-model:visible="detailVisible"
      :header="`账号详情：${selectedAccount}`"
      maximizable
      modal
      :style="{ width: '900px', maxWidth: '95vw' }"
      :breakpoints="{ '960px': '95vw' }"
      class="game-dialog"
    >
      <div v-if="detailLoading" class="flex items-center justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <div v-else-if="detailData" class="space-y-6">
        <!-- 汇总卡片 -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="card p-4">
            <p class="text-xs text-neutral-text-secondary">出勤天数</p>
            <p class="text-2xl font-bold text-primary">{{ detailData.summary?.attendance_count || 0 }}</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-neutral-text-secondary">总伤害</p>
            <p class="text-2xl font-bold text-status-error">{{ formatNumber(detailData.summary?.total_damage || 0) }}</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-neutral-text-secondary">总治疗</p>
            <p class="text-2xl font-bold text-status-success">{{ formatNumber(detailData.summary?.total_healing || 0) }}</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-neutral-text-secondary">K/D</p>
            <p class="text-2xl font-bold text-secondary">{{ detailData.summary?.kd_ratio || 0 }}</p>
          </div>
        </div>

        <TabView>
          <!-- 角色列表 -->
          <TabPanel header="角色统计" value="0">
            <DataTable
              :value="detailData.characters || []"
              class="w-full game-table"
              removable-sort
            >
              <Column field="character_name" header="角色名">
                <template #body="{ data }">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                      :style="{ backgroundColor: getProfessionColor(data.profession) }"
                    >
                      {{ data.character_name.charAt(0) }}
                    </div>
                    <span class="font-medium">{{ data.character_name }}</span>
                  </div>
                </template>
              </Column>
              <Column field="profession" header="职业">
                <template #body="{ data }">
                  <span :style="{ color: getProfessionColor(data.profession) }" class="font-medium">
                    {{ getProfessionName(data.profession) }}
                  </span>
                </template>
              </Column>
              <Column field="attendance_count" header="出勤天数" sortable>
                <template #body="{ data }">
                  <span class="text-primary font-bold">{{ data.attendance_count }}</span>
                </template>
              </Column>
              <Column field="total_damage" header="总伤害" sortable>
                <template #body="{ data }">
                  <span class="text-status-error font-semibold">{{ formatNumber(data.total_damage) }}</span>
                </template>
              </Column>
              <Column field="total_healing" header="总治疗" sortable>
                <template #body="{ data }">
                  <span class="text-status-success font-semibold">{{ formatNumber(data.total_healing) }}</span>
                </template>
              </Column>
              <Column field="avg_dps" header="平均DPS" sortable />
              <Column field="kd_ratio" header="K/D" sortable />
              <Column field="avg_score" header="评分" sortable>
                <template #body="{ data }">
                  <span
                    :class="{
                      'game-badge game-badge-legendary': data.avg_score >= 90,
                      'game-badge game-badge-exotic': data.avg_score >= 80 && data.avg_score < 90,
                      'game-badge game-badge-rare': data.avg_score >= 70 && data.avg_score < 80,
                      'game-badge': data.avg_score < 70
                    }"
                  >
                    {{ data.avg_score }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </TabPanel>

          <!-- 最近战斗 -->
          <TabPanel header="最近战斗" value="1">
            <DataTable
              :value="detailData.recent_fights || []"
              class="w-full game-table"
            >
              <Column field="fight_date" header="战斗时间">
                <template #body="{ data }">
                  {{ formatDateTime(data.fight_date) }}
                </template>
              </Column>
              <Column field="character_name" header="角色" />
              <Column field="profession" header="职业">
                <template #body="{ data }">
                  <span :style="{ color: getProfessionColor(data.profession) }" class="font-medium">
                    {{ getProfessionName(data.profession) }}
                  </span>
                </template>
              </Column>
              <Column field="map_name" header="地图" />
              <Column field="damage" header="伤害">
                <template #body="{ data }">
                  <span class="text-status-error font-semibold">{{ formatNumber(data.damage) }}</span>
                </template>
              </Column>
              <Column field="dps" header="DPS" />
              <Column field="healing" header="治疗">
                <template #body="{ data }">
                  <span class="text-status-success font-semibold">{{ formatNumber(data.healing) }}</span>
                </template>
              </Column>
              <Column field="killed" header="击杀" />
              <Column field="dead_count" header="死亡" />
              <Column field="ai_score" header="评分" />
            </DataTable>
          </TabPanel>
        </TabView>
      </div>
    </Dialog>

    <Toast />
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤管理页面 v2.0
 * 更新日期：2026-05-04
 * 后端接口：/api/v1/attendance/accounts
 * 核心规则：
 *   1. 统计归属日期 = fight.start_time（与 upload_time 无关）
 *   2. 同一角色自然日内无论多少日志，只计 1 次出勤
 *   3. 同一账号按自然日去重（当天多角色只计 1 次账号出勤）
 */

import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

// 职业工具
import { getProfessionName, getProfessionColor } from '@/utils/profession/professionUtils'

// PrimeVue 组件
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Paginator from 'primevue/paginator'
import ProgressSpinner from 'primevue/progressspinner'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'

// 子组件
import WelcomeBanner from '@/components/attendance/WelcomeBanner.vue'

// 服务层
import { attendanceService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'

const toast = useToast()

// ============================================
// 加载状态
// ============================================
const loading = ref(false)
const detailLoading = ref(false)

// ============================================
// 筛选条件
// ============================================
const dateRange = ref<Date[] | null>(null)
const searchQuery = ref('')
const filterMap = ref<string | null>(null)
const filterProfession = ref<string | null>(null)

const filterOptions = ref({
  maps: [] as string[],
  professions: [] as string[]
})

// ============================================
// 数据列表
// ============================================
const accountList = ref<any[]>([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})
const currentSort = ref({ field: 'attendance_count', order: 'desc' })

// ============================================
// 统计卡片
// ============================================
const statCards = ref({
  totalAccounts: 0,
  totalDuration: 0,
  totalDamage: 0,
  totalHealing: 0
})

// ============================================
// 详情对话框
// ============================================
const detailVisible = ref(false)
const selectedAccount = ref('')
const detailData = ref<any>(null)

// ============================================
// API 数据获取
// ============================================

/** 获取筛选选项 */
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

/** 获取账号出勤列表 */
const fetchAccounts = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
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
      pagination.value.total = data.total || 0

      // 计算统计卡片（基于当前页数据汇总，如需全局统计可再调一个接口）
      statCards.value.totalAccounts = pagination.value.total
      statCards.value.totalDuration = accountList.value.reduce((sum, item) => sum + (item.total_duration_sec || 0), 0)
      statCards.value.totalDamage = accountList.value.reduce((sum, item) => sum + (item.total_damage || 0), 0)
      statCards.value.totalHealing = accountList.value.reduce((sum, item) => sum + (item.total_healing || 0), 0)
    } else {
      accountList.value = []
      pagination.value.total = 0
      toast.add({ severity: 'warn', summary: '提示', detail: '暂无数据', life: 3000 })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取数据失败', life: 5000 })
  } finally {
    loading.value = false
  }
}

/** 打开账号详情 */
const openDetail = async (account: string) => {
  selectedAccount.value = account
  detailVisible.value = true
  detailLoading.value = true
  detailData.value = null

  try {
    let startDate: string | null = null
    let endDate: string | null = null
    if (dateRange.value && dateRange.value.length === 2) {
      if (dateRange.value[0]) startDate = formatDateParam(dateRange.value[0])
      if (dateRange.value[1]) endDate = formatDateParam(dateRange.value[1])
    }

    const result = await ApiResponseWrapper.wrap(
      attendanceService.getAccountDetail(account, startDate, endDate),
      { showErrorMessage: true }
    )

    if (result.success && result.data) {
      detailData.value = result.data
    } else {
      toast.add({ severity: 'warn', summary: '提示', detail: '暂无详情数据', life: 3000 })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取详情失败', life: 5000 })
  } finally {
    detailLoading.value = false
  }
}

// ============================================
// 事件处理
// ============================================

const onPageChange = (event: any) => {
  pagination.value.page = (event.page || 0) + 1
  fetchAccounts()
}

const onSort = (event: any) => {
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
  pagination.value.page = 1
  currentSort.value = { field: 'attendance_count', order: 'desc' }
  fetchAccounts()
}

const exportExcel = () => {
  toast.add({ severity: 'info', summary: '导出', detail: 'Excel 导出功能开发中', life: 3000 })
}

const exportCSV = () => {
  toast.add({ severity: 'info', summary: '导出', detail: 'CSV 导出功能开发中', life: 3000 })
}

// ============================================
// 工具函数
// ============================================

const formatDateParam = (date: Date): string => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const formatDate = (iso: string): string => {
  try {
    const d = new Date(iso)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

const formatDateTime = (iso: string): string => {
  try {
    const d = new Date(iso)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

const formatNumber = (num: number | string | undefined): string => {
  const n = Number(num)
  if (!n && n !== 0) return '0'
  if (n >= 1000000) {
    return (n / 1000000).toFixed(1) + 'M'
  } else if (n >= 1000) {
    return (n / 1000).toFixed(1) + 'K'
  }
  return n.toLocaleString()
}

const formatDuration = (seconds: number | string | undefined): string => {
  const s = Number(seconds)
  if (!s || isNaN(s)) return '0分钟'
  const hours = Math.floor(s / 3600)
  const minutes = Math.floor((s % 3600) / 60)
  if (hours > 0 && minutes > 0) {
    return `${hours}小时${minutes}分钟`
  }
  if (hours > 0) {
    return `${hours}小时`
  }
  return `${minutes}分钟`
}

// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchFilters()
  fetchAccounts()
})
</script>

<style scoped lang="css">
/* 游戏化卡片变体 */
.card-mythic {
  position: relative;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);
  overflow: hidden;
  box-shadow: 0 1px 3px var(--color-shadow);
  border-left: 3px solid var(--color-mythic);
}
</style>
