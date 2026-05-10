<template>
  <div class="sr-timeline-view">
    <div class="timeline-container">
      <div class="timeline-ruler">
        <div v-for="tick in ticks" :key="tick.time" class="ruler-tick" :style="{ left: tick.position + '%' }">
          <div class="tick-line" />
          <span class="tick-label">{{ formatTime(tick.time * 1000) }}</span>
        </div>
      </div>
      <div class="timeline-content">
        <div v-for="(skill, idx) in tracks" :key="idx" class="skill-track">
          <div class="track-header">
            <img v-if="skill.icon" :src="skill.icon" class="track-icon" loading="lazy">
            <span class="track-name">{{ skill.name }}</span>
            <span class="track-count">{{ skill.casts.length }}</span>
          </div>
          <div class="track-timeline">
            <div
              v-for="(cast, castIdx) in skill.casts"
              :key="castIdx"
              class="cast-bar"
              :class="`state-${cast.state}`"
              :style="{ left: cast.position + '%', width: cast.width + '%' }"
              @mouseenter="$emit('hover-skill', cast)"
              @mousemove="$emit('mousemove', $event)"
              @mouseleave="$emit('leave-skill')"
            >
              <div class="cast-bar-inner"><span class="cast-duration">{{ cast.duration }}ms</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TimelineTick, SkillTrack } from '@/utils/combat/rotationTypes'
import { formatTime } from '@/utils/combat/rotation'

defineProps<{ ticks: TimelineTick[]; tracks: SkillTrack[] }>()
defineEmits<{
  'hover-skill': [skill: any]
  'leave-skill': []
  'mousemove': [event: MouseEvent]
}>()
</script>

<style scoped>
.sr-timeline-view { display: flex; flex-direction: column; gap: 0.5rem; }
.timeline-container { background: rgba(255,255,255,0.02); border-radius: 0.5rem; overflow: hidden; }
.timeline-ruler { position: relative; height: 32px; padding-left: 160px; background: rgba(255,255,255,0.03); border-bottom: 1px solid rgba(255,255,255,0.05); }
.ruler-tick { position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; }
.tick-line { width: 1px; height: 8px; background: rgba(255,255,255,0.15); }
.tick-label { font-size: 0.6rem; color: var(--color-text-muted, #64748b); margin-top: 2px; white-space: nowrap; }
.timeline-content { max-height: 350px; overflow-y: auto; }
.skill-track { display: flex; align-items: center; height: 40px; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.15s; }
.skill-track:hover { background: rgba(255,255,255,0.02); }
.track-header { width: 160px; flex-shrink: 0; display: flex; align-items: center; gap: 0.5rem; padding: 0 0.5rem; background: rgba(255,255,255,0.02); border-right: 1px solid rgba(255,255,255,0.05); }
.track-icon { width: 24px; height: 24px; border-radius: 0.25rem; }
.track-name { flex: 1; font-size: 0.7rem; color: var(--color-text-secondary, #94a3b8); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.track-count { font-size: 0.65rem; color: var(--color-text-muted, #64748b); background: rgba(255,255,255,0.05); padding: 0.125rem 0.375rem; border-radius: 0.25rem; }
.track-timeline { flex: 1; position: relative; height: 100%; }
.cast-bar { position: absolute; top: 8px; bottom: 8px; border-radius: 0.25rem; cursor: pointer; transition: opacity 0.15s; min-width: 3px; }
.cast-bar:hover { opacity: 0.85; }
.cast-bar.state-full { background: rgba(34,211,238,0.7); border: 1px solid rgba(34,211,238,0.9); }
.cast-bar.state-interrupted { background: rgba(239,68,68,0.7); border: 1px solid rgba(239,68,68,0.9); }
.cast-bar.state-instant { background: rgba(59,130,246,0.7); border: 1px solid rgba(59,130,246,0.9); }
.cast-bar.state-swap { background: rgba(168,85,247,0.7); border: 1px solid rgba(168,85,247,0.9); }
.cast-bar-inner { display: flex; align-items: center; justify-content: center; height: 100%; padding: 0 0.25rem; }
.cast-duration { font-size: 0.55rem; color: rgba(255,255,255,0.8); white-space: nowrap; }
</style>
