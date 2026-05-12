<template>
  <div
    v-if="showWarning"
    class="service-warning fixed top-0 left-0 right-0 z-[1000] bg-[linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)]"
  >
    <div class="warning-content flex items-center justify-center gap-3 p-[12px 24px] max-w-[1200px] m-[0 auto] max-md:py-2.5 max-md:px-4">
      <i class="pi pi-exclamation-triangle warning-icon text-[20px] text-[#d97706]" />
      <span class="warning-text text-[14px] font-medium text-[#78350f] max-md:text-[13px]">
        {{ warningMessage }}
      </span>
      <button
        class="close-btn flex items-center justify-center w-7 h-7 bg-black/[0.05] rounded-full cursor-pointer text-[#92400e] hover:bg-black/10 hover:text-[#78350f]"
        @click="dismissWarning"
      >
        <i class="pi pi-times" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const showWarning = ref(false)
const warningMessage = ref('后端服务未响应，请检查服务是否正常启动')
let checkInterval: number | null = null

const checkServiceStatus = async () => {
  try {
    const response = await axios.get('/api/v1/health', { timeout: 3000 })
    if (response.status >= 200 && response.status < 300) {
      showWarning.value = false
      return true
    }
  } catch (error) {
    console.debug('后端服务未响应:', error)
  }
  
  showWarning.value = true
  return false
}

const dismissWarning = () => {
  showWarning.value = false
  sessionStorage.setItem('serviceWarningDismissed', 'true')
  // 停止检查
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
}

onMounted(() => {
  // 检查是否已经隐藏过警告
  if (!sessionStorage.getItem('serviceWarningDismissed')) {
    // 立即检查一次
    checkServiceStatus()
    // 每30秒检查一次
    checkInterval = window.setInterval(checkServiceStatus, 30000)
  }
})

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
})
</script>


