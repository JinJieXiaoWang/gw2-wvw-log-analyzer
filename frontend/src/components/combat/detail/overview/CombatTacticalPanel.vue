<script setup lang="ts">
import { fmtCompact } from '@/composables/combat/useCombatHelpers'
import type { EiAnalysisAggregate, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { TACTICAL_LAYER_STYLES, TACTICAL_DISPLAY_LIMITS, TACTICAL_LABEL_MAP } from '@/config/tacticalPanelConfig'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

/** 职业到Tailwind颜色类的映射（消除 :style 违规） */
const PROFESSION_TEXT_COLOR_MAP: Record<string, string> = {
  Dragonhunter: 'text-amber-400',
  Firebrand: 'text-orange-400',
  Willbender: 'text-orange-400',
  Luminary: 'text-amber-300',
  Berserker: 'text-orange-600',
  Spellbreaker: 'text-orange-400',
  Bladesworn: 'text-orange-300',
  Paragon: 'text-orange-400',
  Scrapper: 'text-amber-800',
  Holosmith: 'text-amber-700',
  Mechanist: 'text-stone-400',
  Amalgam: 'text-stone-300',
  Druid: 'text-green-500',
  Soulbeast: 'text-green-400',
  Untamed: 'text-green-300',
  Galeshot: 'text-green-200',
  Daredevil: 'text-slate-500',
  Deadeye: 'text-slate-400',
  Specter: 'text-slate-300',
  Antiquary: 'text-slate-300',
  Tempest: 'text-pink-600',
  Weaver: 'text-pink-500',
  Catalyst: 'text-pink-400',
  Evoker: 'text-pink-300',
  Chronomancer: 'text-purple-600',
  Mirage: 'text-purple-500',
  Virtuoso: 'text-purple-400',
  Troubadour: 'text-purple-300',
  Reaper: 'text-cyan-500',
  Scourge: 'text-cyan-400',
  Harbinger: 'text-cyan-300',
  Ritualist: 'text-cyan-200',
  Herald: 'text-indigo-700',
  Renegade: 'text-indigo-400',
  Vindicator: 'text-indigo-300',
  Conduit: 'text-indigo-200',
}

interface Props {
  players: EiAnalysisPlayer[]
  commanders: EiAnalysisPlayer[]
  buffLeaders: Record<string, EiAnalysisPlayer[]>
  supportLeaders: Record<string, EiAnalysisPlayer[]>
  defenseLeaders: Record<string, EiAnalysisPlayer[]>
  agg: EiAnalysisAggregate
  leaderLabels?: Record<string, string>
}

const props = defineProps<Props>()

const { t } = useI18n()

const getLabel = (key: string): string => {
  return props.leaderLabels?.[key] || t(TACTICAL_LABEL_MAP[key] as string) || key
}

// ========== 计算属性（替代原脚本顶层计算，确保响应式）==========

const dpsTopN = computed(() =>
  props.players.slice().sort((a, b) => b.dps - a.dps).slice(0, TACTICAL_DISPLAY_LIMITS.topDpsCount)
)

/** 武器切换次数（修复字段名与标签不匹配问题） */
const totalWeaponSwaps = computed(() =>
  props.players.reduce((s, p) => s + (p.swap_count || 0), 0)
)

const avgMight = computed(() =>
  props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.might_uptime || 0), 0) / props.players.length) : 0
)
const avgFury = computed(() =>
  props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.fury_uptime || 0), 0) / props.players.length) : 0
)
const avgQuick = computed(() =>
  props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.quickness_uptime || 0), 0) / props.players.length) : 0
)
const avgAlac = computed(() =>
  props.players.length ? Math.round(props.players.reduce((s, p) => s + (p.alacrity_uptime || 0), 0) / props.players.length) : 0
)
const totalDeaths = computed(() =>
  props.players.reduce((s, p) => s + (p.dead_count || 0), 0)
)
const totalDowns = computed(() =>
  props.players.reduce((s, p) => s + (p.down_count || 0), 0)
)

/** 平均闪避次数（修复类型：返回 number，模板中格式化） */
const avgDodge = computed(() =>
  props.players.length
    ? props.players.reduce((s, p) => s + (p.dodge_count || 0), 0) / props.players.length
    : 0
)

const totalHealing = computed(() =>
  props.players.reduce((s, p) => s + (p.healing || 0), 0)
)
const totalResurrects = computed(() =>
  props.players.reduce((s, p) => s + (p.resurrects || 0), 0)
)
</script>

