import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { buildsService } from '@/services/build/buildsService'
import { configManager } from '@/services/core/configManager'

export function useBuildParser() {
  const toast = useToast()
  const buildCode = ref('')
  const isParsing = ref(false)
  const parseError = ref('')
  const parsedData = ref<any>(null)
  const showSaveDialog = ref(false)
  const isSaving = ref(false)
  const showImportDialog = ref(false)

  const eliteSpecName = computed(() => {
    if (!parsedData.value?.specializations) return ''
    const eliteSpec = parsedData.value.specializations.find((spec: any) => spec.is_elite)
    return eliteSpec?.name_cn || ''
  })

  const getProfessionColor = (profession: string) => {
    const colors: Record<string, string> = { Warrior: '#E85D04', Guardian: '#FAA307', Revenant: '#9D4EDD', Ranger: '#06D6A0', Engineer: '#7B8FA1', Necromancer: '#8D0801', Mesmer: '#4361EE', Elementalist: '#FF6B6B' }
    return colors[profession] || '#6C757D'
  }

  const getProfessionInitial = (profession: string) => profession.charAt(0).toUpperCase()
  const cleanIconUrl = (iconUrl: string): string => iconUrl?.trim().replace(/^[`'"]+|[`'"]+$/g, '') || ''

  const handleParseBuildCode = async () => {
    if (!buildCode.value.trim()) { parseError.value = '请输入Build代码'; return }
    const codePattern = /^\[&[A-Za-z0-9+/=]+\]$/
    if (!codePattern.test(buildCode.value.trim())) { parseError.value = 'Build代码格式不正确，应为 [&...] 格式'; return }
    isParsing.value = true; parseError.value = ''
    try {
      const response = await buildsService.parseBuild(buildCode.value.trim())
      if (response.success && response.data) {
        parsedData.value = response.data
        toast.add({ severity: 'success', summary: '解析成功', detail: 'Build代码解析完成', life: configManager.get('ui').toastLife })
      } else { parseError.value = '解析失败，请稍后重试' }
    } catch (error) {
      parseError.value = error instanceof Error ? error.message : '解析失败'
      toast.add({ severity: 'error', summary: '解析失败', detail: parseError.value, life: configManager.get('ui').toastErrorLife })
    } finally { isParsing.value = false }
  }

  const handleClearCode = () => { buildCode.value = ''; parsedData.value = null; parseError.value = '' }
  const handleImportBuildCode = (code: string) => { buildCode.value = code; showImportDialog.value = false }

  const handleSaveBuild = async (buildData: any) => {
    if (isSaving.value) return
    isSaving.value = true
    try {
      const saveResponse = await buildsService.createBuild(buildData)
      if (!saveResponse.success) {
        throw new Error('保存失败')
      }
      showSaveDialog.value = false
      toast.add({ severity: 'success', summary: '保存成功', detail: 'Build配置已保存', life: configManager.get('ui').toastLife })
    } catch (error) {
      toast.add({ severity: 'error', summary: '保存失败', detail: error instanceof Error ? error.message : '保存失败', life: configManager.get('ui').toastErrorLife })
    } finally { isSaving.value = false }
  }

  const handleCopyBuildCode = async () => {
    if (!buildCode.value) return
    try {
      await navigator.clipboard.writeText(buildCode.value)
      toast.add({ severity: 'success', summary: '复制成功', detail: 'Build代码已复制到剪贴板', life: configManager.get('ui').toastLife })
    } catch {
      toast.add({ severity: 'error', summary: '复制失败', detail: '无法复制到剪贴板', life: configManager.get('ui').toastLife })
    }
  }

  return { buildCode, isParsing, parseError, parsedData, showSaveDialog, isSaving, showImportDialog, eliteSpecName, getProfessionColor, getProfessionInitial, cleanIconUrl, handleParseBuildCode, handleClearCode, handleImportBuildCode, handleSaveBuild, handleCopyBuildCode }
}
