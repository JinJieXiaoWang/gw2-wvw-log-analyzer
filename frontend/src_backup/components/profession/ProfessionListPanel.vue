<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <h3 class="text-base font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-primary/10">
          <i class="pi pi-sitemap text-primary text-sm" />
        </div>
        职业列表
      </h3>
      <BaseButton
        label="刷新数据"
        icon="pi pi-refresh"
        variant="secondary"
        size="small"
        @click="$emit('refresh')"
      />
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="prof in professions"
        :key="prof.profession_key"
        class="card p-0 overflow-hidden group relative"
      >
        <div
          class="flex items-center gap-4 p-5 border-b border-neutral-border/50"
          :style="{ borderLeftWidth: '4px', borderLeftColor: prof.color }"
        >
          <span class="text-2xl">{{ prof.icon }}</span>
          <div class="flex-1 min-w-0">
            <h4 class="text-base font-semibold text-neutral-text">
              {{ prof.profession_name }}
            </h4>
            <p class="text-xs text-neutral-text-secondary">
              {{ prof.profession_name_en }}
            </p>
          </div>
          <div
            v-if="canEdit"
            class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button
              class="p-1.5 rounded-lg hover:bg-primary/20 text-primary transition-colors"
              title="编辑"
              @click="$emit('edit', 'profession', prof)"
            >
              <i class="pi pi-pencil text-sm" />
            </button>
          </div>
        </div>
        <div class="p-5 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">默认角色</span>
            <Tag
              :value="getRoleName(prof.default_role)"
              severity="info"
              class="text-xs"
            />
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">精英特长</span>
            <span class="text-neutral-text font-medium">{{ prof.elite_specializations?.length || 0 }} 个</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">状态</span>
            <Tag
              :value="prof.is_active ? '启用' : '禁用'"
              :severity="prof.is_active ? 'success' : 'danger'"
              class="text-xs"
            />
          </div>
        </div>
        <div
          v-if="prof.elite_specializations?.length"
          class="px-5 pb-5"
        >
          <div class="flex flex-wrap gap-2">
            <Tag
              v-for="spec in prof.elite_specializations"
              :key="spec.spec_key"
              :value="spec.spec_name"
              severity="secondary"
              class="text-xs"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Tag from 'primevue/tag'

defineProps<{
  professions: any[]
  canEdit: boolean
  getRoleName: (key: string) => string
}>()

defineEmits<{
  refresh: []
  edit: [type: 'profession' | 'spec', item: any]
}>()
</script>
