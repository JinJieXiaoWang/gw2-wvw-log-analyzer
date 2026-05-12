<template>
  <div class="card rounded-xl border-neutral-border/50 overflow-hidden flex flex-col h-full">
    <div class="p-4 border-b border-neutral-border/50 flex-shrink-0">
      <h4 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
        <i class="pi pi-list text-primary" />
        玩家排行榜
      </h4>
    </div>
    <div class="flex-1 overflow-hidden">
      <DataTable
        :value="sortedPlayerList"
        :virtualScrollerOptions="{ itemSize: 48 }"
        scrollable
        scrollHeight="calc(100vh - 320px)"
        class="w-full cursor-pointer"
        striped-rows
        @row-click="$emit('row-click', $event)"
      >
        <Column
          field="rank"
          header="#"
          style="width: 50px"
        >
          <template #body="{ index }">
            <span
              class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold"
              :class="rankClass(index)"
            >{{ index + 1 }}</span>
          </template>
        </Column>
        <Column
          field="profession"
          header="职业"
          style="min-width: 90px"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <img
                :src="getProfessionIconUrl(data.profession)"
                class="w-6 h-6 rounded-full"
                :alt="getProfessionName(data.profession)"
              >
              <span
                class="text-xs"
                :style="{ backgroundColor: getProfessionColor(data.profession) + '20', color: getProfessionColor(data.profession) }"
              >{{ getProfessionName(data.profession) }}</span>
            </div>
          </template>
        </Column>
        <Column
          field="name"
          header="玩家"
          style="min-width: 120px"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <span class="text-xs font-medium text-neutral-text truncate max-w-[100px]">{{ data.character_name || data.account }}</span>
              <Tag
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
          header="小队"
          style="width: 60px"
        >
          <template #body="{ data }">
            <span
              class="text-xs px-1.5 py-0.5 rounded font-medium"
              :style="{ backgroundColor: groupColor(data.group_id) + '20', color: groupColor(data.group_id) }"
            >
              G{{ data.group_id || '-' }}
            </span>
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
          header="伤害"
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
            >
              {{ data.ai_score != null ? data.ai_score.toFixed(1) : '-' }}
            </span>
          </template>
        </Column>
        <Column
          field="score_grade"
          header="等级"
          style="width: 50px"
        >
          <template #body="{ data }">
            <Tag
              :value="data.score_grade || '-'"
              :severity="scoreSeverity(data.score_grade)"
              class="text-[10px] px-1"
            />
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { fmtCompact, groupColor, rankClass, scoreSeverity, scoreValueColor } from '@/composables/combat/useCombatHelpers'
import { useProfessionHelpers } from '@/composables/useProfession'

const { getProfessionName, getProfessionColor, getProfessionIconUrl } = useProfessionHelpers()

defineProps<{
  sortedPlayerList: EiAnalysisPlayer[]
}>()

defineEmits<{
  'row-click': [event: any]
}>()
</script>
