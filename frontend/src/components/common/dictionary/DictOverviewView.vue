<template>
  <div class="overview-container">
    <div class="overview-header">
      <div class="header-info">
        <i class="pi pi-book header-icon" />
        <div class="header-text">
          <h2 class="header-title">
            {{ HEADER_TITLE }}
          </h2>
          <p class="header-subtitle">
            {{ HEADER_SUBTITLE }}
          </p>
        </div>
      </div>
      <BaseButton
        label="进入管理"
        icon="pi pi-arrow-right"
        severity="primary"
        @click="$emit('enter-management')"
      />
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="pi pi-folder" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ typeStats.total }}</span><span class="stat-label">{{ STAT_LABEL_TOTAL }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-check-circle" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ typeStats.enabled }}</span><span class="stat-label">{{ STAT_LABEL_ENABLED }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-list" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ dataStats.total }}</span><span class="stat-label">{{ STAT_LABEL_DATA_TOTAL }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="pi pi-database" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ cacheStatus ? CACHE_STATUS_NORMAL : CACHE_STATUS_NEED_REFRESH }}</span><span class="stat-label">{{ STAT_LABEL_CACHE_STATUS }}</span>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h3 class="section-title">
        {{ SECTION_TITLE_ACTIONS }}
      </h3>
      <div class="action-grid">
        <div
          class="action-card"
          @click="$emit('enter-management')"
        >
          <i class="pi pi-cog action-icon" />
          <span class="action-label">{{ ACTION_LABEL_MANAGE }}</span>
          <p class="action-desc">
            {{ ACTION_DESC_MANAGE }}
          </p>
        </div>
        <div
          class="action-card"
          @click="$emit('quick-reload')"
        >
          <i class="pi pi-refresh action-icon" />
          <span class="action-label">{{ ACTION_LABEL_RELOAD }}</span>
          <p class="action-desc">
            {{ ACTION_DESC_RELOAD }}
          </p>
        </div>
      </div>
    </div>

    <div
      v-if="dictTypes.length > 0"
      class="types-preview"
    >
      <div class="preview-header">
        <h3 class="section-title">
          {{ SECTION_TITLE_PREVIEW }}
        </h3>
        <BaseButton
          label="查看全部"
          size="small"
          text
          @click="$emit('enter-management')"
        />
      </div>
      <div class="types-list">
        <div
          v-for="type in dictTypes.slice(0, PREVIEW_MAX_ITEMS)"
          :key="type.dict_id"
          class="type-item"
        >
          <div class="type-info">
            <span class="type-name">{{ type.dict_name }}</span>
            <DictTag
              dict-type="sys_normal_disable"
              :value="type.status"
              size="small"
            />
          </div>
          <span class="type-code">{{ type.dict_type }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

import type { DictType } from '@/services/system/dictionaryService'

// ============ 常量定义 ============
const HEADER_TITLE = '字典管理'
const HEADER_SUBTITLE = '系统枚举数据配置和管理中心'

const STAT_LABEL_TOTAL = '字典分类'
const STAT_LABEL_ENABLED = '启用分类'
const STAT_LABEL_DATA_TOTAL = '字典项总数'
const STAT_LABEL_CACHE_STATUS = '缓存状态'

const CACHE_STATUS_NORMAL = '正常'
const CACHE_STATUS_NEED_REFRESH = '需要刷新'

const SECTION_TITLE_ACTIONS = '常用操作'
const SECTION_TITLE_PREVIEW = '分类预览'

const ACTION_LABEL_MANAGE = '分类管理'
const ACTION_DESC_MANAGE = '管理字典分类和属性配置'
const ACTION_LABEL_RELOAD = '刷新缓存'
const ACTION_DESC_RELOAD = '立即刷新系统字典缓存'

const PREVIEW_MAX_ITEMS = 6
// =================================

defineProps<{
  dictTypes: DictType[]
  typeStats: { total: number; enabled: number }
  dataStats: { total: number }
  cacheStatus: boolean
}>()

defineEmits<{
  'enter-management': []
  'quick-reload': []
}>()
</script>

<style scoped>
.overview-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.header-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.header-subtitle {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0.25rem 0 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--surface-card);
  border-radius: 0.75rem;
  border: 1px solid var(--surface-border);
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  font-size: 1.125rem;
}

.stat-icon.primary { background: var(--primary-100); color: var(--primary-color); }
.stat-icon.success { background: var(--green-100); color: var(--green-500); }
.stat-icon.info { background: var(--blue-100); color: var(--blue-500); }
.stat-icon.warning { background: var(--orange-100); color: var(--orange-500); }

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  display: block;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.quick-actions {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.action-card {
  padding: 1.25rem;
  background: var(--surface-card);
  border-radius: 0.75rem;
  border: 1px solid var(--surface-border);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.action-card:hover {
  box-shadow: 0 4px 12px var(--color-shadow);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  display: block;
}

.action-label {
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
}

.action-desc {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.types-preview {
  background: var(--surface-card);
  border-radius: 0.75rem;
  border: 1px solid var(--surface-border);
  padding: 1rem 1.25rem;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.types-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.type-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  background: var(--surface-hover);
}

.type-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.type-name {
  font-weight: 500;
}

.type-code {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-family: monospace;
}
</style>
