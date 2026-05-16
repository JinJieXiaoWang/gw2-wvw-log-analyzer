<template>
  <div class="config-card">
    <div class="card-header">
      <div class="icon-box icon-primary">
        <i class="pi pi-cog text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          核心功能
        </h4>
        <span class="text-xs text-color-secondary">影响系统核心行为</span>
      </div>
    </div>
    <div class="space-y-4">
      <div class="config-row">
        <div class="config-info">
          <div class="icon-badge icon-blue">
            <i class="pi pi-chart-line" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">评分模式</label>
            <p class="text-xs text-color-secondary">
              选择评分规则的应用方式
            </p>
          </div>
        </div>
        <BaseSelect
          v-model="configs.scoring_mode"
          :options="scoringModeOptions"
          option-label="label"
          option-value="value"
          class="w-full sm:w-40 max-w-full"
          @change="emit('markChanged', 'scoring_mode')"
        />
      </div>
      <div class="config-row">
        <div class="config-info">
          <div class="icon-badge icon-green">
            <i class="pi pi-server" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">默认服务器</label>
            <p class="text-xs text-color-secondary">
              新建日志时默认选中的服务器
            </p>
          </div>
        </div>
        <BaseInput
          v-model="configs.default_server"
          class="w-full sm:w-40 max-w-full"
          @input="emit('markChanged', 'default_server')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'

defineProps<{
  configs: Record<string, any>
  scoringModeOptions: any[]
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

.icon-primary {
  @apply bg-gradient-to-br from-primary to-secondary;
}

.icon-badge {
  @apply w-8 h-8 rounded flex items-center justify-center;
}

.icon-blue {
  background-color: var(--color-primary-alpha-10);
  color: var(--color-primary);
}

.icon-green {
  background-color: var(--color-success-alpha-10);
  color: var(--color-success);
}
</style>
