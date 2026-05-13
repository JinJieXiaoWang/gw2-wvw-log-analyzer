<template>
  <div class="data-table-container">
    <DataTable
      v-if="selectedDictType"
      :value="filteredDictData"
      :loading="loading"
      :paginator="filteredDictData.length > 10"
      :rows="10"
      :rows-per-page-options="[10, 20, 50]"
      striped-rows
      removable-sort
      sort-field="dict_sort"
      :sort-order="1"
      class="dict-data-table"
    >
      <Column
        field="dict_sort"
        header="排序"
        sortable
        style="width: 80px"
      >
        <template #body="{ data }">
          <span class="sort-value">{{ data.dict_sort }}</span>
        </template>
      </Column>
      <Column
        field="dict_label"
        header="标签"
        sortable
      >
        <template #body="{ data }">
          <div class="label-cell">
            <span class="label-text">{{ data.dict_label }}</span>
            <span
              v-if="data.is_default === 1"
              class="default-badge"
            >默认</span>
          </div>
        </template>
      </Column>
      <Column
        field="dict_value"
        header="值"
        sortable
      >
        <template #body="{ data }">
          <span class="value-text">{{ data.dict_value }}</span>
        </template>
      </Column>
      <Column
        field="css_class"
        header="颜色"
        style="width: 120px"
      >
        <template #body="{ data }">
          <div
            v-if="data.css_class"
            class="color-cell"
          >
            <span
              class="color-swatch"
              :style="{ backgroundColor: data.css_class }"
            />
            <span class="color-value">{{ data.css_class }}</span>
          </div>
          <span
            v-else
            class="no-color"
          >-</span>
        </template>
      </Column>
      <Column
        field="list_class"
        header="列表样式"
        style="width: 100px"
      >
        <template #body="{ data }">
          <span
            v-if="data.list_class"
            class="list-class"
          >{{ data.list_class }}</span>
          <span
            v-else
            class="no-color"
          >-</span>
        </template>
      </Column>
      <Column
        field="status"
        header="状态"
        sortable
        style="width: 80px"
      >
        <template #body="{ data }">
          <BaseTag
            :value="data.status === 0 ? '启用' : '禁用'"
            :severity="data.status === 0 ? 'success' : 'danger'"
          />
        </template>
      </Column>
      <Column
        field="remark"
        header="备注"
      >
        <template #body="{ data }">
          <span class="remark-text">{{ data.remark || '-' }}</span>
        </template>
      </Column>
      <Column
        v-if="isAdmin"
        header="操作"
        style="width: 150px"
        frozen
        align-frozen="right"
      >
        <template #body="{ data }">
          <div class="action-buttons">
            <BaseButton
              icon="pi pi-pencil"
              severity="warning"
              text
              rounded
              size="small"
              @click="$emit('edit', data)"
            />
            <BaseButton
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="$emit('delete', data)"
            />
          </div>
        </template>
      </Column>
      <template #empty>
        <EmptyState
          icon="pi pi-inbox"
          title="暂无数据"
        />
      </template>
    </DataTable>
    <div
      v-else
      class="no-selection"
    >
      <i class="pi pi-book" />
      <h3>请选择字典分类</h3>
      <p>从左侧列表选择一个字典分类来查看和编辑数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import EmptyState from '@/components/common/ui/display/EmptyState.vue'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { DictData, DictType } from '@/services/system/dictionaryService'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'

defineProps<{
  selectedDictType: DictType | null
  filteredDictData: DictData[]
  loading: boolean
  isAdmin: boolean
}>()

defineEmits<{
  edit: [data: DictData]
  delete: [data: DictData]
}>()
</script>

<style scoped>
.data-table-container {
  flex: 1;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  min-height: 300px;
  display: flex;
  flex-direction: column;
}
.dict-data-table {
  font-size: 14px;
  flex: 1;
  min-height: 0;
}
.dict-data-table ::deep .p-datatable-header {
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}
.dict-data-table ::deep .p-datatable-footer {
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
}
.dict-data-table ::deep .p-paginator {
  background: var(--color-bg);
  border: none;
}
.sort-value, .value-text, .remark-text {
  color: var(--color-text);
}
.label-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.label-text {
  color: var(--color-text);
  font-weight: 500;
}
.default-badge {
  font-size: 10px;
  background: var(--color-primary);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
}
.color-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
}
.color-value {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.no-color {
  color: var(--color-text-tertiary);
}
.list-class {
  font-size: 12px;
  color: var(--color-success);
}
.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}
.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  gap: 16px;
  padding: 40px;
}
.no-selection i {
  font-size: 64px;
  color: var(--color-text-tertiary);
}
.no-selection h3 {
  font-size: 20px;
  color: var(--color-text);
  margin: 0;
}
.no-selection p {
  margin: 0;
  text-align: center;
}

@media (max-width: 768px) {
  .data-table-container {
    min-height: 200px;
  }
  .action-buttons {
    flex-direction: column;
  }
}
</style>
