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
            aria-label="伤害构成环形图"
            role="img"
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
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span class="text-3xl font-bold text-neutral-text">{{ fmtCompact(donut.total) }}</span>
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
                aria-hidden="true"
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
                {{ safePercent(item.percent) }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 伤害贡献排行 -->
      <div>
        <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
          <i
            class="pi pi-trophy text-yellow-500"
            aria-hidden="true"
          /> 伤害贡献排行
        </h4>
        <DataTable
          :value="processedPlayers"
          :paginator="true"
          :rows="10"
          class="w-full"
          scrollable
          empty-message="暂无数据"
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
                :aria-label="'第' + (index + 1) + '名'"
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
                  alt=""
                  @error="handleImageError"
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
              <span class="text-sm">{{ data.displayPercent }}%</span>
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
import { fmtCompact, getProfessionIconUrl, getProfessionName, rankClass } from '@/composables/combat/useCombatHelpers'
import type { EiAnalysisAggregate, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

interface DonutData {
  total: number
  p: number | string
  c: number | string
  b: number | string
  pd: string | number
  cd: string | number
  bd: string | number
  co: number | string
  bo: number | string
}

const props = defineProps<{
  donut: DonutData
  agg: EiAnalysisAggregate
  topDpsPlayers: EiAnalysisPlayer[]
  breakbarPct: number
}>()

const visible = defineModel<boolean>('visible', { default: false })

/**
 * 安全地格式化百分比，处理 null/undefined/NaN
 */
const safePercent = (val: number | string | undefined | null): string => {
  if (val === undefined || val === null) return '0.0'
  const num = Number(val)
  if (isNaN(num)) return '0.0'
  return num.toFixed(1)
}

/**
 * 处理图片加载失败，隐藏破损图标
 */
const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  if (target) {
    target.style.display = 'none'
  }
}

/**
 * 预处理玩家列表，计算占比，避免模板中除以零错误
 */
const processedPlayers = computed(() => {
  const total = props.donut?.total || 0

  return props.topDpsPlayers.map(player => {
    let percent = 0
    if (total > 0) {
      percent = (player.damage / total) * 100
    }

    return {
      ...player,
      displayPercent: percent.toFixed(1)
    }
  })
})

const legendItems = computed(() => [
  { label: '直伤', value: fmtCompact(props.agg.total_power_damage), percent: props.donut.p, dotClass: 'bg-primary', borderClass: 'border-primary/20', bgClass: 'bg-primary/10', valueClass: 'text-primary' },
  { label: '症状', value: fmtCompact(props.agg.total_condi_damage), percent: props.donut.c, dotClass: 'bg-success', borderClass: 'border-success/20', bgClass: 'bg-success/10', valueClass: 'text-success' },
  { label: '破甲', value: fmtCompact(props.agg.total_breakbar_damage), percent: props.donut.b, dotClass: 'bg-secondary', borderClass: 'border-secondary/20', bgClass: 'bg-secondary/10', valueClass: 'text-secondary' },
])
</script>
