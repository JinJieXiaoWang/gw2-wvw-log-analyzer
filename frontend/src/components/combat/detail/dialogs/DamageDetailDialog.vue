<template>
  <Dialog
    v-model:visible="visible"
    header="伤害构成详情"
    :style="{ width: '800px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
  >
    <div class="space-y-6">
      <!-- 环形图 + 图例 -->
      <div class="flex flex-col sm:flex-row items-center gap-6">
        <div class="relative w-48 h-48">
          <svg
            viewBox="0 0 100 100"
            class="w-full h-full -rotate-90 transform transition-all duration-500"
          >
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-border)"
              stroke-width="12"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-primary)"
              stroke-width="12"
              :stroke-dasharray="data.donut.pd"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-success)"
              stroke-width="12"
              :stroke-dasharray="data.donut.cd"
              :stroke-dashoffset="data.donut.co"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-secondary)"
              stroke-width="12"
              :stroke-dasharray="data.donut.bd"
              :stroke-dashoffset="data.donut.bo"
              class="transition-all duration-700"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-bold text-neutral-text">{{ fmtCompact(data.donut.total) }}</span>
            <span class="text-xs text-neutral-text-secondary mt-1">总伤害</span>
          </div>
        </div>
        <div class="flex-1 space-y-4">
          <div
            v-for="item in legendItems"
            :key="item.label"
            class="flex items-center justify-between p-4 rounded-xl border"
            :class="item.borderClass + ' ' + item.bgClass"
          >
            <div class="flex items-center gap-3">
              <span
                class="w-4 h-4 rounded-full"
                :class="item.dotClass"
              /><span class="text-sm font-semibold text-neutral-text">{{ item.label }}</span>
            </div>
            <div class="text-right">
              <p
                class="text-xl font-bold"
                :class="item.valueClass"
              >
                {{ item.value }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ item.percent }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 伤害排行 -->
      <div>
        <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
          <i class="pi pi-trophy text-yellow-500" /> 伤害贡献排行
        </h4>
        <DataTable
          :value="data.topDpsPlayers"
          :paginator="true"
          :rows="10"
          class="w-full"
          scrollable
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
            style="min-width: 140px"
          >
            <template #body="{ data }">
              <div class="flex items-center gap-2">
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
            field="damage"
            header="总伤害"
            style="min-width: 120px"
          >
            <template #body="{ data }">
              <span class="text-sm font-bold text-primary">{{ fmtCompact(data.damage) }}</span>
            </template>
          </Column>
          <Column
            field="power_damage"
            header="ֱ直伤"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm text-primary/80">{{ fmtCompact(data.power_damage) }}</span>
            </template>
          </Column>
          <Column
            field="condi_damage"
            header="֢症状伤害"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm text-success/80">{{ fmtCompact(data.condi_damage) }}</span>
            </template>
          </Column>
          <Column
            field="dps"
            header="DPS"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm font-semibold text-neutral-text">{{ fmtCompact(data.dps) }}</span>
            </template>
          </Column>
          <Column
            field="damage_percent"
            header="伤害比"
            style="min-width: 80px"
          >
            <template #body="{ data }">
              <span class="text-sm">{{ ((data.damage / Math.max(props.data.donut.total, 1)) * 100).toFixed(1) }}%</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { rankClass } from '@/utils/combat/combatFormatters'
import type { EiAnalysisAggregate, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

interface DonutData {
  total: number
  p: number
  c: number
  b: number
  pd: string
  cd: string
  bd: string
  co: number
  bo: number
}

interface DamageDialogData {
  donut: DonutData
  agg: EiAnalysisAggregate
  topDpsPlayers: EiAnalysisPlayer[]
}

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  data: DamageDialogData
}>()

const legendItems = computed(() => [
  { label: 'ֱ直伤', value: fmtCompact(props.data.agg.total_power_damage), percent: props.data.donut.p, dotClass: 'bg-primary', borderClass: 'border-primary/20', bgClass: 'bg-primary/10', valueClass: 'text-primary' },
  { label: '֢症状伤害', value: fmtCompact(props.data.agg.total_condi_damage), percent: props.data.donut.c, dotClass: 'bg-success', borderClass: 'border-success/20', bgClass: 'bg-success/10', valueClass: 'text-success' },
  { label: '破甲', value: fmtCompact(props.data.agg.total_breakbar_damage), percent: props.data.donut.b, dotClass: 'bg-secondary', borderClass: 'border-secondary/20', bgClass: 'bg-secondary/10', valueClass: 'text-secondary' },
])
</script>
