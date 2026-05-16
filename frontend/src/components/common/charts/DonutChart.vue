<template>
  <div
    class="donut-chart"
    :style="containerStyle"
  >
    <svg
      viewBox="0 0 100 100"
      class="donut-svg"
      role="img"
      :aria-label="mergedLabels.ariaLabel"
    >
      <!-- 背景轨道 -->
      <circle
        v-if="mergedConfig.trackColor"
        cx="50"
        cy="50"
        :r="mergedConfig.radius"
        fill="none"
        :stroke="mergedConfig.trackColor"
        :stroke-width="mergedConfig.strokeWidth"
      />
      <!-- 数据段 -->
      <circle
        v-for="(segment, index) in computedSegments"
        :key="index"
        cx="50"
        cy="50"
        :r="mergedConfig.radius"
        fill="none"
        :stroke="segment.color"
        :stroke-width="mergedConfig.strokeWidth"
        :stroke-dasharray="segment.dashArray"
        :stroke-dashoffset="segment.dashOffset"
        transform="rotate(-90 50 50)"
        class="donut-segment"
      />
    </svg>
    <div
      v-if="showCenter"
      class="donut-center"
    >
      <slot>
        <span
          v-if="mergedLabels.centerText"
          class="donut-center-text"
        >{{ mergedLabels.centerText }}</span>
        <span
          v-if="mergedLabels.centerSubtext"
          class="donut-center-subtext"
        >{{ mergedLabels.centerSubtext }}</span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'

/** 环形图数据段 */
export interface DonutSegment {
  color: string
  value: number
  label?: string
}

/** 环形图外观配置 */
export interface DonutConfig {
  /** 图表尺寸（像素） */
  size?: number
  /** 描边宽度 */
  strokeWidth?: number
  /** 圆环半径 */
  radius?: number
  /** 轨道背景色 */
  trackColor?: string
}

/** 环形图中心文本配置 */
export interface DonutLabels {
  /** 中心主文本 */
  centerText?: string
  /** 中心副文本 */
  centerSubtext?: string
  /** 无障碍标签 */
  ariaLabel?: string
}

const props = withDefaults(defineProps<{
  segments: DonutSegment[]
  config?: DonutConfig
  labels?: DonutLabels
}>(), {
  config: () => ({}),
  labels: () => ({}),
})

const slots = useSlots()

/** 合并后的配置（含默认值） */
const mergedConfig = computed<Required<DonutConfig>>(() => ({
  size: 120,
  strokeWidth: 12,
  radius: 40,
  trackColor: '',
  ...props.config,
}))

/** 合并后的标签配置（含默认值） */
const mergedLabels = computed<Required<DonutLabels>>(() => ({
  centerText: '',
  centerSubtext: '',
  ariaLabel: '环形图',
  ...props.labels,
}))

const containerStyle = computed(() => ({
  width: `${mergedConfig.value.size}px`,
  height: `${mergedConfig.value.size}px`,
}))

const circumference = computed(() => 2 * Math.PI * mergedConfig.value.radius)

const total = computed(() => props.segments.reduce((sum, s) => sum + (s.value || 0), 0))

const computedSegments = computed(() => {
  let accumulated = 0
  return props.segments.map((segment) => {
    const percent = total.value > 0 ? segment.value / total.value : 0
    const length = percent * circumference.value
    const dashArray = `${length} ${circumference.value}`
    const dashOffset = -accumulated
    accumulated += length
    return {
      color: segment.color,
      dashArray,
      dashOffset,
    }
  })
})

const showCenter = computed(() => {
  return mergedLabels.value.centerText || mergedLabels.value.centerSubtext || !!slots.default
})
</script>

<style scoped>
.donut-chart {
  position: relative;
  display: inline-block;
  flex-shrink: 0;
}

.donut-svg {
  width: 100%;
  height: 100%;
}

.donut-segment {
  transition: stroke-dasharray 0.5s ease, stroke-dashoffset 0.5s ease;
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  text-align: center;
}

.donut-center-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.donut-center-subtext {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.2;
}
</style>
