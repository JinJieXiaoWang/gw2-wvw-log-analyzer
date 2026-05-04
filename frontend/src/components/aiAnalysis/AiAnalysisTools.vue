<template>
  <div class="bg-gray-800 rounded-lg p-4">
    <h2 class="text-xl font-semibold mb-4">
      AI分析工具
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors" 
          @click="analyzeFight"
        >
          开始分析
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
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors" 
          @click="analyzeMember"
        >
          开始分析
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
          >
        </div>
        <button 
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors" 
          @click="analyzeBuild"
        >
          开始分析
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI分析工具组件
 * 功能：提供AI分析工具的输入界面
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'

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

// 事件处理
const analyzeFight = () => {
  if (!localFightId.value) return
  emit('analyze-fight', localFightId.value)
}

const analyzeMember = () => {
  if (!localMemberId.value) return
  emit('analyze-member', localMemberId.value)
}

const analyzeBuild = () => {
  if (!localBuildId.value) return
  emit('analyze-build', localBuildId.value)
}
</script>