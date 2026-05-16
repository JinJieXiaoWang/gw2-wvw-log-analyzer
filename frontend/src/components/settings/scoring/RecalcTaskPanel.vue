<template>
  <div
    v-if="task"
    class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5 shadow-lg"
  >
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <i
          v-if="task.status === ScoringRuleStatus.PROCESSING"
          class="pi pi-spinner pi-spin text-ai"
        />
        <i
          v-else-if="task.status === ScoringRuleStatus.COMPLETED"
          class="pi pi-check-circle text-green-500"
        />
        <i
          v-else-if="task.status === ScoringRuleStatus.FAILED"
          class="pi pi-times-circle text-red-500"
        />
        <i
          v-else
          class="pi pi-clock text-color-secondary"
        />
        <span class="font-medium">历史数据重算任务</span>
        <Tag
          :value="task.status"
          :severity="severity"
          class="text-xs"
        />
      </div>
      <BaseButton
        v-if="task.status === ScoringRuleStatus.COMPLETED || task.status === ScoringRuleStatus.FAILED"
        icon="pi pi-times"
        text
        rounded
        size="small"
        @click="emit('close')"
      />
    </div>
    <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden mb-2">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="task.status === ScoringRuleStatus.COMPLETED ? 'bg-green-500' : task.status === ScoringRuleStatus.FAILED ? 'bg-red-500' : 'bg-primary-500'"
        :style="{ width: task.progress_percent + '%' }"
      />
    </div>
    <div class="flex justify-between text-xs text-color-secondary">
      <span>{{ task.updated_records }} / {{ task.total_records }} 条记录</span>
      <span>{{ task.progress_percent?.toFixed(1) || 0 }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ScoringRuleStatus } from '@/constants/dictValues'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Tag from 'primevue/tag'

const { task, severity } = defineProps<{
  task: any
  severity: string
}>()
const emit = defineEmits(['close'])
</script>
