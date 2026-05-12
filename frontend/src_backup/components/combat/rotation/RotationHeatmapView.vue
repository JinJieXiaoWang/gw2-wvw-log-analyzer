<template>
  <div class="sr-heatmap-view flex flex-col gap-2">
    <div class="heatmap-container bg-white/[0.02] rounded-lg p-3">
      <div class="heatmap-header flex justify-between items-center mb-3">
        <span class="heatmap-title text-[0.8rem] font-semibold text-[var(--color-text-primary,#f1f5f9)]">技能使用热力图</span>
        <div class="heatmap-legend flex items-center gap-2">
          <span class="legend-text text-[0.65rem] text-[var(--color-text-muted,#64748b)]">少</span>
          <div class="legend-gradient w-[60px] h-3 rounded-sm" />
          <span class="legend-text text-[0.65rem] text-[var(--color-text-muted,#64748b)]">多</span>
        </div>
      </div>
      <div class="heatmap-grid max-h-[300px] overflow-y-auto">
        <div
          v-for="(row, rowIdx) in rows"
          :key="rowIdx"
          class="heatmap-row flex items-center gap-2 mb-1"
        >
          <div class="heatmap-label w-[120px] shrink-0 text-[0.65rem] text-[var(--color-text-secondary,#94a3b8)] overflow-hidden text-ellipsis whitespace-nowrap">
            {{ row.label }}
          </div>
          <div class="heatmap-cells flex gap-px flex-1">
            <div
              v-for="(cell, colIdx) in row.cells"
              :key="colIdx"
              class="heatmap-cell flex-1 h-5 rounded-sm min-w-3 cursor-pointer transition-opacity duration-150"
              :style="{ background: getHeatmapColor(cell.count) }"
              :title="`${row.label} - ${colIdx}秒: ${cell.count}次`"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HeatmapRow } from '@/utils/combat/rotationTypes'
import { getHeatmapColor } from '@/utils/combat/rotation'

defineProps<{ rows: HeatmapRow[] }>()
</script>

<style scoped>
.legend-gradient { background: linear-gradient(90deg, rgba(148,163,184,0.1), rgba(34,211,238,0.25), rgba(34,211,238,0.5), rgba(34,211,238,0.75), rgba(34,211,238,1)); }
.heatmap-cell:hover { opacity: 0.8; }
</style>
