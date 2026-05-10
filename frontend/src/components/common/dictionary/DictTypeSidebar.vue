<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <h2 class="sidebar-title">字典分类</h2>
      <span class="dict-count">{{ filteredDictTypes.length }} 个分类</span>
    </div>
    <div class="search-box">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText v-model="localSearch" placeholder="搜索分类..." size="small" class="w-full" />
      </IconField>
    </div>
    <div class="dict-type-list">
      <div
        v-for="dictType in filteredDictTypes"
        :key="dictType.dict_id"
        class="dict-type-item"
        :class="{ active: selectedDictType?.dict_id === dictType.dict_id }"
        @click="$emit('select', dictType)"
      >
        <div class="dict-type-info">
          <span class="dict-type-name">{{ dictType.dict_name }}</span>
          <span class="dict-type-code">{{ dictType.dict_type }}</span>
        </div>
        <div class="dict-type-meta">
          <BaseTag
            :value="dictType.status === 0 ? '启用' : '禁用'"
            :severity="dictType.status === 0 ? 'success' : 'danger'"
            class="status-tag"
          />
        </div>
      </div>
      <EmptyState v-if="filteredDictTypes.length === 0" icon="pi pi-inbox" title="暂无分类" />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import BaseTag from '@/components/common/ui/BaseTag.vue'
import type { DictType } from '@/services/system/dictionaryService'

const props = defineProps<{
  collapsed: boolean
  searchKeyword: string
  filteredDictTypes: DictType[]
  selectedDictType: DictType | null
}>()

const emit = defineEmits<{
  'update:searchKeyword': [value: string]
  select: [dictType: DictType]
}>()

const localSearch = computed({
  get: () => props.searchKeyword,
  set: v => emit('update:searchKeyword', v)
})
</script>

<style scoped>
.sidebar {
  width: 300px;
  flex-shrink: 0;
  background: #2a2a2a;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}
.sidebar.collapsed { width: 60px; }
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-title { font-size: 16px; font-weight: 600; color: #e5e5e5; margin: 0; }
.dict-count { font-size: 12px; color: #909399; background: #333; padding: 2px 8px; border-radius: 10px; }
.search-box { padding: 12px 16px; }
.dict-type-list { flex: 1; overflow-y: auto; padding: 8px; }
.dict-type-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; border-radius: 8px; cursor: pointer; transition: all 0.2s; margin-bottom: 4px;
}
.dict-type-item:hover { background: #333; }
.dict-type-item.active { background: rgba(22, 93, 255, 0.2); border: 1px solid #165dff; }
.dict-type-info { display: flex; flex-direction: column; gap: 4px; }
.dict-type-name { font-size: 14px; font-weight: 500; color: #e5e5e5; }
.dict-type-code { font-size: 12px; color: #909399; }
.status-tag { font-size: 10px; }
.empty-list {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 40px 20px; color: #909399; gap: 12px;
}
</style>
