<template>
  <div class="damage-analysis-view space-y-6">
    <!-- 伤害统计表格 -->
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-chart-bar text-primary mr-2" />
        伤害排名
      </h3>
      <DataTable
        :value="sortedPlayers"
        striped-rows
        class="w-full"
        :paginator="sortedPlayers.length > 20"
        :rows="20"
      >
        <Column
          field="rank"
          header="排名"
          style="width: 60px"
        >
          <template #body="{ data }">
            <div
              class="flex items-center justify-center w-7 h-7 rounded-full font-bold text-xs"
              :class="{
                'bg-yellow-500/20 text-yellow-500': data.rank === 1,
                'bg-gray-400/20 text-gray-400': data.rank === 2,
                'bg-orange-400/20 text-orange-400': data.rank === 3,
                'bg-neutral-bg text-neutral-text-secondary': data.rank > 3
              }"
            >
              {{ data.rank }}
            </div>
          </template>
        </Column>
        <Column
          field="name"
          header="玩家"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                :style="{ backgroundColor: getProfessionColor(data.profession) }"
              >
                {{ data.name.charAt(0) }}
              </div>
              <div>
                <div class="text-sm font-medium text-neutral-text">
                  {{ data.name }}
                </div>
                <div class="text-xs text-neutral-text-secondary">
                  {{ getProfessionName(data.profession) }}
                </div>
              </div>
            </div>
          </template>
        </Column>
        <Column
          field="damage"
          header="总伤害"
          sortable
        >
          <template #body="{ data }">
            <span class="text-primary font-semibold">{{ formatNumber(data.damage) }}</span>
          </template>
        </Column>
        <Column
          field="powerDamage"
          header="直伤"
          sortable
        >
          <template #body="{ data }">
            <span class="text-neutral-text">{{ formatNumber(data.powerDamage) }}</span>
          </template>
        </Column>
        <Column
          field="condiDamage"
          header="症状伤"
          sortable
        >
          <template #body="{ data }">
            <span class="text-status-warning">{{ formatNumber(data.condiDamage) }}</span>
          </template>
        </Column>
        <Column
          field="dps"
          header="DPS"
          sortable
        >
          <template #body="{ data }">
            <span class="font-semibold">{{ formatNumber(data.dps) }}</span>
          </template>
        </Column>
        <Column
          field="damageTaken"
          header="承伤"
          sortable
        >
          <template #body="{ data }">
            <span class="text-status-error">{{ formatNumber(data.damageTaken || 0) }}</span>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- 目标伤害 -->
    <div
      v-if="targets.length > 0"
      class="card"
    >
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-target text-primary mr-2" />
        目标承伤
      </h3>
      <div class="space-y-3">
        <div
          v-for="target in targets"
          :key="target.instanceID"
          class="flex items-center gap-4 p-3 rounded-lg bg-neutral-bg/50"
        >
          <div class="flex-1">
            <span class="font-medium text-neutral-text">{{ target.name || '未知目标' }}</span>
          </div>
          <div class="text-right">
            <p class="font-semibold text-primary">
              {{ formatNumber(target.dpsAll?.[0]?.damageTaken || 0) }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              承伤
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { formatCompactNumber as formatNumber } from '@/utils/core/helpers';
import { getProfessionColor } from '@/utils/profession/professionUtils';
import { getProfessionName } from '@/services/professionService';

const props = defineProps<{
  players: any[];
  targets: any[];
  duration: number;
}>();

const durationSec = computed(() => Math.max(props.duration / 1000, 1));

const sortedPlayers = computed(() => {
  return [...props.players]
    .map((p) => {
      const dmg = p.dpsAll?.[0]?.damage || 0;
      const power = p.dpsAll?.[0]?.powerDamage || 0;
      const condi = p.dpsAll?.[0]?.condiDamage || 0;
      return {
        ...p,
        rank: 0,
        damage: dmg,
        powerDamage: power,
        condiDamage: condi,
        dps: Math.round(dmg / durationSec.value),
      };
    })
    .sort((a, b) => b.damage - a.damage)
    .map((p, idx) => ({ ...p, rank: idx + 1 }));
});
</script>
