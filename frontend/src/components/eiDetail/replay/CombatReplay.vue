<template>
  <div class="combat-replay-container flex flex-col gap-4 h-full">
    <div class="replay-canvas-wrapper flex-1 bg-[var(--color-background)] rounded-xl overflow-hidden relative">
      <div class="replay-canvas w-full h-[400px] relative bg-[linear-gradient(135deg,#1a1a2e_0%,#16213e_100%)]">
        <div class="battlefield-grid absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />
        <div class="time-indicator absolute top-4 right-4 bg-black/70 py-2 px-4 rounded-lg text-xl font-semibold text-primary font-mono">
          <span>{{ formatTime(currentTime) }}</span>
        </div>
        <div
          v-for="player in displayPlayers"
          :key="player.instanceID"
          class="player-marker absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 z-10 hover:z-20"
          :class="{ 'z-20': player.instanceID === selectedPlayerId }"
          :style="getPlayerPosition(player)"
        >
          <div
            class="marker-dot w-4 h-4 rounded-full border-2 border-white shadow-[0_0_10px_rgba(255,255,255,0.5)] transition-all duration-300"
            :class="{ 'w-5 h-5 shadow-[0_0_15px_rgba(255,255,255,0.8)]': player.instanceID === selectedPlayerId }"
            :style="{ backgroundColor: player.color }"
          />
          <span class="marker-name absolute bottom-full left-1/2 -translate-x-1/2 bg-black/80 py-1 px-2 rounded text-xs text-white whitespace-nowrap mb-1 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
            :class="{ 'opacity-100': player.instanceID === selectedPlayerId }"
          >{{ player.name }}</span>
        </div>
        <div
          v-for="effect in activeEffects"
          :key="effect.id"
          class="skill-effect absolute -translate-x-1/2 -translate-y-1/2 text-primary text-3xl z-[15] animate-float"
          :style="effect.style"
        >
          <i :class="effect.icon" />
        </div>
        <div
          v-for="target in targets"
          :key="target.uniqueID"
          class="target-marker absolute -translate-x-1/2 -translate-y-1/2 z-[5]"
          :style="getTargetPosition(target)"
        >
          <div class="target-icon w-10 h-10 bg-red-500/30 border-2 border-red-500 rounded-full flex items-center justify-center text-red-500 text-xl animate-pulse-custom">
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
    <div class="event-log bg-neutral-card rounded-xl p-4 max-h-[200px] overflow-hidden flex flex-col">
      <h3 class="log-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0 mb-3">
        <i class="pi pi-list" /> 战斗事件
      </h3>
      <div class="log-content flex-1 overflow-y-auto flex flex-col gap-2">
        <div
          v-for="event in recentEvents"
          :key="event.id"
          class="log-item flex gap-3 p-2 bg-neutral-card-hover rounded-md text-[0.8125rem]"
          :class="{
            'border-l-[3px] border-l-red-500': event.type === 'damage',
            'border-l-[3px] border-l-green-500': event.type === 'heal',
            'border-l-[3px] border-l-amber-500': event.type === 'buff',
            'border-l-[3px] border-l-violet-500': event.type === 'cc'
          }"
        >
          <span class="log-time font-mono text-[var(--color-accent)] font-medium">{{ formatTime(event.time) }}</span>
          <span class="log-content-text text-neutral-text-secondary">{{ event.content }}</span>
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

<style scoped>
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
@keyframes float {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
}
.animate-pulse-custom {
  animation: pulse 2s infinite;
}
.animate-float {
  animation: float 1s ease-in-out infinite;
}
</style>
