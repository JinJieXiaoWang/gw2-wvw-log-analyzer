<template>
  <div
    v-if="files.length === 0"
    class="border-2 border-dashed border-neutral-border rounded-2xl p-8 text-center transition-all cursor-pointer"
    :class="{ 'border-primary bg-primary/5 scale-[1.02]': isDragging }"
    @dragover.prevent="$emit('dragover')"
    @dragleave.prevent="$emit('dragleave')"
    @drop.prevent="$emit('drop', $event)"
    @click="$emit('trigger')"
  >
    <div class="w-20 h-20 mx-auto bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl flex items-center justify-center mb-4">
      <i class="pi pi-cloud-upload text-4xl text-primary" />
    </div>
    <p class="text-neutral-text text-lg font-medium mb-2">拖拽文件到此处或点击选择</p>
    <p class="text-xs text-neutral-text-secondary mb-4">支持 .zevtc 格式文件，最多可选择 100 个文件</p>
    <BaseButton label="选择文件" icon="pi pi-folder-open" class="btn-game" @click.stop="$emit('trigger')" />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/BaseButton.vue'

defineProps<{
  files: File[]
  isDragging: boolean
}>()

defineEmits<{
  (e: 'trigger'): void
  (e: 'dragover'): void
  (e: 'dragleave'): void
  (e: 'drop', event: DragEvent): void
}>()
</script>
