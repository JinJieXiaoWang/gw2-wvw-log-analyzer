<template>
  <div class="toolbar">
    <div class="toolbar-left">
      <h3 class="toolbar-title">
        <template v-if="selectedDictType">
          {{ selectedDictType.dict_name }}
          <span class="type-code">({{ selectedDictType.dict_type }})</span>
        </template>
        <template v-else>
          请选择字典分类
        </template>
      </h3>
    </div>
    <div class="toolbar-right">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="localSearch"
          placeholder="搜索数据..."
          size="small"
          :disabled="!selectedDictType"
        />
      </IconField>
      <BaseSelect
        v-model="localStatus"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="状态筛选"
        size="small"
        class="status-select"
        :disabled="!selectedDictType"
      />
      <BaseButton
        v-if="canWrite"
        label="新增"
        icon="pi pi-plus"
        severity="success"
        size="small"
        :disabled="!selectedDictType"
        @click="$emit('add')"
      />
      <BaseButton
        v-if="canWrite && selectedDictType"
        label="编辑分类"
        icon="pi pi-pencil"
        severity="warning"
        outlined
        size="small"
        @click="$emit('edit-type')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import type { DictType } from '@/services/system/dictionaryService'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import { computed } from 'vue'

const props = defineProps<{
  selectedDictType: DictType | null
  canWrite: boolean
  statusOptions: { label: string; value: number | null }[]
  dataSearchKeyword: string
  statusFilter: number | null
}>()

const emit = defineEmits<{
  'update:dataSearchKeyword': [value: string]
  'update:statusFilter': [value: number | null]
  add: []
  'edit-type': []
}>()

const localSearch = computed({
  get: () => props.dataSearchKeyword,
  set: v => emit('update:dataSearchKeyword', v)
})

const localStatus = computed({
  get: () => props.statusFilter,
  set: v => emit('update:statusFilter', v)
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  gap: 16px;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.toolbar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  white-space: nowrap;
}
.type-code {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-left: 8px;
  font-family: monospace;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.status-select {
  width: 120px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .toolbar-left {
    justify-content: center;
  }
  .toolbar-right {
    justify-content: center;
  }
}
</style>
