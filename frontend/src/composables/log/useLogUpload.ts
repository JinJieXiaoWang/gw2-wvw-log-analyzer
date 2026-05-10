import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { logsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatBytes } from '@/utils/core/helpers'
import { configManager } from '@/services/core/configManager'

type UploadPhase = 'idle' | 'uploading' | 'processing' | 'completed'
type FileUploadPhase = 'pending' | 'uploading' | 'processing' | 'success' | 'error' | 'cancelled'

interface UploadItem {
  phase: FileUploadPhase
  transportPercent: number
  overallPercent: number
  errorMsg?: string
}

export interface UseLogUploadOptions {
  onUploadSuccess?: () => void
}

export function useLogUpload(options: UseLogUploadOptions = {}) {
  const toast = useToast()
  const isDragging = ref(false)
  const selectedFiles = ref<File[]>([])
  const fileInput = ref<HTMLInputElement | null>(null)
  const uploadPhase = ref<UploadPhase>('idle')
  const currentUploadIndex = ref(0)
  const uploadItems = ref<UploadItem[]>([])
  const currentError = ref('')
  const uploadComplete = ref(false)

  const isUploading = computed(() => uploadPhase.value === 'uploading' || uploadPhase.value === 'processing')

  const overallProgress = computed(() => {
    if (selectedFiles.value.length === 0) return 0
    const total = uploadItems.value.reduce((sum, item) => sum + (item?.overallPercent || 0), 0)
    return total / selectedFiles.value.length
  })

  const successCount = computed(() => uploadItems.value.filter(i => i?.phase === 'success').length)
  const failedCount = computed(() => uploadItems.value.filter(i => i?.phase === 'error').length)
  const failedItems = computed(() =>
    uploadItems.value
      .map((item, idx) => ({ name: selectedFiles.value[idx]?.name, error: item?.errorMsg, phase: item?.phase }))
      .filter(i => i.phase === 'error')
  )

  const formatFileSize = formatBytes

  const triggerFileInput = () => fileInput.value?.click()

  const addFiles = (files: File[]) => {
    const zevtcFiles = files.filter(f => f.name.toLowerCase().endsWith('.zevtc'))
    const remainingSlots = 100 - selectedFiles.value.length
    const filesToAdd = zevtcFiles.slice(0, remainingSlots)
    if (zevtcFiles.length > remainingSlots) {
      toast.add({
        severity: 'warn',
        summary: '提示',
        detail: `最多支持100个文件，已自动截取前 ${remainingSlots} 个`,
        life: configManager.get('ui').toastLife
      })
    }
    filesToAdd.forEach(file => {
      if (!selectedFiles.value.some(f => f.name === file.name)) selectedFiles.value.push(file)
    })
    uploadComplete.value = false
    uploadPhase.value = 'idle'
    uploadItems.value = []
    currentError.value = ''
  }

  const onFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      addFiles(Array.from(target.files))
      target.value = ''
    }
  }

  const removeFile = (index: number) => {
    selectedFiles.value.splice(index, 1)
    uploadItems.value.splice(index, 1)
  }

  const clearFiles = () => {
    selectedFiles.value = []
    uploadItems.value = []
    uploadComplete.value = false
    uploadPhase.value = 'idle'
    currentError.value = ''
  }

  const onDragOver = () => { isDragging.value = true }
  const onDragLeave = () => { isDragging.value = false }
  const onDrop = (event: DragEvent) => {
    isDragging.value = false
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      addFiles(Array.from(event.dataTransfer.files))
    }
  }

  const uploadSingleFile = async (
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<{ success: boolean; message?: string }> => {
    try {
      const wrappedResult = await ApiResponseWrapper.wrap(
        logsService.uploadLog(file, { auto_parse: true }, onProgress),
        { showErrorMessage: false }
      )
      if (wrappedResult.success) return { success: true }
      return { success: false, message: wrappedResult.error?.message || '上传失败' }
    } catch (error: any) {
      return { success: false, message: error.message || '上传失败' }
    }
  }

  const uploadFiles = async () => {
    if (selectedFiles.value.length === 0) return
    const totalFiles = selectedFiles.value.length
    uploadPhase.value = 'uploading'
    uploadComplete.value = false
    currentError.value = ''
    currentUploadIndex.value = 0
    uploadItems.value = selectedFiles.value.map(() => ({
      phase: 'pending' as FileUploadPhase,
      transportPercent: 0,
      overallPercent: 0,
    }))

    for (let i = 0; i < totalFiles; i++) {
      currentUploadIndex.value = i
      uploadItems.value[i].phase = 'uploading'
      const onFileProgress = (singlePercent: number) => {
        uploadItems.value[i].transportPercent = singlePercent
        uploadItems.value[i].overallPercent = singlePercent * 0.7
      }
      const result = await uploadSingleFile(selectedFiles.value[i], onFileProgress)
      if (result.success) {
        uploadItems.value[i].phase = 'success'
        uploadItems.value[i].overallPercent = 100
      } else {
        uploadItems.value[i].phase = 'error'
        uploadItems.value[i].errorMsg = result.message
        uploadItems.value[i].overallPercent = 0
      }
    }

    uploadPhase.value = 'completed'
    uploadComplete.value = true
    if (successCount.value > 0) options.onUploadSuccess?.()

    if (failedCount.value === 0) {
      toast.add({ severity: 'success', summary: '上传成功', detail: `成功上传 ${successCount.value} 个文件`, life: configManager.get('ui').toastLife })
    } else if (successCount.value > 0) {
      toast.add({ severity: 'warn', summary: '部分上传成功', detail: `成功 ${successCount.value} 个，失败 ${failedCount.value} 个`, life: configManager.get('ui').toastLife })
    } else {
      toast.add({ severity: 'error', summary: '上传失败', detail: `${failedCount.value} 个文件上传失败`, life: configManager.get('ui').toastLife })
    }
  }

  const reset = () => {
    if (!uploadComplete.value) {
      selectedFiles.value = []
      uploadItems.value = []
    }
    uploadPhase.value = 'idle'
    currentError.value = ''
  }

  return {
    isDragging, selectedFiles, fileInput, uploadPhase, currentUploadIndex,
    uploadItems, currentError, uploadComplete, isUploading, overallProgress,
    successCount, failedCount, failedItems, formatFileSize, triggerFileInput,
    onFileSelect, addFiles, removeFile, clearFiles, onDragOver, onDragLeave,
    onDrop, uploadFiles, reset,
  }
}
