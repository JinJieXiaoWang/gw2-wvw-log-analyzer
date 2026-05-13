<template>
  <div class="space-y-5">
    <!-- ͷ部 -->
    <div class="flex items-center gap-3">
      <div class="p-2 rounded-lg bg-yellow-500/10">
        <i class="pi pi-trophy text-yellow-500" />
      </div>
      <h3 class="text-lg font-semibold text-neutral-text">
        玩家排行 & 小队编制
      </h3>
      <BaseTag
        :value="`${data.players.length}人`"
        severity="info"
        class="text-xs"
      />
    </div>

    <!-- 主内容区 -->
    <div class="grid grid-cols-1 xl:grid-cols-5 gap-5">
      <!-- 宸︿晶锛氭帓行榜 -->
      <div class="xl:col-span-3 card rounded-xl border-neutral-border/50 overflow-hidden flex flex-col h-full">
        <div class="p-4 border-b border-neutral-border/50 flex-shrink-0">
          <h4 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
            <i class="pi pi-list text-primary" />
            排行榜
          </h4>
        </div>
        <div class="flex-1 overflow-auto">
          <DataTable
            :value="data.sortedPlayerList"
            size="small"
            class="w-full"
          >
            <Column style="min-width: 120px">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-medium text-neutral-text truncate max-w-[100px]">{{ data.character_name || data.account }}</span>
                  <BaseTag
                    v-if="data.has_commander_tag"
                    icon="pi pi-star-fill"
                    severity="warn"
                    value=""
                    class="text-[8px] w-4 h-4 p-0 flex items-center justify-center"
                  />
                </div>
              </template>
            </Column>
            <Column
              field="group_id"
              header="玩家分组"
              style="width: 60px"
            >
              <template #body="{ data }">
                <span
                  class="text-xs px-1.5 py-0.5 rounded font-medium"
                  :style="groupStyle(data.group_id)"
                >G{{ data.group_id || '-' }}</span>
              </template>
            </Column>
            <Column
              field="dps"
              header="DPS"
              style="width: 80px"
            >
              <template #body="{ data }">
                <span class="text-xs font-semibold text-primary">{{ fmtCompact(data.dps) }}</span>
              </template>
            </Column>
            <Column
              field="damage"
              header="直伤伤害"
              style="min-width: 90px"
            >
              <template #body="{ data }">
                <span class="text-xs font-bold text-neutral-text">{{ fmtCompact(data.damage) }}</span>
              </template>
            </Column>
            <Column
              field="killed"
              header="击杀"
              style="width: 50px"
            >
              <template #body="{ data }">
                <span class="text-xs font-semibold text-success">{{ data.killed || 0 }}</span>
              </template>
            </Column>
            <Column
              field="dead_count"
              header="死亡"
              style="width: 50px"
            >
              <template #body="{ data }">
                <span
                  :class="data.dead_count > 0 ? 'text-error font-semibold' : 'text-neutral-text-secondary'"
                  class="text-xs"
                >{{ data.dead_count || 0 }}</span>
              </template>
            </Column>
            <Column
              field="ai_score"
              header="评分"
              style="width: 60px"
              sortable
            >
              <template #body="{ data }">
                <span
                  class="text-xs font-bold"
                  :class="scoreValueColor(data.ai_score)"
                >{{ data.ai_score != null ? data.ai_score.toFixed(1) : '-' }}</span>
              </template>
            </Column>
            <Column
              field="score_grade"
              header="等级"
              style="width: 50px"
            >
              <template #body="{ data }">
                <BaseTag
                  :value="data.score_grade || '-'"
                  :severity="scoreSeverity(data.score_grade)"
                  class="text-[10px] px-1"
                />
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="xl:col-span-2">
        <SquadRoster
          :commanders="data.commanders"
          :groups="data.groups"
          :ungrouped="data.ungrouped"
          @player-click="emit('player-click', $event)"
        />
      </div>
    </div>

    <!-- 敌方目标 -->
    <div
      v-if="data.enemyPlayers.length"
      class="card p-4 rounded-xl border-error/20 bg-error/5"
    >
      <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
        <div class="p-1 rounded bg-error/20">
          <i class="pi pi-exclamation-triangle text-error text-xs" />
        </div>
        敌方目标 ({{ data.enemyPlayers.length }})
      </h4>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="p in data.enemyPlayers.slice(0, 10)"
          :key="p.id"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-error/10 border border-error/20"
        >
          <img
            :src="getProfessionIconUrl(p.profession)"
            class="w-6 h-6 rounded-full border border-error/30"
          >
          <span class="text-xs text-neutral-text">{{ p.character_name || 'δ֪' }}</span>
          <span class="text-[10px] text-error font-semibold">{{ fmtCompact(p.damage) }}</span>
        </div>
        <div
          v-if="data.enemyPlayers.length > 10"
          class="flex items-center px-3 py-1.5 text-xs text-neutral-text-secondary"
        >
          +{{ data.enemyPlayers.length - 10 }} 更多
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionColor, getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { rankClass, groupColor, scoreValueColor, scoreSeverity } from '@/utils/combat/combatFormatters'
import SquadRoster from './SquadRoster.vue'
import type { EiAnalysisGroup, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

interface SquadData {
  players: EiAnalysisPlayer[]
  sortedPlayerList: EiAnalysisPlayer[]
  commanders: EiAnalysisPlayer[]
  groups: EiAnalysisGroup[]
  ungrouped: EiAnalysisPlayer[]
  enemyPlayers: EiAnalysisPlayer[]
}

const props = defineProps<{ data: SquadData }>()
const emit = defineEmits<{
  'row-click': [event: any]
  'player-click': [player: EiAnalysisPlayer]
}>()

function profStyle(prof: string) {
  const c = getProfessionColor(prof)
  return { backgroundColor: c + '20', color: c }
}

function groupStyle(id: number) {
  const c = groupColor(id)
  return { backgroundColor: c + '20', color: c }
}
</script>
