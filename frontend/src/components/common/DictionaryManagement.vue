<template>
  <div class="dictionary-management">
    <!-- 主内容区 -->
    <div class="content-layout">
      <!-- 左侧字典类型列表 -->
      <aside
        class="sidebar"
        :class="{ collapsed: isCollapsed }"
      >
        <div class="sidebar-header">
          <h2 class="sidebar-title">
            字典分类
          </h2>
          <span class="dict-count">{{ dictTypes.length }} 个分类</span>
        </div>

        <div class="search-box">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="searchKeyword"
              placeholder="搜索分类..."
              size="small"
              class="w-full"
            />
          </IconField>
        </div>

        <div class="dict-type-list">
          <div
            v-for="dictType in filteredDictTypes"
            :key="dictType.dict_id"
            class="dict-type-item"
            :class="{ active: selectedDictType?.dict_id === dictType.dict_id }"
            @click="selectDictType(dictType)"
          >
            <div class="dict-type-info">
              <span class="dict-type-name">{{ dictType.dict_name }}</span>
              <span class="dict-type-code">{{ dictType.dict_type }}</span>
            </div>
            <div class="dict-type-meta">
              <Tag
                :value="dictType.status === 0 ? '启用' : '禁用'"
                :severity="dictType.status === 0 ? 'success' : 'danger'"
                class="status-tag"
              />
            </div>
          </div>

          <div
            v-if="filteredDictTypes.length === 0"
            class="empty-list"
          >
            <i class="pi pi-inbox" />
            <span>暂无分类</span>
          </div>
        </div>
      </aside>

      <!-- 右侧字典数据区 -->
      <main class="main-content">
        <!-- 数据概览卡片 -->
        <div class="overview-cards">
          <div class="overview-card">
            <div class="card-icon primary">
              <i class="pi pi-list" />
            </div>
            <div class="card-content">
              <span class="card-value">{{ dictData.length }}</span>
              <span class="card-label">当前页数据</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon success">
              <i class="pi pi-check-circle" />
            </div>
            <div class="card-content">
              <span class="card-value">{{ enabledCount }}</span>
              <span class="card-label">启用数量</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon warning">
              <i class="pi pi-ban" />
            </div>
            <div class="card-content">
              <span class="card-value">{{ disabledCount }}</span>
              <span class="card-label">禁用数量</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon info">
              <i class="pi pi-sitemap" />
            </div>
            <div class="card-content">
              <span class="card-value">{{ dictTypes.length }}</span>
              <span class="card-label">分类总数</span>
            </div>
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <h3 class="toolbar-title">
              <template v-if="selectedDictType">
                {{ selectedDictType.dict_name }}
                <span class="text-xs text-neutral-text-secondary ml-2">
                  ({{ selectedDictType.dict_type }})
                </span>
              </template>
              <template v-else>
                请选择字典分类
              </template>
            </h3>
          </div>
          <div class="toolbar-right">
            <IconField>
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="dataSearchKeyword"
                placeholder="搜索数据..."
                size="small"
                :disabled="!selectedDictType"
              />
            </IconField>
            <Select
              v-model="statusFilter"
              :options="statusOptions"
              option-label="label"
              option-value="value"
              placeholder="状态筛选"
              size="small"
              class="status-select"
              :disabled="!selectedDictType"
            />
            <Button
              v-if="isAdmin"
              label="新增"
              icon="pi pi-plus"
              severity="success"
              size="small"
              :disabled="!selectedDictType"
              @click="openAddDialog"
            />
            <Button
              v-if="isAdmin && selectedDictType"
              label="编辑分类"
              icon="pi pi-pencil"
              severity="warning"
              outlined
              size="small"
              @click="openEditTypeDialog"
            />
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="data-table-container">
          <DataTable
            v-if="selectedDictType"
            :value="filteredDictData"
            :loading="loading"
            :paginator="filteredDictData.length > 10"
            :rows="10"
            :rows-per-page-options="[10, 20, 50]"
            striped-rows
            removable-sort
            sort-field="dict_sort"
            :sort-order="1"
            class="dict-data-table"
          >
            <Column
              field="dict_sort"
              header="排序"
              sortable
              style="width: 80px"
            >
              <template #body="{ data }">
                <span class="sort-value">{{ data.dict_sort }}</span>
              </template>
            </Column>

            <Column
              field="dict_label"
              header="标签"
              sortable
            >
              <template #body="{ data }">
                <div class="label-cell">
                  <span class="label-text">{{ data.dict_label }}</span>
                  <span
                    v-if="data.is_default === 1"
                    class="default-badge"
                  >默认</span>
                </div>
              </template>
            </Column>

            <Column
              field="dict_value"
              header="值"
              sortable
            >
              <template #body="{ data }">
                <span class="value-text">{{ data.dict_value }}</span>
              </template>
            </Column>

            <Column
              field="css_class"
              header="颜色"
              style="width: 120px"
            >
              <template #body="{ data }">
                <div
                  v-if="data.css_class"
                  class="color-cell"
                >
                  <span
                    class="color-swatch"
                    :style="{ backgroundColor: data.css_class }"
                  />
                  <span class="color-value">{{ data.css_class }}</span>
                </div>
                <span
                  v-else
                  class="no-color"
                >-</span>
              </template>
            </Column>

            <Column
              field="list_class"
              header="列表样式"
              style="width: 100px"
            >
              <template #body="{ data }">
                <span
                  v-if="data.list_class"
                  class="list-class"
                >{{ data.list_class }}</span>
                <span
                  v-else
                  class="no-color"
                >-</span>
              </template>
            </Column>

            <Column
              field="status"
              header="状态"
              sortable
              style="width: 80px"
            >
              <template #body="{ data }">
                <Tag
                  :value="data.status === 0 ? '启用' : '禁用'"
                  :severity="data.status === 0 ? 'success' : 'danger'"
                />
              </template>
            </Column>

            <Column
              field="remark"
              header="备注"
            >
              <template #body="{ data }">
                <span class="remark-text">{{ data.remark || '-' }}</span>
              </template>
            </Column>

            <Column
              v-if="isAdmin"
              header="操作"
              style="width: 150px"
              frozen
              align-frozen="right"
            >
              <template #body="{ data }">
                <div class="action-buttons">
                  <Button
                    icon="pi pi-pencil"
                    severity="warning"
                    text
                    rounded
                    size="small"
                    @click="openEditDialog(data)"
                  />
                  <Button
                    icon="pi pi-trash"
                    severity="danger"
                    text
                    rounded
                    size="small"
                    @click="confirmDelete(data)"
                  />
                </div>
              </template>
            </Column>

            <template #empty>
              <div class="table-empty">
                <i class="pi pi-inbox" />
                <span v-if="!selectedDictType">请选择左侧字典分类</span>
                <span v-else>暂无数据</span>
              </div>
            </template>
          </DataTable>

          <div
            v-else
            class="no-selection"
          >
            <i class="pi pi-book" />
            <h3>请选择字典分类</h3>
            <p>从左侧列表选择一个字典分类来查看和编辑数据</p>
          </div>
        </div>
      </main>
    </div>

    <!-- 新增/编辑字典项弹窗 -->
    <Dialog
      v-model:visible="showDataDialog"
      :header="editingData ? '编辑字典项' : '新增字典项'"
      :style="{ width: '500px' }"
      :modal="true"
      class="dict-data-dialog"
    >
      <div class="dialog-form">
        <div class="form-row">
          <label class="form-label">标签 *</label>
          <InputText
            v-model="dataForm.dict_label"
            placeholder="请输入显示标签"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">值 *</label>
          <InputText
            v-model="dataForm.dict_value"
            placeholder="请输入存储值"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">排序</label>
          <InputNumber
            v-model="dataForm.dict_sort"
            :min="0"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">CSS样式/颜色</label>
          <ColorPickerInput v-model="dataForm.css_class" />
        </div>
        <div class="form-row">
          <label class="form-label">列表样式</label>
          <InputText
            v-model="dataForm.list_class"
            placeholder="如: primary, secondary"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">状态</label>
          <Select
            v-model="dataForm.status"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">备注</label>
          <Textarea
            v-model="dataForm.remark"
            placeholder="请输入备注说明"
            rows="3"
            class="w-full"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          severity="secondary"
          outlined
          @click="showDataDialog = false"
        />
        <Button
          :label="editingData ? '保存' : '新增'"
          severity="primary"
          :loading="saving"
          @click="saveData"
        />
      </template>
    </Dialog>

    <!-- 编辑分类弹窗 -->
    <Dialog
      v-model:visible="showTypeDialog"
      header="编辑字典分类"
      :style="{ width: '450px' }"
      :modal="true"
      class="dict-type-dialog"
    >
      <div class="dialog-form">
        <div class="form-row">
          <label class="form-label">分类名称 *</label>
          <InputText
            v-model="typeForm.dict_name"
            placeholder="请输入分类名称"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">分类编码 *</label>
          <InputText
            v-model="typeForm.dict_type"
            placeholder="请输入分类编码"
            :disabled="!!editingType"
            class="w-full"
          />
          <small class="form-hint">编码一旦创建不可修改</small>
        </div>
        <div class="form-row">
          <label class="form-label">排序</label>
          <InputNumber
            v-model="typeForm.sort_order"
            :min="0"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">状态</label>
          <Select
            v-model="typeForm.status"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
        <div class="form-row">
          <label class="form-label">备注</label>
          <Textarea
            v-model="typeForm.remark"
            placeholder="请输入备注说明"
            rows="3"
            class="w-full"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          severity="secondary"
          outlined
          @click="showTypeDialog = false"
        />
        <Button
          v-if="isAdmin"
          label="保存"
          severity="primary"
          :loading="saving"
          @click="saveType"
        />
      </template>
    </Dialog>

    <!-- 初始化确认弹窗 -->
    <Dialog
      v-model:visible="showInitDialog"
      header="初始化字典数据"
      :style="{ width: '450px' }"
      :modal="true"
      class="init-dialog"
    >
      <div class="init-warning">
        <i class="pi pi-exclamation-triangle" />
        <div class="warning-content">
          <h4>确认要初始化字典数据吗？</h4>
          <p>初始化操作将重置所有字典数据到系统默认值。</p>
          <p class="warning-text">
            此操作不可恢复，请谨慎操作！
          </p>
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          severity="secondary"
          outlined
          @click="showInitDialog = false"
        />
        <Button
          label="确认初始化"
          severity="danger"
          :loading="initializing"
          @click="handleInit"
        />
      </template>
    </Dialog>

    <!-- 删除确认弹窗 -->
    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
