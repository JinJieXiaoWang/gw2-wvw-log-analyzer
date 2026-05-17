<script setup lang="ts">
/**
 * BaseMenubar - 导航菜单栏封装组件
 *
 * 基于 PrimeVue Menubar 封装，提供：
 * 1. 项目标准菜单数据格式适配
 * 2. 全部样式走 Tailwind，不依赖外部 CSS 文件
 * 3. 桌面端水平 Menubar + 移动端折叠面板
 * 4. 自定义 item 插槽，保持与项目设计系统一致
 *
 * 样式覆盖说明：
 * 由于 Menubar 内部 DOM 结构复杂，部分样式通过 scoped :deep() 覆盖。
 * 这是封装第三方组件时的必要手段，已控制在最小范围。
 */

import { computed, ref } from 'vue'
import Menubar from 'primevue/menubar'
import type { MenuItem as PrimeMenuItem } from 'primevue/menuitem'
import type { AppMenuItem } from '@/utils/menu/menuAdapter'
import { adaptToMenubar } from '@/utils/menu/menuAdapter'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

interface Props {
  /** 项目格式菜单数据 */
  model: AppMenuItem[]
  /** 当前激活路由路径 */
  activeRoute?: string
  /** 是否移动端菜单展开 */
  mobileOpen?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'navigate': [path: string]
  'update:mobileOpen': [value: boolean]
}>()

const localMobileOpen = ref(false)
const isMobileOpen = computed({
  get: () => props.mobileOpen ?? localMobileOpen.value,
  set: v => {
    localMobileOpen.value = v
    emit('update:mobileOpen', v)
  }
})

/** 转换为 PrimeVue 格式 */
const primeModel = computed<PrimeMenuItem[]>(() =>
  adaptToMenubar(props.model, path => emit('navigate', path))
)

/** 判断路由是否激活 */
const isActive = (path?: string) => {
  if (!path || !props.activeRoute) return false
  return path === '/' ? (props.activeRoute === '/' || props.activeRoute === '/dashboard') : props.activeRoute.startsWith(path)
}

/** 获取菜单项的 path（从 url 或 items 中递归查找） */
const getItemPath = (item: PrimeMenuItem): string | undefined => {
  if (item.url) return item.url
  if (item.items && item.items.length > 0) {
    const first = item.items[0]
    if (typeof first === 'object' && 'url' in first) return first.url
  }
  return undefined
}

/** Menubar PT 配置：容器级别样式 */
const menubarPt = {
  root: { class: 'bg-transparent border-0 p-0' },
  start: { class: 'hidden' },
  end: { class: 'hidden' },
  button: { class: 'hidden' },
}
</script>

<template>
  <div class="base-menubar">
    <!-- 桌面端 Menubar -->
    <Menubar
      :model="primeModel"
      :pt="menubarPt"
      class="hidden lg:flex"
    >
      <template #item="{ item, props: itemProps, hasSubmenu }">
        <a
          v-bind="itemProps.action"
          class="flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 group relative"
          :class="[
            isActive(getItemPath(item))
              ? 'text-primary bg-primary/10'
              : 'text-neutral-text-secondary hover:text-neutral-text hover:bg-neutral-bg'
          ]"
          @click.prevent="item.command?.({ originalEvent: $event, item })"
        >
          <i
            v-if="item.icon"
            :class="item.icon"
            class="text-sm"
          />
          <span class="text-sm font-medium">{{ item.label }}</span>
          <i
            v-if="hasSubmenu"
            class="pi pi-angle-down text-xs transition-transform group-hover:rotate-180"
          />
          <!-- 激活下划线指示器 -->
          <div
            v-if="isActive(getItemPath(item))"
            class="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full"
          />
          <div
            v-else
            class="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-300 group-hover:w-3/4"
          />
        </a>
      </template>

      <!-- 子菜单自定义渲染 -->
      <template #submenuicon>
        <span />
      </template>
    </Menubar>

    <!-- 移动端触发按钮 -->
    <BaseButton
      class="lg:hidden p-2.5"
      severity="secondary"
      variant="text"
      :icon="isMobileOpen ? 'pi pi-times' : 'pi pi-bars'"
      @click="isMobileOpen = !isMobileOpen"
    />

    <!-- 移动端菜单面板 -->
    <div
      v-if="isMobileOpen"
      class="lg:hidden absolute top-full left-0 right-0 mt-2 mx-4 z-50"
    >
      <div class="card border-neutral-border rounded-xl shadow-2xl overflow-hidden p-2 space-y-1">
        <template
          v-for="item in model"
          :key="item.path || item.label"
        >
          <router-link
            v-if="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
            :class="isActive(item.path) ? 'bg-primary/10 text-primary' : 'text-neutral-text hover:bg-neutral-bg'"
            @click="isMobileOpen = false"
          >
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :class="isActive(item.path) ? 'bg-gradient-to-br from-primary to-secondary text-white shadow-lg shadow-primary/30' : 'bg-neutral-bg text-neutral-text-secondary'"
            >
              <i :class="item.icon" />
            </div>
            <div class="flex-1">
              <span class="text-sm font-semibold">{{ item.label }}</span>
              <span
                v-if="item.description"
                class="text-xs text-neutral-text-disabled block mt-0.5"
              >{{ item.description }}</span>
            </div>
            <i
              v-if="isActive(item.path)"
              class="pi pi-check-circle text-primary"
            />
          </router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
 * 以下 :deep() 用于覆盖 PrimeVue Menubar 内部无法通过 PT 控制的样式。
 * Menubar 内部渲染了多层嵌套 DOM（ul > li > a > submenu），
 * 其中 submenu 的容器样式（位置、阴影、背景等）必须通过 :deep() 覆盖。
 */

:deep(.p-menubar-root-list) {
  @apply flex items-center gap-1;
}

:deep(.p-menubar-item) {
  @apply relative;
}

:deep(.p-menubar-submenu) {
  @apply absolute top-full left-0 mt-2 min-w-[200px] bg-neutral-card border-neutral-border rounded-xl shadow-2xl p-2 space-y-1 z-50;
}

:deep(.p-menubar-submenu .p-menubar-item-link) {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-neutral-text hover:bg-neutral-bg transition-colors;
}

/* 桌面端强制隐藏移动端触发按钮（作为 lg:hidden 的后备） */
@media (min-width: 1024px) {
  .base-menubar > button {
    display: none !important;
  }
}

/* 覆盖 PrimeVue Menubar 默认黑色背景/边框，确保与系统UI风格一致 */
:deep(.p-menubar) {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

/* 覆盖根级别菜单项默认的 hover 黑色背景，让 Tailwind hover 类生效 */
:deep(.p-menubar-root-list > .p-menubar-item > .p-menubar-item-link:hover) {
  background: transparent !important;
}

/* 子菜单项文字颜色：覆盖 PrimeVue 默认样式 */
:deep(.p-menubar-submenu .p-menubar-item-label) {
  @apply text-neutral-text;
}

/* 子菜单项图标颜色 */
:deep(.p-menubar-submenu .p-menubar-item-icon) {
  @apply text-neutral-text-secondary;
}

/* 覆盖 PrimeVue Menubar 默认激活状态颜色，确保 Tailwind text-primary 生效 */
:deep(.p-menubar-item-link.p-highlight),
:deep(.p-menubar-item-link[aria-current='page']) {
  @apply text-primary;
}
</style>
