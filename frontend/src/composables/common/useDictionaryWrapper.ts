import { NormalDisable } from '@/constants/dictValues'
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { dictionaryService, type DictType } from '@/services/system/dictionaryService'
import { usePermission } from '@/composables/system/usePermission'
import { configManager } from '@/services/core/configManager'

export function useDictionaryWrapper() {
  const toast = useToast()
  const { isOperator, isSuperAdmin } = usePermission()

  const viewMode = ref<'overview' | 'management'>('overview')
  const dictManagementRef = ref()
  const dictTypes = ref<DictType[]>([])
  const loading = ref(false)
  const refreshing = ref(false)
  const initializing = ref(false)
  const cacheStatus = ref(true)
  const showInitDialog = ref(false)
  const isCollapsed = ref(false)

  const canWrite = computed(() => isOperator.value || isSuperAdmin.value)
  const typeStats = computed(() => ({
    total: dictTypes.value.length,
    enabled: dictTypes.value.filter(t => String(t.status) === NormalDisable.ENABLED).length,
    disabled: dictTypes.value.filter(t => String(t.status) === NormalDisable.DISABLED).length,
  }))
  const dataStats = computed(() => ({ total: dictTypes.value.length * 5 }))

  function toggleSidebar() {
    isCollapsed.value = !isCollapsed.value
    if (dictManagementRef.value?.toggleSidebar) dictManagementRef.value.toggleSidebar()
  }

  async function loadOverviewData() {
    loading.value = true
    try {
      dictTypes.value = await dictionaryService.getAllTypes()
    } catch (error) { console.error('[DictionaryWrapper] 加载概览数据失败', error) }
    finally { loading.value = false }
  }

  async function handleQuickReload() {
    refreshing.value = true
    try {
      const success = await dictionaryService.reloadCache()
      if (success) {
        cacheStatus.value = true
        toast.add({ severity: 'success', summary: '刷新成功', detail: '字典缓存已刷新', life: configManager.get('ui').toastLife })
      }
    } catch (error) { console.error('[DictionaryWrapper] 刷新缓存失败', error) }
    finally { refreshing.value = false }
  }

  async function handleReloadCache() {
    await handleQuickReload()
    if (dictManagementRef.value?.handleReloadCache) await dictManagementRef.value.handleReloadCache()
  }

  async function handleInitData() {
    initializing.value = true
    try {
      const success = await dictionaryService.init()
      if (success) {
        toast.add({ severity: 'success', summary: '初始化成功', detail: '字典数据已重新初始化', life: configManager.get('ui').toastLife })
        showInitDialog.value = false
        await loadOverviewData()
      }
    } catch (error) { console.error('[DictionaryWrapper] 初始化数据失败', error) }
    finally { initializing.value = false }
  }

  return {
    viewMode, dictManagementRef, dictTypes, loading, refreshing, initializing,
    cacheStatus, showInitDialog, isCollapsed, canWrite, typeStats, dataStats,
    toggleSidebar, loadOverviewData, handleQuickReload, handleReloadCache, handleInitData
  }
}
