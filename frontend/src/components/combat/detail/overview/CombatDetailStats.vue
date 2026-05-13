<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <div class="flex items-center justify-between mb-5">
      <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-secondary/10">
          <i class="pi pi-sliders-h text-secondary" />
        </div>
        详细战斗统计
      </h3>
      <BaseButton
        :label="showDetailStats ? '收起' : '展开'"
        :icon="showDetailStats ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
        variant="secondary"
        size="small"
        @click="showDetailStats = !showDetailStats"
      />
    </div>
    <div
      v-show="showDetailStats"
      class="space-y-5"
    >
      <!-- 伤害细分 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="card p-4 rounded-xl bg-gradient-to-br from-primary/10 to-transparent border-primary/20">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">直伤总量</span>
            <div class="p-1.5 rounded-lg bg-primary/20">
              <i class="pi pi-bolt text-primary text-sm" />
            </div>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-primary">
              {{ fmtCompact(agg.total_power_damage) }}
            </p>
            <div class="mt-2 flex items-center justify-center gap-2">
              <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full transition-all duration-700"
                  :style="{ width: powerPct + '%' }"
                />
              </div>
              <span class="text-sm font-semibold text-primary">{{ powerPct }}%</span>
            </div>
          </div>
        </div>
        <div class="card p-4 rounded-xl bg-gradient-to-br from-success/10 to-transparent border-success/20">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">症状总量</span>
            <div class="p-1.5 rounded-lg bg-success/20">
              <i class="pi pi-flame text-success text-sm" />
            </div>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-success">
              {{ fmtCompact(agg.total_condi_damage) }}
            </p>
            <div class="mt-2 flex items-center justify-center gap-2">
              <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                <div
                  class="h-full bg-success rounded-full transition-all duration-700"
                  :style="{ width: condiPct + '%' }"
                />
              </div>
              <span class="text-sm font-semibold text-success">{{ condiPct }}%</span>
            </div>
          </div>
        </div>
        <div class="card p-4 rounded-xl bg-gradient-to-br from-secondary/10 to-transparent border-secondary/20">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-medium text-neutral-text-secondary uppercase tracking-wider">破甲总量</span>
            <div class="p-1.5 rounded-lg bg-secondary/20">
              <i class="pi pi-hammer text-secondary text-sm" />
            </div>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-secondary">
              {{ fmtCompact(agg.total_breakbar_damage) }}
            </p>
            <div class="mt-2 flex items-center justify-center gap-2">
              <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
                <div
                  class="h-full bg-secondary rounded-full transition-all duration-700"
                  :style="{ width: breakbarPct + '%' }"
                />
              </div>
              <span class="text-sm font-semibold text-secondary">{{ breakbarPct }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细数据表格 -->
      <DataTable
        :value="players"
        striped-rows
        :paginator="true"
        :rows="10"
        class="w-full"
        scrollable
      >
        <Column
          field="character_name"
          header="玩家"
          style="min-width: 140px"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <img
                :src="getProfessionIconUrl(data.profession)"
                class="w-7 h-7 rounded-full"
              >
              <div>
                <p class="text-sm font-medium">
                  {{ data.character_name || data.account }}
                </p>
                <p
                  v-if="data.account && data.character_name"
                  class="text-[10px] text-neutral-text-secondary truncate"
                >
                  {{ data.account }}
                </p>
                <p class="text-[10px] text-neutral-text-secondary">
                  {{ getProfessionName(data.profession) }}
                </p>
              </div>
            </div>
          </template>
        </Column>
        <Column
          field="damage"
          header="伤害"
          style="min-width: 90px"
        >
          <template #body="{ data }">
            <span class="text-sm font-semibold text-primary">{{ fmtCompact(data.damage) }}</span>
          </template>
        </Column>
        <Column
          field="dps"
          header="DPS"
          style="min-width: 80px"
        >
          <template #body="{ data }">
            <span class="text-sm font-semibold text-status-error">{{ fmtCompact(data.dps) }}</span>
          </template>
        </Column>
        <Column
          field="power_damage"
          header="直伤"
          style="min-width: 90px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ fmtCompact(data.power_damage) }}</span>
          </template>
        </Column>
        <Column
          field="condi_damage"
          header="症状"
          style="min-width: 90px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ fmtCompact(data.condi_damage) }}</span>
          </template>
        </Column>
        <Column
          field="breakbar_damage"
          header="破甲"
          style="min-width: 90px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ fmtCompact(data.breakbar_damage) }}</span>
          </template>
        </Column>
        <Column
          field="flanking_rate"
          header="侧身率"
          style="min-width: 80px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ data.flanking_rate.toFixed(1) }}%</span>
          </template>
        </Column>
        <Column
          field="glance_rate"
          header="擦过率"
          style="min-width: 80px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ data.glance_rate.toFixed(1) }}%</span>
          </template>
        </Column>
        <Column
          field="missed"
          header="未命中"
          style="min-width: 80px"
        />
        <Column
          field="interrupts"
          header="打断"
          style="min-width: 70px"
        />
        <Column
          field="swap_count"
          header="换武器"
          style="min-width: 80px"
        />
        <Column
          field="blocked_count"
          header="格挡"
          style="min-width: 70px"
        />
        <Column
          field="evaded_count"
          header="闪避"
          style="min-width: 70px"
        />
        <Column
          field="dodge_count"
          header="翻滚"
          style="min-width: 70px"
        />
        <Column
          field="boon_strips"
          header="剥增益"
          style="min-width: 85px"
        />
        <Column
          field="condition_cleanses"
          header="清症"
          style="min-width: 70px"
        />
        <Column
          field="downed"
          header="击倒"
          style="min-width: 70px"
        >
          <template #body="{ data }">
            <span class="text-sm font-semibold text-warning">{{ data.downed || 0 }}</span>
          </template>
        </Column>
        <Column
          field="stun_break"
          header="解控"
          style="min-width: 70px"
        >
          <template #body="{ data }">
            <span class="text-sm">{{ data.stun_break || 0 }}</span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { fmtCompact, getProfessionIconUrl, getProfessionName } from '@/composables/combat/useCombatHelpers'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import { ref } from 'vue'

const { players, agg, powerPct, condiPct, breakbarPct } = defineProps<{
  players: any[]
  agg: any
  powerPct: number
  condiPct: number
  breakbarPct: number
}>()

const showDetailStats = ref(false)
</script>
