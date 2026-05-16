<template>
  <div class="config-card">
    <div class="card-header">
      <div class="icon-box icon-red">
        <i class="pi pi-database text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          系统维护
        </h4>
        <span class="text-xs text-color-secondary">数据备份与维护设置</span>
      </div>
    </div>
    <div class="config-row">
      <div class="config-info">
        <div class="icon-badge icon-red">
          <i class="pi pi-history" />
        </div>
        <div>
          <label class="text-sm font-medium text-color">自动备份</label>
          <p class="text-xs text-color-secondary">
            是否启用自动数据库备份
          </p>
        </div>
      </div>
      <BaseToggleSwitch
        v-model="configs.auto_backup"
        @change="emit('markChanged', 'auto_backup')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseToggleSwitch from '@/components/common/ui/input/BaseToggleSwitch.vue'

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

.icon-red {
  background-color: var(--color-error-alpha-10);
  color: var(--color-error);
}

.icon-badge {
  @apply w-8 h-8 rounded flex items-center justify-center;
}
</style>
