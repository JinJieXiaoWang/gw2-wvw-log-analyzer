<template>
  <div
    class="dictionary-wrapper"
    :class="{ 'embedded': isEmbedded }"
  >
    <template v-if="viewMode === 'overview'">
      <DictOverviewView
        v-bind="overviewProps"
        @enter-management="viewMode = 'management'"
        @quick-reload="handleQuickReload"
      />
    </template>
    <template v-else>
      <DictManagementHeader
        :can-write="canWrite"
        :is-collapsed="isCollapsed"
        :refreshing="refreshing"
        :show-back="true"
        @back="viewMode = 'overview'"
        @toggle-sidebar="toggleSidebar"
        @reload-cache="handleReloadCache"
        @init-data="showInitDialog = true"
      />
      <DictionaryManagementCore 
        ref="dictManagementRef" 
        :show-overview-cards="true"
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
import { computed, onMounted } from 'vue'
import DictionaryManagementCore from './DictionaryManagement.vue'
import DictManagementHeader from './DictManagementHeader.vue'
import DictOverviewView from './DictOverviewView.vue'

const props = defineProps<{
  isEmbedded?: boolean
}>()

const {
  viewMode, dictManagementRef, dictTypes, refreshing, initializing,
  cacheStatus, showInitDialog, isCollapsed, canWrite, typeStats, dataStats,
  toggleSidebar, loadOverviewData, handleQuickReload, handleReloadCache, handleInitData
} = useDictionaryWrapper()

/** 概览视图 props（用 computed 包裹避免 Volar 类型推断问题） */
const overviewProps = computed(() => ({
  dictTypes: dictTypes.value,
  typeStats: typeStats.value,
  dataStats: dataStats.value,
  cacheStatus: cacheStatus.value,
}))

onMounted(() => { loadOverviewData() })
</script>

<style scoped src="@/styles/components/common/dictionary/DictionaryManagementWrapper.css"></style>
