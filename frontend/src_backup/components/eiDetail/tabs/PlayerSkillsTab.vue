<template>
  <div class="tab-content">
    <div
      v-if="isLoading"
      class="loading-content"
    >
      <i class="pi pi-spin pi-spinner text-2xl text-primary" />
      <span class="loading-text">正在加载技能数据...</span>
    </div>
    <div
      v-else-if="error"
      class="error-content"
    >
      <i class="pi pi-exclamation-triangle text-2xl text-status-error" />
      <span class="error-text">{{ error }}</span>
    </div>
    <div
      v-else
      class="skills-content"
    >
      <h4 class="section-title">
        <i class="pi pi-bar-chart" />
        技能释放统计
      </h4>
      <div class="skills-chart-container">
        <div class="skills-chart">
          <div
            v-for="skill in stats"
            :key="skill.name"
            class="skill-bar-item"
          >
            <div class="skill-info">
              <span class="skill-name">{{ skill.name }}</span>
              <span class="skill-count">{{ skill.count }}次</span>
            </div>
            <div class="skill-bar-bg">
              <div
                class="skill-bar-fill"
                :style="{ width: skill.percentage + '%', backgroundColor: skill.color }"
              />
            </div>
            <div class="skill-percentage">
              {{ skill.percentage }}%
            </div>
          </div>
        </div>
      </div>
      <div class="skills-summary">
        <div class="summary-item">
          <span class="summary-label">总释放次数</span>
          <span class="summary-value">{{ totalCount }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">平均间隔</span>
          <span class="summary-value">{{ avgInterval }}ms</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">最高频率技能</span>
          <span class="summary-value">{{ topSkill }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { combatAnalysisService } from '@/services'
import type { PlayerRotationResponse, PlayerQueryParams } from '@/services/combat/combatAnalysisService'

const { player, logId } = defineProps<{
  player: Player
  logId?: number
}>()

const isLoading = ref(false)
const error = ref('')
const stats = ref<any[]>([])
const totalCount = ref(0)
const avgInterval = ref(0)
const topSkill = ref('')

const colors = ['#4A6FA5', '#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3', '#A8E6CF']

async function load() {
  if (!logId) {
    error.value = '缺少日志ID'
    return
  }
  isLoading.value = true
  error.value = ''
  try {
    const params: PlayerQueryParams = {
      instance_id: typeof player.instanceID === 'number' ? player.instanceID : undefined,
      account_name: player.account || undefined,
      member_name: player.name || undefined,
    }
    const result = await combatAnalysisService.getPlayerRotation(logId, { ...params, output_format: 'summary' })
    if (!result.success || !result.data) {
      error.value = result.message || '加载失败'
      return
    }
    if (combatAnalysisService.isAmbiguousResponse(result.data)) {
      error.value = result.data.message || '存在多个同名玩家'
      return
    }
    transform(result.data as PlayerRotationResponse)
  } catch (e: any) {
    error.value = e.response?.data?.message || '网络错误'
  } finally {
    isLoading.value = false
  }
}

function transform(data: PlayerRotationResponse) {
  stats.value = Object.entries(data.skill_frequency)
    .map(([name, count], index) => ({
      name,
      count: count as number,
      percentage: Math.round(((count as number) / data.total_skills) * 100),
      color: colors[index % colors.length],
    }))
    .sort((a, b) => b.count - a.count)
  totalCount.value = data.total_skills
  avgInterval.value = Math.floor(data.duration_ms / data.total_skills)
  topSkill.value = stats.value[0]?.name || '无'
}

watch(() => player, () => {
  stats.value = []
  if (logId) load()
}, { immediate: true })
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.875rem 0;
}
.section-title i {
  color: var(--color-primary);
}
.loading-content, .error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}
.loading-text, .error-text {
  font-size: 0.875rem;
}
.error-text {
  color: var(--color-error);
}
.skills-chart-container {
  margin-bottom: 1.5rem;
}
.skills-chart {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}
.skill-bar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.skill-info {
  min-width: 80px;
  display: flex;
  justify-content: space-between;
}
.skill-name {
  font-size: 0.875rem;
  color: var(--color-text);
}
.skill-count {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}
.skill-bar-bg {
  flex: 1;
  height: 12px;
  background-color: var(--color-bg-secondary);
  border-radius: 6px;
  overflow: hidden;
}
.skill-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease-out;
}
.skill-percentage {
  min-width: 40px;
  text-align: right;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.skills-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.5rem;
}
.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}
.summary-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.summary-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
}
@media (max-width: 640px) {
  .skills-summary {
    grid-template-columns: 1fr;
  }
}
</style>
