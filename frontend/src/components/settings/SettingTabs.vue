<template>
  <div class="card sticky top-6">
    <!-- 装饰性顶部渐变 -->
    <div class="sidebar-top-gradient" />

    <div class="space-y-1 relative">
      <button
        v-for="section in settingSections"
        :key="section.id"
        class="sidebar-btn text-left group"
        :class="activeSection === section.id ? 'sidebar-btn-active' : 'sidebar-btn-inactive'"
        @click="selectSection(section)"
      >
        <!-- 左侧激活指示器 -->
        <div
          class="indicator-bar"
          :class="activeSection === section.id
            ? 'indicator-active'
            : 'indicator-inactive'"
        />

        <!-- 图标容器 -->
        <div
          class="icon-container"
          :class="activeSection === section.id ? 'icon-active': 'icon-inactive'"
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

        <!-- 外部链接图标 -->
        <i
          v-if="section.isExternal"
          class="pi pi-external-link text-xs text-neutral-text-disabled flex-shrink-0"
          title="在新面板打开"
        />

        <!-- 右侧箭头（非外部链接） -->
        <i
          v-else
          class="arrow-icon text-xs transition-all duration-200 flex-shrink-0"
          :class="activeSection === section.id
            ? 'arrow-active'
            : 'arrow-inactive'"
        />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SettingTabs - 设置页面选项卡导航组件
 * 功能：显示设置页面的选项卡导航，提供精致的视觉反馈
 */

import { useRouter } from 'vue-router'

interface SettingSection {
  id: string
  label: string
  icon: string
  isExternal?: boolean
  path?: string
}

interface Props {
  activeSection: string
  settingSections: SettingSection[]
}

withDefaults(defineProps<Props>(), {
  activeSection: '',
  settingSections: () => []
})

const router = useRouter()

const emit = defineEmits<{
  'select-section': [sectionId: string]
}>()

const selectSection = (section: SettingSection) => {
  if (section.isExternal && section.path) {
    router.push(section.path)
    return
  }
  emit('select-section', section.id)
}
</script>

<style scoped lang="postcss">
.sidebar-top-gradient {
  @apply absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-secondary to-transparent opacity-60;
}

.sidebar-btn {
  @apply w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200;
}

.sidebar-btn-active {
  @apply bg-gradient-to-r from-primary/15 to-transparent text-primary;
}

.sidebar-btn-inactive {
  @apply text-neutral-text-secondary hover:bg-neutral-bg hover:text-neutral-text;
}

.indicator-bar {
  @apply w-1 h-6 rounded-full transition-all duration-300 flex-shrink-0;
}

.indicator-active {
  @apply bg-primary shadow-glow-primary opacity-100;
}

.indicator-inactive {
  @apply bg-transparent opacity-0 group-hover:bg-neutral-border group-hover:opacity-100;
}

.icon-container {
  @apply w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200;
}

.icon-active {
  @apply bg-primary/20 text-primary shadow-sm;
}

.icon-inactive {
  @apply bg-neutral-bg text-neutral-text-disabled group-hover:bg-neutral-card group-hover:text-neutral-text-secondary;
}

.arrow-icon {
  @apply transition-all duration-200;
}

.arrow-active {
  @apply text-primary opacity-100 translate-x-0;
}

.arrow-inactive {
  @apply text-neutral-text-disabled opacity-0 -translate-x-1 group-hover:opacity-50 group-hover:translate-x-0;
}
</style>
