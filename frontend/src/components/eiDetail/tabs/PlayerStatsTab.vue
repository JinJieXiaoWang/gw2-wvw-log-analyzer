<template>
  <div class="tab-content">
    <!-- 主要数据卡片 -->
    <div class="stats-grid grid grid-cols-2 max-sm:grid-cols-1 gap-4 mb-6">
      <div class="stat-card damage flex items-center gap-3 p-4 bg-neutral-bg-secondary rounded-xl">
        <div class="stat-icon w-11 h-11 flex items-center justify-center rounded-[0.625rem] bg-[linear-gradient(135deg,#ef4444,#f97316)]">
          <i class="pi pi-bolt text-[1.375rem] text-white" />
        </div>
        <div class="stat-info flex flex-col gap-0.5">
          <span class="stat-value text-[1.375rem] font-bold text-neutral-text">{{ fmtNum(player.dpsAll?.[0]?.damage) }}</span>
          <span class="stat-label text-xs text-neutral-text-secondary">总伤害</span>
        </div>
      </div>
      <div class="stat-card dps flex items-center gap-3 p-4 bg-neutral-bg-secondary rounded-xl">
        <div class="stat-icon w-11 h-11 flex items-center justify-center rounded-[0.625rem] bg-[linear-gradient(135deg,#3b82f6,#8b5cf6)]">
          <i class="pi pi-gauge text-[1.375rem] text-white" />
        </div>
        <div class="stat-info flex flex-col gap-0.5">
          <span class="stat-value text-[1.375rem] font-bold text-neutral-text">{{ player.dps }}</span>
          <span class="stat-label text-xs text-neutral-text-secondary">DPS</span>
        </div>
      </div>
      <div class="stat-card score flex items-center gap-3 p-4 bg-neutral-bg-secondary rounded-xl">
        <div class="stat-icon w-11 h-11 flex items-center justify-center rounded-[0.625rem] bg-[linear-gradient(135deg,#f59e0b,#eab308)]">
          <i class="pi pi-trophy text-[1.375rem] text-white" />
        </div>
        <div class="stat-info flex flex-col gap-0.5">
          <span class="stat-value text-[1.375rem] font-bold text-neutral-text">{{ player.total_score }}</span>
          <span class="stat-label text-xs text-neutral-text-secondary">评分</span>
        </div>
      </div>
      <div class="stat-card hps flex items-center gap-3 p-4 bg-neutral-bg-secondary rounded-xl">
        <div class="stat-icon w-11 h-11 flex items-center justify-center rounded-[0.625rem] bg-[linear-gradient(135deg,#22c55e,#10b981)]">
          <i class="pi pi-heart text-[1.375rem] text-white" />
        </div>
        <div class="stat-info flex flex-col gap-0.5">
          <span class="stat-value text-[1.375rem] font-bold text-neutral-text">{{ player.hps || 0 }}</span>
          <span class="stat-label text-xs text-neutral-text-secondary">HPS</span>
        </div>
      </div>
    </div>

    <!-- 详细数据 -->
    <div class="detail-section mb-6 last:mb-0">
      <h4 class="section-title flex items-center gap-2 text-sm font-semibold text-neutral-text-secondary uppercase tracking-[0.05em] m-[0 0 0.875rem 0]">
        <i class="pi pi-chart-bar text-primary" />
        战斗数据详情
      </h4>
      <div class="detail-grid grid grid-cols-2 max-sm:grid-cols-1 gap-2.5">
        <div
          v-for="item in detailItems"
          :key="item.label"
          class="detail-item flex justify-between items-center p-[0.625rem 0.875rem] bg-neutral-bg-secondary rounded-lg"
        >
          <span class="detail-label text-[0.8125rem] text-neutral-text-secondary">{{ item.label }}</span>
          <span class="detail-value text-sm font-semibold text-neutral-text">{{ item.value }}</span>
        </div>
      </div>
    </div>

    <!-- 战斗状态 -->
    <div class="detail-section mb-6 last:mb-0">
      <h4 class="section-title flex items-center gap-2 text-sm font-semibold text-neutral-text-secondary uppercase tracking-[0.05em] m-[0 0 0.875rem 0]">
        <i class="pi pi-shield text-primary" />
        战斗状态
      </h4>
      <div class="status-grid grid grid-cols-4 max-sm:grid-cols-2 gap-3.5">
        <div
          v-for="s in statusItems"
          :key="s.label"
          class="status-item flex flex-col items-center gap-2.5 p-3.5 bg-neutral-bg-secondary rounded-[0.625rem]"
          :class="{ danger: s.danger }"
        >
          <i :class="[s.icon, 'text-2xl', s.danger ? 'text-status-error' : 'text-neutral-text-secondary']" />
          <div class="status-data text-center">
            <span class="status-value block text-xl font-bold" :class="s.danger ? 'text-status-error' : 'text-neutral-text'">{{ s.value }}</span>
            <span class="status-label block text-xs text-neutral-text-secondary">{{ s.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 武器配置 -->
    <div class="detail-section mb-6 last:mb-0">
      <h4 class="section-title flex items-center gap-2 text-sm font-semibold text-neutral-text-secondary uppercase tracking-[0.05em] m-[0 0 0.875rem 0]">
        <i class="pi pi-sword text-primary" />
        武器配置
      </h4>
      <div class="weapons-box p-3.5 bg-neutral-bg-secondary rounded-[0.625rem]">
        <span class="weapons-text text-sm text-neutral-text">{{ player.weapons?.join(' / ') || '未记录' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player } from '@/types/eliteInsights'

const { player } = defineProps<{
  player: Player
}>()

const fmtNum = (n?: number) => {
  const num = n || 0
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K'
  return num.toString()
}

const detailItems = computed(() => [
  { label: '直伤', value: fmtNum(player.dpsAll?.[0]?.powerDamage) },
  { label: '症状', value: fmtNum(player.dpsAll?.[0]?.condiDamage) },
  { label: '暴击率', value: (player.critRate || 0) + '%' },
  { label: '暴击伤害', value: (player.critDamage || 0) + '%' },
  { label: '精准', value: (player.precision || 0).toString() },
  { label: '威力', value: (player.power || 0).toString() },
  { label: '坚韧', value: (player.toughness || 0).toString() },
  { label: '体力', value: (player.vitality || 0).toString() },
])

const statusItems = computed(() => [
  { icon: 'pi pi-skull-crossbones', value: player.downs, label: '倒地', danger: player.downs > 0 },
  { icon: 'pi pi-heart-broken', value: player.deaths, label: '死亡', danger: player.deaths > 0 },
  { icon: 'pi pi-shield', value: player.cc, label: 'CC', danger: false },
  { icon: 'pi pi-wind', value: player.cleanses, label: '清除', danger: false },
])
</script>

