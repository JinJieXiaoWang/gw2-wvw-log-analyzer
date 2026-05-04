<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.4s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-chart-line text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            技能释放时序图
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            可视化技能释放顺序
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          label="简化视图"
          size="small"
          :class="timelineView === 'simple' ? 'btn-game' : 'btn-ghost'"
          @click="updateTimelineView('simple')"
        />
        <Button
          label="详细视图"
          size="small"
          :class="timelineView === 'detail' ? 'btn-game' : 'btn-ghost'"
          @click="updateTimelineView('detail')"
        />
      </div>
    </div>
    <div class="h-64 flex items-center justify-center text-neutral-text-disabled">
      <div class="text-center">
        <i class="pi pi-chart-bar text-5xl mb-3 opacity-50" />
        <p class="text-sm">
          时序图加载中...
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能释放时序图组件
 * 功能：显示技能释放顺序的可视化图表
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'

// Props
const props = defineProps<{
  timelineView: string
}>()

// 确保props被使用
console.log(props.timelineView)

// Emits
const emit = defineEmits([
  'update:timeline-view'
])

// 事件处理
const updateTimelineView = (view: string) => {
  emit('update:timeline-view', view)
}
</script>