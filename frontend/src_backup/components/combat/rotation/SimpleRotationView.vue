<template>
  <div class="simple-rotation">
    <div
      v-for="(cycle, cycleIdx) in cycles"
      :key="cycleIdx"
      class="cycle-row"
    >
      <div class="cycle-number">
        #{{ cycleIdx + 1 }}
      </div>
      <div class="cycle-skills">
        <div
          v-for="(evt, evtIdx) in cycle.events"
          :key="evtIdx"
          class="sr-skill"
          :class="[`sr-state-${evt.state}`, { 'sr-swap': evt.isSwap, 'sr-auto': evt.autoAttack }]"
          @mouseenter="hoveredEvent = evt"
          @mouseleave="hoveredEvent = null"
        >
          <template v-if="evt.isSwap">
            <div class="sr-swap-icon">
              <i class="pi pi-sync" />
            </div>
          </template>
          <template v-else>
            <img
              v-if="evt.icon"
              :src="evt.icon"
              class="sr-icon"
              :alt="evt.name"
              loading="lazy"
            >
            <div
              v-else
              class="sr-icon-placeholder"
            >
              {{ evt.name?.charAt(0) || '?' }}
            </div>
            <span
              v-if="evt.state === 'instant'"
              class="sr-instant-mark"
            >!</span>
          </template>
          <Transition name="tooltip-fade">
            <div
              v-if="hoveredEvent === evt"
              class="sr-tooltip"
            >
              <div class="sr-tooltip-header">
                <img
                  v-if="evt.icon"
                  :src="evt.icon"
                  class="sr-tooltip-icon"
                >
                <span class="sr-tooltip-title">{{ evt.name || 'δ֪技能' }}</span>
              </div>
              <div class="sr-tooltip-body">
                <div class="sr-tooltip-row">
                  <span class="sr-tooltip-key">״̬:</span><span
                    class="sr-tooltip-value"
                    :class="`text-${evt.state}`"
                  >{{ stateLabels[evt.state] }}</span>
                </div>
                <div class="sr-tooltip-row">
                  <span class="sr-tooltip-key">ʱ间:</span><span class="sr-tooltip-value">{{ formatTime(evt.castTime / 1000) }}</span>
                </div>
                <div class="sr-tooltip-row">
                  <span class="sr-tooltip-key">持续:</span><span class="sr-tooltip-value">{{ evt.duration }}ms</span>
                </div>
                <div
                  v-if="evt.timeGained !== 0"
                  class="sr-tooltip-row"
                >
                  <span class="sr-tooltip-key">动画差:</span><span
                    class="sr-tooltip-value"
                    :class="evt.timeGained < 0 ? 'text-interrupted' : ''"
                  >{{ evt.timeGained > 0 ? '+' : '' }}{{ evt.timeGained }}ms</span>
                </div>
                <div class="sr-tooltip-row">
                  <span class="sr-tooltip-key">急速:</span><span class="sr-tooltip-value">{{ Math.round((evt.quickness || 0) * 100) }}%</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
      <div
        v-if="cycle.duration > 0"
        class="cycle-duration"
      >
        {{ formatDuration(cycle.duration / 1000) }}
      </div>
    </div>
    <div
      v-if="cycles.length === 0"
      class="empty-cycles"
    >
      <i class="pi pi-info-circle" /><span>û有可展示的技能循环数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { STATE_LABELS, type RotationEvent } from '@/composables/combat/useSkillRotationTimeline'
import type { FlatEvent, SimpleCycle } from '@/composables/combat/useSkillRotationTimeline'

defineProps<{
  cycles: SimpleCycle[]
  formatTime: (s: number) => string
  formatDuration: (s: number) => string
}>()

const hoveredEvent = ref<FlatEvent | null>(null)
const stateLabels = STATE_LABELS
</script>
