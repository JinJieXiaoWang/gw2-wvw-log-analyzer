<template>
  <Dialog
    v-model:visible="visible"
    :header="title"
    :style="{ width: '700px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
  >
    <div class="space-y-4">
      <!-- 统计ժҪ -->
      <div
        class="flex items-center gap-4 p-3 rounded-xl bg-neutral-bg-secondary border
               border-neutral-border/50">
        <div class="flex items-center gap-2">
          <i class="pi pi-users text-primary" /><span class="text-sm text-neutral-text">共 {{ data.statDetailList.length }} 人</span>
        </div>
        <div
          v-if="data.statDetailList.length > 0"
          class="flex items-center gap-2 ml-auto"
        >
          <span class="text-xs text-neutral-text-secondary">ƽ均值：</span>
          <span class="text-sm font-semibold text-primary">{{ data.statDetailAverage.toFixed(1) }}{{ unitSuffix }}</span>
        </div>
      </div>

      <!-- 玩家列表 -->
      <DataTable
        :value="data.statDetailList"
        :paginator="true"
        :rows="10"
        class="w-full"
        scrollable
        scroll-height="400px"
      >
        <Column
          field="rank"
          header="排名"
          style="width: 60px"
        >
          <template #body="{ index }">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
              :class="rankClass(index)"
            >{{ index + 1 }}</span>
          </template>
        </Column>
        <Column
          field="character_name"
          header="玩家"
          style="min-width: 160px"
        >
          <template #body="{ data }">
            <div
              class="flex items-center gap-2 cursor-pointer hover:text-primary transition-colors"
              @click="emit('player-click', data)"
            >
              <img
                :src="getProfessionIconUrl(data.profession)"
                class="w-6 h-6 rounded-full"
              >
              <div>
                <p class="text-sm font-medium">
                  {{ data.character_name || data.account }}
                </p>
                <p class="text-xs text-neutral-text-secondary">
                  {{ getProfessionName(data.profession) }}
                </p>
              </div>
            </div>
          </template>
        </Column>
        <Column
          field="account"
          header="账号"
          style="min-width: 120px"
        >
          <template #body="{ data }">
            <span class="text-xs text-neutral-text-secondary">{{ data.account }}</span>
          </template>
        </Column>
        <Column
          v-for="field in data.currentStatCategory"
          :key="field"
          :field="field"
          :header="CATEGORY_FIELDS[data.currentStatType]?.labels[field] || field"
          style="min-width: 100px"
        >
          <template #body="{ data: rowData }">
            <span
              class="text-sm font-semibold"
              :class="getStatValueClass(field, rowData)"
            >{{ getStatValue(rowData, field) }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { rankClass } from '@/utils/combat/combatFormatters'
import { type StatCategory, CATEGORY_FIELDS, getStatValue, getStatValueClass } from '@/utils/combat/combatStats'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

interface StatDialogData {
  statDetailList: EiAnalysisPlayer[]
  currentStatCategory: string[]
  currentStatType: StatCategory
  statDetailAverage: number
}

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  title: string
  data: StatDialogData
}>()

const emit = defineEmits<{
  'player-click': [player: EiAnalysisPlayer]
}>()

const unitSuffix = computed(() => {
  const t = props.data.currentStatType
  return t === 'condition_cleanses' || t === 'boon_strips' || t === 'damage_taken' || t === 'position' ? '' : '%'
})
</script>
