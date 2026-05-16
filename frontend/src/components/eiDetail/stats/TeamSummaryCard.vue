<template>
  <div class="team-summary-card">
    <TeamSummaryHeader :player-count="teamStats.playerCount" />

    <div class="stats-grid">
      <TeamSummaryDamage
        :total-damage="totalDamage"
        :avg-dps="teamStats.avgDps"
        :total-dps="teamStats.totalDps"
      />
      <TeamSummarySurvival
        :total-downs="teamStats.totalDowns"
        :total-deaths="teamStats.totalDeaths"
      />
      <TeamSummarySupport
        :total-cleanses="teamStats.totalCleanses"
        :total-strips="teamStats.totalStrips"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 团队统计卡片组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import TeamSummaryDamage from './TeamSummaryDamage.vue'
import TeamSummaryHeader from './TeamSummaryHeader.vue'
import TeamSummarySupport from './TeamSummarySupport.vue'
import TeamSummarySurvival from './TeamSummarySurvival.vue'

interface Props {
  teamStats: {
    playerCount: number
    totalDps: number
    avgDps: number
    totalDowns: number
    totalDeaths: number
    totalCleanses: number
    totalStrips: number
  }
  totalDamage: {
    total: number
    power: number
    condi: number
  }
}

defineProps<Props>()
</script>

<style scoped lang="css">
.team-summary-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}
</style>
