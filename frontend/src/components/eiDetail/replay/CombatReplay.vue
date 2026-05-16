<template>
  <div class="combat-replay-container">
    <CombatReplayCanvas
      :players="showPlayers ? players : []"
      :effects="showEffects ? effects : []"
      :targets="targets"
      :current-time="currentTime"
      :selected-player-id="selectedPlayerId"
    />

    <ReplayControls
      :is-playing="isPlaying"
      :current-time="currentTime"
      :duration="duration"
      :progress-percent="progressPercent"
      :playback-speed="playbackSpeed"
      :show-players="showPlayers"
      :show-targets="showTargets"
      :show-effects="showEffects"
      @toggle-play="togglePlay"
      @step-backward="stepBackward"
      @step-forward="stepForward"
      @restart="restart"
      @seek="seekTo"
      @update:playback-speed="playbackSpeed = $event"
      @update:show-players="showPlayers = $event"
      @update:show-targets="showTargets = $event"
      @update:show-effects="showEffects = $event"
    />

    <CombatReplayEventLog
      :events="events"
      :current-time="currentTime"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ReplayControls from './ReplayControls.vue'
import CombatReplayCanvas from './CombatReplayCanvas.vue'
import CombatReplayEventLog from './CombatReplayEventLog.vue'

const props = defineProps<{
  players: any[]
  effects: any[]
  targets: any[]
  events: any[]
  selectedPlayerId: number | null
  duration: number
}>()

const currentTime = ref(0)
const isPlaying = ref(false)
const playbackSpeed = ref(1)
const showPlayers = ref(true)
const showTargets = ref(true)
const showEffects = ref(true)

const progressPercent = computed(() => props.duration > 0 ? (currentTime.value / props.duration) * 100 : 0)

function togglePlay() { isPlaying.value = !isPlaying.value }
function stepBackward() { currentTime.value = Math.max(0, currentTime.value - 5) }
function stepForward() { currentTime.value = Math.min(props.duration, currentTime.value + 5) }
function restart() { currentTime.value = 0; isPlaying.value = false }
function seekTo(time: number) { currentTime.value = time }
</script>

<style scoped lang="css">
.combat-replay-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.replay-controls {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.control-btn {
  width: 40px;
  height: 40px;
  border: none;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  color: var(--color-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-btn:hover {
  background-color: var(--color-accent);
  color: white;
}

.control-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.speed-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-card-hover);
  color: var(--color-text);
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.timeline-track {
  position: relative;
  height: 8px;
  background-color: var(--color-card-hover);
  border-radius: 4px;
  cursor: pointer;
}

.timeline-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: var(--color-accent);
  border-radius: 4px;
  transition: width 0.1s;
}

.timeline-slider {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.timeline-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
</style>
