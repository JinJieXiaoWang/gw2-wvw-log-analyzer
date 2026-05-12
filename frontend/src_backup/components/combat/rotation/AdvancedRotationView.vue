<template>
  <div class="advanced-rotation">
    <div
      ref="trackRef"
      class="ar-track"
      @scroll="handleScroll"
    >
      <div
        class="ar-content"
        :style="contentStyle"
      >
        <div class="ar-time-grid">
          <div
            v-for="tick in timeTicks"
            :key="tick.time"
            class="ar-grid-line"
            :style="{ left: tick.position + '%' }"
          />
        </div>
        <div
          v-for="skillRow in skillRows"
          :key="String(skillRow.skillId)"
          class="ar-skill-row"
        >
          <div
            class="ar-row-label"
            :style="{ transform: `translateX(${scrollLeft}px)` }"
          >
            <img
              v-if="skillRow.icon"
              :src="skillRow.icon"
              class="ar-row-icon"
              loading="lazy"
            >
            <span class="ar-row-name">{{ skillRow.name }}</span>
          </div>
          <div class="ar-row-bars">
            <div
              v-for="(cast, castIdx) in skillRow.casts"
              :key="castIdx"
              class="ar-cast-bar"
              :class="`ar-state-${cast.state}`"
              :style="{ left: cast.left + '%', width: cast.width + '%' }"
              @mouseenter="hoveredEvent = cast"
              @mouseleave="hoveredEvent = null"
            >
              <img
                v-if="skillRow.icon"
                :src="skillRow.icon"
                class="ar-bar-icon"
                loading="lazy"
              >
              <Transition name="tooltip-fade">
                <div
                  v-if="hoveredEvent === cast"
                  class="ar-tooltip"
                >
                  <div class="ar-tooltip-title">
                    {{ skillRow.name }}
                  </div>
                  <div class="ar-tooltip-row">
                    <span>״̬:</span><span :class="`text-${cast.state}`">{{ stateLabels[cast.state] }}</span>
                  </div>
                  <div class="ar-tooltip-row">
                    <span>ʱ间:</span><span>{{ formatTime(cast.castTime / 1000) }}</span>
                  </div>
                  <div class="ar-tooltip-row">
                    <span>持续:</span><span>{{ cast.duration }}ms</span>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="ar-time-ruler">
      <div
        v-for="tick in timeTicks"
        :key="tick.time"
        class="ar-ruler-tick"
        :style="{ left: tick.position + '%' }"
      >
        <div class="ar-tick-line" />
        <span class="ar-tick-label">{{ formatTime(tick.time) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { STATE_LABELS, type AdvancedSkillRow, type AdvancedCast, type TimeTick } from '@/composables/combat/useSkillRotationTimeline'

defineProps<{
  skillRows: AdvancedSkillRow[]
  timeTicks: TimeTick[]
  contentStyle: Record<string, string>
  scrollLeft: number
  formatTime: (s: number) => string
}>()

const emit = defineEmits<{
  scroll: []
}>()

const hoveredEvent = ref<AdvancedCast | null>(null)
const trackRef = ref<HTMLDivElement | null>(null)
const stateLabels = STATE_LABELS

function handleScroll() {
  emit('scroll')
}
</script>
