<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- 出勤趋势 -->
    <div class="card">
      <div class="flex items-center gap-2 mb-4">
        <i class="pi pi-chart-line text-primary" />
        <span class="font-semibold">出勤趋势</span>
      </div>
      <div class="h-64 flex items-center justify-center">
        <svg viewBox="0 0 400 200" class="w-full h-full">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#165DFF" />
              <stop offset="100%" stop-color="#7B61FF" />
            </linearGradient>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#165DFF" stop-opacity="0.3" />
              <stop offset="100%" stop-color="#165DFF" stop-opacity="0" />
            </linearGradient>
          </defs>
          <line x1="50" y1="30" x2="380" y2="30" stroke="#2A2A2A" stroke-width="1" />
          <line x1="50" y1="75" x2="380" y2="75" stroke="#2A2A2A" stroke-width="1" />
          <line x1="50" y1="120" x2="380" y2="120" stroke="#2A2A2A" stroke-width="1" />
          <line x1="50" y1="165" x2="380" y2="165" stroke="#2A2A2A" stroke-width="1" />
          <text x="40" y="30" fill="#909399" font-size="10" text-anchor="end">10</text>
          <text x="40" y="75" fill="#909399" font-size="10" text-anchor="end">8</text>
          <text x="40" y="120" fill="#909399" font-size="10" text-anchor="end">6</text>
          <text x="40" y="165" fill="#909399" font-size="10" text-anchor="end">4</text>
          <path :d="chartLinePath" fill="none" stroke="url(#lineGradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <path :d="chartAreaPath" fill="url(#areaGradient)" />
          <circle v-for="(point, index) in chartPoints" :key="index" :cx="point.x" :cy="point.y" r="4" fill="#165DFF" />
          <text x="80" y="185" fill="#909399" font-size="10">周һ</text>
          <text x="140" y="185" fill="#909399" font-size="10">周二</text>
          <text x="200" y="185" fill="#909399" font-size="10">周三</text>
          <text x="260" y="185" fill="#909399" font-size="10">周四</text>
          <text x="320" y="185" fill="#909399" font-size="10">周五</text>
        </svg>
      </div>
      <div class="flex items-center justify-between mt-4 text-xs text-neutral-text-secondary">
        <span>最近7天出勤记¼</span>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-primary" />
          <span>出勤次数</span>
        </div>
      </div>
    </div>

    <!-- 综合能力 -->
    <div class="card">
      <div class="flex items-center gap-2 mb-4">
        <i class="pi pi-star text-secondary" />
        <span class="font-semibold">综合能力</span>
      </div>
      <div class="h-64 flex items-center justify-center">
        <svg viewBox="0 0 200 200" class="w-full max-w-[200px]">
          <polygon v-for="level in [100, 80, 60, 40, 20]" :key="level" :points="getHexagonPoints(level)" fill="none" stroke="#2A2A2A" stroke-width="1" />
          <line v-for="i in 6" :key="'axis-' + i" x1="100" y1="100" :x2="getAxisPoint(i - 1).x" :y2="getAxisPoint(i - 1).y" stroke="#2A2A2A" stroke-width="1" />
          <polygon :points="radarPolygonPoints" fill="url(#abilityGradient)" stroke="#7B61FF" stroke-width="2" />
          <circle v-for="(point, index) in radarCirclePoints" :key="index" :cx="point.x" :cy="point.y" r="5" fill="#7B61FF" />
          <text v-for="(label, index) in radarLabels" :key="index" :x="label.x" :y="label.y" fill="#E5E5E5" font-size="11" text-anchor="middle">{{ label.text }}</text>
          <defs>
            <linearGradient id="abilityGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#7B61FF" stop-opacity="0.4" />
              <stop offset="100%" stop-color="#165DFF" stop-opacity="0.2" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <div class="grid grid-cols-3 gap-2 mt-4">
        <div class="text-center p-2 rounded-lg bg-surface-100/30">
          <p class="text-lg font-bold text-status-error">{{ abilities.damage }}</p>
          <p class="text-xs text-neutral-text-secondary">输出</p>
        </div>
        <div class="text-center p-2 rounded-lg bg-surface-100/30">
          <p class="text-lg font-bold text-status-success">{{ abilities.healing }}</p>
          <p class="text-xs text-neutral-text-secondary">治疗</p>
        </div>
        <div class="text-center p-2 rounded-lg bg-surface-100/30">
          <p class="text-lg font-bold text-secondary">{{ abilities.survival }}</p>
          <p class="text-xs text-neutral-text-secondary">生存</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  chartPoints: { x: number; y: number }[]
  chartLinePath: string
  chartAreaPath: string
  radarPolygonPoints: string
  radarCirclePoints: { x: number; y: number }[]
  radarLabels: { x: number; y: number; text: string }[]
  getHexagonPoints: (r: number) => string
  getAxisPoint: (i: number) => { x: number; y: number }
  abilities: Record<string, number>
}>()
</script>
