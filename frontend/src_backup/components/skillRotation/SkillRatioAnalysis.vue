<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.7s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-secondary/30 to-primary/30 flex items-center justify-center">
        <i class="pi pi-chart-pie text-secondary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          技能占比分析
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          各技能的贡献占比
        </p>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="h-64 flex items-center justify-center text-neutral-text-disabled">
        <div class="text-center">
          <i class="pi pi-chart-pie text-5xl mb-3 opacity-50" />
          <p class="text-sm font-medium">
            伤害技能占比
          </p>
        </div>
      </div>
      <div class="h-64 flex items-center justify-center text-neutral-text-disabled">
        <div class="text-center">
          <i class="pi pi-chart-pie text-5xl mb-3 opacity-50" />
          <p class="text-sm font-medium">
            冷却技能使用
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能占比分析组件
 * 功能：显示技能占比分析图表
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */
</script>