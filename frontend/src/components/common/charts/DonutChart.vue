<template>
  <div
    class="donut-chart"
    :style="containerStyle"
  >
    <svg
      viewBox="0 0 100 100"
      class="donut-svg"
      role="img"
      :aria-label="ariaLabel"
    >
      <!-- 背景轨道 -->
      <circle
        v-if="trackColor"
        cx="50"
        cy="50"
        :r="radius"
        fill="none"
        :stroke="trackColor"
        :stroke-width="strokeWidth"
      />
      <!-- 数据段 -->
      <circle
        v-for="(segment, index) in computedSegments"
        :key="index"
        cx="50"
        cy="50"
        :r="radius"
        fill="none"
        :stroke="segment.color"
        :stroke-width="strokeWidth"
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
          v-if="centerText"
          class="donut-center-text"
        >{{ centerText }}</span>
        <span
          v-if="centerSubtext"
          class="donut-center-subtext"
        >{{ centerSubtext }}</span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'

export interface DonutSegment {
  color: string
  value: number
  label?: string
}

const props = withDefaults(defineProps<{
  segments: DonutSegment[]
  size?: number
  strokeWidth?: number
  radius?: number
  centerText?: string
  centerSubtext?: string
  trackColor?: string
  ariaLabel?: string
}>(), {
  size: 120,
  strokeWidth: 12,
  radius: 40,
  ariaLabel: '环形图',
})

const slots = useSlots()

const containerStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
}))

const circumference = computed(() => 2 * Math.PI * props.radius)

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
  return props.centerText || props.centerSubtext || !!slots.default
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
