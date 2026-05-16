/**
 * useScoringRules - 战斗模块评分规则 composable（兼容 wrapper）
 * 现为重导出统一版本，启用全部功能
 */

import { useScoringRules as useScoringRulesBase } from '@/composables/scoring/useScoringRules'

export function useScoringRules() {
  return useScoringRulesBase({
    enableProfessionRules: true,
    enableRecalculation: true,
    enableVersionHistory: true,
  })
}
