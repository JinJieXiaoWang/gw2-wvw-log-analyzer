/**
 * 数据加载管理 Hook
 * 功能：统一的数据加载、加载状态管理、错误处理
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { ref, computed } from 'vue'
import { logError, createErrorFromError, getErrorMessage } from '@/utils/error/errorHandler'

interface UseDataOptions<T> {
  initialData?: T
  initialLoading?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: any) => void
  defaultValue?: T
}

export function useData<T = any>(options: UseDataOptions<T> = {}) {
  const data = ref<T | null>(options.initialData || null)
  const isLoading = ref(options.initialLoading || false)
  const error = ref<any>(null)
  const isSuccess = ref(false)
  const isError = computed(() => error.value !== null)
  const errorMessage = computed(() => getErrorMessage(error.value))

  async function execute(
    fetchFn: () => Promise<T>,
    executeOptions: { showLoading?: boolean } = {}
  ): Promise<T | null> {
    if (executeOptions.showLoading !== false) {
      isLoading.value = true
    }
    error.value = null
    isSuccess.value = false

    try {
      const result = await fetchFn()
      data.value = result
      isSuccess.value = true
      
      if (options.onSuccess) {
        options.onSuccess(result)
      }
      
      return result
    } catch (err) {
      error.value = createErrorFromError(err)
      logError(err)
      
      if (options.onError) {
        options.onError(err)
      }
      
      return options.defaultValue || null
    } finally {
      isLoading.value = false
    }
  }

  function setData(newData: T) {
    data.value = newData
    isSuccess.value = true
    error.value = null
  }

  function clearData() {
    data.value = options.initialData || null
    error.value = null
    isSuccess.value = false
  }

  function reset() {
    clearData()
    isLoading.value = false
  }

  return {
    data,
    isLoading,
    error,
    isSuccess,
    isError,
    errorMessage,
    execute,
    setData,
    clearData,
    reset
  }
}

export function useAsyncAction<T = any>() {
  const isLoading = ref(false)
  const error = ref<any>(null)

  async function execute(action: () => Promise<T>): Promise<T | null> {
    isLoading.value = true
    error.value = null

    try {
      const result = await action()
      return result
    } catch (err) {
      error.value = createErrorFromError(err)
      logError(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    execute
  }
}
