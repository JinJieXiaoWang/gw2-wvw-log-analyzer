<template>
  <div class="management-header">
    <div class="header-left">
      <BaseButton
        v-if="showBack"
        icon="pi pi-arrow-left"
        severity="secondary"
        text
        @click="$emit('back')"
      />
      <div class="header-text">
        <h2 class="header-title">
          字典管理
        </h2>
        <p class="header-subtitle">
          管理系统中的枚举数据和配置项
        </p>
      </div>
    </div>
    <div class="header-right">
      <BaseButton
        v-if="isAdmin"
        :label="isCollapsed ? '展开' : '收起'"
        :icon="isCollapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'"
        severity="secondary"
        outlined
        size="small"
        @click="$emit('toggle-sidebar')"
      />
      <BaseButton
        v-if="isAdmin"
        label="刷新缓存"
        icon="pi pi-refresh"
        severity="info"
        outlined
        size="small"
        :loading="refreshing"
        @click="$emit('reload-cache')"
      />
      <BaseButton
        v-if="isAdmin"
        label="初始化数据"
        icon="pi pi-database"
        severity="warning"
        outlined
        size="small"
        @click="$emit('init-data')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

defineProps<{
  isAdmin: boolean
  isCollapsed: boolean
  refreshing: boolean
  showBack?: boolean
}>()

defineEmits<{
  back: []
  'toggle-sidebar': []
  'reload-cache': []
  'init-data': []
}>()
</script>