/**
 * 字典管理页面组件
 * 功能：提供字典类型和字典数据的增删改查功能
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useDictTypes } from '@/composables/core/useDictMapping'
import { dictionaryService, type DictType, type DictData } from '@/services/system/dictionaryService'
import { usePermission } from '@/composables/system/usePermission'
import ColorPickerInput from '@/components/common/ColorPickerInput.vue'

// =============================================
// 权限判断
// =============================================
const { isAuthenticated } = usePermission()
const isAdmin = computed(() => isAuthenticated.value)

// =============================================
// Toast & Confirm
// =============================================
const toast = useToast()
const confirm = useConfirm()

// =============================================
// 状态
// =============================================
const isCollapsed = ref(false)
const searchKeyword = ref('')
const dataSearchKeyword = ref('')
const statusFilter = ref<number | null>(null)
const refreshing = ref(false)
const saving = ref(false)
const initializing = ref(false)
const showDataDialog = ref(false)
const showTypeDialog = ref(false)
const showInitDialog = ref(false)
const editingData = ref<DictData | null>(null)
const editingType = ref<DictType | null>(null)

// =============================================
// 字典类型相关
// =============================================
const { data: dictTypes, loading: typesLoading, loadDictTypes, refresh: refreshTypes } = useDictTypes()

const filteredDictTypes = computed(() => {
  if (!searchKeyword.value) return dictTypes.value
  const keyword = searchKeyword.value.toLowerCase()
  return dictTypes.value.filter(
    t => t.dict_name.toLowerCase().includes(keyword) || t.dict_type.toLowerCase().includes(keyword)
  )
})

const selectedDictType = ref<DictType | null>(null)

function selectDictType(dictType: DictType) {
  selectedDictType.value = dictType
  loadDictDataByType(dictType.dict_type)
}

// =============================================
// 字典数据相关
// =============================================
const dictData = ref<DictData[]>([])
const dataLoading = ref(false)

async function loadDictDataByType(dictType: string) {
  dataLoading.value = true
  try {
    const result = await dictionaryService.getData(dictType, 1, 200)
    if (result) {
      dictData.value = result.items
    }
  } catch (error) {
    console.error('[DictionaryManagement] 加载字典数据失败', error)
    toast.add({
      severity: 'error',
      summary: '加载失败',
      detail: '无法加载字典数据',
      life: 3000
    })
  } finally {
    dataLoading.value = false
  }
}

const filteredDictData = computed(() => {
  let result = dictData.value

  if (statusFilter.value !== null) {
    result = result.filter(d => d.status === statusFilter.value)
  }

  if (dataSearchKeyword.value) {
    const keyword = dataSearchKeyword.value.toLowerCase()
    result = result.filter(
      d =>
        d.dict_label.toLowerCase().includes(keyword) ||
        d.dict_value.toLowerCase().includes(keyword) ||
        (d.remark && d.remark.toLowerCase().includes(keyword))
    )
  }

  return result
})

const enabledCount = computed(() => dictData.value.filter(d => d.status === 0).length)
const disabledCount = computed(() => dictData.value.filter(d => d.status === 1).length)

const loading = computed(() => dataLoading.value || typesLoading.value)

// =============================================
// 表单数据
// =============================================
const statusOptions = [
  { label: '全部', value: null },
  { label: '启用', value: 0 },
  { label: '禁用', value: 1 }
]

const dataForm = ref({
  dict_label: '',
  dict_value: '',
  dict_sort: 0,
  css_class: '',
  list_class: '',
  status: 0,
  remark: ''
})

const typeForm = ref({
  dict_name: '',
  dict_type: '',
  sort_order: 0,
  status: 0,
  remark: ''
})

// =============================================
// 操作方法
// =============================================
function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

function openAddDialog() {
  editingData.value = null
  dataForm.value = {
    dict_label: '',
    dict_value: '',
    dict_sort: 0,
    css_class: '',
    list_class: '',
    status: 0,
    remark: ''
  }
  showDataDialog.value = true
}

function openEditDialog(data: DictData) {
  editingData.value = data
  dataForm.value = {
    dict_label: data.dict_label,
    dict_value: data.dict_value,
    dict_sort: data.dict_sort,
    css_class: data.css_class || '',
    list_class: data.list_class || '',
    status: data.status,
    remark: data.remark || ''
  }
  showDataDialog.value = true
}

function openEditTypeDialog() {
  if (!selectedDictType.value) return
  editingType.value = selectedDictType.value
  typeForm.value = {
    dict_name: selectedDictType.value.dict_name,
    dict_type: selectedDictType.value.dict_type,
    sort_order: selectedDictType.value.sort_order,
    status: selectedDictType.value.status,
    remark: selectedDictType.value.remark || ''
  }
  showTypeDialog.value = true
}

async function saveData() {
  if (!selectedDictType.value || !dataForm.value.dict_label || !dataForm.value.dict_value) {
    toast.add({
      severity: 'warn',
      summary: '表单不完整',
      detail: '请填写标签和值',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    if (editingData.value) {
      await dictionaryService.updateDataItem(editingData.value.dict_code, {
        dict_label: dataForm.value.dict_label,
        dict_value: dataForm.value.dict_value,
        dict_sort: dataForm.value.dict_sort,
        css_class: dataForm.value.css_class,
        list_class: dataForm.value.list_class,
        status: dataForm.value.status,
        remark: dataForm.value.remark
      })
      toast.add({
        severity: 'success',
        summary: '更新成功',
        detail: '字典项已更新',
        life: 3000
      })
    } else {
      await dictionaryService.createDataItem({
        dict_type: selectedDictType.value.dict_type,
        dict_label: dataForm.value.dict_label,
        dict_value: dataForm.value.dict_value,
        dict_sort: dataForm.value.dict_sort,
        css_class: dataForm.value.css_class,
        list_class: dataForm.value.list_class,
        status: dataForm.value.status,
        remark: dataForm.value.remark
      })
      toast.add({
        severity: 'success',
        summary: '创建成功',
        detail: '字典项已创建',
        life: 3000
      })
    }

    showDataDialog.value = false
    await loadDictDataByType(selectedDictType.value.dict_type)
  } catch (error) {
    console.error('[DictionaryManagement] 保存字典项失败', error)
    toast.add({
      severity: 'error',
      summary: '保存失败',
      detail: '保存字典项时发生错误',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

async function saveType() {
  if (!typeForm.value.dict_name || !typeForm.value.dict_type) {
    toast.add({
      severity: 'warn',
      summary: '表单不完整',
      detail: '请填写分类名称和编码',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    if (editingType.value) {
      await dictionaryService.updateDictType(editingType.value.dict_id, {
        dict_name: typeForm.value.dict_name,
        sort_order: typeForm.value.sort_order,
        status: typeForm.value.status,
        remark: typeForm.value.remark
      })
      toast.add({
        severity: 'success',
        summary: '更新成功',
        detail: '字典分类已更新',
        life: 3000
      })
    } else {
      await dictionaryService.createDictType({
        dict_name: typeForm.value.dict_name,
        dict_type: typeForm.value.dict_type,
        sort_order: typeForm.value.sort_order,
        status: typeForm.value.status,
        remark: typeForm.value.remark
      })
      toast.add({
        severity: 'success',
        summary: '创建成功',
        detail: '字典分类已创建',
        life: 3000
      })
    }

    showTypeDialog.value = false
    await refreshTypes()
  } catch (error) {
    console.error('[DictionaryManagement] 保存字典分类失败', error)
    toast.add({
      severity: 'error',
      summary: '保存失败',
      detail: '保存字典分类时发生错误',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

function confirmDelete(data: DictData) {
  confirm.require({
    message: `确定要删除字典项 "${data.dict_label}" 吗？`,
    header: '确认删除',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await dictionaryService.deleteDataItem(data.dict_code)
        toast.add({
          severity: 'success',
          summary: '删除成功',
          detail: '字典项已删除',
          life: 3000
        })
        if (selectedDictType.value) {
          await loadDictDataByType(selectedDictType.value.dict_type)
        }
      } catch (error) {
        console.error('[DictionaryManagement] 删除字典项失败', error)
        toast.add({
          severity: 'error',
          summary: '删除失败',
          detail: '删除字典项时发生错误',
          life: 3000
        })
      }
    }
  })
}

async function handleReloadCache() {
  refreshing.value = true
  try {
    const success = await dictionaryService.reloadCache()
    if (success) {
      toast.add({
        severity: 'success',
        summary: '刷新成功',
        detail: '字典缓存已刷新',
        life: 3000
      })
      await refreshTypes()
    }
  } catch (error) {
    console.error('[DictionaryManagement] 刷新缓存失败', error)
    toast.add({
      severity: 'error',
      summary: '刷新失败',
      detail: '刷新缓存时发生错误',
      life: 3000
    })
  } finally {
    refreshing.value = false
  }
}

async function handleInit() {
  initializing.value = true
  try {
    const success = await dictionaryService.init()
    if (success) {
      toast.add({
        severity: 'success',
        summary: '初始化成功',
        detail: '字典数据已初始化',
        life: 3000
      })
      showInitDialog.value = false
      await refreshTypes()
    }
  } catch (error) {
    console.error('[DictionaryManagement] 初始化失败', error)
    toast.add({
      severity: 'error',
      summary: '初始化失败',
      detail: '初始化字典数据时发生错误',
      life: 3000
    })
  } finally {
    initializing.value = false
  }
}

// =============================================
// 生命周期
// =============================================
onMounted(async () => {
  await loadDictTypes()
})

// 暴露方法给父组件
defineExpose({
  toggleSidebar,
  handleReloadCache
})
</script>

<style scoped>
.dictionary-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  gap: 16px;
}

.content-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.sidebar {
  width: 300px;
  flex-shrink: 0;
  background: #2a2a2a;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #e5e5e5;
  margin: 0;
}

.dict-count {
  font-size: 12px;
  color: #909399;
  background: #333;
  padding: 2px 8px;
  border-radius: 10px;
}

.search-box {
  padding: 12px 16px;
}

.dict-type-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.dict-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.dict-type-item:hover {
  background: #333;
}

.dict-type-item.active {
  background: rgba(22, 93, 255, 0.2);
  border: 1px solid #165dff;
}

.dict-type-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dict-type-name {
  font-size: 14px;
  font-weight: 500;
  color: #e5e5e5;
}

.dict-type-code {
  font-size: 12px;
  color: #909399;
}

.status-tag {
  font-size: 10px;
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview-card {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.card-icon.primary {
  background: rgba(22, 93, 255, 0.2);
  color: #165dff;
}

.card-icon.success {
  background: rgba(38, 191, 99, 0.2);
  color: #26bf63;
}

.card-icon.warning {
  background: rgba(255, 125, 0, 0.2);
  color: #ff7d00;
}

.card-icon.info {
  background: rgba(0, 200, 150, 0.2);
  color: #00c896;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #e5e5e5;
}

.card-label {
  font-size: 12px;
  color: #909399;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #2a2a2a;
  border-radius: 12px;
  padding: 12px 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-title {
  font-size: 16px;
  font-weight: 600;
  color: #e5e5e5;
  margin: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-select {
  width: 120px;
}

.data-table-container {
  flex: 1;
  background: #2a2a2a;
  border-radius: 12px;
  overflow: hidden;
}

.dict-data-table {
  font-size: 14px;
}

.sort-value,
.value-text,
.remark-text {
  color: #e5e5e5;
}

.label-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label-text {
  color: #e5e5e5;
  font-weight: 500;
}

.default-badge {
  font-size: 10px;
  background: #165dff;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
}

.color-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #333;
}

.color-value {
  font-size: 12px;
  color: #909399;
}

.no-color {
  color: #909399;
}

.list-class {
  font-size: 12px;
  color: #00c896;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
  gap: 12px;
}

.table-empty i {
  font-size: 48px;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  gap: 16px;
}

.no-selection i {
  font-size: 64px;
  color: #333;
}

.no-selection h3 {
  font-size: 20px;
  color: #e5e5e5;
  margin: 0;
}

.no-selection p {
  margin: 0;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #e5e5e5;
}

.form-hint {
  font-size: 12px;
  color: #909399;
}

.color-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-preview {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #333;
}

.init-warning {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 125, 0, 0.1);
  border-radius: 8px;
  border: 1px solid #ff7d00;
}

.init-warning i {
  font-size: 32px;
  color: #ff7d00;
}

.warning-content h4 {
  margin: 0 0 8px 0;
  color: #e5e5e5;
}

.warning-content p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.warning-text {
  color: #ff7d00 !important;
  font-weight: 500;
}
</style>