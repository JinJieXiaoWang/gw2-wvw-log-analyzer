import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { skillRotationService } from '@/services/build/skillRotationService'
import { logsService } from '@/services/combat/logsService'
import { configManager } from '@/services/core/configManager'

export function useSkillRotation() {
  const toast = useToast()
  const isAnalyzing = ref(false)
  const selectedLogId = ref('')
  const selectedMemberId = ref('')
  const viewMode = ref<'actual' | 'ideal'>('actual')
  const analysisResult = ref<any>(null)
  const logOptions = ref<any[]>([])
  const memberOptions = ref<any[]>([])

  const currentRotation = computed(() => {
    if (!analysisResult.value) return []
    return viewMode.value === 'actual' ? analysisResult.value.rotations : analysisResult.value.idealRotation
  })

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const loadLogs = async () => {
    try {
      const response = await logsService.getLogs({})
      if (response.success && response.data) {
        const data = response.data as Record<string, unknown>
        const items = Array.isArray(data) ? data : ((data.items as unknown[]) || [])
        logOptions.value = items.map((log) => ({ value: (log as Record<string, unknown>).id, label: (log as Record<string, unknown>).filename as string || (log as Record<string, unknown>).fileName as string || `Log ${(log as Record<string, unknown>).id}` }))
      }
    } catch (error: unknown) {
      toast.add({ severity: 'error', summary: '加载失败', detail: '日志列表加载失败，请刷新重试', life: configManager.get('ui').toastErrorLife })
    }
  }

  const handleLogChange = async () => {
    selectedMemberId.value = ''
    if (!selectedLogId.value) { memberOptions.value = []; return }
    try {
      const response = await logsService.getLog(Number(selectedLogId.value))
      const data = response.success ? response.data : null
      const members = data?.members || data?.players || []
      memberOptions.value = members.map((m) => ({ id: (m as Record<string, unknown>).id || (m as Record<string, unknown>).member_id, name: (m as Record<string, unknown>).name as string || (m as Record<string, unknown>).character_name as string || (m as Record<string, unknown>).account as string || (m as Record<string, unknown>).accountName as string || `Player ${(m as Record<string, unknown>).id}` }))
    } catch (error: unknown) {
      toast.add({ severity: 'error', summary: '加载失败', detail: '日志详情加载失败，请刷新重试', life: configManager.get('ui').toastErrorLife })
    }
  }

  const handleAnalyze = async () => {
    if (!selectedLogId.value || !selectedMemberId.value) {
      toast.add({ severity: 'warn', summary: '请选择日志和玩家', detail: '请先选择一个战斗日志和玩家', life: configManager.get('ui').toastLife })
      return
    }
    isAnalyzing.value = true
    try {
      const rotationResponse = await skillRotationService.analyzeSkillRotationByIds(selectedLogId.value, selectedMemberId.value)
      if (rotationResponse.success && rotationResponse.data) {
        analysisResult.value = rotationResponse.data
        toast.add({ severity: 'success', summary: '分析完成', detail: '技能循环分析完成', life: configManager.get('ui').toastLife })
      }
    } catch (error) {
      toast.add({ severity: 'error', summary: '分析失败', detail: error instanceof Error ? error.message : '分析技能循环失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      isAnalyzing.value = false
    }
  }

  onMounted(() => loadLogs())

  return { isAnalyzing, selectedLogId, selectedMemberId, viewMode, analysisResult, logOptions, memberOptions, currentRotation, formatTime, handleLogChange, handleAnalyze }
}
