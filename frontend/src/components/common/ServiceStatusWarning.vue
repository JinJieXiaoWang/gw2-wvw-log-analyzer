<template>
  <div
    v-if="showWarning"
    class="service-warning"
  >
    <div class="warning-content">
      <i class="pi pi-exclamation-triangle warning-icon" />
      <span class="warning-text">
        {{ warningMessage }}
      </span>
      <button
        class="close-btn"
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

<style scoped>
.service-warning {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-bottom: 2px solid #f59e0b;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
}

.warning-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.warning-icon {
  font-size: 20px;
  color: #d97706;
}

.warning-text {
  font-size: 14px;
  font-weight: 500;
  color: #78350f;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  cursor: pointer;
  color: #92400e;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #78350f;
}

@media (max-width: 768px) {
  .warning-content {
    padding: 10px 16px;
  }

  .warning-text {
    font-size: 13px;
  }
}
</style>