<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-ai/10">
        <i class="pi pi-sitemap text-ai" />
      </div>
      {{ t('tactical.panelTitle') }}
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Team Portrait -->
      <div
        class="p-4 rounded-xl border bg-gradient-to-br from-info/10 to-blue-500/10 border-info/20"
      >
        <div class="flex items-center gap-2 mb-3">
          <i class="pi pi-users text-info" />
          <span class="text-sm font-semibold text-white">{{ t('tactical.layers.team') }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.playerCount') }}</span>
            <span class="text-white font-medium">{{ players.length }} {{ t('tactical.units.person') }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.commander') }}</span>
            <span class="text-white font-medium">{{ commanders.map(c => c.character_name).join(', ') || t('tactical.labels.noCommander') }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.weaponSwapCount') }}</span>
            <span class="text-white font-medium">{{ totalWeaponSwaps }} {{ t('tactical.units.times') }}</span>
          </div>
        </div>
      </div>

      <!-- Damage Layer -->
      <div
        class="p-4 rounded-xl border bg-gradient-to-br from-primary/10 to-purple-500/10 border-primary/20"
      >
        <div class="flex items-center gap-2 mb-3">
          <i class="pi pi-chart-line text-primary" />
          <span class="text-sm font-semibold text-white">{{ t('tactical.layers.damage') }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.totalDamage') }}</span>
            <span class="text-primary font-medium">{{ fmtCompact(agg.total_damage) }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.damageBreakdown') }}</span>
            <span class="text-white font-medium">{{ fmtCompact(agg.total_power_damage) }} / {{ fmtCompact(agg.total_condi_damage) }} / {{ fmtCompact(agg.total_breakbar_damage) }}</span>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs text-neutral-text-secondary">{{ t('tactical.labels.topDps') }}:</span>
            <span
              v-for="p in dpsTopN"
              :key="p.id"
              class="text-xs px-1.5 py-0.5 rounded bg-black/20"
              :class="PROFESSION_TEXT_COLOR_MAP[p.profession] || 'text-neutral-text'"
            >
              {{ p.character_name }} {{ fmtCompact(p.dps) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Buff Layer -->
      <div
        class="p-4 rounded-xl border bg-gradient-to-br from-warning/10 to-amber-500/10 border-warning/20"
      >
        <div class="flex items-center gap-2 mb-3">
          <i class="pi pi-shield text-warning" />
          <span class="text-sm font-semibold text-white">{{ t('tactical.layers.buff') }}</span>
        </div>
        <!-- 响应式Buff网格：从2列到4列自适应 -->
        <div
          class="grid gap-2"
          style="grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));"
        >
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">
              {{ avgMight }}%
            </div>
            <div class="text-[10px] text-neutral-text-secondary">
              {{ getLabel('might') }}
            </div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">
              {{ avgFury }}%
            </div>
            <div class="text-[10px] text-neutral-text-secondary">
              {{ getLabel('fury') }}
            </div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">
              {{ avgQuick }}%
            </div>
            <div class="text-[10px] text-neutral-text-secondary">
              {{ getLabel('quickness') }}
            </div>
          </div>
          <div class="text-center p-2 bg-black/20 rounded-lg">
            <div class="text-lg font-bold text-warning">
              {{ avgAlac }}%
            </div>
            <div class="text-[10px] text-neutral-text-secondary">
              {{ getLabel('alacrity') }}
            </div>
          </div>
        </div>
        <div
          v-if="buffLeaders && Object.keys(buffLeaders).length"
          class="mt-2 space-y-1"
        >
          <div
            v-for="(leaders, key) in buffLeaders"
            :key="key"
            class="flex items-center gap-2 text-xs"
          >
            <span class="text-neutral-text-secondary w-16 truncate">{{ getLabel(key) }}</span>
            <span class="text-white">{{ leaders.slice(0, TACTICAL_DISPLAY_LIMITS.maxLeadersDisplay).map(p => p.character_name).join(', ') }}</span>
          </div>
        </div>
      </div>

      <!-- Survival Layer -->
      <div
        class="p-4 rounded-xl border bg-gradient-to-br from-status-success/10 to-emerald-500/10 border-status-success/20"
      >
        <div class="flex items-center gap-2 mb-3">
          <i class="pi pi-heart text-status-success" />
          <span class="text-sm font-semibold text-white">{{ t('tactical.layers.survival') }}</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.deathDowned') }}</span>
            <span class="text-error font-medium">{{ totalDeaths }} / {{ totalDowns }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.avgDodge') }}</span>
            <span class="text-white font-medium">{{ avgDodge.toFixed(1) }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-neutral-text-secondary">{{ t('tactical.labels.totalHealingRes') }}</span>
            <span class="text-status-success font-medium">{{ fmtCompact(totalHealing) }} / {{ totalResurrects }}</span>
          </div>
        </div>
        <div
          v-if="defenseLeaders && Object.keys(defenseLeaders).length"
          class="mt-2 space-y-1"
        >
          <div
            v-for="(leaders, key) in defenseLeaders"
            :key="key"
            class="flex items-center gap-2 text-xs"
          >
            <span class="text-neutral-text-secondary w-16 truncate">{{ getLabel(key) }}</span>
            <span class="text-white">{{ leaders.slice(0, TACTICAL_DISPLAY_LIMITS.maxLeadersDisplay).map(p => p.character_name).join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
