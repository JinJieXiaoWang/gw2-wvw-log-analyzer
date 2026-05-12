<template>
  <div class="space-y-4">
    <!-- 指挥官 -->
    <div
      class="card p-4 rounded-xl border-yellow-500/20 bg-gradient-to-br
             from-yellow-500/5 to-transparent">
      <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
        <div class="p-1 rounded bg-yellow-500/20">
          <i class="pi pi-star-fill text-yellow-500 text-xs" />
        </div>
        指挥官 ({{ commanders.length }})
      </h4>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="cmd in commanders"
          :key="cmd.id"
            class="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/10 border
                   border-yellow-500/30 hover:border-yellow-500/50 transition-all
                   cursor-pointer"
          @click="emit('player-click', cmd)"
        >
          <img
            :src="getProfessionIconUrl(cmd.profession)"
            class="w-8 h-8 rounded-full border border-yellow-500/50"
          >
          <div class="min-w-0">
            <p class="text-xs font-semibold text-neutral-text truncate max-w-[80px]">
              {{ cmd.character_name || cmd.account }}
            </p>
            <p class="text-[10px] text-yellow-500/80">
              {{ getProfessionName(cmd.profession) }}
            </p>
          </div>
        </div>
        <div
          v-if="commanders.length === 0"
            class="flex items-center gap-2 text-neutral-text-secondary text-xs px-3 py-2
                   rounded-lg bg-neutral-bg-secondary"
        >
          <i class="pi pi-info-circle" /><span>无指挥官</span>
        </div>
      </div>
    </div>

    <!-- 玩家分组列表 -->
    <div class="space-y-3">
      <div
        v-for="g in groups"
        :key="g.id"
        class="card p-3 rounded-xl border transition-all cursor-pointer"
        :style="{ borderColor: groupColor(g.id) + '40', backgroundColor: groupColor(g.id) + '08' }"
        @click="toggleGroup(g.id)"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                     text-white"
              :style="{ backgroundColor: groupColor(g.id) }"
            >{{ g.id || '?' }}</span>
            <span class="text-sm font-semibold text-neutral-text">玩家分组 {{ g.id || '无分组' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :style="{ backgroundColor: groupColor(g.id) + '20', color: groupColor(g.id) }"
            >{{ g.players.length }}人</span>
            <i
              :class="expandedId === g.id ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              class="text-neutral-text-secondary text-xs"
            />
          </div>
        </div>
        <div class="flex flex-wrap gap-1 mb-2">
          <div
            v-for="p in g.players.slice(0, 5)"
            :key="p.id"
            class="relative"
          >
            <img
              :src="getProfessionIconUrl(p.profession)"
              class="w-6 h-6 rounded-full border"
              :style="{ borderColor: groupColor(g.id) + '60' }"
              :title="p.character_name || p.account"
            >
            <div
              v-if="p.has_commander_tag"
                class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-yellow-500 rounded-full flex
                       items-center justify-center"
            >
              <i class="pi pi-star-fill text-[6px] text-yellow-900" />
            </div>
          </div>
          <div
            v-if="g.players.length > 5"
              class="w-6 h-6 rounded-full bg-neutral-bg flex items-center justify-center
                     text-[10px] text-neutral-text-secondary"
          >
            +{{ g.players.length - 5 }}
          </div>
        </div>
        <div
          v-show="expandedId === g.id"
          class="pt-2 border-t border-neutral-border/30 space-y-2"
        >
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-text-secondary">总伤害</span><span class="font-semibold text-primary">{{ fmtCompact(g.total_damage) }}</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-text-secondary">平均DPS</span><span class="font-semibold text-neutral-text">{{ fmtCompact(g.avg_dps) }}</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-text-secondary">平均评分</span><span
              class="font-semibold"
              :class="scoreValueColor(g.avg_score)"
            >{{ g.avg_score?.toFixed(1) ?? '-' }}</span>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-text-secondary">总击倒</span><span class="font-semibold text-warning">{{ g.total_downed }}</span>
          </div>
        </div>
      </div>

      <!-- 未分组玩家 -->
      <div
        v-if="ungrouped.length > 0"
        class="card p-3 rounded-xl border border-dashed border-neutral-border/50"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                     bg-neutral-bg text-neutral-text-secondary">?</span>
            <span class="text-sm font-semibold text-neutral-text-secondary">未分组玩家 ({{ ungrouped.length }})</span>
          </div>
        </div>
        <div class="flex flex-wrap gap-1">
          <div
            v-for="p in ungrouped.slice(0, 8)"
            :key="p.id"
            class="relative"
          >
            <img
              :src="getProfessionIconUrl(p.profession)"
                class="w-6 h-6 rounded-full border border-neutral-border/50 cursor-pointer
                       hover:border-primary/50 transition-colors"
              @click.stop="emit('player-click', p)"
            >
            <div
              v-if="p.has_commander_tag"
                class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-yellow-500 rounded-full flex
                       items-center justify-center"
            >
              <i class="pi pi-star-fill text-[6px] text-yellow-900" />
            </div>
          </div>
          <div
            v-if="ungrouped.length > 8"
              class="w-6 h-6 rounded-full bg-neutral-bg flex items-center justify-center
                     text-[10px] text-neutral-text-secondary"
          >
            +{{ ungrouped.length - 8 }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 小队花名册组件
 * 功能：展示指挥官列表和玩家分组信息
 * 更新：2026-05-12 - 使用后端预计算数据，移除前端计算逻辑
 */
import type { EiAnalysisGroup, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { groupColor, scoreValueColor } from '@/utils/combat/combatFormatters'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionIconUrl, getProfessionName } from '@/utils/profession/professionUtils'
import { ref } from 'vue'

interface Props {
  commanders: EiAnalysisPlayer[]
  groups: EiAnalysisGroup[]
  ungrouped: EiAnalysisPlayer[]
}

defineProps<Props>()
const emit = defineEmits<{ 'player-click': [player: EiAnalysisPlayer] }>()

const expandedId = ref<number | null>(null)

const toggleGroup = (id: number) => {
  expandedId.value = expandedId.value === id ? null : id
}
</script>
