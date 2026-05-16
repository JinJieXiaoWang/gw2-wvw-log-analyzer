<template>
  <aside
    class="sidebar"
    :class="{ collapsed }"
  >
    <div class="sidebar-header">
      <h2 class="sidebar-title">
        字典分类
      </h2>
      <span class="dict-count">{{ filteredDictTypes.length }} 个分类</span>
    </div>
    <div class="search-box">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="localSearch"
          placeholder="搜索分类..."
          size="small"
          class="w-full"
        />
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
          <DictTag
            dict-type="sys_normal_disable"
            :value="dictType.status"
            class="status-tag"
          />
        </div>
      </div>
      <EmptyState
        v-if="filteredDictTypes.length === 0"
        icon="pi pi-inbox"
        title="暂无分类"
      />
    </div>
  </aside>
</template>

<script setup lang="ts">

import type { DictType } from '@/services/system/dictionaryService'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import { computed } from 'vue'

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
  height: 100%;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 60px;
}
.sidebar.collapsed .sidebar-title,
.sidebar.collapsed .dict-count,
.sidebar.collapsed .search-box,
.sidebar.collapsed .dict-type-info,
.sidebar.collapsed .dict-type-meta {
  display: none;
}
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}
.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}
.dict-count {
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-bg);
  padding: 2px 8px;
  border-radius: 10px;
}
.search-box {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.dict-type-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.dict-type-list::-webkit-scrollbar {
  width: 6px;
}
.dict-type-list::-webkit-scrollbar-track {
  background: transparent;
}
.dict-type-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}
.dict-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
  background: transparent;
}
.dict-type-item:hover {
  background: var(--color-bg);
}
.dict-type-item.active {
  background: var(--color-primary-alpha-10);
  border: 1px solid var(--color-primary);
}
.dict-type-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}
.dict-type-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dict-type-code {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-family: monospace;
}
.status-tag {
  font-size: 10px;
}
.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
  gap: 12px;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 100%;
    height: auto;
    max-height: 200px;
  }
  .sidebar.collapsed {
    width: 100%;
    max-height: 60px;
  }
}
</style>
