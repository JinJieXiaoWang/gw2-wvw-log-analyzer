<template>
  <div class="dictionary-wrapper" :class="{ 'embedded': isEmbedded }">
    <template v-if="!isEmbedded && viewMode === 'overview'">
      <DictOverviewView
        :dict-types="dictTypes"
        :type-stats="typeStats"
        :data-stats="dataStats"
        :cache-status="cacheStatus"
        @enter-management="viewMode = 'management'"
        @quick-reload="handleQuickReload"
      />
    </template>
    <template v-else>
      <template v-if="!isEmbedded">
        <DictManagementHeader
          :is-admin="isAdmin"
          :is-collapsed="isCollapsed"
          :refreshing="refreshing"
          @back="viewMode = 'overview'"
          @toggle-sidebar="toggleSidebar"
          @reload-cache="handleReloadCache"
          @init-data="showInitDialog = true"
        />
      </template>
      <DictionaryManagementCore 
        ref="dictManagementRef" 
        :show-overview-cards="!isEmbedded"
      />
    </template>

    <BaseDialog
      v-model:visible="showInitDialog"
      header="初始化字典数据"
      width="500px"
      confirm-label="确认初始化"
      confirm-severity="warning"
      :loading="initializing"
      @confirm="handleInitData"
    >
      <div class="init-dialog-content">
        <i class="pi pi-exclamation-triangle warning-icon" />
        <p class="warning-text">
          此操作将重新初始化所有字典数据，可能会覆盖现有数据，是否继续？
        </p>
      </div>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import { useDictionaryWrapper } from '@/composables/common/useDictionaryWrapper'
import { onMounted } from 'vue'
import DictionaryManagementCore from './DictionaryManagement.vue'
import DictManagementHeader from './DictManagementHeader.vue'
import DictOverviewView from './DictOverviewView.vue'

defineProps<{
  isEmbedded?: boolean
}>()

const {
  viewMode, dictManagementRef, dictTypes, refreshing, initializing,
  cacheStatus, showInitDialog, isCollapsed, isAdmin, typeStats, dataStats,
  toggleSidebar, loadOverviewData, handleQuickReload, handleReloadCache, handleInitData
} = useDictionaryWrapper()

onMounted(() => { loadOverviewData() })
</script>

<style scoped src="@/styles/components/common/dictionary/DictionaryManagementWrapper.css"></style>
