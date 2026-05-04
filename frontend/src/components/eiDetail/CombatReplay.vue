<template>
  <div class="combat-replay-container">
    <!-- 回放画布区域 -->
    <div class="replay-canvas-wrapper">
      <div class="replay-canvas">
        <!-- 战场背景 -->
        <div class="battlefield-grid" />
        
        <!-- 时间指示器 -->
        <div class="time-indicator">
          <span>{{ formatTime(currentTime) }}</span>
        </div>
        
        <!-- 玩家位置标记 -->
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
        
        <!-- 技能效果 -->
        <div
          v-for="effect in activeEffects"
          :key="effect.id"
          class="skill-effect"
          :style="effect.style"
        >
          <i :class="effect.icon" />
        </div>
        
        <!-- 目标标记 -->
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

    <!-- 控制面板 -->
    <div class="replay-controls">
      <!-- 播放控制 -->
      <div class="control-group">
        <button
          class="control-btn"
          @click="togglePlay"
        >
          <i :class="isPlaying ? 'pi pi-pause' : 'pi pi-play'" />
        </button>
        <button
          class="control-btn"
          @click="stepBackward"
        >
          <i class="pi pi-fast-backward" />
        </button>
        <button
          class="control-btn"
          @click="stepForward"
        >
          <i class="pi pi-fast-forward" />
        </button>
        <button
          class="control-btn"
          @click="restart"
        >
          <i class="pi pi-rotate-left" />
        </button>
      </div>

      <!-- 时间轴 -->
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
            @input="seekTo"
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

      <!-- 速度控制 -->
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

      <!-- 显示选项 -->
      <div class="control-group">
        <label class="checkbox-label">
          <input
            v-model="showPlayers"
            type="checkbox"
          >
          <span>显示玩家</span>
        </label>
        <label class="checkbox-label">
          <input
            v-model="showTargets"
            type="checkbox"
          >
          <span>显示目标</span>
        </label>
        <label class="checkbox-label">
          <input
            v-model="showEffects"
            type="checkbox"
          >
          <span>显示技能效果</span>
        </label>
      </div>
    </div>

    <!-- 事件日志 -->
    <div class="event-log">
      <h3 class="log-title">
        <i class="pi pi-list" />
        战斗事件
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { Player } from '@/types/eliteInsights'

const props = defineProps<{
  players: Player[]
  targets: any[]
  duration: number
  selectedPlayerId?: number | null
}>()

const emit = defineEmits(['select-player'])

// 状态
const isPlaying = ref(false)
const currentTime = ref(0)
const playbackSpeed = ref(1)
const showPlayers = ref(true)
const showTargets = ref(true)
const showEffects = ref(true)

let playInterval: number | null = null

// 计算属性
const progressPercent = computed(() => {
  if (props.duration === 0) return 0
  return (currentTime.value / props.duration) * 100
})

const displayPlayers = computed(() => {
  if (!showPlayers.value) return []
  return props.players.map(p => ({
    ...p,
    color: getPlayerColor(p.profession)
  }))
})

const activeEffects = computed(() => {
  if (!showEffects.value) return []
  // 模拟技能效果
  return [
    { id: 1, icon: 'pi pi-bolt', style: { top: '30%', left: '40%' } },
    { id: 2, icon: 'pi pi-shield', style: { top: '50%', left: '60%' } },
    { id: 3, icon: 'pi pi-heart', style: { top: '40%', left: '50%' } }
  ]
})

const recentEvents = computed(() => {
  // 模拟战斗事件
  return [
    { id: 1, time: currentTime.value, type: 'damage', content: '一统康师傅 对 Dummy WvW Agent 造成 12,500 伤害' },
    { id: 2, time: currentTime.value - 1000, type: 'heal', content: '玩家A 治疗 玩家B 5,000 生命' },
    { id: 3, time: currentTime.value - 2000, type: 'buff', content: '玩家C 获得 勇猛 增益' },
    { id: 4, time: currentTime.value - 3000, type: 'damage', content: '玩家D 对 Dummy WvW Agent 造成 8,700 伤害' },
    { id: 5, time: currentTime.value - 4000, type: 'cc', content: '玩家E 控制了 Dummy WvW Agent' }
  ]
})

