<template>
  <div class="replay-canvas-wrapper">
    <div class="replay-canvas">
      <div class="battlefield-grid" />
      <div class="time-indicator">
        <span>{{ formatTime(currentTime) }}</span>
      </div>
      <div
        v-for="player in players"
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
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  players: any[]
  effects: any[]
  targets: any[]
  currentTime: number
  selectedPlayerId: number | null
}>()

const activeEffects = computed(() => props.effects.filter((e: any) => e.start <= props.currentTime && e.end >= props.currentTime))

function getPlayerPosition(player: any) {
  const pos = player.positions?.find((p: any) => p.time <= props.currentTime)
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
</script>

<style scoped lang="css">
.replay-canvas-wrapper {
  flex: 1;
  background-color: var(--color-background);
  border-radius: 0.75rem;
  overflow: hidden;
  position: relative;
}

.replay-canvas {
  width: 100%;
  height: 400px;
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.battlefield-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.time-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
  font-family: monospace;
}

.player-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.player-marker:hover,
.player-marker.selected {
  z-index: 20;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.player-marker.selected .marker-dot {
  width: 20px;
  height: 20px;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
}

.marker-name {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.8);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: white;
  white-space: nowrap;
  margin-bottom: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.player-marker:hover .marker-name,
.player-marker.selected .marker-name {
  opacity: 1;
}

.target-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 5;
}

.target-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(239, 68, 68, 0.3);
  border: 2px solid #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  font-size: 1.25rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.skill-effect {
  position: absolute;
  transform: translate(-50%, -50%);
  color: var(--color-primary);
  font-size: 2rem;
  animation: float 1s ease-in-out infinite;
  z-index: 15;
}

@keyframes float {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.2);
  }
}
</style>
