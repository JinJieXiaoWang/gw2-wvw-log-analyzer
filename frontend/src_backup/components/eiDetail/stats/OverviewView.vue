<template>
  <div class="overview-view space-y-6">
    <!-- KPI 卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card bg-gradient-to-br from-primary/20 to-primary/5 border-primary/30">
        <div class="flex items-center gap-3 mb-2">
          <i class="pi pi-bolt text-primary text-xl" />
          <span class="text-sm text-neutral-text-secondary">总伤害</span>
        </div>
        <p class="text-2xl font-bold text-primary">
          {{ formatNumber(totalDamage) }}
        </p>
        <p class="text-xs text-neutral-text-disabled mt-1">
          场均 {{ formatNumber(avgDamage) }}
        </p>
      </div>
      <div class="card bg-gradient-to-br from-status-warning/20 to-status-warning/5 border-status-warning/30">
        <div class="flex items-center gap-3 mb-2">
          <i class="pi pi-shield text-status-warning text-xl" />
          <span class="text-sm text-neutral-text-secondary">总承伤</span>
        </div>
        <p class="text-2xl font-bold text-status-warning">
          {{ formatNumber(totalDamageTaken) }}
        </p>
        <p class="text-xs text-neutral-text-disabled mt-1">
          场均 {{ formatNumber(avgDamageTaken) }}
        </p>
      </div>
      <div class="card bg-gradient-to-br from-secondary/20 to-secondary/5 border-secondary/30">
        <div class="flex items-center gap-3 mb-2">
          <i class="pi pi-star text-secondary text-xl" />
          <span class="text-sm text-neutral-text-secondary">击杀数</span>
        </div>
        <p class="text-2xl font-bold text-secondary">
          {{ totalKills }}
        </p>
        <p class="text-xs text-neutral-text-disabled mt-1">
          场均 {{ avgKills }}
        </p>
      </div>
      <div class="card bg-gradient-to-br from-status-error/20 to-status-error/5 border-status-error/30">
        <div class="flex items-center gap-3 mb-2">
          <i class="pi pi-times-circle text-status-error text-xl" />
          <span class="text-sm text-neutral-text-secondary">死亡数</span>
        </div>
        <p class="text-2xl font-bold text-error">
          {{ totalDeaths }}
        </p>
        <p class="text-xs text-neutral-text-disabled mt-1">
          场均 {{ avgDeaths }}
        </p>
      </div>
    </div>

    <!-- DPS 排行榜 + 职业分布 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- DPS 排行榜前10 -->
      <div class="card lg:col-span-2">
        <h3 class="text-lg font-semibold text-neutral-text mb-4">
          <i class="pi pi-trophy text-primary mr-2" />
          DPS 排行榜 TOP10
        </h3>
        <div class="space-y-2">
          <div
            v-for="(player, idx) in topDpsPlayers"
            :key="player.instanceID"
            class="flex items-center gap-4 p-3 rounded-lg hover:bg-neutral-bg/50 transition-colors cursor-pointer"
            @click="$emit('select-player', player.instanceID)"
          >
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm"
              :class="{
                'bg-yellow-500/20 text-yellow-500': idx === 0,
                'bg-gray-400/20 text-gray-400': idx === 1,
                'bg-orange-400/20 text-orange-400': idx === 2,
                'bg-neutral-bg text-neutral-text-secondary': idx > 2
              }"
            >
              {{ idx + 1 }}
            </div>
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
              :style="{ backgroundColor: getProfessionColor(player.profession) }"
            >
              {{ player.name.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-medium text-neutral-text truncate">{{ player.name }}</span>
                <Tag
                  v-if="player.hasCommanderTag"
                  icon="pi pi-star-fill"
                  severity="warning"
                  value="指挥官"
                  class="text-xs"
                />
              </div>
              <span class="text-xs text-neutral-text-secondary">{{ player.profession }}</span>
            </div>
            <div class="text-right">
              <p class="font-semibold text-primary">
                {{ formatNumber(player.dpsAll?.[0]?.damage || 0) }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ formatNumber(player.dps || 0) }} DPS
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 职业分布 -->
      <div class="card">
        <h3 class="text-lg font-semibold text-neutral-text mb-4">
          <i class="pi pi-users text-primary mr-2" />
          职业分布
        </h3>
        <div class="space-y-3">
          <div
            v-for="(count, prof) in professionCounts"
            :key="prof"
            class="flex items-center gap-3"
          >
            <span
              class="w-3 h-3 rounded-full shrink-0"
              :style="{ backgroundColor: getProfessionColor(prof) }"
            />
            <span class="text-sm text-neutral-text flex-1">{{ prof }}</span>
            <div class="flex items-center gap-2">
              <div class="w-24 h-2 rounded-full bg-neutral-bg overflow-hidden">
                <div
                  class="h-full rounded-full transition-all"
                  :style="{ width: (count / maxProfCount * 100) + '%', backgroundColor: getProfessionColor(prof) }"
                />
              </div>
              <span class="text-sm font-semibold text-primary w-6 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Tag from 'primevue/tag';
import { formatCompactNumber as formatNumber } from '@/utils/core/helpers';
import { getProfessionColor } from '@/utils/profession/professionUtils';

const props = defineProps<{
  players: any[];
  duration: number;
}>();

defineEmits(['select-player']);

const totalDamage = computed(() => props.players.reduce((s, p) => s + (p.dpsAll?.[0]?.damage || 0), 0));
const avgDamage = computed(() => Math.round(totalDamage.value / Math.max(props.players.length, 1)));
const totalDamageTaken = computed(() => props.players.reduce((s, p) => s + (p.defenses?.[0]?.damageTaken || 0), 0));
const avgDamageTaken = computed(() => Math.round(totalDamageTaken.value / Math.max(props.players.length, 1)));
const totalKills = computed(() => props.players.reduce((s, p) => s + (p.kills || 0), 0));
const avgKills = computed(() => Math.round(totalKills.value / Math.max(props.players.length, 1) * 10) / 10);
const totalDeaths = computed(() => props.players.reduce((s, p) => s + (p.deaths || 0), 0));
const avgDeaths = computed(() => Math.round(totalDeaths.value / Math.max(props.players.length, 1) * 10) / 10);

const topDpsPlayers = computed(() => {
  return [...props.players]
    .sort((a, b) => (b.dpsAll?.[0]?.damage || 0) - (a.dpsAll?.[0]?.damage || 0))
    .slice(0, 10);
});

const professionCounts = computed(() => {
  const counts: Record<string, number> = {};
  props.players.forEach(p => {
    const prof = p.profession || 'Unknown';
    counts[prof] = (counts[prof] || 0) + 1;
  });
  return counts;
});

const maxProfCount = computed(() => {
  return Math.max(...Object.values(professionCounts.value), 1);
});
</script>