// 方法
function getPlayerColor(profession: string): string {
  const colors: Record<string, string> = {
    Warrior: '#C41E3A',
    Guardian: '#228B22',
    Ranger: '#32CD32',
    Engineer: '#FFD700',
    Thief: '#8B4513',
    Elementalist: '#4169E1',
    Mesmer: '#9400D3',
    Necromancer: '#00CED1',
    Revenant: '#8A2BE2',
    Herald: '#8A2BE2',
    Chronomancer: '#9400D3',
    Druid: '#228B22',
    Scrapper: '#FFD700',
    Daredevil: '#8B4513',
    Tempest: '#4169E1',
    Berserker: '#C41E3A',
    Spellbreaker: '#C41E3A',
    Soulbeast: '#32CD32',
    Holosmith: '#FFD700',
    Deadeye: '#8B4513',
    Weaver: '#4169E1',
    Mirage: '#9400D3',
    Reaper: '#00CED1',
    Renegade: '#8A2BE2',
    Dragonhunter: '#228B22',
    Firebrand: '#228B22',
    Chrono: '#9400D3',
    Mechanist: '#FFD700',
    Catalyst: '#4169E1',
    Harbinger: '#00CED1'
  }
  return colors[profession] || '#888888'
}

function getPlayerPosition(player: any) {
  // 模拟玩家位置
  const baseX = 20 + Math.sin(player.instanceID * 0.5) * 30
  const baseY = 20 + Math.cos(player.instanceID * 0.3) * 25
  const offsetX = Math.sin(currentTime.value / 1000 + player.instanceID) * 5
  const offsetY = Math.cos(currentTime.value / 1500 + player.instanceID) * 5
  
  return {
    left: `${baseX + offsetX}%`,
    top: `${baseY + offsetY}%`
  }
}

function getTargetPosition(_target: any) {
  return {
    left: '50%',
    top: '50%'
  }
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  const remainingMs = Math.floor((ms % 1000) / 10)
  
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${remainingMs.toString().padStart(2, '0')}`
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    startPlayback()
  } else {
    stopPlayback()
  }
}

function startPlayback() {
  if (playInterval) return
  
  playInterval = window.setInterval(() => {
    if (currentTime.value >= props.duration) {
      currentTime.value = props.duration
      isPlaying.value = false
      stopPlayback()
      return
    }
    currentTime.value += 100 * playbackSpeed.value
  }, 100)
}

function stopPlayback() {
  if (playInterval) {
    clearInterval(playInterval)
    playInterval = null
  }
}

function stepBackward() {
  currentTime.value = Math.max(0, currentTime.value - 1000)
}

function stepForward() {
  currentTime.value = Math.min(props.duration, currentTime.value + 1000)
}

function restart() {
  stopPlayback()
  currentTime.value = 0
  isPlaying.value = false
}

function seekTo(event: Event) {
  const target = event.target as HTMLInputElement
  currentTime.value = Number(target.value)
}

watch(playbackSpeed, () => {
  if (isPlaying.value) {
    stopPlayback()
    startPlayback()
  }
})

onMounted(() => {})

onUnmounted(() => {
  stopPlayback()
})
</script>

<style scoped lang="css">
.combat-replay-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

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
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
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
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
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

.event-log {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  padding: 1rem;
  max-height: 200px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.75rem 0;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.log-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem;
  background-color: var(--color-card-hover);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
}

.log-time {
  font-family: monospace;
  color: var(--color-accent);
  font-weight: 500;
}

.log-content-text {
  color: var(--color-text-secondary);
}

.log-item.damage {
  border-left: 3px solid #ef4444;
}

.log-item.heal {
  border-left: 3px solid #22c55e;
}

.log-item.buff {
  border-left: 3px solid #f59e0b;
}

.log-item.cc {
  border-left: 3px solid #8b5cf6;
}
</style>