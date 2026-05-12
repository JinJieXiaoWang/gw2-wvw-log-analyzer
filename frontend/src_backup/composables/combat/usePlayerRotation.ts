import { computed } from 'vue'
import type { ComputedRef, Ref } from 'vue'
import type { PlayerRotationData, EiAnalysisFight } from '@/services/ei/eiAnalysisService'
import { getSkillIconUrl } from '@/utils/skillIcons'
import { generateTimelineData, generateHeatmapData, generateCycleData } from '@/utils/combat/rotation'
import type { TimelineTick, SkillTrack, HeatmapRow, SkillCycle } from '@/utils/combat/rotationTypes'

export function usePlayerRotation(
  playerRotation: Ref<PlayerRotationData | null>,
  fightSummary: ComputedRef<EiAnalysisFight>
) {
  const sortedSkillCasts = computed(() => {
    if (!playerRotation.value?.skill_casts) return []
    const map = playerRotation.value.skill_map || {}
    return Object.entries(playerRotation.value.skill_casts)
      .map(([skillId, count]) => {
        const name = map[skillId]?.name || `技能 #${skillId}`
        const iconUrl = map[skillId]?.icon || ''
        return {
          skillId,
          count,
          name,
          icon: getSkillIconUrl(name, iconUrl),
        }
      })
      .sort((a, b) => b.count - a.count)
  })

  const rotationEvents = computed(() => {
    if (!playerRotation.value?.rotation) return []
    const map = playerRotation.value.skill_map || {}
    const events: any[] = []
    playerRotation.value.rotation.forEach((rot: any) => {
      if (!rot || typeof rot !== 'object') return
      const skillId = rot.id ?? 0
      const name = map[String(skillId)]?.name || `技能 #${skillId}`
      const iconUrl = map[String(skillId)]?.icon || ''
      const icon = getSkillIconUrl(name, iconUrl)
      ;(rot.skills || []).forEach((cast: any) => {
        events.push({
          time: (cast.castTime ?? 0) / 1000,
          skillId,
          duration: cast.duration ?? 0,
          casts: 1,
          name,
          icon,
          state: cast.interrupted ? 'interrupted' : cast.instant ? 'instant' : cast.isSwap ? 'swap' : cast.isTraitProc ? 'trait' : 'full',
          autoAttack: cast.autoAttack,
          isSwap: cast.isSwap,
          isInstant: cast.instant,
          isTraitProc: cast.isTraitProc,
        })
      })
    })
    return events.slice(0, 100)
  })

  const hasPlayerDetailData = computed(() => {
    if (!playerRotation.value) return false
    const hasConsumables = (
      (playerRotation.value.consumables?.food?.length || 0) > 0 ||
      (playerRotation.value.consumables?.utility?.length || 0) > 0
    )
    return (
      (playerRotation.value.weapons?.length || 0) > 0 ||
      sortedSkillCasts.value.length > 0 ||
      rotationEvents.value.length > 0 ||
      hasConsumables
    )
  })

  const timelineTicks = computed<TimelineTick[]>(() => {
    const duration = fightSummary.value.duration_sec || 120
    return generateTimelineData(rotationEvents.value, duration).ticks
  })

  const timelineTracks = computed<SkillTrack[]>(() => {
    const duration = fightSummary.value.duration_sec || 120
    return generateTimelineData(rotationEvents.value, duration).tracks
  })

  const heatmapRows = computed<HeatmapRow[]>(() => {
    return generateHeatmapData(sortedSkillCasts.value, rotationEvents.value)
  })

  const skillCycles = computed<SkillCycle[]>(() => {
    return generateCycleData(rotationEvents.value)
  })

  return {
    sortedSkillCasts,
    rotationEvents,
    hasPlayerDetailData,
    timelineTicks,
    timelineTracks,
    heatmapRows,
    skillCycles,
  }
}
