<template>
  <div class="config-card">
    <div class="card-header">
      <div class="icon-box icon-cyan">
        <i class="pi pi-file-export text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          导出格式
        </h4>
        <span class="text-xs text-color-secondary">数据导出的默认格式</span>
      </div>
    </div>
    <div class="config-row">
      <div class="config-info">
        <div class="icon-badge icon-cyan">
          <i class="pi pi-file" />
        </div>
        <div>
          <label class="text-sm font-medium text-color">默认导出格式</label>
          <p class="text-xs text-color-secondary">
            选择默认的数据导出格式
          </p>
        </div>
      </div>
      <BaseSelect
        v-model="configs.export_format"
        :options="exportFormatOptions"
        option-label="label"
        option-value="value"
        class="w-full sm:w-32 max-w-full"
        @change="emit('markChanged', 'export_format')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'

defineProps<{
  configs: Record<string, any>
  exportFormatOptions: any[]
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

.icon-cyan {
  background-color: var(--color-ai-alpha-10);
  color: var(--color-ai);
}

.icon-badge {
  @apply w-8 h-8 rounded flex items-center justify-center;
}
</style>
