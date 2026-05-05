<template>
  <div class="card sticky top-6">
    <!-- 装饰性顶部渐变 -->
    <div
      class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-secondary to-transparent opacity-60"
    />

    <div class="space-y-1 relative">
      <button
        v-for="section in settingSections"
        :key="section.id"
        class="w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 text-left group"
        :class="activeSection === section.id
          ? 'bg-gradient-to-r from-primary/15 to-transparent text-primary'
          : 'text-neutral-text-secondary hover:bg-neutral-bg hover:text-neutral-text'"
        @click="selectSection(section.id)"
      >
        <!-- 左侧激活指示器 -->
        <div
          class="w-1 h-6 rounded-full transition-all duration-300 flex-shrink-0"
          :class="activeSection === section.id
            ? 'bg-primary shadow-glow-primary opacity-100'
            : 'bg-transparent opacity-0 group-hover:bg-neutral-border group-hover:opacity-100'"
        />

        <!-- 图标容器 -->
        <div
          class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200"
          :class="activeSection === section.id
            ? 'bg-primary/20 text-primary shadow-sm'
            : 'bg-neutral-bg text-neutral-text-disabled group-hover:bg-neutral-card group-hover:text-neutral-text-secondary'"
        >
          <i
            :class="section.icon"
            class="text-sm"
          />
        </div>

        <!-- 文字 -->
        <span
          class="text-sm font-medium transition-colors duration-200 flex-1"
          :class="activeSection === section.id ? 'text-primary' : ''"
        >
          {{ section.label }}
        </span>

        <!-- 右侧箭头 -->
        <i
          class="pi pi-chevron-right text-xs transition-all duration-200 flex-shrink-0"
          :class="activeSection === section.id
            ? 'text-primary opacity-100 translate-x-0'
            : 'text-neutral-text-disabled opacity-0 -translate-x-1 group-hover:opacity-50 group-hover:translate-x-0'"
        />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SettingSidebar - 设置页面侧边导航栏组件
 * 功能：显示设置页面的导航选项，提供精致的视觉反馈
 * 更新日期：2026-05-04
 */

defineProps<{
  activeSection: string
  settingSections: Array<{
    id: string
    label: string
    icon: string
  }>
}>()

const emit = defineEmits<{
  'select-section': [sectionId: string]
}>()

const selectSection = (sectionId: string) => {
  emit('select-section', sectionId)
}
</script>
