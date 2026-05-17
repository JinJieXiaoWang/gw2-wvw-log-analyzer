<template>
  <div
    class="card-legendary animate-slide-in-up"
    style="animation-delay: 0.2s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-status-success/30 to-primary/30 flex items-center justify-center">
          <i class="pi pi-check-circle text-status-success" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            理想循环
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            完美的技能释放顺序
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <BaseButton
          icon="pi pi-copy"
          variant="ghost"
          size="small"
          @click="copyIdealRotation"
        />
        <BaseButton
          icon="pi pi-pencil"
          variant="ghost"
          size="small"
          @click="editIdealRotation"
        />
      </div>
    </div>
    <div class="space-y-3">
      <div
        v-for="(skill, index) in rotation"
        :key="skill.id"
        class="flex items-center gap-4 p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="w-10 h-10 bg-gradient-to-br from-status-success/30 to-status-success rounded-full flex items-center justify-center text-status-success font-bold text-lg">
          {{ index + 1 }}
        </div>
        <div class="flex-1">
          <p class="text-neutral-text font-bold text-lg">
            {{ skill.name }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ skill.description }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm font-semibold text-neutral-text">
            {{ skill.castingTime }}s
          </p>
          <p class="text-xs text-neutral-text-disabled">
            施放时间
          </p>
        </div>
        <div class="w-20">
          <div class="game-progress">
            <div
              class="game-progress-primary"
              :style="{ width: skill.utilization + '%' }"
            />
          </div>
          <p class="text-xs text-center mt-1 text-status-success">
            {{ skill.utilization }}%
          </p>
        </div>
      </div>
    </div>
    <div class="mt-4 p-4 bg-gradient-to-r from-status-success/20 to-primary/20 rounded-xl border border-status-success/30">
      <div class="flex items-center justify-between">
        <span class="text-sm text-neutral-text-secondary font-medium">循环总时间</span>
        <span class="text-xl font-bold game-number-legendary">{{ totalTime }}s</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 理想技能循环组件
 * 功能：显示理想技能循环
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { computed } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

// Props
const props = defineProps<{
  rotation: Array<{
    id: number
    name: string
    description: string
    castingTime: number
    utilization: number
  }>
}>()

// 确保props被使用

// Emits
const emit = defineEmits([
  'copy-rotation',
  'edit-rotation'
])

// 计算属性
const totalTime = computed(() => props.rotation.reduce((sum, s) => sum + (s.castingTime || 0), 0))

// 事件处理
const copyIdealRotation = () => {
  emit('copy-rotation')
}

const editIdealRotation = () => {
  emit('edit-rotation')
}
</script>