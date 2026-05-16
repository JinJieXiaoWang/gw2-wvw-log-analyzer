import { computed, ref } from 'vue'
import { useSkillRotation } from './useSkillRotation'
import { STATE_LABELS } from '@/utils/combat/rotation'
import type {
  RotationEvent,
  FlatEvent,
  SimpleCycle,
  AdvancedCast,
  AdvancedSkillRow,
  TimeTick,
} from '@/utils/combat/rotationTypes'

export type { RotationEvent, FlatEvent, SimpleCycle, AdvancedCast, AdvancedSkillRow, TimeTick }

export { STATE_LABELS }

export function getStateLabel(state: string): string {
  return STATE_LABELS[state] || state
}

export function useSkillRotationTimeline(props: { events: RotationEvent[]; fightDuration?: number }) {
  const rotation = useSkillRotation(props.events, props.fightDuration)

  // 限制 viewMode 为 simple / advanced，保持原有 API 兼容
  const viewMode = ref<'simple' | 'advanced'>('simple')

  return {
    viewMode,
    showAutoAttacks: rotation.showAutoAttacks,
    showInstantCast: rotation.showInstantCast,
    hoveredEvent: rotation.hoveredEvent,
    advancedTrackRef: rotation.advancedTrackRef,
    advancedScrollLeft: rotation.advancedScrollLeft,
    advancedContentStyle: rotation.advancedContentStyle,
    flatEvents: computed<FlatEvent[]>(() => {
      const events = [...props.events].sort((a, b) => a.castTime - b.castTime)
      return events.map(evt => {
        let state: FlatEvent['state']
        if (evt.isSwap) state = 'full'
        else if (evt.isInstant || evt.duration === 0) state = 'instant'
        else if (evt.timeGained < -30 || evt.duration < 150) state = 'interrupted'
        else if (evt.duration > 0) state = 'full'
        else state = 'unknown'
        return { ...evt, state }
      })
    }),
    simpleCycles: rotation.simpleCycles,
    advancedSkillRows: rotation.advancedSkillRows,
    advancedTimeTicks: rotation.advancedTimeTicks,
    formatTime: rotation.formatTime,
    formatDuration: rotation.formatDuration,
    handleAdvancedScroll: rotation.handleAdvancedScroll,
  }
}
