<template>
  <div class="config-card">
    <div class="card-header">
      <div class="icon-box icon-amber">
        <i class="pi pi-bolt text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          解析参数
        </h4>
        <span class="text-xs text-color-secondary">日志解析相关配置</span>
      </div>
    </div>
    <div class="space-y-4">
      <div class="config-row">
        <div class="config-info">
          <div class="icon-badge icon-purple">
            <i class="pi pi-spinner" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">解析并行数</label>
            <p class="text-xs text-color-secondary">
              批量解析时的并行任务数
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="configs.parse_parallel"
          :min="1"
          :max="8"
          class="w-full sm:w-24 max-w-full"
          @blur="emit('markChanged', 'parse_parallel')"
        />
      </div>
      <div class="config-row">
        <div class="config-info">
          <div class="icon-badge icon-teal">
            <i class="pi pi-calendar" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">数据保留天数</label>
            <p class="text-xs text-color-secondary">
              超过此天数的日志将被清理
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="configs.retention_days"
          :min="30"
          :max="3650"
          suffix=" 天"
          class="w-full sm:w-32 max-w-full"
          @blur="emit('markChanged', 'retention_days')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'

defineProps<{
  configs: Record<string, any>
}>()

const emit = defineEmits<{
  markChanged: [key: string]
}>()
</script>

<style scoped>
.config-card {
  @apply bg-neutral-card border border-neutral-border rounded-2xl p-5 shadow-sm;
}

.card-header {
  @apply flex items-center gap-3 mb-4;
}

.config-row {
  @apply flex items-center gap-3 p-3 bg-neutral-bg-secondary rounded-lg flex-wrap sm:flex-nowrap;
}

.config-info {
  @apply flex items-center gap-3 flex-1 min-w-0;
}

.icon-box {
  @apply w-10 h-10 rounded-lg flex items-center justify-center;
}

.icon-amber {
  @apply bg-gradient-to-br from-amber-500 to-orange-600;
}

.icon-badge {
  @apply w-8 h-8 rounded flex items-center justify-center;
}

.icon-purple {
  background-color: var(--color-secondary-alpha-10);
  color: var(--color-secondary);
}

.icon-teal {
  background-color: var(--color-ai-alpha-10);
  color: var(--color-ai);
}
</style>
