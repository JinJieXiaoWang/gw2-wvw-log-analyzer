<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <h3 class="text-base font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-ai/10">
          <i class="pi pi-bullseye text-ai text-sm" />
        </div>
        角色定位列表
      </h3>
      <BaseButton
        label="刷新数据"
        icon="pi pi-refresh"
        variant="secondary"
        size="small"
        @click="$emit('refresh')"
      />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="role in roleTypes"
        :key="role.role_key"
        class="card p-5 flex items-center gap-4 group"
      >
        <div
          class="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0"
          :style="{ backgroundColor: role.color + '20', color: role.color }"
        >
          <span class="text-2xl">{{ role.icon }}</span>
        </div>
        <div class="min-w-0">
          <h4 class="text-base font-semibold text-neutral-text">
            {{ role.role_name }}
          </h4>
          <p class="text-xs text-neutral-text-secondary font-mono">
            {{ role.role_key }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

defineProps<{
  roleTypes: any[]
}>()

defineEmits<{
  refresh: []
}>()
</script>
