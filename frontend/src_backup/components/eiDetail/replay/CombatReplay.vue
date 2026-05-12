<template>
  <div class="combat-replay-container">
    <div class="replay-canvas-wrapper">
      <div class="replay-canvas">
        <div class="battlefield-grid" />
        <div class="time-indicator">
          <span>{{ formatTime(currentTime) }}</span>
        </div>
        <div
          v-for="player in displayPlayers"
          :key="player.instanceID"
          class="player-marker"
          :style="getPlayerPosition(player)"
          :class="{ selected: player.instanceID === selectedPlayerId }"
        >
          <div
            class="marker-dot"
            :style="{ backgroundColor: player.color }"
          />
          <span class="marker-name">{{ player.name }}</span>
        </div>
        <div
          v-for="effect in activeEffects"
          :key="effect.id"
          class="skill-effect"
          :style="effect.style"
        >
          <i :class="effect.icon" />
        </div>
        <div
          v-for="target in targets"
          :key="target.uniqueID"
          class="target-marker"
          :style="getTargetPosition(target)"
        >
          <div class="target-icon">
            <i class="pi pi-target" />
          </div>
        </div>
      </div>
    </div>

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

    <!-- 战斗事件日志 -->
    <div class="event-log">
      <h3 class="log-title">
        <i class="pi pi-list" /> 战斗事件
      </h3>
      <div class="log-content">
        <div
          v-for="event in recentEvents"
          :key="event.id"
          class="log-item"
          :class="event.type"
        >
          <span class="log-time">{{ formatTime(event.time) }}</span>
          <span class="log-content-text">{{ event.content }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ReplayControls from './ReplayControls.vue'

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

const displayPlayers = computed(() => showPlayers.value ? props.players : [])
const activeEffects = computed(() => showEffects.value ? props.effects.filter((e: any) => e.start <= currentTime.value && e.end >= currentTime.value) : [])
const progressPercent = computed(() => props.duration > 0 ? (currentTime.value / props.duration) * 100 : 0)
const recentEvents = computed(() => props.events.filter((e: any) => e.time <= currentTime.value).slice(-20))

function getPlayerPosition(player: any) {
  const pos = player.positions?.find((p: any) => p.time <= currentTime.value)
  return pos ? { left: `${pos.x}%`, top: `${pos.y}%` } : { display: 'none' }
}

function getTargetPosition(target: any) {
  return { left: `${target.x}%`, top: `${target.y}%` }
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

function togglePlay() { isPlaying.value = !isPlaying.value }
function stepBackward() { currentTime.value = Math.max(0, currentTime.value - 5) }
function stepForward() { currentTime.value = Math.min(props.duration, currentTime.value + 5) }
function restart() { currentTime.value = 0; isPlaying.value = false }
function seekTo(time: number) { currentTime.value = time }
</script>

<style scoped>@import './CombatReplay.css';</style>
