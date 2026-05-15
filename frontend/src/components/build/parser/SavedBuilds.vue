<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.8s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rarity-legendary/30 to-rarity-exotic/30 flex items-center justify-center">
          <i class="pi pi-bookmark text-rarity-legendary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            已保存的Build
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            你的Build收藏
          </p>
        </div>
      </div>
      <BaseButton
        label="刷新"
        icon="pi pi-refresh"
        class="btn-ghost"
        size="small"
        @click="loadSavedBuilds"
      />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="build in savedBuilds"
        :key="build.id"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl cursor-pointer transition-all hover:shadow-lg"
        @click="loadBuild(build)"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold shadow-md"
            :style="{ background: `linear-gradient(135deg, ${getProfessionColor(build.profession)}, ${getProfessionColor(build.profession)}88)` }"
          >
            {{ getProfessionName(build.profession).charAt(0) }}
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-neutral-text">
              {{ build.name }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              {{ getProfessionName(build.profession) }}
            </p>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-xs text-neutral-text-disabled">{{ build.updatedAt }}</span>
          <div class="flex gap-1">
            <BaseButton
              icon="pi pi-eye"
              class="btn-ghost"
              size="small"
              @click.stop="loadBuild(build)"
            />
            <BaseButton
              icon="pi pi-trash"
              class="btn-ghost"
              size="small"
              severity="danger"
              @click.stop="deleteBuild(build)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getProfessionName } from '@/services/professionService'
/**
 * 已保存的Build组件
 * 功能：展示用户保存的Build列表
 * 作者：帅姐姐
 * 日期：2026-04-27
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'

defineProps<{
  savedBuilds: Array<{
    id: string
    name: string
    profession: string
    code: string
    updatedAt: string
  }>
}>()

// Emits
const emit = defineEmits<{
  'load-build': [build: any]
  'delete-build': [build: any]
  'load-saved-builds': []
}>()

// 事件处理
const loadBuild = (build: any) => {
  emit('load-build', build)
}

const deleteBuild = (build: any) => {
  emit('delete-build', build)
}

const loadSavedBuilds = () => {
  emit('load-saved-builds')
}

// 方法
const getProfessionColor = (profession: string) => {
  const colors: Record<string, string> = {
    '战士': '#E85D04',
    '守护者': '#FAA307',
    '潜行者': '#9D4EDD',
    '元素师': '#FF6B6B',
    '工程师': '#7B8FA1',
    '猎人': '#06D6A0',
    '唤灵师': '#8D0801',
    '幻术师': '#4361EE',
    '游侠': '#2EC4B6'
  }
  return colors[profession] || '#6C757D'
}
</script>