<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold">AI配置管理</h2>
      <div 
        class="flex items-center gap-2 px-3 py-1 rounded-full text-sm"
        :class="statusConfig.valid ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'"
      >
        <span class="w-2 h-2 rounded-full" :class="statusConfig.valid ? 'bg-green-500' : 'bg-red-500'"></span>
        {{ statusConfig.valid ? 'AI已启用' : 'AI未配置' }}
      </div>
    </div>

    <!-- 状态概览 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm text-gray-400 mb-2">当前提供商</h3>
        <p class="text-lg font-semibold">{{ statusConfig.provider || '未配置' }}</p>
      </div>
      <div class="bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm text-gray-400 mb-2">缓存状态</h3>
        <p class="text-lg font-semibold">{{ statusConfig.cacheEnabled ? '已启用' : '已禁用' }}</p>
      </div>
      <div class="bg-gray-700 rounded-lg p-4">
        <h3 class="text-sm text-gray-400 mb-2">降级策略</h3>
        <p class="text-lg font-semibold">{{ statusConfig.fallbackEnabled ? '已启用' : '已禁用' }}</p>
      </div>
    </div>

    <!-- 配置表单 -->
    <div class="bg-gray-700 rounded-lg p-4 mb-6">
      <h3 class="font-medium mb-4">API密钥配置</h3>
      
      <!-- 提供商选择 -->
      <div class="mb-4">
        <label class="block text-sm text-gray-400 mb-2">选择AI提供商</label>
        <select 
          v-model="configForm.provider"
          class="w-full bg-gray-600 rounded-lg px-4 py-2 text-white border-gray-500 focus:border-blue-500 focus:outline-none"
        >
          <option value="deepseek">DeepSeek</option>
          <option value="openai">OpenAI</option>
          <option value="qwen">通义千问</option>
        </select>
      </div>

      <!-- API密钥输入 -->
      <div class="mb-4">
        <label class="block text-sm text-gray-400 mb-2">API密钥</label>
        <div class="relative">
          <input 
            v-model="configForm.apiKey"
            :type="showApiKey ? 'text' : 'password'"
            placeholder="输入您的API密钥"
            class="w-full bg-gray-600 rounded-lg px-4 py-2 text-white border-gray-500 focus:border-blue-500 focus:outline-none pr-20"
          />
          <button 
            @click="showApiKey = !showApiKey"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            <SvgIcon :icon="showApiKey ? 'eye-off' : 'eye'" :size="18" />
          </button>
        </div>
      </div>

      <!-- 测试配置 -->
      <div class="flex gap-3">
        <button 
          @click="testConfiguration"
          :disabled="testing || !configForm.apiKey"
          class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
        >
          <span v-if="testing" class="flex items-center justify-center gap-2">
            <span class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></span>
            测试中...
          </span>
          <span v-else>测试配置</span>
        </button>
      </div>
    </div>

    <!-- 测试结果 -->
    <div v-if="testResult" class="mb-6">
      <div 
        class="rounded-lg p-4"
        :class="testResult.success ? 'bg-green-900/30 border border-green-700' : 'bg-red-900/30 border border-red-700'"
      >
        <div class="flex items-center gap-2 mb-2">
          <SvgIcon 
            :icon="testResult.success ? 'check' : 'x'" 
            :size="20" 
            :class="testResult.success ? 'text-green-400' : 'text-red-400'"
          />
          <span :class="testResult.success ? 'text-green-400' : 'text-red-400'" class="font-medium">
            {{ testResult.success ? '配置验证成功' : '配置验证失败' }}
          </span>
        </div>
        <p class="text-sm text-gray-300">{{ testResult.message }}</p>
      </div>
    </div>

    <!-- 缓存统计 -->
    <div class="bg-gray-700 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-medium">缓存统计</h3>
        <button 
          @click="clearCache"
          :disabled="clearingCache"
          class="px-3 py-1 text-sm bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded transition-colors"
        >
          <span v-if="clearingCache" class="flex items-center gap-1">
            <span class="animate-spin rounded-full h-3 w-3 border-t-2 border-b-2 border-white"></span>
            清除中...
          </span>
          <span v-else>清除缓存</span>
        </button>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-400">缓存条目数</p>
          <p class="text-xl font-semibold">{{ cacheStats.totalEntries || 0 }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-400">最大容量</p>
          <p class="text-xl font-semibold">{{ cacheStats.maxSize || 5000 }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { aiService } from '@/services'
import { onMounted, reactive, ref } from 'vue'

// 表单数据
const configForm = reactive({
  provider: 'deepseek',
  apiKey: ''
})

// 状态
const showApiKey = ref(false)
const testing = ref(false)
const clearingCache = ref(false)
const testResult = ref<{ success: boolean; message: string } | null>(null)

// 状态配置
const statusConfig = reactive({
  valid: false,
  provider: '',
  cacheEnabled: false,
  fallbackEnabled: false
})

// 缓存统计
const cacheStats = reactive({
  totalEntries: 0,
  maxSize: 0
})

// 获取AI状态
const loadStatus = async () => {
  try {
    const response = await aiService.getStatus()
    if (response.success && response.data) {
      const data = response.data as any
      statusConfig.valid = data.config?.enabled || false
      statusConfig.provider = data.config?.provider || ''
      statusConfig.cacheEnabled = data.config?.cache_enabled || false
      statusConfig.fallbackEnabled = data.config?.fallback_enabled || false
      cacheStats.totalEntries = data.cache?.total_entries || 0
      cacheStats.maxSize = data.cache?.max_size || 0
    }
  } catch (error) {
    console.error('获取AI状态失败:', error)
  }
}

// 测试配置
const testConfiguration = async () => {
  if (!configForm.apiKey) {
    testResult.value = { success: false, message: '请先输入API密钥' }
    return
  }

  testing.value = true
  try {
    // 使用用户输入的密钥进行测试
    const response = await aiService.testConfigurationWithKey(configForm.provider, configForm.apiKey)
    if (response.success && response.data) {
      const data = response.data as any
      if (data.valid) {
        testResult.value = { 
          success: true, 
          message: `配置有效！提供商: ${data.provider}，AI服务连接成功` 
        }
      } else {
        testResult.value = { 
          success: false, 
          message: data.message || '配置无效，请检查API密钥是否正确' 
        }
      }
    } else {
      testResult.value = { success: false, message: '测试请求失败' }
    }
  } catch (error) {
    testResult.value = { 
      success: false, 
      message: `测试失败: ${error instanceof Error ? error.message : '未知错误'}` 
    }
  } finally {
    testing.value = false
  }
}

// 清除缓存
const clearCache = async () => {
  clearingCache.value = true
  try {
    const response = await aiService.clearCache()
    if (response.success) {
      cacheStats.totalEntries = 0
      testResult.value = { success: true, message: '缓存已成功清除' }
    } else {
      testResult.value = { success: false, message: '清除缓存失败' }
    }
  } catch (error) {
    testResult.value = { 
      success: false, 
      message: `清除缓存失败: ${error instanceof Error ? error.message : '未知错误'}` 
    }
  } finally {
    clearingCache.value = false
  }
}

onMounted(() => {
  loadStatus()
})
</script>