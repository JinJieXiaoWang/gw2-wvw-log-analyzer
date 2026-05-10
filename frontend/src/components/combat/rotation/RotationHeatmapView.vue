<template>
  <div class="sr-heatmap-view">
    <div class="heatmap-container">
      <div class="heatmap-header">
        <span class="heatmap-title">技能使用热力ͼ</span>
        <div class="heatmap-legend">
          <span class="legend-text">少</span>
          <div class="legend-gradient" />
          <span class="legend-text">多</span>
        </div>
      </div>
      <div class="heatmap-grid">
        <div v-for="(row, rowIdx) in rows" :key="rowIdx" class="heatmap-row">
          <div class="heatmap-label">{{ row.label }}</div>
          <div class="heatmap-cells">
            <div
              v-for="(cell, colIdx) in row.cells"
              :key="colIdx"
              class="heatmap-cell"
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
.sr-heatmap-view { display: flex; flex-direction: column; gap: 0.5rem; }
.heatmap-container { background: rgba(255,255,255,0.02); border-radius: 0.5rem; padding: 0.75rem; }
.heatmap-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.heatmap-title { font-size: 0.8rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); }
.heatmap-legend { display: flex; align-items: center; gap: 0.5rem; }
.legend-text { font-size: 0.65rem; color: var(--color-text-muted, #64748b); }
.legend-gradient { width: 60px; height: 12px; border-radius: 0.25rem; background: linear-gradient(90deg, rgba(148,163,184,0.1), rgba(34,211,238,0.25), rgba(34,211,238,0.5), rgba(34,211,238,0.75), rgba(34,211,238,1)); }
.heatmap-grid { max-height: 300px; overflow-y: auto; }
.heatmap-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.heatmap-label { width: 120px; flex-shrink: 0; font-size: 0.65rem; color: var(--color-text-secondary, #94a3b8); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.heatmap-cells { display: flex; gap: 1px; flex: 1; }
.heatmap-cell { flex: 1; height: 20px; border-radius: 2px; min-width: 12px; cursor: pointer; transition: opacity 0.15s; }
.heatmap-cell:hover { opacity: 0.8; }
</style>
