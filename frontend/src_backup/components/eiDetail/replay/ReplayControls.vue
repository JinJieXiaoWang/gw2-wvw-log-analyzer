<template>
  <div class="replay-controls">
    <div class="control-group">
      <button
        class="control-btn"
        @click="emit('togglePlay')"
      >
        <i :class="isPlaying ? 'pi pi-pause' : 'pi pi-play'" />
      </button>
      <button
        class="control-btn"
        @click="emit('stepBackward')"
      >
        <i class="pi pi-fast-backward" />
      </button>
      <button
        class="control-btn"
        @click="emit('stepForward')"
      >
        <i class="pi pi-fast-forward" />
      </button>
      <button
        class="control-btn"
        @click="emit('restart')"
      >
        <i class="pi pi-rotate-left" />
      </button>
    </div>
    <div class="timeline-container">
      <div class="timeline-track">
        <div
          class="timeline-progress"
          :style="{ width: progressPercent + '%' }"
        />
        <input
          type="range"
          class="timeline-slider"
          :min="0"
          :max="duration"
          :value="currentTime"
          @input="emit('seek', Number(($event.target as HTMLInputElement).value))"
        >
      </div>
      <div class="timeline-labels">
        <span>{{ formatTime(0) }}</span>
        <span>{{ formatTime(duration / 4) }}</span>
        <span>{{ formatTime(duration / 2) }}</span>
        <span>{{ formatTime(duration * 3 / 4) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>
    <div class="control-group">
      <span class="control-label">速度</span>
      <select
        v-model="playbackSpeed"
        class="speed-select"
      >
        <option :value="0.25">
          0.25x
        </option>
        <option :value="0.5">
          0.5x
        </option>
        <option :value="1">
          1x
        </option>
        <option :value="2">
          2x
        </option>
        <option :value="4">
          4x
        </option>
      </select>
    </div>
    <div class="control-group">
      <label class="checkbox-label"><input
        v-model="showPlayers"
        type="checkbox"
      ><span>显示玩家</span></label>
      <label class="checkbox-label"><input
        v-model="showTargets"
        type="checkbox"
      ><span>显示目标</span></label>
      <label class="checkbox-label"><input
        v-model="showEffects"
        type="checkbox"
      ><span>显示技能效果</span></label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const { isPlaying, currentTime, duration, progressPercent } = defineProps<{
  isPlaying: boolean
  currentTime: number
  duration: number
  progressPercent: number
}>()

const emit = defineEmits(['togglePlay', 'stepBackward', 'stepForward', 'restart', 'seek'])

const playbackSpeed = defineModel<number>('playbackSpeed', { default: 1 })
const showPlayers = defineModel<boolean>('showPlayers', { default: true })
const showTargets = defineModel<boolean>('showTargets', { default: true })
const showEffects = defineModel<boolean>('showEffects', { default: true })

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>@import './CombatReplay.css';</style>
