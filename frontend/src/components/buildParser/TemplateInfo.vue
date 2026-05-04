<template>
  <div
    class="card-legendary animate-slide-in-up"
    style="animation-delay: 0.2s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rarity-legendary/30 to-rarity-exotic/30 flex items-center justify-center">
        <i class="pi pi-star text-rarity-legendary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          模板信息
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          职业和基本信息
        </p>
      </div>
    </div>
    <div class="flex items-center gap-4 mb-4 p-4 bg-neutral-bg rounded-xl">
      <div
        class="w-16 h-16 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg"
        :style="{ background: `linear-gradient(135deg, ${getProfessionColor(parsedBuild.profession)}, ${getProfessionColor(parsedBuild.profession)}88)` }"
      >
        {{ parsedBuild.profession.charAt(0) }}
      </div>
      <div>
        <p class="text-xl font-semibold text-neutral-text">
          {{ parsedBuild.profession }}
        </p>
        <p class="text-sm text-neutral-text-secondary">
          {{ parsedBuild.templateType }}
        </p>
      </div>
    </div>
    <div class="space-y-3">
      <div class="flex items-center justify-between p-3 bg-neutral-bg rounded-xl">
        <span class="text-sm text-neutral-text-secondary">模板名称</span>
        <span class="text-sm text-neutral-text font-medium">{{ parsedBuild.name || '未命名' }}</span>
      </div>
      <div class="flex items-center justify-between p-3 bg-neutral-bg rounded-xl">
        <span class="text-sm text-neutral-text-secondary">模板代码</span>
        <span class="text-sm text-neutral-text font-mono">{{ parsedBuild.code }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 模板信息组件
 * 功能：显示解析后的Build模板信息
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

defineProps<{
  parsedBuild: {
    profession: string
    templateType: string
    name?: string
    code: string
  }
}>()

// 方法
const getProfessionColor = (profession: string) => {
  const colors: Record<string, string> = {
    '战士': '#E85D04',
    '守护者': '#FAA307',
    '潜行者': '#9D4EDD',
    '元素使': '#FF6B6B',
    '工程师': '#7B8FA1',
    '猎人': '#06D6A0',
    '唤灵师': '#8D0801',
    '镜像师': '#4361EE',
    '游侠': '#2EC4B6'
  }
  return colors[profession] || '#6C757D'
}
</script>