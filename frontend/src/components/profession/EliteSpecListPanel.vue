<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <h3 class="text-base font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-secondary/10">
          <i class="pi pi-star text-secondary text-sm" />
        </div>
        精英特长列表
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
        v-for="spec in eliteSpecs"
        :key="spec.spec_key"
        class="card p-0 overflow-hidden group relative"
      >
        <div
          class="flex items-center gap-4 p-5 border-b border-neutral-border/50"
          :style="{ borderLeftWidth: '4px', borderLeftColor: spec.color }"
        >
          <span class="text-2xl">{{ spec.icon }}</span>
          <div class="flex-1 min-w-0">
            <h4 class="text-base font-semibold text-neutral-text">
              {{ spec.spec_name }}
            </h4>
            <p class="text-xs text-neutral-text-secondary">
              {{ spec.spec_name_en }}
            </p>
          </div>
          <div
            v-if="canEdit"
            class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <button
              class="p-1.5 rounded-lg hover:bg-primary/20 text-primary transition-colors"
              title="编辑"
              @click="$emit('edit', 'spec', spec)"
            >
              <i class="pi pi-pencil text-sm" />
            </button>
          </div>
        </div>
        <div class="p-5 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">所属职业</span>
            <Tag
              :value="getProfessionName(spec.profession_key)"
              severity="info"
              class="text-xs"
            />
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">角色定位</span>
            <Tag
              :value="getRoleName(spec.role_type)"
              severity="info"
              class="text-xs"
            />
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">状态</span>
            <DictTag
              dict-type="sys_normal_disable"
              :value="spec.is_active ? 0 : 1"
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
  eliteSpecs: any[]
  canEdit: boolean
  getRoleName: (key: string) => string
  getProfessionName: (key: string) => string
}>()

defineEmits<{
  refresh: []
  edit: [type: 'profession' | 'spec', item: any]
}>()
</script>
