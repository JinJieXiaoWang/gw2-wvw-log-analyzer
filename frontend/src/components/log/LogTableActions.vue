<template>
  <div class="table-actions flex items-center gap-2">
    <a v-if="data.dpsReportPermalink" :href="data.dpsReportPermalink" target="_blank" class="no-underline">
      <BaseButton v-tooltip.top="'查看 EI 报告'" icon="pi pi-external-link" size="small" text class="action-btn" />
    </a>
    <BaseButton
      v-tooltip.top="'查看详情'"
      icon="pi pi-eye"
      size="small"
      text
      class="action-btn"
      @click="$emit('view', data)"
    />
    <BaseButton
      v-if="data.status === 'pending' || data.status === 'failed'"
      v-tooltip.top="'重新解析'"
      icon="pi pi-refresh"
      size="small"
      text
      class="action-btn"
      :loading="parsing"
      @click="$emit('parse', data)"
    />
    <BaseButton
      v-tooltip.top="'删除日志'"
      icon="pi pi-trash"
      size="small"
      text
      severity="danger"
      class="action-btn"
      @click="$emit('delete', data)"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/BaseButton.vue'

defineProps<{
  data: any
  parsing: boolean
}>()

defineEmits<{
  (e: 'view', data: any): void
  (e: 'parse', data: any): void
  (e: 'delete', data: any): void
}>()
</script>
