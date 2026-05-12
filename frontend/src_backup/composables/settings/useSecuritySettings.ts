import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { authStore } from '@/composables/system/usePermission'
import { configManager } from '@/services/core/configManager'

export function useSecuritySettings() {
  const toast = useToast()
  const isLoggingOut = ref(false)
  const showChangePasswordDialog = ref(false)

  const handleLogout = async () => {
    isLoggingOut.value = true
    try {
      await authStore.logout()
      return true
    } catch (error) {
      console.error('Logout failed:', error)
      toast.add({ severity: 'error', summary: '登出失败', detail: '请稍后重试', life: configManager.get('ui').toastLife })
      return false
    } finally {
      isLoggingOut.value = false
    }
  }

  return { isLoggingOut, showChangePasswordDialog, handleLogout }
}
