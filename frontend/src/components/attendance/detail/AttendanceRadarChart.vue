<template>
  <div class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
    <div class="card-header flex items-center gap-2 p-4 border-b border-neutral-border/20">
      <i class="pi pi-star text-secondary text-lg" />
      <h3 class="font-semibold text-neutral-text">
        综合能力
      </h3>
    </div>
    <div class="card-body p-4">
      <div class="h-64 flex items-center justify-center">
        <svg
          viewBox="0 0 200 200"
          class="w-full max-w-[180px]"
        >
          <defs>
            <linearGradient
              id="abilityGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop
                offset="0%"
                stop-color="#7B61FF"
                stop-opacity="0.4"
              />
              <stop
                offset="100%"
                stop-color="#165DFF"
                stop-opacity="0.2"
              />
            </linearGradient>
          </defs>
          <polygon
            v-for="level in [90, 72, 54, 36, 18]"
            :key="level"
            :points="getHexagonPoints(level)"
            fill="none"
            stroke="#2A2A2A"
            stroke-width="1"
          />
          <line
            v-for="i in 6"
            :key="'axis-' + i"
            x1="100"
            y1="100"
            :x2="getAxisPoint(i - 1).x"
            :y2="getAxisPoint(i - 1).y"
            stroke="#2A2A2A"
            stroke-width="1"
          />
          <polygon
            :points="radarPolygonPoints"
            fill="url(#abilityGradient)"
            stroke="#7B61FF"
            stroke-width="2"
          />
          <circle
            v-for="(point, index) in radarCirclePoints"
            :key="index"
            :cx="point.x"
            :cy="point.y"
            r="5"
            fill="#7B61FF"
            stroke="#fff"
            stroke-width="2"
          />
          <text
            v-for="(label, index) in radarLabels"
            :key="index"
            :x="label.x"
            :y="label.y"
            fill="#E5E5E5"
            font-size="11"
            text-anchor="middle"
          >{{ label.text }}</text>
        </svg>
      </div>
      <div class="grid grid-cols-3 gap-2 mt-4">
        <div
          v-for="entry in abilityEntries.slice(0, 6)"
          :key="entry.key"
          class="text-center p-2 rounded-xl bg-surface-700/50"
        >
          <p
            class="text-lg font-bold"
            :class="getAbilityColorClass(entry.key)"
          >
            {{ entry.value }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ entry.label }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail'

const { detailData } = defineProps<{
  detailData: any
}>()

const {
  abilityEntries, radarPolygonPoints, radarCirclePoints, radarLabels,
  getHexagonPoints, getAxisPoint,
} = useAttendanceDetail(() => detailData)

const getAbilityColorClass = (key: string): string => {
  const map: Record<string, string> = {
    damage: 'text-status-error',
    healing: 'text-status-success',
    survival: 'text-secondary',
    support: 'text-status-success',
    utility: 'text-primary',
    mobility: 'text-info-500',
  }
  return map[key] || 'text-neutral-text'
}
</script>
