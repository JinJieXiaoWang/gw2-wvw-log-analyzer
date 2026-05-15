<template>
  <Dialog
    v-model:visible="localVisible"
    header="解析进度详情"
    modal
    :style="{ width: '500px' }"
    class="custom-dialog"
  >
    <div class="space-y-2 max-h-80 overflow-y-auto">
      <div
        v-for="item in progressList"
        :key="item.logId"
        class="flex items-center justify-between p-3 rounded-lg"
        :class="{
          'bg-status-success/10 border border-status-success/20': item.status === ParseStatus.COMPLETED,
          'bg-status-error/10 border border-status-error/20': item.status === ParseStatus.FAILED || item.status === 'timeout',
          'bg-primary/5 border border-primary/10': item.status === ParseStatus.PARSING
        }"
      >
        <div class="flex items-center gap-2 min-w-0">
          <i
            class="pi"
            :class="{
              'pi-check-circle text-status-success': item.status === ParseStatus.COMPLETED,
              'pi-times-circle text-status-error': item.status === ParseStatus.FAILED || item.status === 'timeout',
              'pi-spin pi-spinner text-primary': item.status === ParseStatus.PARSING
            }"
          />
          <span class="text-sm text-neutral-text truncate">{{ item.fileName }}</span>
        </div>
        <span class="text-xs font-medium flex-shrink-0 ml-2">
          <span
            v-if="item.status === ParseStatus.COMPLETED"
            class="text-status-success"
          >完成</span>
          <span
            v-else-if="item.status === ParseStatus.FAILED"
            class="text-status-error"
          >失败</span>
          <span
            v-else-if="item.status === 'timeout'"
            class="text-status-error"
          >超时</span>
          <span
            v-else
            class="text-primary"
          >{{ item.progress }}%</span>
        </span>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import { computed } from 'vue'
import { ParseStatus } from '@/constants/dictValues'

interface ParseProgressItem {
  logId: number
  fileName: string
  status: string
  progress: number
}

const props = defineProps<{
  visible: boolean
  progressList: ParseProgressItem[]
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})
</script>
