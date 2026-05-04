<template>
  <div class="theme-switcher relative">
    <button
      class="theme-switcher-btn flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-neutral-bg transition-all group"
      :style="{ background: isOpen ? 'var(--color-bg)' : 'transparent' }"
      @click="toggleDropdown"
    >
      <div 
        class="w-8 h-8 rounded-lg flex items-center justify-center transition-all"
        :style="{ background: currentTheme?.previewGradient || defaultPreviewGradient }"
      >
        <span
          class="pi"
          :class="currentTheme?.icon || 'pi-palette'"
        />
      </div>
      <span
        class="text-sm font-medium group-hover:text-neutral-text transition-colors"
        :style="{ color: isOpen ? 'var(--color-text)' : 'var(--color-text-secondary)' }"
      >
        {{ currentTheme?.name || '主题' }}
      </span>
      <i
        class="pi pi-chevron-down text-xs transition-transform"
        :class="{ 'rotate-180': isOpen }"
        :style="{ color: 'var(--color-text-disabled)' }"
      />
    </button>

    <transition name="dropdown">
      <div
        v-if="isOpen"
        class="theme-dropdown absolute top-full mt-2 right-0 w-56 rounded-xl shadow-xl overflow-hidden z-50"
        :style="{ background: 'var(--color-card)', border: '1px solid var(--color-border)' }"
        @click.stop
      >
        <div class="p-2">
          <div
            v-for="theme in themes"
            :key="theme.id"
            class="theme-option flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all"
            :style="{ background: savedThemeId === theme.id ? 'var(--color-primary-alpha-10)' : 'transparent' }"
            @mouseenter="previewTheme(theme.id)"
            @mouseleave="cancelPreview()"
            @click="selectTheme(theme.id)"
          >
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :style="{ background: theme.previewGradient }"
            >
              <span
                class="pi"
                :class="theme.icon"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p
                class="text-sm font-medium leading-tight"
                :style="{ color: 'var(--color-text)' }"
              >
                {{ theme.name }}
              </p>
              <p
                class="text-xs truncate"
                :style="{ color: 'var(--color-text-disabled)' }"
              >
                {{ theme.description }}
              </p>
            </div>
            <i 
              v-if="savedThemeId === theme.id" 
              class="pi pi-check text-sm flex-shrink-0" 
              :style="{ color: 'var(--color-primary)' }"
            />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ThemeService } from '@/services/system/themeService'
import { useSettingsStore } from '@/store/system/settings'
import type { ThemeConfig } from '@/constants/themes'
import { getDefaultTheme } from '@/constants/themes'

const isOpen = ref(false)
const themes = ref<ThemeConfig[]>([])
const savedThemeId = ref(ThemeService.getSavedTheme().id)
// 响应式变量跟踪当前主题，确保UI正确更新
const currentThemeRef = ref<ThemeConfig>(ThemeService.getCurrentTheme())

const defaultPreviewGradient = 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'

const defaultTheme = getDefaultTheme()

const currentTheme = computed(() => {
  return currentThemeRef.value || defaultTheme
})

function loadThemes() {
  themes.value = ThemeService.getAllThemes()
  savedThemeId.value = ThemeService.getSavedTheme().id
  currentThemeRef.value = ThemeService.getCurrentTheme()
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    cancelPreview()
  }
}

function previewTheme(themeId: string) {
  ThemeService.previewTheme(themeId)
}

function cancelPreview() {
  ThemeService.cancelPreview()
}

function selectTheme(themeId: string) {
  const settingsStore = useSettingsStore()
  settingsStore.setGameTheme(themeId)
  savedThemeId.value = themeId
  isOpen.value = false
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.theme-switcher')) {
    isOpen.value = false
    cancelPreview()
  }
}

let unsubscribe: () => void

onMounted(() => {
  loadThemes()
  unsubscribe = ThemeService.subscribe((theme) => {
    // 更新响应式主题引用，触发UI更新
    currentThemeRef.value = theme
    if (!ThemeService.getIsPreviewMode()) {
      savedThemeId.value = theme.id
    }
  })
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.theme-switcher-btn .pi {
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-size: 1rem;
}

.rotate-180 {
  transform: rotate(180deg);
}

.theme-dropdown {
  animation: dropdown-appear 0.2s ease-out;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

.theme-option:hover .pi {
  transform: scale(1.1);
}

.theme-option .pi {
  transition: transform 0.2s ease;
}

/* 悬停预览效果 */
.theme-option:hover {
  background: var(--color-bg);
}
</style>
