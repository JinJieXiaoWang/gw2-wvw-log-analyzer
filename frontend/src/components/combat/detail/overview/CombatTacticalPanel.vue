<script setup lang="ts">
import type { EiAnalysisPlayer, EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { getProfessionName, getProfessionColor } from '@/composables/combat/useCombatHelpers'
import { fmtCompact } from '@/composables/combat/useCombatHelpers'

interface Props {
  players: EiAnalysisPlayer[]
  commanders: EiAnalysisPlayer[]
  buffLeaders: Record<string, EiAnalysisPlayer[]>
  supportLeaders: Record<string, EiAnalysisPlayer[]>
  defenseLeaders: Record<string, EiAnalysisPlayer[]>
  agg: EiAnalysisAggregate
}

const props = defineProps<Props>()

const LAYER_CONFIG = {
  team: { label: '团队画像', icon: 'pi pi-users', color: 'text-info', bg: 'from-info/10 to-blue-500/10', border: 'border-info/20' },
  damage: { label: '输出分析', icon: 'pi pi-chart-line', color: 'text-primary', bg: 'from-primary/10 to-purple-500/10', border: 'border-primary/20' },
  buff: { label: '增益覆盖', icon: 'pi pi-shield', color: 'text-warning', bg: 'from-warning/10 to-amber-500/10', border: 'border-warning/20' },
  survival: { label: '生存统计', icon: 'pi pi-heart', color: 'text-status-success', bg: 'from-status-success/10 to-emerald-500/10', border: 'border-status-success/20' },
} as const

const dpsTop3 = props.players.slice().sort((a, b) => b.dps - a.dps).slice(0, 3)
const totalCasts = props.players.reduce((s, p) => s + (p.swap_count || 0), 0)
const avgMight = props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.might_uptime || 0), 0) / props.players.length) : 0
const avgFury = props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.fury_uptime || 0), 0) / props.players.length) : 0
const avgQuick = props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.quickness_uptime || 0), 0) / props.players.length) : 0
const avgAlac = props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.alacrity_uptime || 0), 0) / props.players.length) : 0
const totalDeaths = props.players.reduce((s, p) => s + (p.dead_count || 0), 0)
const totalDowns = props.players.reduce((s, p) => s + (p.down_count || 0), 0)
const avgDodge = props.players.length ? (props.players.reduce((s, p) => s + (p.dodge_count || 0), 0) / props.players.length).toFixed(1) : '0'
const totalHealing = props.players.reduce((s, p) => s + (p.healing || 0), 0)
const totalResurrects = props.players.reduce((s, p) => s + (p.resurrects || 0), 0)
</script>

<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-ai/10">
        <i class="pi pi-sitemap text-ai" />
      </div>
      战术分析面板
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Team Portrait -->
      <div class="p-4 rounded-xl border bg-gradient-to-br" :class="[LAYER_CONFIG.team.bg, LAYER_CONFIG.team.border]">
        <div class="flex items-center gap-2 mb-3">
          <i :class="[LAYER_CONFIG.team.icon, LAYER_CONFIG.team.color]" />
          <span class="text-sm font-semibold text-white">{{ LAYER_CONFIG.team.label }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">参战人数</span>
            <span class="text-white font-medium">{{ players.length }} 人</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">指挥官</span>
            <span class="text-white font-medium">{{ commanders.map(c => c.character_name).join(', ') || '无' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">平均技能施放</span>
            <span class="text-white font-medium">{{ totalCasts }} 次</span>
          </div>
        </div>
      </div>

      <!-- Damage Layer -->
      <div class="p-4 rounded-xl border bg-gradient-to-br" :class="[LAYER_CONFIG.damage.bg, LAYER_CONFIG.damage.border]">
        <div class="flex items-center gap-2 mb-3">
          <i :class="[LAYER_CONFIG.damage.icon, LAYER_CONFIG.damage.color]" />
          <span class="text-sm font-semibold text-white">{{ LAYER_CONFIG.damage.label }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">总伤害</span>
            <span class="text-primary font-medium">{{ fmtCompact(agg.total_damage) }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">直伤 / 症状 / 破蔑视</span>
            <span class="text-white font-medium">{{ fmtCompact(agg.total_power_damage) }} / {{ fmtCompact(agg.total_condi_damage) }} / {{ fmtCompact(agg.total_breakbar_damage) }}</span>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs text-neutral-text-secondary">Top DPS:</span>
            <span v-for="p in dpsTop3" :key="p.id" class="text-xs px-1.5 py-0.5 rounded bg-black/20" :style="{ color: getProfessionColor(p.profession) }">
              {{ p.character_name }} {{ fmtCompact(p.dps) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Buff Layer -->
      <div class="p-4 rounded-xl border bg-gradient-to-br" :class="[LAYER_CONFIG.buff.bg, LAYER_CONFIG.buff.border]">
        <div class="flex items-center gap-2 mb-3">
          <i :class="[LAYER_CONFIG.buff.icon, LAYER_CONFIG.buff.color]" />
          <span class="text-sm font-semibold text-white">{{ LAYER_CONFIG.buff.label }}</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">{{ avgMight }}%</div>
            <div class="text-[10px] text-neutral-text-secondary">Might</div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">{{ avgFury }}%</div>
            <div class="text-[10px] text-neutral-text-secondary">Fury</div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">{{ avgQuick }}%</div>
            <div class="text-[10px] text-neutral-text-secondary">Quickness</div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">{{ avgAlac }}%</div>
            <div class="text-[10px] text-neutral-text-secondary">Alacrity</div>
          </div>
        </div>
        <div v-if="buffLeaders && Object.keys(buffLeaders).length" class="mt-2 space-y-1">
          <div v-for="(leaders, key) in buffLeaders" :key="key" class="flex items-center gap-2 text-xs">
            <span class="text-neutral-text-secondary w-16 truncate">{{ key }}</span>
            <span class="text-white">{{ leaders.slice(0, 2).map(p => p.character_name).join(', ') }}</span>
          </div>
        </div>
      </div>

      <!-- Survival Layer -->
      <div class="p-4 rounded-xl border bg-gradient-to-br" :class="[LAYER_CONFIG.survival.bg, LAYER_CONFIG.survival.border]">
        <div class="flex items-center gap-2 mb-3">
          <i :class="[LAYER_CONFIG.survival.icon, LAYER_CONFIG.survival.color]" />
          <span class="text-sm font-semibold text-white">{{ LAYER_CONFIG.survival.label }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">死亡 / 击倒</span>
            <span class="text-error font-medium">{{ totalDeaths }} / {{ totalDowns }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">场均翻滚</span>
            <span class="text-white font-medium">{{ avgDodge }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">总治疗 / 复活</span>
            <span class="text-status-success font-medium">{{ fmtCompact(totalHealing) }} / {{ totalResurrects }}</span>
          </div>
        </div>
        <div v-if="defenseLeaders && Object.keys(defenseLeaders).length" class="mt-2 space-y-1">
          <div v-for="(leaders, key) in defenseLeaders" :key="key" class="flex items-center gap-2 text-xs">
            <span class="text-neutral-text-secondary w-16 truncate">{{ key }}</span>
            <span class="text-white">{{ leaders.slice(0, 2).map(p => p.character_name).join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
