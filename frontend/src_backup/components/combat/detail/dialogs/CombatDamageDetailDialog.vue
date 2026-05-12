<script setup lang="ts">
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type { EiAnalysisPlayer, EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { fmtCompact, getProfessionIconUrl, getProfessionName, rankClass } from '@/composables/combat/useCombatHelpers'

const props = defineProps<{
  donut: any
  agg: EiAnalysisAggregate
  topDpsPlayers: EiAnalysisPlayer[]
  breakbarPct: number
}>()

const visible = defineModel<boolean>('visible', { default: false })
</script>

<template>
  <Dialog
    :visible="visible"
    header="伤害构成详情"
    :style="{ width: '800px', maxWidth: '95vw' }"
    :modal="true"
    :draggable="false"
    @update:visible="visible = $event"
  >
    <div class="space-y-6">
      <!-- 环形图 -->
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
              :stroke-dasharray="donut.pd"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-success)"
              stroke-width="12"
              :stroke-dasharray="donut.cd"
              :stroke-dashoffset="donut.co"
              class="transition-all duration-700"
            />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="var(--color-secondary)"
              stroke-width="12"
              :stroke-dasharray="donut.bd"
              :stroke-dashoffset="donut.bo"
              class="transition-all duration-700"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-bold text-neutral-text">{{ fmtCompact(donut.total) }}</span>
            <span class="text-xs text-neutral-text-secondary mt-1">总伤害</span>
          </div>
        </div>
        <div class="flex-1 space-y-4">
          <div class="flex items-center justify-between p-4 rounded-xl bg-primary/10 border border-primary/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-primary" />
              <span class="text-sm font-semibold text-neutral-text">直伤</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-primary">
                {{ fmtCompact(agg.total_power_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ donut.p }}%
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between p-4 rounded-xl bg-success/10 border border-success/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-success" />
              <span class="text-sm font-semibold text-neutral-text">症状</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-success">
                {{ fmtCompact(agg.total_condi_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ donut.c }}%
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between p-4 rounded-xl bg-secondary/10 border border-secondary/20">
            <div class="flex items-center gap-3">
              <span class="w-4 h-4 rounded-full bg-secondary" />
              <span class="text-sm font-semibold text-neutral-text">破甲</span>
            </div>
            <div class="text-right">
              <p class="text-xl font-bold text-secondary">
                {{ fmtCompact(agg.total_breakbar_damage) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ breakbarPct }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 伤害排行表格 -->
      <div>
        <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
          <i class="pi pi-trophy text-yellow-500" /> 伤害贡献排行
        </h4>
        <DataTable
          :value="topDpsPlayers"
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
            header="直伤"
            style="min-width: 100px"
          >
            <template #body="{ data }">
              <span class="text-sm text-primary/80">{{ fmtCompact(data.power_damage) }}</span>
            </template>
          </Column>
          <Column
            field="condi_damage"
            header="症状"
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
            header="占比"
            style="min-width: 80px"
          >
            <template #body="{ data }">
              <span class="text-sm">{{ ((data.damage / donut.total) * 100).toFixed(1) }}%</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </Dialog>
</template>
