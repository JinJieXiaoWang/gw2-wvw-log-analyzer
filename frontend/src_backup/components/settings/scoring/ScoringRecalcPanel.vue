<template>
  <div
    v-if="data.task"
    class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5 shadow-lg"
  >
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <i
          v-if="data.task.status === 'processing'"
          class="pi pi-spinner pi-spin text-ai"
        />
        <i
          v-else-if="data.task.status === 'completed'"
          class="pi pi-check-circle text-green-500"
        />
        <i
          v-else-if="data.task.status === 'failed'"
          class="pi pi-times-circle text-red-500"
        />
        <i
          v-else
          class="pi pi-clock text-color-secondary"
        />
        <span class="font-medium">历史数据重算任务</span>
        <BaseTag
          :value="data.task.status"
          :severity="data.statusSeverity"
          class="text-xs"
        />
      </div>
      <BaseButton
        v-if="data.task.status === 'completed' || data.task.status === 'failed'"
        icon="pi pi-times"
        text
        rounded
        size="small"
        @click="emit('dismiss')"
      />
    </div>
    <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden mb-2">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="data.task.status === 'completed' ? 'bg-green-500' : data.task.status === 'failed' ? 'bg-red-500' : 'bg-primary-500'"
        :style="{ width: data.task.progress_percent + '%' }"
      />
    </div>
    <div class="flex justify-between text-xs text-color-secondary">
      <span>{{ data.task.updated_records }} / {{ data.task.total_records }} 条记录/span>
        <span>{{ data.task.progress_percent?.toFixed(1) || 0 }}%</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'

interface RecalcPanelData {
  task: any
  statusSeverity: string
}

const props = defineProps<{ data: RecalcPanelData }>()
const emit = defineEmits<{ dismiss: [] }>()
</script>
