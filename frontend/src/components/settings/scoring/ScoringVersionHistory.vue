<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5 shadow-lg">
    <h4 class="flex items-center gap-2 text-lg font-semibold text-color mb-4"><i class="pi pi-history text-primary-500" />规则版本历ʷ</h4>
    <DataTable :value="data.versions" size="small" striped-rows class="text-sm">
      <Column field="version" header="版本鍙? style="width: 90px">
        <template #body="{ data }"><span class="px-2 py-0.5 rounded-md bg-primary-500/10 text-primary-500 text-xs font-mono font-semibold">v{{ data.version }}</span></template>
      </Column>
      <Column field="description" header="变更描述" />
      <Column field="status" header="״漼? style="width: 100px">
        <template #body="{ data }"><BaseTag :value="data.status" :severity="data.status === 'completed' ? 'success' : data.status === 'processing' ? 'warning' : data.status === 'failed' ? 'danger' : 'info'" class="text-xs" /></template>
      </Column>
      <Column header="进度" style="width: 140px">
        <template #body="{ data }">
          <div v-if="data.total_records > 0" class="flex items-center gap-2">
            <div class="flex-1 h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
              <div class="h-full bg-primary-500 rounded-full transition-all" :style="{ width: (data.total_records ? (data.updated_records / data.total_records * 100) : 0) + '%' }" />
            </div>
            <span class="text-xs text-color-secondary whitespace-nowrap">{{ data.updated_records }}/{{ data.total_records }}</span>
          </div>
          <span v-else class="text-color-secondary text-xs">-</span>
        </template>
      </Column>
      <Column field="created_at" header="创建时间" style="width: 160px">
        <template #body="{ data }">{{ data.formatDate(data.created_at) }}</template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import BaseTag from '@/components/common/ui/BaseTag.vue'

interface VersionHistoryData {
  versions: any[]
  formatDate: (date?: string) => string
}

const props = defineProps<{ data: VersionHistoryData }>()
</script>
