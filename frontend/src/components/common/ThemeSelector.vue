<template>
  <div class="theme-selector">
    <div class="theme-selector-header">
      <h3 class="text-lg font-semibold mb-2">
        游戏主题
      </h3>
      <p class="text-sm text-secondary">
        选择您喜欢的游戏风格主题
      </p>
    </div>
    
    <div class="theme-grid">
      <div
        v-for="theme in themes"
        :key="theme.id"
        class="theme-card"
        :class="{ active: currentThemeId === theme.id }"
        @click="selectTheme(theme.id)"
      >
        <div 
          class="theme-preview"
          :style="{ background: theme.previewGradient }"
        >
          <span
            class="pi"
            :class="theme.icon"
          />
        </div>
        
        <div class="theme-info">
          <h4 class="font-medium">
            {{ theme.name }}
          </h4>
          <p class="text-xs text-secondary">
            {{ theme.description }}
          </p>
        </div>
        
        <div
          v-if="currentThemeId === theme.id"
          class="theme-check"
        >
          <span class="pi pi-check" />
        </div>
      </div>
    </div>
    
    <div class="theme-actions">
      <button 
        class="btn btn-secondary btn-sm"
        @click="resetToDefault"
      >
        <span class="pi pi-refresh mr-1" />
        重置为默认
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ThemeService } from '@/services/system/themeService'
import type { ThemeConfig } from '@/constants/themes'

const themes = ref<ThemeConfig[]>([])
const currentThemeId = ref(ThemeService.getCurrentThemeId())

function loadThemes() {
  themes.value = ThemeService.getAllThemes()
}

function selectTheme(themeId: string) {
  ThemeService.applyTheme(themeId)
  currentThemeId.value = themeId
}

function resetToDefault() {
  ThemeService.resetToDefault()
  currentThemeId.value = ThemeService.getCurrentThemeId()
}

function handleThemeChange(theme: ThemeConfig) {
  currentThemeId.value = theme.id
}

let unsubscribe: () => void

onMounted(() => {
  loadThemes()
  unsubscribe = ThemeService.subscribe(handleThemeChange)
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})
</script>

<style scoped>
.theme-selector {
  padding: 16px;
}

.theme-selector-header {
  margin-bottom: 16px;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.theme-card {
  position: relative;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.theme-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.theme-card.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary), 0.2);
}

.theme-preview {
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 2rem;
  color: white;
}

.theme-preview .pi {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.theme-info {
  padding: 0 4px;
}

.theme-info h4 {
  margin-bottom: 4px;
  color: var(--color-text);
}

.theme-info p {
  color: var(--color-text-secondary);
}

.theme-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
}

.theme-actions {
  display: flex;
  justify-content: flex-end;
}

.theme-actions .btn {
  padding: 6px 12px;
  font-size: 0.875rem;
}
</style>