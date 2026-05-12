<template>
  <div class="overview-container">
    <div class="overview-header">
      <div class="header-info">
        <i class="pi pi-book header-icon" />
        <div class="header-text">
          <h2 class="header-title">
            字典管理
          </h2>
          <p class="header-subtitle">
            系统枚举数据配置和管理中心
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
          <span class="stat-value">{{ typeStats.total }}</span><span class="stat-label">字典分类</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-check-circle" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ typeStats.enabled }}</span><span class="stat-label">启用分类</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-list" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ dataStats.total }}</span><span class="stat-label">字典项总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="pi pi-database" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ cacheStatus ? '正常' : '需要刷新' }}</span><span class="stat-label">缓存状态</span>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h3 class="section-title">
        常用操作
      </h3>
      <div class="action-grid">
        <div
          class="action-card"
          @click="$emit('enter-management')"
        >
          <i class="pi pi-cog action-icon" />
          <span class="action-label">分类管理</span>
          <p class="action-desc">
            管理字典分类和属性配置
          </p>
        </div>
        <div
          class="action-card"
          @click="$emit('quick-reload')"
        >
          <i class="pi pi-refresh action-icon" />
          <span class="action-label">刷新缓存</span>
          <p class="action-desc">
            立即刷新系统字典缓存
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
          分类预览
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
          v-for="type in dictTypes.slice(0, 6)"
          :key="type.dict_id"
          class="type-item"
        >
          <div class="type-info">
            <span class="type-name">{{ type.dict_name }}</span>
            <BaseTag
              :value="type.status === 0 ? '启用' : '禁用'"
              :severity="type.status === 0 ? 'success' : 'danger'"
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
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import type { DictType } from '@/services/system/dictionaryService'

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
