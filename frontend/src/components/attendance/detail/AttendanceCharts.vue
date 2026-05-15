<template>
  <div class="container mx-auto px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 出勤趋势图 -->
      <div class="lg:col-span-2 card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
        <div class="card-header flex items-center justify-between p-4 border-b border-neutral-border/20">
          <div class="flex items-center gap-2">
            <i class="pi pi-chart-line text-primary text-lg" />
            <h3 class="font-semibold text-neutral-text">
              出勤趋势
            </h3>
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">最近7天</span>
          </div>
          <Dropdown
            v-model="timeRange"
            :options="timeRangeOptions"
            option-label="label"
            option-value="value"
            class="w-32"
            placeholder="时间范围"
            @change="emit('timeRangeChange', timeRange)"
          />
        </div>
        <div class="card-body p-4">
          <div class="h-64 flex items-center justify-center">
            <svg
              viewBox="0 0 600 250"
              class="w-full h-full"
            >
              <defs>
                <linearGradient
                  id="trendLineGradient"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop
                    offset="0%"
                    stop-color="#165DFF"
                  />
                  <stop
                    offset="100%"
                    stop-color="#7B61FF"
                  />
                </linearGradient>
                <linearGradient
                  id="trendAreaGradient"
                  x1="0%"
                  y1="0%"
                  x2="0%"
                  y2="100%"
                >
                  <stop
                    offset="0%"
                    stop-color="#165DFF"
                    stop-opacity="0.25"
                  />
                  <stop
                    offset="100%"
                    stop-color="#165DFF"
                    stop-opacity="0"
                  />
                </linearGradient>
              </defs>
              <line
                v-for="i in 5"
                :key="'h-' + i"
                x1="60"
                :y1="30 + i * 44"
                x2="560"
                :y2="30 + i * 44"
                stroke="#2A2A2A"
                stroke-width="1"
                stroke-dasharray="4"
              />
              <line
                v-for="i in 7"
                :key="'v-' + i"
                :x1="60 + i * 80"
                y1="30"
                :x2="60 + i * 80"
                y2="220"
                stroke="#2A2A2A"
                stroke-width="1"
                stroke-dasharray="4"
              />
              <text
                x="50"
                y="35"
                fill="#909399"
                font-size="11"
                text-anchor="end"
              >10</text>
              <text
                x="50"
                y="79"
                fill="#909399"
                font-size="11"
                text-anchor="end"
              >8</text>
              <text
                x="50"
                y="123"
                fill="#909399"
                font-size="11"
                text-anchor="end"
              >6</text>
              <text
                x="50"
                y="167"
                fill="#909399"
                font-size="11"
                text-anchor="end"
              >4</text>
              <text
                x="50"
                y="211"
                fill="#909399"
                font-size="11"
                text-anchor="end"
              >2</text>
              <path
                :d="chartAreaPath"
                fill="url(#trendAreaGradient)"
              />
              <path
                :d="chartLinePath"
                fill="none"
                stroke="url(#trendLineGradient)"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <g
                v-for="(point, index) in chartPoints"
                :key="index"
              >
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="6"
                  fill="#165DFF"
                  stroke="#fff"
                  stroke-width="2"
                />
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="3"
                  fill="#fff"
                />
              </g>
              <text
                x="100"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周一</text>
              <text
                x="180"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周二</text>
              <text
                x="260"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周三</text>
              <text
                x="340"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周四</text>
              <text
                x="420"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周五</text>
              <text
                x="500"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周六</text>
              <text
                x="580"
                y="245"
                fill="#909399"
                font-size="11"
                text-anchor="middle"
              >周日</text>
            </svg>
          </div>
          <div class="flex items-center justify-between mt-4 px-2">
            <span class="text-xs text-neutral-text-secondary">出勤次数统计</span>
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-primary" />
              <span class="text-xs text-neutral-text-secondary">出勤次数</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 雷达图 -->
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Dropdown from 'primevue/dropdown'
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail'

const { detailData } = defineProps<{
  detailData: any
}>()
const emit = defineEmits(['timeRangeChange'])

const timeRange = ref('7d')
import { TIME_RANGE_OPTIONS_NO_ALL } from '@/constants/options'
const timeRangeOptions = TIME_RANGE_OPTIONS_NO_ALL

const {
  abilities, abilityEntries, chartPoints, chartLinePath, chartAreaPath,
  radarPolygonPoints, radarCirclePoints, radarLabels,
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
