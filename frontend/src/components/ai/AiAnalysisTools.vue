<template>
  <div class="bg-gray-800 rounded-lg p-4" :class="{ 'opacity-50': disabled }">
    <h2 class="text-xl font-semibold mb-4">
      AI分析工具
    </h2>
    
    <!-- 未配置提示 -->
    <div v-if="disabled" class="text-center py-8 text-yellow-400">
      <p>请先在配置管理中完成AI配置</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gray-700 rounded p-4">
        <h3 class="font-medium mb-2">
          分析战斗
        </h3>
        <div class="mb-2">
          <label class="block text-sm mb-1">战斗ID</label>
          <input 
            v-model="localFightId" 
            type="text" 
            class="w-full bg-gray-600 rounded px-3 py-2 text-sm"
            placeholder="输入战斗ID"
            :disabled="analyzing"
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded transition-colors" 
          :disabled="analyzing || !localFightId"
          @click="analyzeFight"
        >
          <span v-if="analyzing" class="flex items-center justify-center gap-2">
            <span class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></span>
            分析中...
          </span>
          <span v-else>开始分析</span>
        </button>
      </div>
      
      <div class="bg-gray-700 rounded p-4">
        <h3 class="font-medium mb-2">
          分析成员
        </h3>
        <div class="mb-2">
          <label class="block text-sm mb-1">成员ID</label>
          <input 
            v-model="localMemberId" 
            type="text" 
            class="w-full bg-gray-600 rounded px-3 py-2 text-sm"
            placeholder="输入成员ID"
            :disabled="analyzing"
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded transition-colors" 
          :disabled="analyzing || !localMemberId"
          @click="analyzeMember"
        >
          <span v-if="analyzing" class="flex items-center justify-center gap-2">
            <span class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></span>
            分析中...
          </span>
          <span v-else>开始分析</span>
        </button>
      </div>
      
      <div class="bg-gray-700 rounded p-4">
        <h3 class="font-medium mb-2">
          分析Build
        </h3>
        <div class="mb-2">
          <label class="block text-sm mb-1">Build ID</label>
          <input 
            v-model="localBuildId" 
            type="text" 
            class="w-full bg-gray-600 rounded px-3 py-2 text-sm"
            placeholder="输入Build ID"
            :disabled="analyzing"
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded transition-colors" 
          :disabled="analyzing || !localBuildId"
          @click="analyzeBuild"
        >
          <span v-if="analyzing" class="flex items-center justify-center gap-2">
            <span class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></span>
            分析中...
          </span>
          <span v-else>开始分析</span>
        </button>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
      <p class="text-red-300 text-sm">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI分析工具组件
 * 功能：提供AI分析工具的输入界面
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-20 - 添加disabled状态、加载状态和错误提示
 */

import { ref } from 'vue'

// Props
defineProps<{
  disabled?: boolean
}>()

// Emits
const emit = defineEmits<{
  'analyze-fight': [fightId: string]
  'analyze-member': [memberId: string]
  'analyze-build': [buildId: string]
}>()

// 本地状态
const localFightId = ref('')
const localMemberId = ref('')
const localBuildId = ref('')
const analyzing = ref(false)
const errorMessage = ref('')

// 清除错误
const clearError = () => {
  errorMessage.value = ''
}

// 事件处理
const analyzeFight = () => {
  if (!localFightId.value) return
  clearError()
  analyzing.value = true
  emit('analyze-fight', localFightId.value)
  localFightId.value = ''
  setTimeout(() => {
    analyzing.value = false
  }, 3000)
}

const analyzeMember = () => {
  if (!localMemberId.value) return
  clearError()
  analyzing.value = true
  emit('analyze-member', localMemberId.value)
  localMemberId.value = ''
  setTimeout(() => {
    analyzing.value = false
  }, 3000)
}

const analyzeBuild = () => {
  if (!localBuildId.value) return
  clearError()
  analyzing.value = true
  emit('analyze-build', localBuildId.value)
  localBuildId.value = ''
  setTimeout(() => {
    analyzing.value = false
  }, 3000)
}
</script>