import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { apiFactory } from '@/services/core/apiService'
import { configManager } from '@/services/core/configManager'

export function useDpsReportTest() {
  const toast = useToast()
  const fileInput = ref<HTMLInputElement | null>(null)
  const isDragging = ref(false)
  const selectedFile = ref<File | null>(null)
  const loading = ref(false)
  const result = ref<Record<string, any> | null>(null)

  const fmtSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const onDrop = (e: DragEvent) => {
    isDragging.value = false
    const files = e.dataTransfer?.files
    if (files?.length) { selectedFile.value = files[0]; result.value = null }
  }

  const onFileChange = (e: Event) => {
    const files = (e.target as HTMLInputElement).files
    if (files?.length) { selectedFile.value = files[0]; result.value = null }
  }

  const startTest = async () => {
    if (!selectedFile.value) return
    loading.value = true; result.value = null
    try {
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      const res = await apiFactory.post('/api/v1/test/dps-report', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 })
      if (res.success && res.data) {
        result.value = res.data as Record<string, any>
        toast.add({ severity: 'success', summary: '测试完成', detail: `总耗时 ${(res.data as Record<string, any>).total_time_ms}ms`, life: configManager.get('ui').toastLife })
      } else {
        toast.add({ severity: 'error', summary: '测试失败', detail: res.message || '未知错误', life: configManager.get('ui').toastErrorLife })
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '请求失败', detail: e.message || '网络错误', life: configManager.get('ui').toastErrorLife })
    } finally { loading.value = false }
  }

  return { fileInput, isDragging, selectedFile, loading, result, fmtSize, onDrop, onFileChange, startTest }
}
