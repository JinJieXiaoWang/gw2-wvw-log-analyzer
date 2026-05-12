<script setup lang="ts">
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { fmtCompact, getProfessionIconUrl, getProfessionName, rankClass } from '@/composables/combat/useCombatHelpers'
import { CATEGORY_FIELDS, getStatValue, getStatValueClass } from '@/composables/combat/useStatDetail'

const props = defineProps<{
  title: string
  statDetailList: EiAnalysisPlayer[]
  statDetailAverage: number
  currentStatType: string
  currentStatCategory: string[]
}>()

const visible = defineModel<boolean>('visible', { default: false })

const emit = defineEmits<{
  'open-player-dialog': [player: EiAnalysisPlayer]
}>()
</script>

<template>
  <Dialog
    :visible="visible"
    :header="title"
    :style="{ width: '700px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
    @update:visible="visible = $event"
  >
    <div class="space-y-4">
      <!-- 统计摘要 -->
      <div class="flex items-center gap-4 p-3 rounded-xl bg-neutral-bg-secondary border border-neutral-border/50">
        <div class="flex items-center gap-2">
          <i class="pi pi-users text-primary" />
          <span class="text-sm text-neutral-text">共 {{ statDetailList.length }} 人</span>
        </div>
        <div
          v-if="statDetailList.length > 0"
          class="flex items-center gap-2 ml-auto"
        >
          <span class="text-xs text-neutral-text-secondary">平均值：</span>
          <span class="text-sm font-semibold text-primary">
            {{ statDetailAverage.toFixed(1) }}{{ currentStatType === 'condition_cleanses' || currentStatType === 'boon_strips' || currentStatType === 'damage_taken' || currentStatType === 'position' ? '' : '%' }}
          </span>
        </div>
      </div>

      <!-- 玩家列表 -->
      <DataTable
        :value="statDetailList"
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
              @click="emit('open-player-dialog', data)"
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
        <!-- 动态字段列：根据当前分类展示一个或多个字段 -->
        <Column
          v-for="field in currentStatCategory"
          :key="field"
          :field="field"
          :header="CATEGORY_FIELDS[currentStatType]?.labels[field] || field"
          style="min-width: 100px"
        >
          <template #body="{ data }">
            <span
              class="text-sm font-semibold"
              :class="getStatValueClass(field, data)"
            >{{ getStatValue(data, field) }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </Dialog>
</template>
