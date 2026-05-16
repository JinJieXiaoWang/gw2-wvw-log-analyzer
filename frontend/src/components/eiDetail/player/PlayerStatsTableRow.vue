<template>
  <tr
    class="player-row"
    :class="{ selected: selectedId === player.instanceID, commander: player.hasCommanderTag }"
    @click="$emit('select-player', player.instanceID)"
  >
    <td class="rank-col">
      <span class="rank-badge" :class="getRankClass(index)">{{ index + 1 }}</span>
    </td>
    <td class="player-col">
      <div class="player-info">
        <img
          :src="getIconUrl(player.profession)"
          :alt="player.profession"
          class="prof-icon"
          @error="handleIconError($event)"
        >
        <div class="player-name-group">
          <span class="player-name">
            {{ player.name }}
            <span v-if="player.hasCommanderTag" class="commander-tag"><i class="pi pi-star-fill" /></span>
          </span>
          <span class="account-name">{{ player.account }}</span>
        </div>
      </div>
    </td>
    <td class="prof-col">
      <span class="prof-name" :style="{ backgroundColor: getColor(player.profession) }">
        {{ getName(player.profession) }}
      </span>
    </td>
    <td class="score-col"><span class="score-value">{{ player.total_score }}</span></td>
    <td class="dmg-col"><span class="damage-value">{{ formatDamage(getPlayerDamage(player)) }}</span></td>
    <td class="dps-col"><span class="dps-value">{{ player.dps }}</span></td>
    <td class="power-col"><span class="power-value">{{ formatDamage(getPlayerPowerDamage(player)) }}</span></td>
    <td class="condi-col"><span class="condi-value">{{ formatDamage(getPlayerCondiDamage(player)) }}</span></td>
    <td class="cc-col"><span class="cc-value">{{ player.cc || 0 }}</span></td>
    <td class="down-col"><span class="down-value">{{ player.downs || 0 }}</span></td>
    <td class="death-col"><span class="death-value">{{ player.deaths || 0 }}</span></td>
    <td class="actions-col">
      <BaseButton size="small" icon="pi pi-eye" @click.stop="$emit('select-player', player.instanceID)" />
    </td>
  </tr>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { useProfession } from '@/composables/useProfession'
import { getProfessionName } from '@/services/professionService'
import type { Player } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'

interface Props {
  player: Player
  index: number
  selectedId: number | null
}
defineProps<Props>()
defineEmits<{
  (e: 'select-player', instanceId: number): void
}>()

const { professions, eliteSpecs } = useProfession()

function getPlayerDamage(player: Player): number {
  return player.dpsAll?.[0]?.damage || 0
}
function getPlayerPowerDamage(player: Player): number {
  return player.dpsAll?.[0]?.powerDamage || 0
}
function getPlayerCondiDamage(player: Player): number {
  return player.dpsAll?.[0]?.condiDamage || 0
}
function getRankClass(index: number): string {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}
function handleIconError(event: Event): void {
  const target = event.target as HTMLImageElement
  target.src = ''
}
function getName(key: string): string {
  return getProfessionName(key)
}
function getColor(key: string): string {
  if (!key) return '#6b7280'
  const profession = professions.find(p => p.profession_key === key)
  if (profession?.color) return profession.color
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec?.color) return spec.color
  return '#6b7280'
}
function getIconUrl(key: string): string {
  if (!key) return ''
  const profession = professions.find(p => p.profession_key === key)
  if (profession?.icon) {
    try { return new URL(`/src/assets/images/prof/${profession.icon}`, import.meta.url).href }
    catch (error) { console.error(`[PlayerStatsTableRow] 加载职业图标失败: ${key}`, error) }
  }
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec?.icon) {
    try { return new URL(`/src/assets/images/prof/${spec.icon}`, import.meta.url).href }
    catch (error) { console.error(`[PlayerStatsTableRow] 加载精英特长图标失败: ${key}`, error) }
  }
  return ''
}
</script>

<style scoped lang="css">
.player-row {
  border-bottom: 1px solid var(--color-border-light);
  transition: background-color 0.2s ease;
}
.player-row:hover { background-color: var(--color-hover); }
.player-row.selected { background-color: var(--color-selected); }
.player-row.commander { background-color: rgba(255, 193, 7, 0.1); }
td { padding: var(--spacing-md); font-size: var(--font-size-sm); }
.rank-col { width: 48px; }
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 600;
  font-size: var(--font-size-xs);
  background-color: var(--color-border);
  color: var(--color-text-secondary);
}
.rank-badge.gold { background-color: #ffc107; color: #1a1a2e; }
.rank-badge.silver { background-color: #9e9e9e; color: #1a1a2e; }
.rank-badge.bronze { background-color: #795548; color: #fff; }
.player-col { min-width: 200px; }
.player-info { display: flex; align-items: center; gap: var(--spacing-md); }
.prof-icon { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; background-color: var(--color-border); }
.player-name-group { display: flex; flex-direction: column; }
.player-name { font-weight: 500; color: var(--color-text-primary); display: flex; align-items: center; gap: var(--spacing-xs); }
.commander-tag { color: #ffc107; }
.account-name { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.prof-col { width: 100px; }
.prof-name {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
.score-col, .dps-col, .dmg-col, .power-col, .condi-col, .cc-col, .down-col, .death-col { text-align: right; }
.score-value { font-weight: 600; color: var(--color-primary); }
.damage-value, .dps-value, .power-value, .condi-value { font-weight: 500; color: var(--color-text-primary); }
.cc-value, .down-value, .death-value { color: var(--color-text-secondary); }
.actions-col { width: 48px; text-align: center; }
</style>
