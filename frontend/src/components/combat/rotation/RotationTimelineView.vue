<template>
  <div class="sr-timeline-view flex flex-col gap-2">
    <div class="timeline-container bg-white/[0.02] rounded-lg overflow-hidden">
      <div class="timeline-ruler relative h-8 pl-40 bg-white/[0.03] border-b border-white/[0.05]">
        <div
          v-for="tick in ticks"
          :key="tick.time"
          class="ruler-tick absolute top-0 -translate-x-1/2 flex flex-col items-center"
          :style="{ left: tick.position + '%' }"
        >
          <div class="tick-line w-px h-2 bg-white/15" />
          <span class="tick-label text-[0.6rem] text-[var(--color-text-muted,#64748b)] mt-0.5 whitespace-nowrap">{{ formatTime(tick.time * 1000) }}</span>
        </div>
      </div>
      <div
        class="timeline-content relative max-h-[350px] overflow-y-auto"
        :class="{ 'overflow-x-auto': minTrackWidth }"
      >
        <div
          v-if="showGridLines"
          class="absolute top-0 bottom-0 left-40 right-0 pointer-events-none z-0"
        >
          <div
            v-for="tick in ticks"
            :key="`grid-${tick.time}`"
            class="absolute top-0 bottom-0 w-px bg-white/[0.04]"
            :style="{ left: tick.position + '%' }"
          />
        </div>
        <div
          v-for="(skill, idx) in tracks"
          :key="idx"
          class="skill-track flex items-center h-10 border-b border-white/[0.03] transition-colors duration-150"
        >
          <div
            class="track-header w-40 shrink-0 flex items-center gap-2 px-2 bg-white/[0.02] border-r border-white/[0.05]"
            :class="{ 'sticky left-0 z-10': minTrackWidth }"
          >
            <img
              v-if="skill.icon"
              :src="skill.icon"
              class="track-icon w-6 h-6 rounded"
              loading="lazy"
            >
            <span class="track-name flex-1 text-[0.7rem] text-[var(--color-text-secondary,#94a3b8)] overflow-hidden text-ellipsis whitespace-nowrap">{{ skill.name }}</span>
            <span class="track-count text-[0.65rem] text-[var(--color-text-muted,#64748b)] bg-white/5 py-0.5 px-1.5 rounded">{{ skill.casts.length }}</span>
          </div>
          <div
            class="track-timeline flex-1 relative h-full"
            :style="minTrackWidth ? { minWidth: minTrackWidth } : {}"
          >
            <div
              v-for="(cast, castIdx) in skill.casts"
              :key="castIdx"
              class="cast-bar absolute top-2 bottom-2 rounded cursor-pointer transition-opacity duration-150 min-w-[3px]"
              :class="`state-${cast.state}`"
              :style="{ left: cast.position + '%', width: cast.width + '%' }"
              @mouseenter="$emit('hover-skill', cast)"
              @mousemove="$emit('mousemove', $event)"
              @mouseleave="$emit('leave-skill')"
            >
              <div class="cast-bar-inner flex items-center justify-center h-full px-1 overflow-hidden">
                <img
                  v-if="showBarIcons && skill.icon && cast.width > 4"
                  :src="skill.icon"
                  class="w-full h-full object-cover opacity-70"
                  loading="lazy"
                >
                <span v-else class="cast-duration text-[0.55rem] text-white/80 whitespace-nowrap">{{ cast.duration }}ms</span>
              </div>
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

defineProps<{
  ticks: TimelineTick[]
  tracks: SkillTrack[]
  minTrackWidth?: string
  showBarIcons?: boolean
  showGridLines?: boolean
}>()

defineEmits<{
  'hover-skill': [skill: any]
  'leave-skill': []
  'mousemove': [event: MouseEvent]
}>()
</script>

<style scoped>
.skill-track:hover { background: rgba(255,255,255,0.02); }
.cast-bar:hover { opacity: 0.85; }
.cast-bar.state-full { background: rgba(34,211,238,0.7); border: 1px solid rgba(34,211,238,0.9); }
.cast-bar.state-interrupted { background: rgba(239,68,68,0.7); border: 1px solid rgba(239,68,68,0.9); }
.cast-bar.state-instant { background: rgba(59,130,246,0.7); border: 1px solid rgba(59,130,246,0.9); }
.cast-bar.state-swap { background: rgba(168,85,247,0.7); border: 1px solid rgba(168,85,247,0.9); }
.cast-bar.state-trait { background: rgba(245,158,11,0.7); border: 1px solid rgba(245,158,11,0.9); }
</style>
