<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.6s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-status-success/30 flex items-center justify-center">
        <i class="pi pi-lightbulb text-primary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          优化建议
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          提升输出的关键技巧
        </p>
      </div>
    </div>
    <div class="space-y-3">
      <div
        v-for="(suggestion, index) in suggestions"
        :key="index"
        class="flex items-start gap-3 p-4 bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/30 rounded-xl hover:border-primary/50 transition-all"
      >
        <div class="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-md">
          {{ index + 1 }}
        </div>
        <div class="flex-1">
          <p class="text-neutral-text font-bold text-sm mb-1">
            {{ suggestion.title }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ suggestion.description }}
          </p>
        </div>
      </div>
    </div>
    <div class="mt-4 p-4 bg-gradient-to-r from-primary/20 to-status-success/20 rounded-xl border border-primary/30">
      <div class="flex items-center gap-3">
        <i class="pi pi-star text-2xl text-status-success animate-pulse" />
        <div>
          <p class="text-sm font-bold text-neutral-text">
            预估提升效果
          </p>
          <p class="text-xs text-neutral-text-secondary">
            DPS提升约 <span class="text-status-success font-bold text-lg">12%</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 优化建议组件
 * 功能：显示技能循环优化建议
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

// Props
const props = defineProps<{
  suggestions: Array<{
    title: string
    description: string
  }>
}>()

// 确保props被使用
console.log(props.suggestions)
</script>