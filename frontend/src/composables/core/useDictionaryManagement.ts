/**
 * 字典管理业务逻辑组合式函数
 */

import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useDictTypes } from '@/composables/core/useDictMapping'
import { dictionaryService, type DictType, type DictData } from '@/services/system/dictionaryService'
import { usePermission } from '@/composables/system/usePermission'
import { useDictStore } from '@/store/system/dict'
import { configManager } from '@/services/core/configManager'
import { STATUS_OPTIONS, EMPTY_DATA_FORM, EMPTY_TYPE_FORM } from '@/utils/core/dictConstants'
import { NormalDisable } from '@/constants/dictValues'

export function useDictionaryManagement() {
  const toast = useToast()
  const confirm = useConfirm()
  const { isAuthenticated } = usePermission()
  const dictStore = useDictStore()
  const isAdmin = computed(() => isAuthenticated.value)

  // ========== ״̬ ==========
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

  // ========== 字典类型 ==========
  const { data: dictTypes, loading: typesLoading, refresh: refreshTypes } = useDictTypes()

  const filteredDictTypes = computed(() => {
    if (!searchKeyword.value) return dictTypes.value
    const kw = searchKeyword.value.toLowerCase()
    return dictTypes.value.filter(
      t => t.dict_name.toLowerCase().includes(kw) || t.dict_type.toLowerCase().includes(kw)
    )
  })

  const selectedDictType = ref<DictType | null>(null)

  function selectDictType(dictType: DictType) {
    selectedDictType.value = dictType
    loadDictDataByType(dictType.dict_type)
  }

  // ========== 字典数据 ==========
  const dictData = ref<DictData[]>([])
  const dataLoading = ref(false)

  async function loadDictDataByType(dictType: string) {
    dataLoading.value = true
    try {
      const result = await dictionaryService.getData(dictType, 1, 200)
      if (result) dictData.value = result.items
    } catch (error) {
      console.error('[DictionaryManagement] 加载字典数据失败', error)
      toast.add({ severity: 'error', summary: '加载失败', detail: '无法加载字典数据', life: configManager.get('ui').toastLife })
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
      const kw = dataSearchKeyword.value.toLowerCase()
      result = result.filter(
        d => d.dict_label.toLowerCase().includes(kw) ||
          d.dict_value.toLowerCase().includes(kw) ||
          (d.remark && d.remark.toLowerCase().includes(kw))
      )
    }
    return result
  })

  const enabledCount = computed(() => dictData.value.filter(d => String(d.status) === NormalDisable.ENABLED).length)
  const disabledCount = computed(() => dictData.value.filter(d => String(d.status) === NormalDisable.DISABLED).length)
  const loading = computed(() => dataLoading.value || typesLoading.value)

  // ========== 表单 ==========
  const dataForm = ref({ ...EMPTY_DATA_FORM })
  const typeForm = ref({ ...EMPTY_TYPE_FORM })

  // ========== 操作 ==========
  function toggleSidebar() {
    isCollapsed.value = !isCollapsed.value
  }

  function openAddDialog() {
    editingData.value = null
    dataForm.value = { ...EMPTY_DATA_FORM }
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
      toast.add({ severity: 'warn', summary: '表单不完整', detail: '请填写标签和值', life: configManager.get('ui').toastLife })
      return
    }
    saving.value = true
    try {
      const payload = {
        dict_label: dataForm.value.dict_label,
        dict_value: dataForm.value.dict_value,
        dict_sort: dataForm.value.dict_sort,
        css_class: dataForm.value.css_class,
        list_class: dataForm.value.list_class,
        status: dataForm.value.status,
        remark: dataForm.value.remark
      }
      if (editingData.value) {
        await dictionaryService.updateDataItem(editingData.value.dict_code, payload)
        toast.add({ severity: 'success', summary: '更新成功', detail: '字典项已更新', life: configManager.get('ui').toastLife })
      } else {
        await dictionaryService.createDataItem({ dict_type: selectedDictType.value.dict_type, ...payload })
        toast.add({ severity: 'success', summary: '创建成功', detail: '字典项已创建', life: configManager.get('ui').toastLife })
      }
      showDataDialog.value = false
      await loadDictDataByType(selectedDictType.value.dict_type)
    } catch (error) {
      console.error('[DictionaryManagement] 保存字典项失败', error)
      toast.add({ severity: 'error', summary: '保存失败', detail: '保存字典项时发生错误', life: configManager.get('ui').toastLife })
    } finally {
      saving.value = false
    }
  }

  async function saveType() {
    if (!typeForm.value.dict_name || !typeForm.value.dict_type) {
      toast.add({ severity: 'warn', summary: '表单不完整', detail: '请填写分类名称和编码', life: configManager.get('ui').toastLife })
      return
    }
    saving.value = true
    try {
      const payload = {
        dict_name: typeForm.value.dict_name,
        sort_order: typeForm.value.sort_order,
        status: typeForm.value.status,
        remark: typeForm.value.remark
      }
      if (editingType.value) {
        await dictionaryService.updateDictType(editingType.value.dict_id, payload)
        toast.add({ severity: 'success', summary: '更新成功', detail: '字典分类已更新', life: configManager.get('ui').toastLife })
      } else {
        await dictionaryService.createDictType({ dict_type: typeForm.value.dict_type, ...payload })
        toast.add({ severity: 'success', summary: '创建成功', detail: '字典分类已创建', life: configManager.get('ui').toastLife })
      }
      showTypeDialog.value = false
      dictStore.cleanDict()
      await refreshTypes()
    } catch (error) {
      console.error('[DictionaryManagement] 保存字典分类失败', error)
      toast.add({ severity: 'error', summary: '保存失败', detail: '保存字典分类时发生错误', life: configManager.get('ui').toastLife })
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
          toast.add({ severity: 'success', summary: '删除成功', detail: '字典项已删除', life: configManager.get('ui').toastLife })
          if (selectedDictType.value) {
            dictStore.removeDict(selectedDictType.value.dict_type)
            await loadDictDataByType(selectedDictType.value.dict_type)
          }
        } catch (error) {
          console.error('[DictionaryManagement] 删除字典项失败', error)
          toast.add({ severity: 'error', summary: '删除失败', detail: '删除字典项时发生错误', life: configManager.get('ui').toastLife })
        }
      }
    })
  }

  async function handleReloadCache() {
    refreshing.value = true
    try {
      const success = await dictionaryService.reloadCache()
      if (success) {
        toast.add({ severity: 'success', summary: '刷新成功', detail: '字典缓存已刷新', life: configManager.get('ui').toastLife })
        dictStore.cleanDict()
        await refreshTypes()
      }
    } catch (error) {
      console.error('[DictionaryManagement] 刷新缓存失败', error)
      toast.add({ severity: 'error', summary: '刷新失败', detail: '刷新缓存时发生错误', life: configManager.get('ui').toastLife })
    } finally {
      refreshing.value = false
    }
  }

  async function handleInit() {
    initializing.value = true
    try {
      const success = await dictionaryService.init()
      if (success) {
        toast.add({ severity: 'success', summary: '初始化成功', detail: '字典数据已初始化', life: configManager.get('ui').toastLife })
        showInitDialog.value = false
        dictStore.cleanDict()
        await refreshTypes()
      }
    } catch (error) {
      console.error('[DictionaryManagement] 初始化失败', error)
      toast.add({ severity: 'error', summary: '初始化失败', detail: '初始化字典数据时发生错误', life: configManager.get('ui').toastLife })
    } finally {
      initializing.value = false
    }
  }

  return {
    isAdmin,
    isCollapsed, searchKeyword, dataSearchKeyword, statusFilter,
    refreshing, saving, initializing,
    showDataDialog, showTypeDialog, showInitDialog,
    editingData, editingType,
    dictTypes, filteredDictTypes, selectedDictType,
    dictData, filteredDictData, enabledCount, disabledCount, loading,
    dataForm, typeForm,
    statusOptions: STATUS_OPTIONS,
    selectDictType, toggleSidebar,
    openAddDialog, openEditDialog, openEditTypeDialog,
    saveData, saveType, confirmDelete, handleReloadCache, handleInit
  }
}
