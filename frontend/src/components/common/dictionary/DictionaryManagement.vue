<template>
  <div class="dictionary-management">
    <div class="content-layout">
      <DictTypeSidebar
        v-model:search-keyword="searchKeyword"
        :collapsed="isCollapsed"
        :filtered-dict-types="filteredDictTypes"
        :selected-dict-type="selectedDictType"
        @select="selectDictType"
      />
      <main class="main-content">
        <DictOverviewCards
          :dict-data-length="dictData.length"
          :enabled-count="enabledCount"
          :disabled-count="disabledCount"
          :dict-types-length="dictTypes.length"
        />
        <DictDataToolbar
          v-model:data-search-keyword="dataSearchKeyword"
          v-model:status-filter="statusFilter"
          :selected-dict-type="selectedDictType"
          :is-admin="isAdmin"
          :status-options="statusOptions"
          @add="openAddDialog"
          @edit-type="openEditTypeDialog"
        />
        <DictDataTable
          :selected-dict-type="selectedDictType"
          :filtered-dict-data="filteredDictData"
          :loading="loading"
          :is-admin="isAdmin"
          @edit="openEditDialog"
          @delete="confirmDelete"
        />
      </main>
    </div>

    <DictDataDialog
      v-model:visible="showDataDialog"
      v-model:form="dataForm"
      :editing-data="editingData"
      :saving="saving"
      :status-options="statusOptions"
      @save="saveData"
    />
    <DictTypeDialog
      v-model:visible="showTypeDialog"
      v-model:form="typeForm"
      :editing-type="editingType"
      :saving="saving"
      :status-options="statusOptions"
      @save="saveType"
    />
    <InitConfirmDialog
      v-model:visible="showInitDialog"
      :initializing="initializing"
      @confirm="handleInit"
    />

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { useDictionaryManagement } from '@/composables/core/useDictionaryManagement'
import DictTypeSidebar from './DictTypeSidebar.vue'
import DictOverviewCards from './DictOverviewCards.vue'
import DictDataToolbar from './DictDataToolbar.vue'
import DictDataTable from './DictDataTable.vue'
import DictDataDialog from './DictDataDialog.vue'
import DictTypeDialog from './DictTypeDialog.vue'
import InitConfirmDialog from './InitConfirmDialog.vue'

const {
  isAdmin, isCollapsed, searchKeyword, dataSearchKeyword, statusFilter,
  refreshing, saving, initializing,
  showDataDialog, showTypeDialog, showInitDialog,
  editingData, editingType,
  dictTypes, filteredDictTypes, selectedDictType,
  dictData, filteredDictData, enabledCount, disabledCount, loading,
  dataForm, typeForm, statusOptions,
  selectDictType, toggleSidebar,
  openAddDialog, openEditDialog, openEditTypeDialog,
  saveData, saveType, confirmDelete, handleReloadCache, handleInit
} = useDictionaryManagement()

onMounted(async () => {
  // dictTypes auto-loaded by useDictTypes
})

defineExpose({ toggleSidebar, handleReloadCache })
</script>

<style scoped>
.dictionary-management { display: flex; flex-direction: column; height: 100%; width: 100%; gap: 16px; }
.content-layout { display: flex; gap: 16px; flex: 1; min-height: 0; }
.main-content { flex: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
</style>
