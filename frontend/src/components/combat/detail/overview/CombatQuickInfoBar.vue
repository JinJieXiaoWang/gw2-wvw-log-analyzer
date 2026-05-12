<script setup lang="ts">
import type { EiAnalysisFight, EiAnalysisResponse, EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { fmtCompact, fmtDuration, fmtDate } from '@/composables/combat/useCombatHelpers'
import Tag from 'primevue/tag'

const props = defineProps<{
  fightSummary: EiAnalysisFight
  logDetail: Record<string, any>
  summary: EiAnalysisResponse | null
  agg: EiAnalysisAggregate
}>()
</script>

<template>
  <div
    class="card p-4 bg-gradient-to-r from-neutral-card to-neutral-bg-secondary
           border-neutral-border/50 rounded-xl">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-6">
        <div
          class="flex items-center gap-2 group cursor-pointer hover:text-primary
                 transition-colors">
          <div class="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
            <i class="pi pi-clock text-primary" />
          </div>
          <div>
            <p class="text-xs text-neutral-text-secondary">
              战斗时长
            </p>
            <p class="text-sm font-semibold text-neutral-text">
              {{ fmtDuration(props.fightSummary.duration_sec || 0) }}
            </p>
          </div>
        </div>
        <div
          class="flex items-center gap-2 group cursor-pointer hover:text-primary
                 transition-colors">
          <div class="p-2 rounded-lg bg-success/10 group-hover:bg-success/20 transition-colors">
            <i class="pi pi-users text-success" />
          </div>
          <div>
            <p class="text-xs text-neutral-text-secondary">
              参战人数
            </p>
            <p class="text-sm font-semibold text-neutral-text">
              {{ summary?.total_players || 0 }} 人
            </p>
          </div>
        </div>
        <div
          class="flex items-center gap-2 group cursor-pointer hover:text-primary
                 transition-colors">
          <div class="p-2 rounded-lg bg-info/10 group-hover:bg-info/20 transition-colors">
            <i class="pi pi-map text-info" />
          </div>
          <div>
            <p class="text-xs text-neutral-text-secondary">
              地图
            </p>
            <p class="text-sm font-semibold text-neutral-text">
              {{ fightSummary.map_name || '-' }}
            </p>
          </div>
        </div>
        <div
          class="flex items-center gap-2 group cursor-pointer hover:text-primary
                 transition-colors">
          <div class="p-2 rounded-lg bg-secondary/10 group-hover:bg-secondary/20 transition-colors">
            <i class="pi pi-calendar text-secondary" />
          </div>
          <div>
            <p class="text-xs text-neutral-text-secondary">
              上传时间
            </p>
            <p class="text-sm font-semibold text-neutral-text">
              {{ fmtDate(logDetail.upload_time) }}
            </p>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a
          v-if="summary?.dps_report_permalink"
          :href="summary.dps_report_permalink"
          target="_blank"
          class="no-underline"
        >
          <Tag
            value="EI报告"
            icon="pi pi-external-link"
            severity="info"
            class="text-xs cursor-pointer hover:bg-info/30 transition-all"
          />
        </a>
        <Tag
          :value="`击杀 ${fightSummary.kill_count || 0}`"
          severity="success"
          class="text-xs px-2 py-1"
        />
        <Tag
          :value="`死亡 ${fightSummary.death_count || 0}`"
          severity="danger"
          class="text-xs px-2 py-1"
        />
        <Tag
          v-if="agg.player_count"
          :value="`平均DPS ${fmtCompact(agg.avg_dps)}`"
          severity="info"
          class="text-xs px-2 py-1"
        />
      </div>
    </div>
  </div>
</template>
