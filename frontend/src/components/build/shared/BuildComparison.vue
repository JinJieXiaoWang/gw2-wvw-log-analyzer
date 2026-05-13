<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.7s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-arrows-h text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            Build对比
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            对比不同的Build的属性
          </p>
        </div>
      </div>
      <BaseButton
        label="添加对比"
        icon="pi pi-plus"
        class="btn-game"
        size="small"
        @click="showCompareDialog"
      />
    </div>
    <div
      v-if="compareBuilds.length > 0"
      class="space-y-4"
    >
      <DataTable
        :value="compareBuilds"
        class="w-full"
      >
        <Column
          field="name"
          header="Build名称"
        />
        <Column
          field="profession"
          header="ְҵ"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                :style="{ background: `linear-gradient(135deg, ${getProfessionColor(data.profession)}, ${getProfessionColor(data.profession)}88)` }"
              >
                {{ data.profession.charAt(0) }}
              </div>
              <span>{{ data.profession }}</span>
            </div>
          </template>
        </Column>
        <Column
          field="power"
          header="威能"
        />
        <Column
          field="precision"
          header="精准"
        />
        <Column
          field="toughness"
          header="坚韧"
        />
        <Column
          field="vitality"
          header="体力"
        />
        <Column
          header="操作"
          style="width: 100px"
        >
          <template #body>
            <BaseButton
              icon="pi pi-trash"
              class="btn-ghost"
              size="small"
              severity="danger"
            />
          </template>
        </Column>
      </DataTable>
    </div>
    <div
      v-else
      class="text-center py-8 text-neutral-text-secondary"
    >
      <i class="pi pi-arrows-h text-4xl mb-3 opacity-50" />
      <p>点击"添加对比"对比不同的Build</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build对比组件
 * 功能：对比不同Build的属性差异
 * 作者：帅姐姐 
 * 创建日期：2026-04-27
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

defineProps<{
  compareBuilds: Array<{
    id: number
    name: string
    profession: string
    code: string
    power: number
    precision: number
    toughness: number
    vitality: number
  }>
}>()

// Emits
const emit = defineEmits<{
  'show-compare-dialog': []
}>()

// 事件处理
const showCompareDialog = () => {
  emit('show-compare-dialog')
}

// 方法
const getProfessionColor = (profession: string) => {
  const colors: Record<string, string> = {
    '战士': '#E85D04',
    '守护者': '#FAA307',
    '潜行者': '#9D4EDD',
    '元素师': '#FF6B6B',
    '工程师': '#7B8FA1',
    '猎人': '#06D6A0',
    '唤灵师': '#8D0801',
    '幻术师': '#4361EE',
    '游侠': '#2EC4B6'
  }
  return colors[profession] || '#6C757D'
}
</script>