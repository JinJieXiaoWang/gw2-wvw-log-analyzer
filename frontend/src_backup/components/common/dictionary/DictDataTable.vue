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
        <div class="table-empty">
          <i class="pi pi-inbox" />
          <span v-if="!selectedDictType">请选择左侧字典分类</span>
          <span v-else>暂无数据</span>
        </div>
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
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { DictData, DictType } from '@/services/system/dictionaryService'

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
.data-table-container { flex: 1; background: #2a2a2a; border-radius: 12px; overflow: hidden; }
.dict-data-table { font-size: 14px; }
.sort-value, .value-text, .remark-text { color: #e5e5e5; }
.label-cell { display: flex; align-items: center; gap: 8px; }
.label-text { color: #e5e5e5; font-weight: 500; }
.default-badge { font-size: 10px; background: #165dff; color: #fff; padding: 2px 6px; border-radius: 4px; }
.color-cell { display: flex; align-items: center; gap: 8px; }
.color-swatch { width: 24px; height: 24px; border-radius: 4px; border: 1px solid #333; }
.color-value { font-size: 12px; color: #909399; }
.no-color { color: #909399; }
.list-class { font-size: 12px; color: #00c896; }
.action-buttons { display: flex; gap: 4px; }
.table-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px 20px; color: #909399; gap: 12px;
}
.table-empty i { font-size: 48px; }
.no-selection {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; color: #909399; gap: 16px;
}
.no-selection i { font-size: 64px; color: #333; }
.no-selection h3 { font-size: 20px; color: #e5e5e5; margin: 0; }
.no-selection p { margin: 0; }
</style>
