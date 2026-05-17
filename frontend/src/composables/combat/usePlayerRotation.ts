import { computed, ref, type ComputedRef, type Ref } from 'vue'
import type { PlayerRotationData, EiAnalysisFight } from '@/services/ei/eiAnalysisService'
import { getSkillIconUrl } from '@/utils/skillIcons'

// 全局技能图标URL缓存，避免重复生成
const iconUrlCache = new Map<string, string>()
function getCachedSkillIconUrl(name: string, iconUrl: string): string {
  const key = `${name}::${iconUrl}`
  if (!iconUrlCache.has(key)) {
    iconUrlCache.set(key, getSkillIconUrl(name, iconUrl))
  }
  return iconUrlCache.get(key)!
}

export function usePlayerRotation(
  playerRotation: Ref<PlayerRotationData | null>,
  fightSummary: ComputedRef<EiAnalysisFight>,
) {
  // ========== 基础数据（所有视图共享）==========

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
          icon: getCachedSkillIconUrl(name, iconUrl),
        }
      })
      .sort((a, b) => b.count - a.count)
  })

  const rotationEvents = computed(() => {
    if (!playerRotation.value?.rotation) return []
    const map = playerRotation.value.skill_map || {}
    const events: Record<string, unknown>[] = []
    playerRotation.value.rotation.forEach((rot: unknown) => {
      if (!rot || typeof rot !== 'object') return
      const r = rot as Record<string, unknown>
      const skillId = (r.id as number) ?? 0
      const name = map[String(skillId)]?.name || `技能 #${skillId}`
      const iconUrl = map[String(skillId)]?.icon || ''
      const icon = getCachedSkillIconUrl(name, iconUrl)
      const duration = (r.duration as number) ?? 0
      const timeGained = (r.timeGained as number) ?? 0
      const quickness = (r.quickness as number) ?? 0
      ;((r.skills as Record<string, unknown>[]) || []).forEach((cast: Record<string, unknown>) => {
        const castDuration = (cast.duration as number) ?? 0
        const castTime = (cast.castTime as number) ?? 0
        const isInterrupted = !!(cast.interrupted || (castDuration < 150 && castDuration > 0))
        const isInstant = !!(cast.instant || castDuration === 0)
        const isSwap = !!(cast.isSwap || (map[String(skillId)]?.is_swap))
        const isTraitProc = !!(cast.isTraitProc || (map[String(skillId)]?.is_trait_proc))
        const autoAttack = !!(cast.autoAttack || (map[String(skillId)]?.auto_attack))
        const state = isInterrupted ? 'interrupted'
          : isSwap ? 'swap'
          : isTraitProc ? 'trait'
          : isInstant ? 'instant'
          : 'full'
        events.push({
          castTime,
          skillId,
          duration: castDuration,
          timeGained: (cast.timeGained as number) ?? timeGained,
          quickness: (cast.quickness as number) ?? quickness,
          name,
          icon,
          state,
          autoAttack,
          isSwap,
          isInstant,
          isTraitProc,
        })
      })
    })
    return events
  })

  const top10SkillCasts = computed(() => sortedSkillCasts.value.slice(0, 10))

  const autoAttackRatio = computed(() => {
    const total = rotationEvents.value.length
    if (!total) return 0
    const aaCount = rotationEvents.value.filter((e: any) => e.autoAttack === true).length
    return Math.round((aaCount / total) * 100)
  })

  const weaponSwapCount = computed(() => {
    return rotationEvents.value.filter((e: any) => e.isSwap === true).length
  })

  const weaponSwapIntervals = computed(() => {
    const swapTimes = rotationEvents.value
      .filter((e: any) => e.isSwap === true)
      .map((e: any) => e.castTime as number)
    if (swapTimes.length < 2) return null
    const intervals: number[] = []
    for (let i = 1; i < swapTimes.length; i++) {
      intervals.push(Math.round((swapTimes[i] - swapTimes[i - 1]) / 1000 * 10) / 10)
    }
    const avg = intervals.reduce((a, b) => a + b, 0) / intervals.length
    return {
      intervals,
      average: Math.round(avg * 10) / 10,
      min: Math.min(...intervals),
      max: Math.max(...intervals),
    }
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

  return {
    sortedSkillCasts,
    top10SkillCasts,
    rotationEvents,
    autoAttackRatio,
    weaponSwapCount,
    weaponSwapIntervals,
    hasPlayerDetailData,
  }
}
