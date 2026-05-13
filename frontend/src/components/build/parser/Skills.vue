<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-secondary/30 to-rarity-exotic/30 flex items-center justify-center">
        <i class="pi pi-bolt text-secondary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          技能配置
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          技能组合搭配
        </p>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="skill in parsedBuild.skills"
        :key="skill.id"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center shadow-sm">
            <i
              :class="skill.icon || 'pi pi-circle'"
              class="text-xl text-primary"
            />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-neutral-text">
              {{ skill.name }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              {{ skill.type }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能配置组件
 * 功能：展示Build的技能组合
 * 作者：帅姐姐
 * 日期：2026-04-27
 */

defineProps<{
  parsedBuild: {
    skills: Array<{
      id: number | string
      name: string
      type: string
      icon?: string
    }>
  }
}>()
</script>